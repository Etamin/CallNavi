import json


data=['bank', 'shopping',  'logistics','aviation', 'hospital','gov', 'hr',  'hotel', 'insurance', 'telecommunications']


for ar in data:
    with open("./Questions/"+ar+".json", 'r') as file:
            questions = json.load(file)
    count=0
    cal={"easy":0,"medium":0,"hard":0}
    for q in questions:
        cal[q["difficulty"]]+=1
        count+=1
    print(ar)
    print(cal)
    print(count)
