import json
from tqdm import tqdm
import os
import time
import yaml
from ollama import Client
client = Client(host='http://:11434')

modelst=['gemma2:27b', 'command-r']
datalst=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']


# Ollama Call
def call_response(context,model):
    response = client.chat(model=model, messages=[
    {
        'role': 'user',
        'content': context,
    },
    ])
    return(response["message"]["content"])

def writefile(l,dct):
    str=json.dumps(dct)
    file=open('results_yaml/'+l+".json",'w')
    file.write(str)
    file.close()

for model in modelst: 
    for data in datalst:
        with open("APIs/"+data+".json", 'r') as file:
            API = json.load(file)["api_ports"]
        with open("./Questions/"+data+".json", 'r') as file:
            question = json.load(file)
        func=""
        func=yaml.dump(API)
        prompt_1='''
        Give the API list with describtion below, then give the question in chatbot, please give me the correct API that should be called. 
        =======API list YAML start=======
        '''
        prompt_2='''
        \n=======API list YAML end======= \n\n=======Question start=======
        '''
        prompt_3='''\n=======Question end=======
        Given the user question, and the APIs, classify and give a correct API name and parameters to call. \n
        Answer should be formatted includes API names and parameters in YAML style, looks like :
        ---
        API:
        - APIname1
        - APIname2
        parameters:
        - parameter1ForAPI1: "***"
        - parameter1ForAPI2: "***"
          parameter2ForAPI2: "***"


        If we cannot get some parameter information from the question, set these parameters to "$$$".
        
        NO explanation/notes in answer! Only YAML STRING!"
        '''
 
        result_call=[]


        for q in tqdm(question):
            
            prompt=prompt_1+func+prompt_2+q['question'][0]['content']+prompt_3
            # print(prompt)
            resp=call_response(prompt,model).replace("```json","").replace("```","")
            # print(resp)
            result_call.append({"predit":resp,"ground_truth":str(q["ground_truth"]['API'])})
        writefile(data+"_1_yaml_"+model,result_call)


    
