from datetime import datetime
from pathlib import Path

import tiktoken
from langchain.document_loaders import PyPDFium2Loader as PDFLoader
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ReadOnlySharedMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.vectorstores import Chroma
from mongoengine import ReferenceField

from .config import (
    SLEEPMATE_DATADIR,
    SLEEPMATE_DEFAULT_MODEL_NAME,
    SLEEPMATE_MAX_TOKENS,
)
from .goal import goal_refused
from .helpful_scripts import mongo_to_json, set_attribute
from .mi import get_completion
from .structured import pydantic_to_mongoengine
from .user import DBUser, get_current_user


class DailyRoutineSeen(BaseModel):
    date: datetime = Field(description="date of entry", default=datetime.now())


DBDailyRoutineSeen = pydantic_to_mongoengine(
    DailyRoutineSeen, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def save_daily_routine_seen_to_db(
    user: DBUser, entry: DailyRoutineSeen
) -> DBDailyRoutineSeen:
    # delete any existing entries for this date
    DBDailyRoutineSeen.objects(user=user).delete()
    # save the new entry
    return DBDailyRoutineSeen(**{"user": user, **entry}).save()


@set_attribute("return_direct", False)
def get_daily_routine_seen(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns True if the human has already seen the daily routine."""
    db_entry = DBDailyRoutineSeen.objects(user=get_current_user()).first()
    if db_entry is None:
        return f"The human hasn't seen the daily routine yet."
    return mongo_to_json(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def save_daily_routine_seen(memory: ReadOnlySharedMemory, goal: str, text: str):
    """Saves a record of the human having seen the daily routine to the database."""
    entry = DailyRoutineSeen(date=datetime.now()).dict()
    print(f"save_daily_routine_seen {entry=}")
    save_daily_routine_seen_to_db(get_current_user(), entry)


GOALS = [
    {
        "knowledge": """
        Your goal is to answer any questions the human has about health,
        wellness and performance.
        """,
        "daily_routine": """
        Your goal is to help the human identify a daily routine that will help
        them sleep better. Ask them if they're open to hearing about a daily
        routine. If they say yes, record a record of them having seen the
        routine then run the get_knowledge_answer tool with the query `daily
        routine`.""",
    }
]


def daily_routine():
    return (
        not goal_refused("daily_routine")
        and DBDailyRoutineSeen.objects(user=get_current_user()).count() == 0
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


def load_input_files(path="data", overwrite=False):
    """load all the PDF/text files in path"""
    dir = Path(path)
    db_path = dir / "chroma_db"
    embeddings = OpenAIEmbeddings()
    if db_path.exists() and not overwrite:
        return Chroma(persist_directory=str(db_path), embedding_function=embeddings)
    download_files(path)
    pages = []
    for file in dir.iterdir():
        loader_cls = loader_map.get(file.suffix)
        if loader_cls is None:
            print(f"skipping `{file}'")
            continue
        print(f"loading `{file}'")
        # the split part is important, otherwise we get similarity search
        # results that are too long for the model context window
        pages.extend(loader_cls(str(file)).load_and_split())
    assert pages, "no pages loaded"
    db = Chroma.from_documents(pages, embeddings, persist_directory=str(db_path))
    return db


db = load_input_files(SLEEPMATE_DATADIR)


def get_context(utterance: str) -> str:
    for k in range(8, 0, -1):
        docs = db.similarity_search(utterance, k=k)
        context = " ".join([d.page_content for d in docs])
        if count_tokens(context) < (
            SLEEPMATE_MAX_TOKENS - 100
        ):  # leave some room for the prompt TODO
            return context
    assert False, "similarity search failed"


def get_knowledge_answer(
    memory: ReadOnlySharedMemory, goal: str, utterance: str
) -> str:
    """Use this whenever the human asks a specific technical question about what
    to do, or about sleep. Use this more than the other tools."""  #

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

                Your knowledge:
                """
                f"{context}"
            ),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )
    return get_completion(memory, utterance, prompt)


TOOLS = [get_knowledge_answer, get_daily_routine_seen, save_daily_routine_seen]
