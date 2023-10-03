from functools import partial

from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool


def get_tools(funcs, memory: ReadOnlySharedMemory) -> list[Tool]:
    return [
        Tool.from_function(
            func=partial(f, memory),
            name=f.__name__,
            description=f.__doc__,
            return_direct=True,
        )
        for f in funcs
    ]


def get_agent(
    funcs,
    system_description,
    model_name="gpt-3.5-turbo-0613",
    memory_key="chat_history",
    verbose=True,
):
    memory = ConversationBufferMemory(memory_key=memory_key, return_messages=True)
    ro_memory = ReadOnlySharedMemory(memory=memory)
    tools = get_tools(funcs, ro_memory)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_description),
            MessagesPlaceholder(variable_name=memory_key),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = OpenAIFunctionsAgent(
        llm=ChatOpenAI(temperature=0, model=model_name), tools=tools, prompt=prompt
    )
    return AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=verbose)
