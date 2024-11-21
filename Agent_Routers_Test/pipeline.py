from langchain_community.llms import Ollama
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from langchain.chains import APIChain
from langchain.chains.api import open_meteo_docs
os.environ["TAVILY_API_KEY"]="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"
# class PromptFactory():
#     developer_template = """You are a very smart Python programmer. \
#     You provide answers for algorithmic and computer problems in Python. \
#     You explain the code in a detailed manner. \

#     Here is a question:
#     {input}"""

#     poet_template = """You are a poet who replies to creative requests with poems in English. \
#     You provide answers which are poems in the style of Lord Byron or Shakespeare. \

#     Here is a question:
#     {input}"""

#     wiki_template = """You are a Wikipedia expert. \
#     You answer common knowledge questions based on Wikipedia knowledge. \
#     Your explanations are detailed and in plain English.

#     Here is a question:
#     {input}"""

#     image_creator_template = """You create a creator of images. \
#     You provide graphic representations of answers using SVG images.

#     Here is a question:
#     {input}"""

#     legal_expert_template = """You are a UK or US legal expert. \
#     You explain questions related to the UK or US legal systems in an accessible language \
#     with a good number of examples.

#     Here is a question:
#     {input}"""



#     prompt_infos = [
#         {
#             'name': 'python programmer',
#             'description': 'Good for questions about coding and algorithms',
#             'prompt_template': developer_template
#         },
#         {
#             'name': 'poet',
#             'description': 'Good for generating poems for creatinve questions',
#             'prompt_template': poet_template
#         },
#         {
#             'name': 'wikipedia expert',
#             'description': 'Good for answering questions about general knwoledge',
#             'prompt_template': wiki_template
#         },
#         {
#             'name': 'graphical artist',
#             'description': 'Good for answering questions which require an image output',
#             'prompt_template': image_creator_template
#         },
#         {
#             'name': 'legal expert',
#             'description': 'Good for answering questions which are related to UK or US law',
#             'prompt_template': legal_expert_template
#         }
#     ]



# def generate_destination_chains():
#     """
#     Creates a list of LLM chains with different prompt templates.
#     """
#     prompt_factory = PromptFactory()
#     destination_chains = {}
#     for p_info in prompt_factory.prompt_infos:
#         name = p_info['name']
#         prompt_template = p_info['prompt_template']
#         chain = LLMChain(
#             llm=cfg.llm, 
#             prompt=PromptTemplate(template=prompt_template, input_variables=['input']))
#         destination_chains[name] = chain
#     default_chain = ConversationChain(llm=cfg.llm, output_key="text")
#     return prompt_factory.prompt_infos, destination_chains, default_chain


llm = Ollama(
    base_url="http://trux-dgx01.uni.lux:11434",
    model="llama3"
)  # assuming you have Ollama installed and have llama3 model pulled with `ollama pull llama3 `
tools = [TavilySearchResults(max_results=1)]
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# chain = (
#     PromptTemplate.from_template(
#         """Given the user question below, and the rules, classify it as either being about `API`, `SQL`, `Translator`, or `RAG`. 

# API: asking about account name, profiles;
# SQL: asking about account balance(using account name), transactions, payment;
# Translator: translation task;
# Summary: Summarize text;
# RAG: other questions;

# Only answer the such step+step as "API+SQL" or 1 step as "Translator".
# Do not respond with more than one line.
# Give the correct order of operation.

# <question>
# {question}
# </question>

# Classification:"""
#     )
#     | agent_executor
#     | StrOutputParser()
# )



context="""Given the user question below, and the rules, classify it as either being about `API`, `SQL`, `Translator`, or `RAG`. 

API: asking about account name, profiles;
SQL: asking about account balance(using account name), transactions, payment;
Translator: translation task;
Summary: Summarize text;
RAG: other questions;

Only answer the such step+step as "API+SQL" or 1 step as "Translator".
Do not respond with more than one line.
Give the correct order of operation.

<question>
{question}
"""

from langchain_core.messages import AIMessage, HumanMessage

print(agent_executor.invoke(
    {
        "input": context+ "What is the name of the customer 53?"+"""
        </question>

Classification:""",
        # Notice that chat_history is a string, since this prompt is aimed at LLMs, not chat models
        # "chat_history": context,
    }
))

# print(chain.invoke({"question": "What is the name of the customer 53?"}))

# print(chain.invoke({"question": "What are the type of cards available at BGL?"}))

# print(chain.invoke({"question": "Translate \"I am your father\" in French"}))

# print(chain.invoke({"question": "How much did the customer 53 paid in Germany"}))



# response=llm.invoke("Tell me a joke")
