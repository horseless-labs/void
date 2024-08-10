from langchain_openai import ChatOpenAI
from langchain.agents import Tool, ZeroShotAgent, AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory

from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_community.utilities import WikipediaAPIWrapper

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

memory = ConversationBufferMemory(memory_key="chat_history", input_key="input", return_messages=True)

wiki = WikipediaAPIWrapper()

tools = [
    Tool(
        name="Language Model",
        func=llm_chain.invoke,
        description="use this tool for general purpose queries and logic"
    ),
    Tool(
        name="wikipedia",
        func=wiki.run,
        description="useful for getting general information about a topic, country, event, or person on wikipedia"
    )
]

template = '''Answer the following questions as best you can. You have access to the following tools:

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

prompt = PromptTemplate.from_template(template)

def init_agent():
    prefix = test_system_message
    suffix = test_system_message

    # prompt = ZeroShotAgent.create_prompt(tools, prefix=prefix, suffix=suffix,
    #                                      input_variables=["input", "chat_history", "agent_scratchpad"])
    
    # llm_chain = LLMChain(llm=ChatOpenAI(temperature=0.5), prompt=prompt)
    with open("openai_api_key.txt", "r") as file:
        key = file.read().strip()
    chat = ChatOpenAI(api_key=key, temperature=0.5)

    llm_chain = prompt | chat
    # agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    agent = create_react_agent(llm=chat, tools=tools, prompt=prompt)
    agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
    return agent_chain

if __name__ == '__main__':
    agent = init_agent()