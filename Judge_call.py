import json
modelst=['xlam']
datalst=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']

for model in modelst:
    count=0
    total=0
    cal={"easy":0,"medium":0,"hard":0}
    cnt={"easy":0,"medium":0,"hard":0}
    for data in datalst:
        with open("./Questions/"+data+".json", 'r') as file:
            question = json.load(file)
        with open("results/"+data+"_1_APIonly_"+model+".json", 'r') as file:
                results = json.load(file)
        total+=len(results)
        for i in range(len(results)):

            pre=results[i]["predit"].replace('\'','').replace('\"','').replace('[','').replace(']','').replace('\n','').replace(' ','').replace('`','').replace('\\','').replace('\n','').lower()
            gt=results[i]["ground_truth"].replace('\'','').replace('\"','').replace('[','').replace(']','').replace('\n','').replace(' ','').replace('`','').replace('\\','').replace('\n','').lower()
            cnt[question[i]["difficulty"]]+=1
            if pre==gt:
                count+=1
                cal[question[i]["difficulty"]]+=1
    print(model)
    print(count/total)
    print("easy:")
    print(cal["easy"]/cnt["easy"])
    print("medium:")
    print(cal["medium"]/cnt["medium"])
    print("hard:")
    print(cal["hard"]/cnt["hard"])