import logging
from datetime import datetime
from typing import Callable, Dict, List, Tuple

from langchain.chains import LLMChain

# kinda almost works with davinci
# model_name = "text-davinci-003"
# from langchain.llms import OpenAI
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema import BaseMessage, OutputParserException
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
from .helpful_scripts import json_dumps

log = logging.getLogger(__name__)


class SummaryResult(BaseModel):
    found: bool = Field(description="whether not the data say anything relevant")
    summary: str = Field(description="text summary")


class TextCorrect(BaseModel):
    correct: bool = Field(description="true if the text meets the constraints")


def get_string_fields_with_values(document: Document) -> dict:
    return {
        field_name: getattr(document, field_name)
        for field_name, field_type in document._fields.items()
        if isinstance(field_type, StringField)
    }


def get_text_correctness(query: str, text: str) -> TextCorrect:
    parser = PydanticOutputParser(pydantic_object=TextCorrect)
    prompt = PromptTemplate(
        template="""
            Does the text below surrounded by triple backticks {query}
            ```{text}```
            {format_instructions}
            Output only a JSON object.
            """,
        input_variables=["query", "text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    llm = ChatAnthropic()
    chain = LLMChain(llm=llm, prompt=prompt)
    output = chain(
        {
            "query": query,
            "text": text,
        }
    )
    text = output["text"]
    bits = text.split("```")
    if len(bits) >= 2:
        text = bits[1]
    return parser.parse(text)


def get_document_summary(query: str, document: Document) -> SummaryResult:
    parser = PydanticOutputParser(pydantic_object=SummaryResult)
    prompt = PromptTemplate(
        template="What does these data from a human say about {query}? "
        "Summarise in a few words from {data}. "
        "Start the summary with it seems like... as if you were talking to the human. "
        "Keep it short and simple. Stay on topic. "
        "Output a JSON object with the following properties: "
        "- `found` whether or not the provided data says anything specific about {query}"
        "- `summary` the text summary",
        input_variables=["query", "data"],
    )
    llm = ChatOpenAI(model_name=SLEEPMATE_PARSER_MODEL_NAME, temperature=0.0)
    chain = LLMChain(llm=llm, prompt=prompt)
    output = chain(
        {
            "query": query,
            "data": json_dumps(get_string_fields_with_values(document)),
        }
    )
    try:
        return parser.parse(output["text"])
    except OutputParserException as e:
        log.error(f"get_document_summary: {e=}")


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


def get_memory_from_messages(
    messages: List[BaseMessage], k: int
) -> ConversationBufferWindowMemory:
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", k=k, return_messages=False
    )
    memory.chat_memory.messages = messages
    return memory


def get_parsed_output(
    query: str,
    get_messages_func: Callable[[int], List[BaseMessage]],
    cls: BaseModel,
    k: int = None,
) -> BaseModel:
    """Get the parsed output from chat_history"""
    # Set up a parser + inject instructions into the prompt template.
    parser = PydanticOutputParser(pydantic_object=cls)
    # if we're going to extract all the fields from the chat history, we need to
    # make sure the history is at least twice as long in order to extract them all
    if k is None:
        k = k = (len(cls.__fields__) * 2) + 5
    memory = get_memory_from_messages(get_messages_func(k=k), k=k + 1)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n"
        "Previous conversation:\n{chat_history}",
        input_variables=["query", "chat_history"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    # llm = OpenAI(model_name=model_name, temperature=0.0)
    llm = ChatOpenAI(model_name=SLEEPMATE_PARSER_MODEL_NAME, temperature=0.0)
    try:
        chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
        output = chain({"query": query})
        return parser.parse(output["text"])
    except OutputParserException as e:
        log.error(f"get_parsed_output: {e=}")


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
        fields[name] = cls(default=field.default, required=field.required, null=True)
    if extra_fields is not None:
        for name, field in extra_fields.items():
            fields[name] = field
    return type(pydantic_model.__name__, (Document,), fields)
