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

from .vectorize import open_faiss_index
from ..models import Message

# TODO: Find a neater way to define these, and maybe a better place to put them.
test_system_message = """Begin!

{chat_history}
Prompt: {input}
{agent_scratchpad}"""

PROMPT = PromptTemplate(
    input_variables=["input", "chat_history", "agent_scratchpad"],
    template=test_system_message
)

llm = ChatOpenAI(temperature=0.5)
llm_chain = PROMPT | llm

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

prompt = hub.pull("hwchase17/structured-chat-agent")

def load_chats(chat_id):
    messages = Message.objects.filter(chat_id=chat_id).order_by('created')
    return list(messages)

def init_agent(chat_id):
    with open("base/services/openai_api_key.txt", "r") as file:
        key = file.read().strip()
    chat = ChatOpenAI(api_key=key, temperature=0.5)

    agent = create_structured_chat_agent(llm=chat, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    memory = ChatMessageHistory(session_id="test-session")
    chats = load_chats(chat_id)

    for chat in chats:
        memory.add_message(chat.body)

    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return agent_with_chat_history

def get_agent_output(agent, human_message, chat_id):
    result = agent.invoke(
        {"input": human_message},
        config={
            "configurable": {
                "session_id": chat_id,
            }
        }
    )

    return result