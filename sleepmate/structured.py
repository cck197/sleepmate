import json
import logging
from datetime import datetime
from typing import List, Tuple

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

# kinda almost works with davinci
# model_name = "text-davinci-003"
# from langchain.llms import OpenAI
from langchain.memory import ReadOnlySharedMemory
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain.schema import OutputParserException
from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    FloatField,
    IntField,
    ListField,
    StringField,
)

from .config import SLEEPMATE_PARSER_MODEL_NAME
from .helpful_scripts import flatten_list

log = logging.getLogger(__name__)


def fix_schema(cls, date_fields):
    """Remove the format from date fields to keep the PydanticOutputParser
    happy."""
    s = cls.schema()
    for key in date_fields:
        try:
            del s["properties"][key]["format"]
        except KeyError:
            pass
    return s


def get_parsed_output(
    query: str, memory: ReadOnlySharedMemory, cls: BaseModel, k: int = None
) -> BaseModel:
    """Get the parsed output from chat_history"""
    # Set up a parser + inject instructions into the prompt template.
    parser = PydanticOutputParser(pydantic_object=cls)
    # if we're going to extract all the fields from the chat history, we need to
    # make sure the history is at least twice as long in order to extract them all
    if k is None:
        k = k = (len(cls.__fields__) * 2) + 5

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n"
        "Previous conversation:\n{chat_history}",
        input_variables=["query", "chat_history"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    # llm = OpenAI(model_name=model_name, temperature=0.0)
    llm = ChatOpenAI(model_name=SLEEPMATE_PARSER_MODEL_NAME, temperature=0.0)
    try:
        # the prompt template expects a string, so we need to set this to False
        return_messages = memory.memory.return_messages
        memory.memory.return_messages = False
        k_ = memory.memory.k
        memory.memory.k = k
        chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
        output = chain({"query": query})
        return parser.parse(output["text"])
    except OutputParserException as e:
        log.error(f"get_parsed_output: {e=}")
    finally:
        memory.memory.return_messages = return_messages
        memory.memory.k = k_


def pydantic_to_mongoengine(pydantic_model, extra_fields=None):
    """Convert a pydantic model to a mongoengine model."""
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
