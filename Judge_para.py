import json


datalst=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']
modelst=['gpt-4o','gpt-4o-mini','llama3.1:70b','llama3.1', 'mistral-small','mistral-nemo', 'command-r','llama3.2','gemma2', 'gemma2:27b','phi3:14b','phi3.5','nemotron-mini','nexusraven','gorilla']

from tqdm import tqdm
from openai import OpenAI
import os
os.environ['OPENAI_API_KEY']=''

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

prompt='''
You will be given a predicted API calling JSON and ground truth couple.
Your task is to provide a 'total rating' scoring on how similar the predicted API calling JSON is to ground truth JSON.
Give your answer as a float on a scale of 0 to 1 with 3 decimals, where 0 means that the predicted JSON is not related to ground truth, and 1.0 means that the answer is completely the same as ground truth.

You should consider if the API calling list is the same or not, and whether all parameters match or not.

Only give a score in [[]], looks like [[1.00]]:

======Begin predict JSON======\n
'''


def AST(predict, gt, difficulty):
    if predict=={} or 'API' not in predict or 'parameters' not in predict:
        return {"order":False, 'structure':False, 'ast':False}
    same_order=False
    ast_match=False
    stru_match=False
    if predict==gt:
        same_order=True
        ast_match=True
        stru_match=True
    else:
        if predict['API']==gt['API']:
            same_order=True
            ast_match=True
            stru_match=True
            if len(gt['parameters'])==len(predict['parameters']):
                for index in range(len(gt['parameters'])):
                    for k in gt['parameters'][index].keys():
                        if k not in predict['parameters'][index]:
                            ast_match=False
                            stru_match=False
                            break
                        else:
                            if gt['parameters'][index][k]!="$$$" and gt['parameters'][index][k]!={}:
                                if gt['parameters'][index][k]!=predict['parameters'][index][k]:
                                    ast_match=False
            else:
                same_order=False
                ast_match=False
                stru_match=False
        else: 
            same_order=False
            ast_match=False
            stru_match=False
        
    return {"order":same_order, 'structure':stru_match, 'ast':ast_match}
for model in modelst:
    count_struc=0
    ast_match=0
    cal_match=0
    count_gpt=0.0
    scal={"easy":0,"medium":0,"hard":0}
    spa={"easy":0,"medium":0,"hard":0}
    for data in datalst:
            with open("./Questions/"+data+".json", 'r') as file:
                question = json.load(file)
            with open("./results_washed/"+data+"_1_washed_"+model+".json", 'r') as file:
                result = json.load(file)
            for i in range(len(result)):
                score=AST(result[i]['predict'],result[i]['ground_truth'],difficulty=question[i]['difficulty'])
                resp=call_response(prompt+json.dumps(result[i]['predict'])+"\n======End of predict JSON======\n======Begin of ground truth JSON======\n"+json.dumps(result[i]['ground_truth'])+"\n======End of ground truth JSON======").replace("[","").replace("]","")
                gptscore=float(resp)
                if score['structure']:
                    count_struc+=1
                if score["order"]:
                    cal_match+=1
                    scal[question[i]["difficulty"]]+=1
                if score["ast"]:
                    ast_match+=1
                    spa[question[i]["difficulty"]]+=1
                count_gpt+=gptscore
                
    print(model)    
    print("GPT score")
    print(count_gpt/729)
    print("Structure Match")
    print(count_struc/729)
    print("API Call\n easy:")
    print(scal["easy"]/456)
    print("medium:")
    print(scal["medium"]/188)
    print("hard:")
    print(scal["hard"]/85)
    print("overall")
    print(cal_match/729)
    print("Para:\n easy:")
    print(spa["easy"]/456)
    print("medium:")
    print(spa["medium"]/188)
    print("hard:")
    print(spa["hard"]/85)
    print("overall")
    print(ast_match/729)
