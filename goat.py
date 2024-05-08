# %%
from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
from langchain_core.prompts.chat import MessagesPlaceholder

from custom_tools import get_nearby_store

# %%
PREFIX = """Answer the following questions as best you can without doing any redundant steps. You have access to the following tools:"""
FORMAT_INSTRUCTIONS = """Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question that includes your last thought"""
SUFFIX = """Begin!

Question: {input}
Thought:{agent_scratchpad}"""


class GOAT:
    def __init__(self):
        load_dotenv(".env")
        self.custom_tools = self.get_custom_tools()
        self.chat_history = MessagesPlaceholder(variable_name="chat_history")
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def get_custom_tools(self, tool_names=list()):
        from langchain.agents import Tool

        tools = []
        if "search" in tool_names:
            from langchain_community.utilities import GoogleSearchAPIWrapper
            
            search = GoogleSearchAPIWrapper()
            search_tool = Tool(
                name="Google Search",
                func=search.run,
                description="A powerful and versatile information retrieval tool that efficiently navigates the vast expanse of the internet to provide users with relevant and diverse results."
            )
            tools.append(search_tool)
        if "locator" in tool_names:
            locator_tool = Tool(
                name="Find a Business",
                func=get_nearby_store,
                description="A tool that searches for nearby convenience stores. Takes as input a query: how you would search for it on google."
            )
            tools.append(locator_tool)
        return tools

    def get_model(self, model_type="chatgpt"):
        if model_type == "lamacpp":
            from langchain_community.llms import LlamaCpp
            from langchain_experimental.chat_models import Llama2Chat

            llm = LlamaCpp(
                model_path="./models/llama-2-13b-chat.Q5_K_M.gguf",
                streaming=False, 
                n_ctx=1024,
                n_gpu_layers=-1,
                n_batch = 512
            )
            model = Llama2Chat(llm=llm)
            return model
        elif model_type == "chatgpt":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(temperature=0)
        else:
            raise NotImplementedError

    def run(self, prompt):
        from langchain.agents import load_tools, initialize_agent
        from langchain.agents.agent_types import AgentType

        llm = self.get_model()

        tools = load_tools(["llm-math"], llm=llm)
        tools.extend(self.custom_tools)

        agent = initialize_agent(
            tools, 
            llm, 
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, 
            verbose=True, 
            handle_parsing_errors=True,
            agent_kwargs={
                'prefix':PREFIX,
                'format_instructions':FORMAT_INSTRUCTIONS,
                'suffix':SUFFIX,
                "memory_prompts": [self.chat_history],
                "input_variables": ["input", "agent_scratchpad", "chat_history"]
            },
            memory=self.memory
        )
        return agent.run(prompt)
