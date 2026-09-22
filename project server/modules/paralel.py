import asyncio
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

import config
from modules import parser
from utilits import helpers

def analyze_file(path):
    res={'total':0,'levels':{},'anomalies':0,'cpu_sum':0,'cpu_count':0}
    limit=config.settings['anomalies_threshold']*100
    for r in parser.file_parse(path):
        res['total']+=1
        res['levels'][r.level]=res['levels'].get(r.level,0)+1
        value=helpers.number(r.message)
        if value is None:
            continue
        if 'usage' in r.message and value>limit:
            res['anomalies']+=1
        if r.message.startswith('CPU'):
            res['cpu_sum']+=value
            res['cpu_count']+=1
    return res

def merge(parts):
    total={'total':0,'levels':{},'anomalies':0,'cpu_sum':0,'cpu_count':0}
    for res in parts:
        total['total']+=res['total']
        total['anomalies']+=res['anomalies']
        total['cpu_sum']+=res['cpu_sum']
        total['cpu_count']+=res['cpu_count']
        for level,count in res['levels'].items():
            total['levels'][level]=total['levels'].get(level,0)+count
    return total

def sequential(paths):
    return merge(analyze_file(path) for path in paths)

def threads(paths,workers=None):
    if workers is None:
        workers=config.settings['max_threads']
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return merge(pool.map(analyze_file,paths))

def processes(paths,workers=None):
    if workers is None:
        workers=config.settings['max_processing']
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return merge(pool.map(analyze_file,paths))

async def read_file(path):
    return await asyncio.to_thread(analyze_file,path)

async def gather_files(paths):
    tasks=[read_file(path) for path in paths]
    parts=await asyncio.gather(*tasks)
    return merge(parts)

def run_async(paths):
    return asyncio.run(gather_files(paths))
