import os
import json
from datetime import datetime,timedelta
import random
import config

os_list=['ubuntu','debian','centos','archlinux','alpine']
enviriment_list=['production','development','testing']
cpu_list=[8,16,32,64,128]
ram_list=[8,16,32,64,128]
status_list=['active','inactive','crashed']


class Server:
    def __init__(self, id):
        self.id = id
        self.name=f'server_{id:02}'
        self.os=random.choice(os_list)
        self.enviriment=random.choice(enviriment_list)
        self.cpu=random.choice(cpu_list)
        self.ram=random.choice(ram_list)
        self.status=random.choices(status_list, weights=[80,15,5])[0]

    def to_dict(self):
        return{
            'id':self.id,
            'name':self.name,
            'os':self.os,
            'enviriment':self.enviriment,
            'cpu':self.cpu,
            'ram':self.ram,
            'status':self.status,
        }
def gen_server(count):
    server_list=[Server(i+1).to_dict() for i in range (count)]
    with open(config.servers_file,'w',encoding='utf-8') as f:
        json.dump(server_list,f,indent=4,ensure_ascii=False)
    return server_list
        
        
        
def gen_message():
    return random.choice([
        f'CPU usage is {random.randint(1,100)}%',
        f'RAM usage is {random.randint(1,100)}%',
        f'network latency is {random.randint(1,300)}ms',
        f'packet loss is {random.randint(0,20)}%',
        f'network traffic is {random.randint(1,1000)}Mbps',
        'connection timeout',
        'service restarted',
    ])

def gen_logs(records,files):
    start=datetime.now()-timedelta(days=7)
    levels=['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    for n in range(files):
        path=os.path.join(config.log1,f'server{n+1}.log')
        with open(path,'w',encoding='utf-8') as f:
            for w in range(records):
                moment=start+timedelta(seconds=random.randint(0,7*24*3600))
                level=random.choices(levels,weights=[70,20,8,2])[0]
                message=gen_message()
                f.write(f"{moment:%Y-%m-%d %H:%M:%S}|server_{n+1:02}|{level}|{message}\n")