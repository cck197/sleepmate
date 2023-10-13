from copy import deepcopy
from datetime import datetime

from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ReadOnlySharedMemory
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
    StringField,
)

# from langchain.chat_models import ChatOpenAI


model_name = "text-davinci-003"
# model_name = "gpt-3.5-turbo"
# model_name = "gpt-4"


def get_parsed_output(query: str, memory: BaseMemory, cls: BaseModel) -> BaseModel:
    """Get the parsed output from chat_history"""
    # Set up a parser + inject instructions into the prompt template.
    parser = PydanticOutputParser(pydantic_object=cls)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\nPrevious conversation:{chat_history}",
        input_variables=["query", "chat_history"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    llm = OpenAI(model_name=model_name, temperature=0.0)
    # llm = ChatOpenAI(model_name=model_name)
    # memory = deepcopy(memory)
    # memory.return_messages = False
    chain = LLMChain(llm=llm, prompt=prompt, memory=tail_memory(memory))
    output = chain({"query": query})
    return parser.parse(output["text"])


def tail_memory(memory: ReadOnlySharedMemory, n: int = 20) -> ReadOnlySharedMemory:
    """Return a read only copy of the memory with only the last n messages."""
    memory_ = deepcopy(memory)
    memory_.memory.chat_memory.messages = memory_.memory.chat_memory.messages[-n:]
    return memory_


def pydantic_to_mongoengine(pydantic_model, extra_fields=None):
    fields = {}
    type_map = {
        str: StringField,
        int: IntField,
        float: FloatField,
        bool: BooleanField,
        datetime: DateTimeField,
    }
    for name, field in pydantic_model.__fields__.items():
        cls = type_map.get(field.outer_type_)
        assert cls is not None, f"Unsupported field type: {field.outer_type_}"
        fields[name] = cls(required=field.required)
    if extra_fields is not None:
        for name, field in extra_fields.items():
            fields[name] = field
    return type(pydantic_model.__name__, (Document,), fields)
