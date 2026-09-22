import os
import config

def log_list():
    if not os.path.exists(config.log1):
        return []
    
    files=[]
    for name in os.listdir(config.log1):
        if name.endswith('.log') and name!="application.log":
            path1=os.path.join(config.log1,name)
            files.append(path1)
    return files

def file_read(path1):
    try:
        with open(path1,'r', encoding='utf-8') as f:
            for line in f:
                yield line
    except Exception as e:
        print(f"Ошибка при чтении файла {path1}: {e}")

def str_count(lines):
    count=0
    for line in lines:
        count+=1
    return count