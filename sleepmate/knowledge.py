import os
from pathlib import Path

from langchain.document_loaders import PyPDFium2Loader as PDFLoader
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ReadOnlySharedMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.vectorstores import Chroma

from .mi import get_completion

model_name = "gpt-4"

loader_map = {
    ".pdf": PDFLoader,
    ".txt": TextLoader,
}

DATADIR = os.environ.get("DATADIR", "data")


def download_files(path="data"):
    """Stub for S3 download"""
    pass


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
        pages.extend(loader_cls(str(file)).load())
    assert pages, "no pages loaded"
    db = Chroma.from_documents(pages, embeddings, persist_directory=str(db_path))
    return db


db = load_input_files(DATADIR)


def get_knowledge_answer(
    memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
) -> str:
    """Use this whenever the human asks a specific technical question about sleep."""
    docs = db.similarity_search(utterance)
    context = " ".join([d.page_content for d in docs])
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                """A human is asking the following question delimited by triple backticks:
    
                Question:
                ```{input}```

                In a couple of paragraphs, answer the question.  Use bullet and
                numbered lists where appropriate.  Do not reveal who you are.
                Be definitive with your response.
                
                Don't say anything that's not mentioned explicitly in the text.
                If you can't answer the question using the text, say "Sorry I'm
                not sure." and nothing else.

                Text:
                """
                f"{context}"
            ),
            # The `variable_name` here is what must align with memory
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )
    return get_completion(memory, utterance, prompt, model_name)


TOOLS = [get_knowledge_answer]
