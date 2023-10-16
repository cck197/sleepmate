import json
from datetime import datetime
from typing import List, Tuple

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

# from langchain.llms import OpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain.schema import BaseMemory
from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    FloatField,
    IntField,
    ListField,
    StringField,
)

from .helpful_scripts import flatten_list

# from langchain.chat_models import ChatOpenAI


# kinda almost works with davinci
# model_name = "text-davinci-003"
# model_name = "gpt-3.5-turbo"
model_name = "gpt-4"


def fix_schema(cls, date_fields):
    s = cls.schema()
    for key in date_fields:
        try:
            del s["properties"][key]["format"]
        except KeyError:
            pass
    return s


def get_memory_tail(
    memory: BaseMemory, k: int = 10, memory_key: str = "chat_history"
) -> BaseMemory:
    """Get the last k messages from memory."""
    new = ConversationBufferWindowMemory(k=k, memory_key=memory_key)
    new.chat_memory.messages = memory.memory.chat_memory.messages[-new.k * 2 :]
    return new


def create_from_positional_args(model_cls, text: str):
    try:
        args = flatten_list(json.loads(text))
    except json.JSONDecodeError:
        return None
    field_names = list(model_cls.__fields__.keys())
    kwargs = {field: arg for field, arg in zip(field_names, args)}
    return model_cls(**kwargs)


def get_parsed_output(
    query: str, memory: BaseMemory, cls: BaseModel, k: int = 10
) -> BaseModel:
    """Get the parsed output from chat_history"""
    # Set up a parser + inject instructions into the prompt template.
    parser = PydanticOutputParser(pydantic_object=cls)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n"
        "Previous conversation:\n{chat_history}",
        input_variables=["query", "chat_history"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    # llm = OpenAI(model_name=model_name, temperature=0.0)
    llm = ChatOpenAI(model_name=model_name, temperature=0.0)
    chain = LLMChain(llm=llm, prompt=prompt, memory=get_memory_tail(memory, k=k))
    output = chain({"query": query})
    return parser.parse(output["text"])


def pydantic_to_mongoengine(pydantic_model, extra_fields=None):
    fields = {}
    type_map = {
        str: StringField,
        int: IntField,
        float: FloatField,
        bool: BooleanField,
        datetime: DateTimeField,
        Tuple[int, int]: ListField,
        List[str]: ListField,
    }
    for name, field in pydantic_model.__fields__.items():
        cls = type_map.get(field.outer_type_)
        assert cls is not None, f"Unsupported field type: {field.outer_type_}"
        fields[name] = cls(default=field.default, required=field.required)
    if extra_fields is not None:
        for name, field in extra_fields.items():
            fields[name] = field
    return type(pydantic_model.__name__, (Document,), fields)
