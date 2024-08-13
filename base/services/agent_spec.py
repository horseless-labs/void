from langchain import hub

from langchain_openai import ChatOpenAI
from langchain.agents import Tool, ZeroShotAgent, AgentExecutor, create_react_agent, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults

from langchain_core.messages import AIMessage, HumanMessage

from vectorize import open_faiss_index

test_system_message = """Begin!

{chat_history}
Prompt: {input}
{agent_scratchpad}"""



PROMPT = PromptTemplate(
    input_variables=["input", "chat_history", "agent_scratchpad"],
    template=test_system_message
)

llm = ChatOpenAI(temperature=0.5)
# llm_chain = LLMChain(llm=llm, prompt=PROMPT)
llm_chain = PROMPT | llm

# memory = ConversationBufferMemory(memory_key="chat_history", input_key="input", return_messages=True)

wiki = WikipediaAPIWrapper()

search = DuckDuckGoSearchRun()

tools = [
    Tool(
        name="Language Model",
        func=llm_chain.invoke,
        description="use this tool for general purpose queries and logic"
    ),
    Tool(
        name="DuckDuckGo",
        func=search.invoke,
        description="useful for when you need to answer questions about current events"
    ),
    Tool(
        name="wikipedia",
        func=wiki.run,
        description="useful for getting more detailed information about a topic, country, event, or person on wikipedia"
    )
]

system = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

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

Question: {input}
Thought:{agent_scratchpad}'''

# prompt = PromptTemplate.from_template(system)
prompt = hub.pull("hwchase17/structured-chat-agent")

def init_agent():
    prefix = test_system_message
    suffix = test_system_message

    with open("openai_api_key.txt", "r") as file:
        key = file.read().strip()
    chat = ChatOpenAI(api_key=key, temperature=0.5)

    llm_chain = prompt | chat
    agent = create_structured_chat_agent(llm=chat, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
    memory = ChatMessageHistory(session_id="test-session")
    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    return agent_with_chat_history

if __name__ == '__main__':
    agent = init_agent()
    human_message = "When was Barack Obama born?"
    agent.invoke(
        {"input": human_message},
        config={"configurable": {"session_id": "test-session"}}
    )