import json
import yaml
from tqdm import tqdm
from openai import OpenAI
import os
os.environ['OPENAI_API_KEY']=''

client = OpenAI()
def call_response(context):
    response = client.chat.completions.create(
    model='gpt-4o-mini', messages=[
    {
        'role': 'user',
        'content': context,
    },
    ])
    return(response.choices[0].message.content)

def writefile(l,dct):
    string=json.dumps(dct,indent=4, sort_keys=True, default=str)
    file=open('results_yaml/'+l+".json",'w')
    file.write(string)
    file.close()

modelst=['llama3.1','mistral-small','gemma2:27b','command-r']

datalst=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']

prompt_call='''
Give the following API calling string, then an API list YAML, and make it into a YAML format. If you cannot find any information about API calling in the input string, please return an empty YAML ---.

If answer said 'Error', give a empty YAML return.

Check the API been called in API list, make sure the type is correct. 

If give a object to a string parameters, transfer it to a string.

If some value of parameters of API are unknown or not fit in our API list, use '$$$' as the position-holder.
If the API call is nested, for example: A(B(string),string), please make the calling order become ['B', 'A'] and the first parameter value of A is '$$$', which means the first parameter is related to an unknow value from function B. 

Remove all unnecessary explanations and notes. Give only the YAML string for answer. No formatting, no label, make sure the output string is YAML loadable.

=======Example of output yaml=====
---
API:
- getAccountID
- openRecurringDeposit
parameters:
- customerID: '123456789'
- customerID: '123456789'
  monthlyInstallment: '500'
  termLength: 12 months

=======End of example yaml========
!!Note: List in API should only contain the API name list, no parameters, all parameters should be wrapped into a dict list.
=======Begin of API yaml=======
'''

prompt_json='''
Give the following API calling string that might contain a YAML, then an API candidate list YAML, and make the API calling string into a YAML format. 
If you cannot find any information about API calling in the input string, please return an empty object YAML like ---.

If the YAML is already in the string, directly output the YAML with trim and make sure all parameters are loadable.

If the answer says 'Error', give an empty YAML return.

Check the API being called in the API list, and make sure the type is correct. 

If given an object to a string parameters, transfer it to a string.

If some value of API parameters are unknown or do not fit in our API list, use '$$$' as the position-holder.

Remove all unnecessary explanations and notes. Give only the YAML string for the answer. No formatting, no label, make sure the output string is YAML loadable.

=======Example of output yaml=====
---
API:
- getAccountID
- openRecurringDeposit
parameters:
- customerID: '123456789'
- customerID: '123456789'
  monthlyInstallment: '500'
  termLength: 12 months

=======End of example yaml========
!!Note: List in API should only contain the API name list, no parameters, all parameters should be wrapped into a dict list.
=======Begin of API yaml=======

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
        with open("./results_yaml/"+data+"_1_yaml_"+model+".json", 'r') as file:
            result = json.load(file)
        
        for i in tqdm(range(len(result))):
            predict = result[i]['predit'].replace('\'','\"').replace('yaml\n','').replace('```','')
            try:   
                newp=yaml.safe_load(predict)
                count+=1
            except:
                prompt=prompt_json+yaml.dump(API)+'\n=======End of API YAML=======\n=======Begin of calling string=======\n'+predict+'=======End of calling string======='
                resp=call_response(prompt)
                try:
                    newp=yaml.safe_load(resp)
                except: 
                    newp={}
            # print(newp)
            result_call.append({"predict":newp,"ground_truth":question[i]["ground_truth"]})
        
        writefile(data+"_1_washed_"+model,result_call)
    print(model)
    print(count/729)