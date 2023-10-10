import re
from datetime import date
from typing import Any, List, Union

from langchain.agents import (
    AgentExecutor,
    AgentOutputParser,
    LLMSingleActionAgent,
    Tool,
)
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.prompts import BaseChatPromptTemplate
from langchain.schema import (
    AgentAction,
    AgentFinish,
    HumanMessage,
    OutputParserException,
)


def insomnia_severity_index(word: str) -> str:
    """Use this when the conversation history is empty or human has yet to agree
    to the Insomnia Severity Index survey."""
    return "insomnia_severity_index"


def open_focus(word: str) -> str:
    """Use this when the human has completed the Valued Living Questionnaire."""
    return "open_focus"


def leaves_on_a_stream(word: str) -> str:
    """Use this when the human has completed the Open Focus exercise."""
    return "leaves_on_a_stream"


def valued_living(word: str) -> str:
    """Use this when the human has recorded a SEEDS diary entry."""
    return "valued_living"


def diary_probe(word: str) -> str:
    """Use this when the human has completed the Insomnia Severity Index, but
    has yet to agree to doing a sleep diary."""
    return "diary_probe"


def diary_entry(word: str) -> str:
    """Use this after the human has agreed to do a sleep diary, and if it has
    been more than two days since the last sleep diary entry. Get today's date
    and subtract the last sleep diary entry date from it. If the difference is
    greater than 2, ask if the human would like to record a sleep diary
    entry."""
    return "diary_entry"


def daily_routine(word: str) -> str:
    """Use this after the human has completed at least one sleep diary entry."""
    return "daily_routine"


def seeds_probe(word: str) -> str:
    """Use this to set up a SEEDS diary after the human was shown a daily
    routine."""
    return "seeds_probe"


def seeds_entry(word: str) -> str:
    """Use this to record a SEEDS diary entry after the human has defined their
    SEEDS."""
    return "seeds_entry"


def get_date(word: str):
    """Returns todays date, use this for any questions related to knowing
    todays date. This function will always return todays date - any date
    mathematics should occur outside this function."""
    return str(date.today())


tools = [
    Tool(name=t.__name__, func=t, description=t.__doc__, return_direct=True)
    for t in [
        get_date,
        insomnia_severity_index,
        open_focus,
        leaves_on_a_stream,
        valued_living,
        diary_probe,
        diary_entry,
        daily_routine,
        seeds_probe,
        seeds_entry,
    ]
]
tools.extend(
    [
        Tool(name=t.__name__, func=t, description=t.__doc__, return_direct=False)
        for t in [
            get_date,
        ]
    ]
)


# Set up a prompt template
class CustomPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n    ".join(
            [f"- {tool.name}: {tool.description}" for tool in self.tools]
        )
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]


class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise OutputParserException(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(
            tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output
        )


class MetaX(object):
    def __init__(self, *args, **kwargs) -> None:
        self.agent_executor = get_meta_agent(*args, **kwargs)

    def __call__(self, *args: Any, **kwds: Any) -> str:
        return self.agent_executor.run("what's the next action?")


def get_meta_agent(
    memory: ConversationBufferMemory, model_name="gpt-4-0613"
) -> AgentExecutor:
    template = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}

    The order of the tools is unimportant! Consider each tool carefully.

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Previous conversation history:
    {chat_history}

    New question: {input}
    {agent_scratchpad}"""

    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps", "chat_history"],
    )
    output_parser = CustomOutputParser()
    llm_chain = LLMChain(
        llm=ChatOpenAI(temperature=0, model_name=model_name),
        prompt=prompt,
    )
    tool_names = [tool.name for tool in tools]
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names,
    )
    # memory = copy.deepcopy(memory)
    # memory.return_messages = False
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=ReadOnlySharedMemory(memory=memory),
    )
