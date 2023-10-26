from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache


def setup_cache():
    set_llm_cache(
        SQLiteCache(database_path="/Users/cck197/Downloads/virtual_greg/.langchain.db")
    )
