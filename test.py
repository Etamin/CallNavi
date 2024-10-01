import json
from tqdm import tqdm
from ollama import Client
client = Client(host='http://trux-dgx01.uni.lux:11434')

modelst=['llama3.1','gemma2','mistral-nemo']
datalst=["bank"]

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
    file=open(l+".json",'w')
    file.write(str)


for data in datalst:
    for model in modelst:

        with open("APIs/"+data+".json", 'r') as file:
            API = json.load(file)["api_ports"]

        with open("./Questions/"+data+".json", 'r') as file:
            question = json.load(file)


        prompt_1='''
        Give the API list of a bank system with describtion below, then give the question in chatbot, please give me the correct API that should be called. 
        =======list start=======
        '''
        prompt_2='''
        \n=======JSON end======= 

        =======Question start=======
        '''
        prompt_3='''\n=======Question end=======
        Given the user question, and the APIs, classify and give a correct API name to call. 

        Answer should be formatted in only one line, and only API names in bracket, looks like "['getCustomerDetails','depositFunds']" or "['getCustomerDetails']".

        NO explanation and NO parameters in answer!"
        '''
        result_call=[]
        apistr=""
        for item in API:
            apistr=apistr+item["name"]+", "+item["description"]+"\n"

        for q in tqdm(question):
            
            prompt=prompt_1+apistr+prompt_2+q['question'][0]['content']+prompt_3
            result_call.append({"predit":call_response(prompt,model),"ground_truth":str(q["ground_truth"]["API"])})
        writefile(data+"_round1_APIonly_"+model,result_call)


    
