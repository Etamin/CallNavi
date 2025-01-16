import json
from tqdm import tqdm
import os
from openai import OpenAI
from ollama import Client
client = Client(host='http://.uni.lux:11434')

modelst=['llama3.1', 'mistral-small','mistral-nemo', 'gemma2', 'gemma2:27b','command-r','llama3.2']
datalst=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']

# client = OpenAI()
# def call_response(context,model):
#     response = client.chat.completions.create(
#     model=model, messages=[
#     {
#         'role': 'user',
#         'content': context,
#     },
#     ])
#     return(response.choices[0].message.content)


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
    file=open('results_stab/'+l+".json",'w')
    file.write(str)
    file.close()

for model in modelst:
    for it in range(5): 
        for data in datalst:
            # Load the API prediction 
            with open("APIs/"+data+".json", 'r') as file:
                API = json.load(file)["api_ports"]

            with open("./Questions/"+data+".json", 'r') as file:
                question = json.load(file)
            func=""
            with open("results_APIonly/"+data+"_1_APIonly_GPTmini.json", 'r') as file:
                callst = json.load(file)
            call=json.loads(callst[i]['predit'].replace("\'","\""))
            for c in call:
                for a in API:
                    if a['name']==c:
                        func+='Function:\ndef '+a['name']+'('+str(a['parameters']).replace('[',"").replace(']',"")+')\n   \"\"\"\n   '+a['description']+'\n\n   Args:\n   '
                        for key in a['parameters']:
                            func+=key+' (str)'
                        func+='\n\n   Returns:\n   '+str(a["returnParameter"]).replace('{','').replace('}','').replace('\'','')+'\n   \"\"\"\n\n'

            prompt_1='''
            Give the API list with describtion below, then give the question in chatbot, please give me the correct API that should be called. 
            =======list start=======
            '''
            prompt_2='''
            \n=======JSON end======= \n\n=======Question start=======
            '''
            prompt_3='''\n=======Question end=======
            Given the user question, and the APIs, classify and give a correct API name and parameters to call. \n
            The output MUST strictly adhere to the following JSON format, and NO other text MUST be included.
            The example format is as follows. Please make sure the parameter type is correct. 
            {'API': ['APIname1', 'APIname2'], 'parameters':[{"parameter1ForAPI1": "***" },{"parameter1ForAPI2": "***", "parameter2ForAPI2": "***"}]}


            If we cannot get some parameter information from the question, set these parameters to "$$$".
            
            NO explanation/notes in answer! Only JSON!"
            '''
            
            result_call=[]
            # apistr=""
            # for item in API:
            #     apistr=apistr+item["name"]+", "+item["description"]+"\n"

            for q in tqdm(question):
                
                prompt=prompt_1+func+prompt_2+q['question'][0]['content']+prompt_3
                # print(prompt)
                resp=call_response(prompt,model)
                result_call.append({"predit":resp,"ground_truth":str(q["ground_truth"])})
                # print(resp)
            writefile(data+"_1_para_"+"xlam",result_call)


    
