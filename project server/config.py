import os
import json
base=os.path.dirname(os.path.abspath(__file__))

defaults={
    'max_threads':8,
    'max_processing':4,
    'log_path':'logs',
    'data_path':'data',
    'anomalies_threshold':0.8,
    'test_servers':50,
    'test_logs':10000
}
settings=dict(defaults)

settings_file=os.path.join(base,'data','settings.json')
data=os.path.join(base,'data')
log1=os.path.join(base,'logs')
servers_file=os.path.join(data,'servers.json')
app_file=os.path.join(log1,'application.log')

def full_path(path):
    if os.path.isabs(path):
        return path
    return os.path.join(base,path)

def apply_paths():
    global data,log1,servers_file,app_file
    data=full_path(settings['data_path'])
    log1=full_path(settings['log_path'])
    servers_file=os.path.join(data,'servers.json')
    app_file=os.path.join(log1,'application.log')

def new_folder():
    for path in (data,log1):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Создана папка {path}")

def setting_file():
    if not os.path.exists(settings_file) or os.path.getsize(settings_file)==0:
        settings_save()
        return
    try:
        with open(settings_file,'r',encoding='utf-8') as f:
            loaded=json.load(f)
    except (json.JSONDecodeError,OSError) as e:
        print(f"Ошибка при чтении файла {settings_file}: {e}")
        return
    for key in defaults:
        if key in loaded:
            settings[key]=loaded[key]
    apply_paths()

def settings_save():
    try:
        with open(settings_file,'w',encoding='utf-8') as f:
            json.dump(settings,f,indent=4,ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка при сохранении файла {settings_file}: {e}")
