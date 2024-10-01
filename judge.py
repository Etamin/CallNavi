import json
data="bank"
models=["GPT","mistral-nemo","gemma2","llama3.1"]
with open("./Questions/"+data+".json", 'r') as file:
            question = json.load(file)
for model in models:
    with open("bank_round1_para_"+model+".json", 'r') as file:
        results = json.load(file)

    count=0
    total=len(results)
    cal={"easy":0,"medium":0,"hard":0}
    for i in range(len(results)):

        pre=results[i]["predict"].replace('\'','').replace('\"','').replace('[','').replace(']','').replace('\n','').replace(' ','').replace('`','').replace('\\','').replace('\n','').lower()
        gt=results[i]["ground_truth"].replace('\'','').replace('\"','').replace('[','').replace(']','').replace('\n','').replace(' ','').replace('`','').replace('\\','').replace('\n','').lower()
        
        if pre==gt:
            count+=1
            cal[question[i]["difficulty"]]+=1
    print(model)
    print(count/total)
    print(cal)