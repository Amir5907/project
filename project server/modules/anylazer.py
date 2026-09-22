import os
import json
import config
from modules import parser

def load_records(paths):
    records=[]
    for record in parser.parse(paths):
        records.append({
            'date':record.date,
            'time':record.time,
            'server':record.server,
            'level':record.level,
            'message':norm(record.message),
        })
    return records

def norm(message):
    words=[]
    for w in message.split():
        digit=False
        for ch in w:
            if ch.isdigit():
                digit=True
        if digit:
            words.append('N')
        else:
            words.append(w)
    return ' '.join(words)

def group_by(records,field):
    res={}
    for r in records:
        key=r[field]
        if key in res:
            res[key]+=1
        else:
            res[key]=1
    return res

def analyze(records):
    result={}
    result['total']=len(records)
    result['level']=group_by(records,'level')
    result['server']=group_by(records,'server')
    result['date']=group_by(records,'date')
    result['message']=group_by(records,'message')
    return result

def show(result):
    print('всего записей:',result['total'])
    for name in ['level','server','date','message']:
        print('=====',name,'=====')
        for key in sorted(result[name]):
            print(key,'-',result[name][key])

def save(data,name):
    path=os.path.join(config.data,name)
    try:
        with open(path,'w',encoding='utf-8') as f:
            json.dump(data,f,indent=4,ensure_ascii=False)
        print('сохранено',path)
    except Exception as e:
        print(f'ошибка при сохранении {path}: {e}')

def run(paths):
    records=load_records(paths)
    if not records:
        print('записей нет')
        return
    result=analyze(records)
    show(result)
    save(records,'records.json')
    save(result,'analysis.json')