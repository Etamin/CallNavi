import json
from tqdm import tqdm
from openai import OpenAI
import os
os.environ['OPENAI_API_KEY']='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'

client = OpenAI()
def call_response(context):
    response = client.chat.completions.create(
    model='gpt-4o', messages=[
    {
        'role': 'user',
        'content': context,
    },
    ])
    return(response.choices[0].message.content)

def writefile(l,dct):
    str=json.dumps(dct)
    file=open(l+".json",'w')
    file.write(str)

with open("APIs/bank.json", 'r') as file:
    API = json.load(file)["api_ports"]

with open("./Questions/bank.json", 'r') as file:
    question = json.load(file)


prompt_1='''
Give the API list of a bank system in JSON file, then give the question in chatbot, please give me the correct API that should be called. 
=======JSON start=======
'''
prompt_2='''
\n=======JSON end======= 

=======Question start=======
'''
prompt_3='''\n=======Question end=======
Given the user question, and the APIs, classify and give a correct API name and parameters to call. 

Answer should be formatted includes API names and parameters in JSON style, looks like :
{'API': ['getCustomerDetails', 'depositFunds'], 'parameters':[{"***": "***" },{"***": "***", "***": "***"}]}

If we cannot get some parameter information from the question, set these parameters to "$$$".

NO explanation/notes in answer! Only the JSON string!"
        '''
result_call=[]
for q in tqdm(question):
    
    prompt=prompt_1+str(API)+prompt_2+q['question'][0]['content']+prompt_3
    result_call.append({"predit":call_response(prompt),"ground_truth":str(q["ground_truth"])})
writefile("bank_round1_para_GPT",result_call)


    
