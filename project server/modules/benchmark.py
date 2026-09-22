import time

import config
from modules import paralel
from utilits import display

def measure(func,paths,workers=None):
    start=time.perf_counter()
    if workers is None:
        result=func(paths)
    else:
        result=func(paths,workers)
    return round(time.perf_counter()-start,2),result

def show_times(times,base):
    display.header('время выполнения')
    width=max(len(name) for name,value in times)
    for name,value in times:
        if value>0:
            speed=f'x{round(base/value,2)}'
        else:
            speed='-'
        print(f'{name:<{width}}  {value:>6} sec   {speed}')

def show_result(result):
    display.header('результат анализа')
    print('всего записей -',result['total'])
    for level in sorted(result['levels']):
        print(f"{level}: {result['levels'][level]}")
    print('аномалий -',result['anomalies'])
    if result['cpu_count']:
        print('среднее CPU -',round(result['cpu_sum']/result['cpu_count'],2))

def run(paths,thread_count=None,process_count=None):
    if thread_count is None:
        thread_count=config.settings['max_threads']
    if process_count is None:
        process_count=config.settings['max_processing']

    display.header(f'обработка {len(paths)} файлов')
    times=[]

    base,result=measure(paralel.sequential,paths)
    times.append(('Sequential',base))

    value,by_threads=measure(paralel.threads,paths,thread_count)
    times.append((f'Threads ({thread_count})',value))

    value,by_async=measure(paralel.run_async,paths)
    times.append(('Async',value))

    value,by_process=measure(paralel.processes,paths,process_count)
    times.append((f'Multiprocessing ({process_count})',value))

    show_times(times,base)
    show_result(result)

    if result==by_threads==by_async==by_process:
        print('\nрезультаты всех режимов совпадают')
    else:
        print('\nвнимание: результаты режимов разошлись')
