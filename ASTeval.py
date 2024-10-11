import json
from tqdm import tqdm
from openai import OpenAI
import os
os.environ['OPENAI_API_KEY']=''

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
As a scoring system, please based on the two JSONs given below, calculate the similarity score from prediction to ground truth. 
If the JSON is in the Same content, give a 1.0 score. If all content does not match, give 0.0.

If the prediction is not a complete JSON, the score will not be higher than 0.5.

Ignore symbols and comments.

If in parameter part, there is a '$$$' in the position, ignore the same parameter in prediction.

ONLY give the score digits back, maxium 3 decimal places.

=========Predict JSON begins=========\n
'''

for model in models:
    with open("bank_round1_para_"+model+".json", 'r') as file:
        results = json.load(file)
    count=0.0
    print(len(results))
    for result in tqdm(results):
        resp=call_response(prompt_1+result['predict']+'\n=========Predict JSON ends=========\n=========Ground-truth JSON begins========='+result['ground_truth']+"\n=========Ground-truth JSON ends=========\n No explanation, no notes, only a float between 0 and 1.")
        count+=float(resp)
    print(count/len(results))
