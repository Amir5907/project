def header(text):
    print(f'\n===== {text} =====')

def frame(data):
    if len(data)==0:
        print('нет данных')
        return
    print(data.to_string())

def count(value):
    print('найдено:',value)
