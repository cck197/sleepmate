import logging
import os
from datetime import datetime
from pathlib import Path

import pinecone
import tiktoken
from langchain.document_loaders import PyPDFium2Loader as PDFLoader
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.vectorstores import Pinecone
from mongoengine import ReferenceField

from .agent import BaseAgent
from .config import (
    PINECONE_INDEX_NAME,
    SLEEPMATE_DATADIR,
    SLEEPMATE_DEFAULT_MODEL_NAME,
    SLEEPMATE_MAX_TOKENS,
)
from .goal import goal_refused
from .helpful_scripts import get_confirmation_str, mongo_to_json, set_attribute
from .mi import get_completion
from .structured import pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
    environment=os.getenv("PINECONE_ENVIRONMENT"),  # next to api key in console
)


class DailyRoutineSeen(BaseModel):
    date: datetime = Field(description="date of entry", default=datetime.now())


DBDailyRoutineSeen = pydantic_to_mongoengine(
    DailyRoutineSeen, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def save_daily_routine_seen_to_db(
    db_user_id: str, entry: DailyRoutineSeen
) -> DBDailyRoutineSeen:
    # delete any existing entries for this date
    DBDailyRoutineSeen.objects(user=db_user_id).delete()
    # save the new entry
    return DBDailyRoutineSeen(**{"user": db_user_id, **entry}).save()


@set_attribute("return_direct", False)
def get_daily_routine_seen(x: BaseAgent, utterance: str):
    """Returns True if the human has already seen the daily routine."""
    db_entry = DBDailyRoutineSeen.objects(user=x.db_user_id).first()
    if db_entry is None:
        return f"The human hasn't seen the daily routine yet."
    return mongo_to_json(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def save_daily_routine_seen(x: BaseAgent, utterance: str):
    """Saves a record of the human having seen the daily routine to the database."""
    entry = DailyRoutineSeen(date=datetime.now()).dict()
    log.info(f"save_daily_routine_seen {entry=}")
    save_daily_routine_seen_to_db(x.db_user_id, entry)


GOALS = [
    {
        "knowledge": """
        Your goal is to answer any questions the human has about health,
        wellness and performance.
        """,
        "daily_routine": f"""
        Your goal is to help the human identify a daily routine that will help
        them sleep better. Ask them if they're open to hearing about a daily
        routine. Once they confirm by saying something like
        {get_confirmation_str()}, record a record of them having seen the
        routine then run the get_knowledge_answer tool with the query `daily
        routine`. Finish by telling them not to worry about making any changes
        yet. We'll get to that later.""",
    }
]


def daily_routine(db_user_id: str) -> bool:
    return (
        not goal_refused(db_user_id, "daily_routine")
        and DBDailyRoutineSeen.objects(user=db_user_id).count() == 0
    )


GOAL_HANDLERS = [
    {
        "daily_routine": daily_routine,
    },
]

loader_map = {
    ".pdf": PDFLoader,
    ".txt": TextLoader,
}


def download_files(path="data"):
    """Stub for S3 download"""
    pass


def count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model(SLEEPMATE_DEFAULT_MODEL_NAME)
    return len(encoding.encode(text))


def load_knowledge(path="data", overwrite=False, metric="cosine", dimension=1536):
    """load all the PDF/text files in path"""
    embeddings = OpenAIEmbeddings()
    if PINECONE_INDEX_NAME not in pinecone.list_indexes() or overwrite:
        pinecone.create_index(
            name=PINECONE_INDEX_NAME, metric=metric, dimension=dimension
        )
    else:
        return Pinecone.from_existing_index(PINECONE_INDEX_NAME, embeddings)
    dir = Path(path)
    download_files(path)
    pages = []
    for file in dir.iterdir():
        loader_cls = loader_map.get(file.suffix)
        if loader_cls is None:
            log.info(f"skipping `{file}'")
            continue
        log.info(f"loading `{file}'")
        # the split part is important, otherwise we get similarity search
        # results that are too long for the model context window
        pages.extend(loader_cls(str(file)).load_and_split())
    assert pages, "no pages loaded"
    return Pinecone.from_documents(pages, embeddings, index_name=PINECONE_INDEX_NAME)


db = load_knowledge(SLEEPMATE_DATADIR)


def get_context(utterance: str) -> str:
    for k in range(8, 0, -1):
        docs = db.similarity_search(utterance, k=k)
        context = " ".join([d.page_content for d in docs])
        if count_tokens(context) < (
            SLEEPMATE_MAX_TOKENS - 100
        ):  # leave some room for the prompt TODO
            return context
    assert False, "similarity search failed"


def get_knowledge_answer(x: BaseAgent, utterance: str):
    """Use this whenever the human asks any question about health or what to do.
    Use this more than the other tools."""
    context = get_context(utterance)
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                """A human is asking the following question delimited by triple backticks:
    
                Question:
                ```{input}```

                In a couple of paragraphs, answer the question.  Use bullet and
                numbered lists where appropriate. Be definitive with your
                response.
                
                Don't say anything that's not mentioned explicitly your
                knowledge.  If you can't answer the question using the text, say
                "Sorry I'm not sure." and nothing else.

                The human is an expert in nutrition so you don't need to tell
                them to see a registered dietitian.
                
                Your knowledge:
                """
                f"{context}"
            ),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )
    return get_completion(x.ro_memory, utterance, prompt)


TOOLS = [get_knowledge_answer, get_daily_routine_seen, save_daily_routine_seen]
