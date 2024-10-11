import json

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
    file=open('results_washed/'+l+".json",'w')
    file.write(str)
    file.close()
# modelst=[ 'mistral-small','mistral-nemo', 'gemma2', 'gemma2:27b','llama3.1:70b','phi3.5','nemotron-mini']
# ,
# modelst=['gpt-4o','gpt-4o-mini','llama3.1:70b','llama3.1', 'mistral-small','mistral-nemo', 'command-r','llama3.2','gemma2', 'gemma2:27b','phi3:14b','phi3.5','nemotron-mini']
modelst=['xlam']
# 'nexusraven',
datalst=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']
# ['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']
# 'bank', 'shopping', 

#'telecommunications'
prompt_call='''
Give the following API calling string, then an API list JSON, and make it into a JSON format. If you cannot find any information about API calling in the input string, please return an empty object JSON like { }.

If answer said 'Error', give a empty JSON return.

Check the API been called in API list, make sure the type is correct. 

If give a object to a string parameters, transfer it to a string.

If some value of parameters of API are unknown or not fit in our API list, use '$$$' as the position-holder.
If the API call is nested, for example: A(B(string),string), please make the calling order become ['B', 'A'] and the first parameter value of A is '$$$', which means the first parameter is related to an unknow value from function B. 

Remove all unnecessary explanations and notes. Give only the JSON string for answer. No formatting, no label, make sure the output string is JSON loadable.

=======Example of output JSON=====
{
        "API": ["getAccountID", "openRecurringDeposit"],
        "parameters": [
          {"customerID": "123456789"},
          {"customerID": "123456789", "monthlyInstallment": "500", "termLength": "12 months"}
        ]
      }
=======End of example JSON========
!!Note: List in API should only contain the API name list, no parameters, all parameters should be wrapped into a dict list.
=======Begin of API JSON=======
'''

prompt_json='''
Give the following API calling string that might contain a JSON, then an API candidate list JSON, and make the API calling into a JSON format. If you cannot find any information about API calling in the input string, please return an empty object JSON like { }.

If the JSON is already in the string, directly output the JSON with trim and make sure all parameters are loadable.

If the answer says 'Error', give an empty JSON return.

Check the API being called in the API list, and make sure the type is correct. 

If given an object to a string parameters, transfer it to a string.

If some value of API parameters are unknown or do not fit in our API list, use '$$$' as the position-holder.

Remove all unnecessary explanations and notes. Give only the JSON string for the answer. No formatting, no label, make sure the output string is JSON loadable.

=======Example of output JSON=====
{
        "API": ["getAccountID", "openRecurringDeposit"],
        "parameters": [
          {"customerID": "123456789"},
          {"customerID": "123456789", "monthlyInstallment": "500", "termLength": "12 months"}
        ]
      }
=======End of example JSON========
!!Note: List in API should only contain the API name list, no parameters, all parameters should be wrapped into a dict list.
=======Begin of API JSON=======

'''
# wash calling func
for model in modelst:
    count=0
    for data in datalst:
        result_call=[]
        with open("APIs/"+data+".json", 'r') as file:
            API = json.load(file)["api_ports"]
        with open("./Questions/"+data+".json", 'r') as file:
            question = json.load(file)
        with open("./results/"+data+"_0_para_"+model+".json", 'r') as file:
            result = json.load(file)
        
        for i in tqdm(range(len(result))):
            predict = result[i]['predit'].replace('\'','\"').replace('```json','').replace('```','')
            try:   
                newp=json.loads(predict)
                count+=1
            except:
                prompt=prompt_call+json.dumps(API)+'\n=======End of API JSON=======\n=======Begin of calling string=======\n'+predict+'=======End of calling string======='
                resp=call_response(prompt)
                try:
                    newp=json.loads(resp)
                except: 
                    newp={}
            result_call.append({"predict":newp,"ground_truth":question[i]["ground_truth"]})
        
        writefile(data+"_1_washed_"+model,result_call)
    print(model)
    print(count/729)