import json
from tqdm import tqdm
from openai import OpenAI
import os
os.environ['OPENAI_API_KEY']=''
datalst=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']
modelst=['gpt-4o-mini']
client = OpenAI()
def call_response(conversation):
    completion = client.chat.completions.create(
        model='gpt-4o-mini', 
        messages=conversation)
    response = completion.choices[0].message.content
    conversation.append({"role": "assistant", "content": response})
    return(conversation)


def writefile(l,dct):
    str=json.dumps(dct)
    file=open('results_backward/'+l+".json",'w')
    file.write(str)
    file.close()

for model in modelst:    
    for data in datalst:    
        with open("./Questions/"+data+".json", 'r') as file:
            question = json.load(file)
        with open("APIs/"+data+".json", 'r') as file:
            API = json.load(file)["api_ports"]
        func=""
        for a in API:
                func+='Function:\ndef '+a['name']+'('+str(a['parameters']).replace('[',"").replace(']',"")+')\n   \"\"\"\n   '+a['description']+'\n\n   Args:\n   '
                for key in a['parameters']:
                    func+=key+' (str)'
                func+='\n\n   Returns:\n   '+str(a["returnParameter"]).replace('{','').replace('}','').replace('\'','')+'\n   \"\"\"\n\n'

        result_call=[]
        format='''
        {’API’: [’getCustomerDetails’, ’deposit-
        Funds’],
        ’parameters’:[{"parameter1ForCall1":
        "***" },{"parameter1ForCall2": "***",
        "parameter2ForCall2": "***"}]}
        '''
        for q in tqdm(question):
            if q['difficulty']=='hard':
                conversation=[]
                prompt_begin=f'''
                Give the API list of a chat-bot system with descriptions below, then give the question in chatbot, please first give me the one API that can answer the final task in th question.   
                =======API list start=======
                {func}
                =======API list end======= 

                =======Question start=======
                {q}
                =======Question end=======
                Given the user question, and the APIs, classify and give a correct last one task API name and parameters to call. 

                The answer should be formatted into the following JSON format:{format}

                We will solve the question in the next steps.

                NO explanation in the answer!
                '''
                conversation.append({"role": "user", "content": prompt_begin})
                conversation=call_response(conversation)

                prompt_loop='''
                Then please based on the answer before, try to find APIs to fill in the missing information needed to complete the final API call list from the previous answer.
                
                Please also check if the API list has solved all sub-questions in the question. If not, please add other APIs and parameters related to the question in the correct order.

                The answer should be formatted into the JSON format in previous talk.
                
                Check if we can get all input parameters from the questions or not, if we can't please don't put <!stop> after the API list.

                If you think all the information is completed to solve the question, please write a <!stop> after the full API list.

                NO explanation in the answer! Only give API calling JSON!
                '''

                flag=False
                predict=''
                for i in range(5):
                    conversation.append({"role": "user", "content": prompt_loop})
                    conversation=call_response(conversation)
                    if "<!stop>" in conversation[-1]['content']:
                        flag=True
                    if flag:
                        predict=conversation[-1]['content'].replace('<!stop>','')
                        break
                result_call.append({"predict":predict,"ground_truth":str(q["ground_truth"])})
        writefile(data+"_1_"+model,result_call)