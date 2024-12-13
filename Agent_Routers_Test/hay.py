from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from typing import List
import sqlite3
import requests
# from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret
from haystack_integrations.components.generators.ollama import OllamaGenerator
import pandas as pd
from haystack import Pipeline
from haystack.components.routers import ConditionalRouter
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack import component
import json

@component
class SQLQuery:

    def __init__(self, sql_database: str):
      self.connection = sqlite3.connect(sql_database, check_same_thread=False)

    @component.output_types(results=List[str], queries=List[str])
    def run(self, queries: List[str]):
        results = []
        for query in queries:
          query=query.replace("```sql","").replace("```","")
          result = pd.read_sql(query, self.connection)
          results.append(f"{result}")
        return {"results": results, "queries": queries}

@component
class RESTCall:
        
    @component.output_types(results=str, queries=List[str])
    def run(self, queries:List[str]):
        print(queries[0])
        call=json.loads(queries[0])
        
        response = requests.get("http://127.0.0.1:5000/"+call["api"], params=call["parameters"])
        return {"results": response.content.decode("utf-8"), "queries": queries}



# ['name':action, 'domain':"sql", ... ]

            
prompt_template_router = """
Create a classification result from the question: {{question}}.

Only if the question is asking about how much did the account ID transfer, please answer "sql".
Only if the question is asking about what is an account's ID of a name, please answer "api".

Only use information that is present in the passage. 
Make sure your response is a simple string only can be 'sql' or 'api'. No explanation or notes.
Answer:
"""


invalid="""
{% if invalid_replies and error_message %}
  You already created the following output in a previous attempt: {{invalid_replies}}
  However, this doesn't comply with the format requirements from above and triggered this exception: {{error_message}}
  Correct the output and try again. Just return the corrected output without any extra explanations.
{% endif %}
"""


api_prompt = """Please select an API function calling. The calling should answer the following Question: {{question}};
The query is to be related to a bank system and include these APIs with descriptions:
APIs: {{apis}};
===============
Make sure your response is only a simple string of API name.
Answer:"""


call_prompt = """Please generate an SQL query. The query should answer the following Question: {{question}};
The query is to be answered for the table is called 'Transactions' with the following
API Name: {{api_name}}
Parameters: {{apipara}};
API Calling format should looks like below:
{{apiformat}}

Make sure your response is a JSON object string without any format lime ```json.
Answer:"""

sql_prompt = """Please generate an SQL query. The query should answer the following Question: {{question}};
            The query is to be answered for the table is called 'Transactions' with the following
            Columns: {{columns}};
            Answer should only include a SQL query string without format like ```sql, no explnations or notes. You should only do question to SQL query translation
            Answer starts with "SELECT":"""

routes = [
        {
            "condition": "{{'sql' in replies[0]}}",
            "output": "{{question}}",
            "output_name": "goto_sql",
            "output_type": str,
        },
        {
            "condition": "{{'api' in replies[0]}}",
            "output": "{{question}}",
            "output_name": "goto_api",
            "output_type": str,
        },
    ]
router = ConditionalRouter(routes=routes)

sql_query = SQLQuery('./bank.sqlite')
api_caller=RESTCall()
# llm = OpenAIGenerator(model="gpt-4",api_key=Secret.from_token(openai_token))
# llm = OllamaGenerator(model="llama3.1", url="http://localhost:11434")


api_format="""
{
   "api":"apiName",
   "parameters":{
      "parameter1":"value1",
      "parameter2":"value2"
   }
}
"""
transaction_colunms="""
Transaction_ID VARCHAR(40) not null primary key,
Time INT,
Client_ID VARCHAR(12) references Source,
Beneficiary_ID VARCHAR(16) references Beneficiary,
Amount Float,
Currency VARCHAR(3),
Transaction_Type VARCHAR(20) not null
"""
api_list="""[GetAccountIDbyName,
GetAccountNamebyID
GetAccount
]"""
pipe = Pipeline()

pipe.add_component("router", router)
pipe.add_component("router_prompt", PromptBuilder(prompt_template_router))
pipe.add_component("sql_prompt", PromptBuilder(sql_prompt))
pipe.add_component("api_prompt", PromptBuilder(api_prompt))
pipe.add_component("call_prompt", PromptBuilder(call_prompt))
# pipe.add_component("routerllm", OpenAIGenerator(model="gpt-4o",api_key=Secret.from_token(openai_token)))
# pipe.add_component("sqlllm", OpenAIGenerator(model="gpt-4o",api_key=Secret.from_token(openai_token)))
# pipe.add_component("apillm", OpenAIGenerator(model="gpt-4o",api_key=Secret.from_token(openai_token)))
# pipe.add_component("callllm", OpenAIGenerator(model="gpt-4o",api_key=Secret.from_token(openai_token)))

pipe.add_component("routerllm", OllamaGenerator(model="gemma2", url="http://localhost:11434"))
pipe.add_component("sqlllm", OllamaGenerator(model="gemma2", url="http://localhost:11434"))
pipe.add_component("apillm", OllamaGenerator(model="gemma2", url="http://localhost:11434"))
pipe.add_component("callllm", OllamaGenerator(model="gemma2", url="http://localhost:11434"))


pipe.add_component("sql_querier", sql_query)
pipe.add_component("api_caller",api_caller)

pipe.connect("router_prompt","routerllm")
pipe.connect("routerllm.replies", "router.replies")

pipe.connect("router.goto_sql", "sql_prompt.question")
pipe.connect("sql_prompt", "sqlllm")
pipe.connect("sqlllm.replies","sql_querier")


pipe.connect("router.goto_api", "api_prompt.question")
pipe.connect("api_prompt", "apillm")
pipe.connect("apillm.replies","call_prompt.api_name")
pipe.connect("call_prompt", "callllm")
pipe.connect("callllm.replies", "api_caller.queries")



result = pipe.run({"question": "How much did the account ID 20001101 transfer all the time?",
"apiformat":api_format,
"columns":transaction_colunms,
"apis":api_list,
"apipara":"""{"name": string}"""
  })
print(result["router.replies"])

print(result["sql_querier"]["results"])

result = pipe.run({"question": "What is account ID of name Sam?",
"apiformat":api_format,
"columns":transaction_colunms,
"apis":api_list,
"apipara":"""{"name": string}"""
})
print(result)

print(result["api_caller"]["results"])

