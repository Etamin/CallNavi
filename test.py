import json
from tqdm import tqdm
import os
from openai import OpenAI
from ollama import Client
client = Client(host='http://:11434')
# 'command-r','llama3.1',,
# modelst=['llama3.1', 'mistral-small','mistral-nemo', 'gemma2', 'gemma2:27b',]
# 'phi3:14b','command-r','llama3.2',
# modelst=[ 'llama3.1:70b','phi3.5','nemotron-mini']
modelst=['llama3.1:70b','llama3.1', 'mistral-small','mistral-nemo', 'gemma2:27b','gemma2', 'command-r','phi3:14b','nemotron-mini','llama3.2','phi3.5',]
datalst=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']
# os.environ['OPENAI_API_KEY']=''

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
            
            with open("APIs/"+data+".json", 'r') as file:
                API = json.load(file)["api_ports"]

            with open("./Questions/"+data+".json", 'r') as file:
                question = json.load(file)
            func=""
            for a in API:
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
            Answer should be formatted includes API names and parameters in JSON style, looks like :
            {'API': ['getCustomerDetails', 'depositFunds'], 'parameters':[{"parameter1ForCall1": "***" },{"parameter1ForCall2": "***", "parameter2ForCall2": "***"}]}


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
                result_call.append({"predit":call_response(prompt,model),"ground_truth":str(q["ground_truth"])})
            writefile(data+"_"+str(it)+"_para_"+model,result_call)


    
