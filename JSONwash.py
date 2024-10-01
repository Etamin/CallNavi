import json
from tqdm import tqdm
from openai import OpenAI
import os
os.environ['OPENAI_API_KEY']='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'

client = OpenAI()

# models=["mistral-nemo","gemma2","llama3.1"]
models=['GPT']
def call_response(context):
    response = client.chat.completions.create(
    model='gpt-4o', messages=[
    {
        'role': 'user',
        'content': context,
    },
    ])
    return(response.choices[0].message.content)
prompt_1='''


=========Predict JSON begins=========\n
'''

for model in models:
    with open("bank_round1_para_"+model+".json", 'r') as file:
        results = json.load(file)
    count=0.0
    print(len(results))
    for result in tqdm(results):
        resp=call_response(prompt_1+result['predict']+'\n=========Predict JSON ends=========')
        count+=float(resp)
    print(count/len(results))