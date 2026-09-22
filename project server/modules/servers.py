import os 
import json
import config

def load_servers():
    if not os.path.exists(config.servers_file):
        return[]
    try:
        with open(config.servers_file,'r',encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return[]

def active(server_list):
    return [s for s in server_list if s.get('status')=='active']

def problem(server_list):
    return [s for s in server_list if s.get('status')!='active']

def find(server_list,text):
    text=text.strip().lower()
    if not text:
        return []
    res=[]
    for s in server_list:
        if text in str(s.get('name','')).lower() or text==str(s.get('id')):
            res.append(s)
    return res

def one(server_list,text):
    res=find(server_list,text)
    if not res:
        return None
    return res[0]

def line(server):
    return (f"{str(server.get('id','-')):>3}  "
            f"{str(server.get('name','-')):<12} "
            f"{str(server.get('status','-')):<9} "
            f"{str(server.get('os','-')):<10} "
            f"cpu {str(server.get('cpu','-')):<4} "
            f"ram {server.get('ram','-')}")

def show_list(server_list):
    if not server_list:
        print('ничего не найдено')
        return
    for server in server_list:
        print(line(server))
    print('всего:',len(server_list))

def show_info(server):
    print('===== информация о сервере =====')
    for key in ('id','name','os','enviriment','cpu','ram','status'):
        print(f'{key:<12} {server.get(key,"-")}')
