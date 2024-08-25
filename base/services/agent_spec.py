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

from langchain_community.callbacks.manager import get_openai_callback

# Handle token cost
from langchain_community.callbacks.openai_info import get_openai_token_cost_for_model
from langchain.callbacks.base import AsyncCallbackHandler
import tiktoken

from typing import List, Any, Dict

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

# Changes to AgentExecutors to enable token-by-token streaming broke
# get_openai_callback(). Borrowing a workaround from
# https://github.com/langchain-ai/langchain/issues/16798 until there is a fix.
# TODO: check for bug fixes there.
# use get_openai_token_cost_for_model to calculate cost
class OpenAITokenAsyncHandler(AsyncCallbackHandler):
    async def on_llm_start(
        self,
        serialized: Dict[str, Any],
        # serialized,
        prompts: List[str],
        **kwargs: Any,
        # **kwargs,
    ) -> None:
        encoding = tiktoken.get_encoding("cl100k_base")
        prompts_string = ''.join(prompts)
        self.num_tokens = len(encoding.encode(prompts_string))
        print("NUM TOKENS: ", self.num_tokens)


    async def on_llm_end(self, response, **kwargs) -> None:
        """Run when chain ends running."""
        text_response = response.generations[0][0].text
        encoding = tiktoken.get_encoding("cl100k_base")
        self.response_string = len(encoding.encode(text_response))
        print("NUM TOKENS RESPONSE: ", self.response_string)

    def get_tokens_info(self):
        return self.num_tokens, self.response_string

def load_chats(chat_id):
    messages = Message.objects.filter(chat_id=chat_id).order_by('created')
    return list(messages)

def init_agent(chat_id):
    with open("base/services/openai_api_key.txt", "r") as file:
        key = file.read().strip()

    tt_cb = OpenAITokenAsyncHandler()

    chat = ChatOpenAI(api_key=key,
                      temperature=0.5,
                      callbacks=[tt_cb]
                      )

    agent = create_structured_chat_agent(llm=chat, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent,
                                                        tools=tools,
                                                        verbose=True,
                                                        handle_parsing_errors=True)
    agent_executor.max_execution_time = 15
    
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

    return agent_with_chat_history, tt_cb

async def get_agent_output(agent, human_message, chat_id):
    agent_response = await agent.ainvoke(
        {"input": human_message},
        config={
            "configurable": {
                "session_id": chat_id,
            }
        }
    )

    return agent_response