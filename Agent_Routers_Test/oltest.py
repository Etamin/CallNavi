import outlines
from enum import Enum
from pydantic import BaseModel, constr

model = outlines.models.transformers("meta-llama/Meta-Llama-3-8B-Instruct")

class router(BaseModel):
    route:int


prompt = """
We have these tools in our platform, here is their functions and 
1, API: give customer name, get the ID;
2, SQL: get customer transaction, payment and balance, only with his/her ID;
3, Translator: translate other languages to English;
4, RAG: other common questions or document retrieval;
5, Summary: summarize text;
        
Given the user question below, and the rules above, classify and give a correct next step route from 1 to 5. 

<question>
Translate \"I am your father\" in French.
<\question>
"""

# generator = outlines.generate.json(model, router)
# answer = generator(prompt)
# print(answer)


class getID(BaseModel):
    name: str

class getBalance(BaseModel):
    user_id:str 
    date: str

# generator = outlines.generate.json(model, getID)
# id = generator('''
# You should build the API JSON to get a response, 
# <question>
# What is the account ID of the customer Sam?
# <\question>
# ''')
# print(id)

generator = outlines.generate.json(model, getBalance)
id = generator('''
You should build the API JSON to get a response, 
<question>
What is the balance of account LN123456 today ?
<\question>
''')
print(id)