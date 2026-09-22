import numpy as np
import pandas as pd
import config
from modules import anylazer, parser
from utilits import display, helpers

levels=['ERROR','CRITICAL','WARNING']

metrics=[
    ('CPU %','CPU'),
    ('RAM %','RAM'),
    ('NETWORK LATENCY ms','network latency'),
    ('PACKET LOSS %','packet loss'),
    ('NETWORK TRAFFIC Mbps','network traffic'),
]

def count_level(records,level):
    res={}
    for r in records:
        if r['level']==level:
            if r['server'] in res:
                res[r['server']]+=1
            else:
                res[r['server']]=1
    return res

def top(counts,n):
    items=sorted(counts.items(),key=lambda x:x[1],reverse=True)
    return items[:n]

def problem_servers(records,n):
    result={}
    for level in levels:
        result[level]=top(count_level(records,level),n)
    return result

def show(result):
    print('\n========== Проблемные серверы ==========')
    for level in result:
        print(f'\nПроблемные серверы ({level}):')
        if not result[level]:
            print('нет записей')
        for server,count in result[level]:
            print(f'{server}   {level}: {count}')

def run(paths,n=5):
    records=anylazer.load_records(paths)
    if not records:
        print('записей нет')
        return
    result=problem_servers(records,n)
    show(result)
    input('\nнажми Enter чтобы вернуться в меню')

def get_values(paths,word):
    values=[]
    for r in parser.parse(paths):
        if word in r.message:
            value=helpers.number(r.message)
            if value is not None:
                values.append(value)
    return values

def np_stats(name,values):
    arr=np.array(values)
    print('=====',name,'=====')
    if len(arr)==0:
        print('нет данных')
        return
    print('среднее -',round(np.mean(arr),2))
    print('медиана -',np.median(arr))
    print('отклонение -',round(np.std(arr),2))
    print('минимум -',np.min(arr))
    print('максимум -',np.max(arr))

def cpu_ram(paths):
    for name,word in metrics:
        np_stats(name,get_values(paths,word))

def anomalies(paths):
    limit=config.settings['anomalies_threshold']*100
    res={}
    for r in parser.parse(paths):
        if 'usage' in r.message:
            value=helpers.number(r.message)
            if value is not None and value>limit:
                if r.server in res:
                    res[r.server]+=1
                else:
                    res[r.server]=1
    print('===== аномалии: нагрузка больше',limit,'% =====')
    for server,count in top(res,10):
        print(server,'-',count)

def to_df(paths):
    rows=[]
    for r in parser.parse(paths):
        rows.append({
            'date':r.date,
            'time':r.time,
            'server':r.server,
            'level':r.level,
            'message':r.message,
        })
    return pd.DataFrame(rows)

def metric_df(df,word):
    res=df[df['message'].str.startswith(word)].copy()
    res['value']=pd.to_numeric(res['message'].apply(helpers.number),errors='coerce')
    return res

def no_data(df):
    if df is None or len(df)==0:
        print('нет данных')
        return True
    return False

def pd_total(df):
    display.header('общая статистика')
    if no_data(df):
        return
    print('всего записей -',len(df))
    print('серверов -',df['server'].nunique())
    print('дней -',df['date'].nunique())
    print('период -',df['date'].min(),'-',df['date'].max())
    display.header('записей по уровням')
    display.frame(df.groupby('level').size().sort_values(ascending=False))

def pd_servers(df):
    display.header('статистика по серверам')
    if no_data(df):
        return
    display.frame(server_table(df).sort_values('Errors',ascending=False))
    pd_sort(df)

def pd_dates(df):
    display.header('статистика по датам')
    if no_data(df):
        return
    table=df.pivot_table(index='date',columns='level',values='message',
                         aggfunc='count',fill_value=0)
    table['Всего']=table.sum(axis=1)
    display.frame(table.sort_index())

def pd_levels(df):
    display.header('статистика по уровням')
    if no_data(df):
        return
    counts=df.groupby('level').size().sort_values(ascending=False)
    display.frame(pd.DataFrame({
        'Записей':counts,
        'Доля %':(counts/len(df)*100).round(1),
    }))
    display.header('уровни по серверам')
    display.frame(df.pivot_table(index='server',columns='level',values='message',
                                 aggfunc='count',fill_value=0))

def pd_load(df):
    display.header('статистика нагрузки')
    if no_data(df):
        return
    pd_stats(df)
    display.header('средняя нагрузка по серверам')
    display.frame(server_load(df))

def pd_anomalies(df):
    limit=config.settings['anomalies_threshold']*100
    display.header(f'статистика аномалий: нагрузка больше {limit} %')
    if no_data(df):
        return
    load=df[df['message'].str.contains('usage')].copy()
    load['value']=pd.to_numeric(load['message'].apply(helpers.number),errors='coerce')
    bad=load[load['value']>limit]
    if len(bad)==0:
        print('аномалий нет')
        return
    print('всего аномалий -',len(bad))
    print('доля от записей о нагрузке -',round(len(bad)/len(load)*100,1),'%')
    display.header('аномалии по серверам')
    display.frame(bad.groupby('server').size().sort_values(ascending=False).head(10))
    display.header('аномалии по датам')
    display.frame(bad.groupby('date').size().sort_index())

def pd_sort(df):
    errors=df[df['level']=='ERROR']
    counts=errors.groupby('server').size().sort_values(ascending=False)
    display.header('серверы по количеству ERROR')
    display.frame(counts.head(10))

def pd_filter(df,level):
    res=df[df['level']==level]
    display.header(f'записи уровня {level}')
    display.frame(res.head(20))
    display.count(len(res))

def pd_stats(df):
    display.header('статистические показатели')
    res={}
    for name,word in metrics:
        res[name]=metric_df(df,word)['value'].describe()
    display.frame(pd.DataFrame(res).round(2))

def server_table(df):
    table=pd.DataFrame({
        'Records':df.groupby('server').size(),
        'Errors':df[df['level']=='ERROR'].groupby('server').size(),
        'Warnings':df[df['level']=='WARNING'].groupby('server').size(),
        'Avg CPU':metric_df(df,'CPU').groupby('server')['value'].mean().round(1),
        'Avg RAM':metric_df(df,'RAM').groupby('server')['value'].mean().round(1),
        'Avg Latency':metric_df(df,'network latency').groupby('server')['value'].mean().round(1),
        'Loss %':metric_df(df,'packet loss').groupby('server')['value'].mean().round(1),
    }).fillna(0)
    table['Records']=table['Records'].astype(int)
    table['Errors']=table['Errors'].astype(int)
    table['Warnings']=table['Warnings'].astype(int)
    table.index.name='Сервер'
    return table

def server_load(df):
    table=pd.DataFrame({
        name:metric_df(df,word).groupby('server')['value'].mean().round(1)
        for name,word in metrics
    }).fillna(0)
    table.index.name='Сервер'
    return table
