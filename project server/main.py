import logging

import config
from modules import log, parser, servers, generator,anylazer,statistic,benchmark
from utilits import validator

def setup_log():
    logging.basicConfig(
        filename=config.app_file,
        level=logging.INFO,
        format=('%(asctime)s|%(levelname)s|%(name)s|%(message)s'),
    encoding='utf-8'
    )

def menu():
    print('=======system monitoring========')
    print('1 servers')
    print('2 logs')
    print('3 analyze')
    print('4 statistic')
    print('5 anomalies')
    print('6 reports')
    print('7 test servers generating')
    print('8 generating test log')
    print('9 benchmark')
    print('0 exit')
    
def filter_rec(path,field,value):
    for record in parser.parse(path):
        if field=='message':
            if value.lower() in record.message.lower():
                yield record
        elif getattr(record,field)==value:
            yield record
            
def show_rec(records,limit=50):
    count=0
    for record in records:
        print(record)
        count+=1
        if count>=limit:
            break
    print(f'показано записей: {count}')
    logging.info(f'показано записей: {count}')


def log_menu():
    paths=log.log_list()
    if not paths:
        print('логов нет')
        return

    while True:
        print('======log menu=====')
        print('1 все записи')
        print('2 только ERROR')
        print('3 только CRITICAL')
        print('4 только WARNING')
        print('5 поиск по сообщению')
        print('6 поиск по серверу')
        print('7 поиск по дате')
        print('8 только INFO')
        print('0 назад')
        choice=input('выбор:').strip()

        if choice=='0':
            return
        elif choice=='1':
            show_rec(parser.parse(paths))
        elif choice=='2':
            show_rec(filter_rec(paths,'level','ERROR'))
        elif choice=='3':
            show_rec(filter_rec(paths,'level','CRITICAL'))
        elif choice=='4':
            show_rec(filter_rec(paths,'level','WARNING'))
        elif choice=='5':
            text1=input('текст сообщения:')
            show_rec(filter_rec(paths,'message',text1))
        elif choice=='6':
            server=input('имя сервера:').strip()
            show_rec(filter_rec(paths,'server',server))
        elif choice=='7':
            date=input('дата(YYYY-MM-DD):').strip()
            show_rec(filter_rec(paths,'date',date))
        elif choice=='8':
            show_rec(filter_rec(paths,'level','INFO'))
        else:
            print('такого пункта нет')

def menu_ser(server_list):
    if not server_list:
        print("список пуст сгенерируйте сервера")
        return

    while True:
        print('======servers=====')
        print('1 все серверы')
        print('2 активные серверы')
        print('3 проблемные серверы')
        print('4 поиск сервера')
        print('5 информация о сервере')
        print('0 назад')
        choice=input('выбор:').strip()

        if choice=='0':
            return
        elif choice=='1':
            servers.show_list(server_list)
        elif choice=='2':
            servers.show_list(servers.active(server_list))
        elif choice=='3':
            servers.show_list(servers.problem(server_list))
        elif choice=='4':
            text=input('имя или id сервера:')
            servers.show_list(servers.find(server_list,text))
        elif choice=='5':
            text=input('имя или id сервера:')
            server=servers.one(server_list,text)
            if server is None:
                print('сервер не найден')
            else:
                servers.show_info(server)
        else:
            print('такого пункта нет')
def gen_sermenu():
    count=validator.int_2('сколько серверов сгененерировать')
    generator.gen_server(count)
    print(f'сгенерировать;{count}')
    logging.info(f'сгенерировано серверов;{count}')
def gen_logmenu():
    records=validator.int_2('сколько записей')
    files=validator.int_2('сколько файлов')
    print(f'сгенерировать {records} записей в {files},файлах')
    logging.info(f'сгенерировано {records},записей в {files}файлах')
    generator.gen_logs(records,files)

def analyze_menu():
    path=log.log_list()
    if not path:
        print('логов нету')
        return
    anylazer.run(path)
    logging.info('анализ выполнен')

def statistic_menu():
    paths=log.log_list()
    if not paths:
        print('логов нету')
        return
    df=None

    while True:
        print('======statistic menu=====')
        print('1 общая статистика')
        print('2 статистика по серверам')
        print('3 статистика по датам')
        print('4 статистика по уровням')
        print('5 статистика нагрузки')
        print('6 статистика аномалий')
        print('0 назад')
        choice=input('выбор:').strip()

        if choice=='0':
            return
        if choice in ('1','2','3','4','5','6') and df is None:
            print('читаю логи...')
            df=statistic.to_df(paths)

        if choice=='1':
            statistic.pd_total(df)
        elif choice=='2':
            statistic.pd_servers(df)
        elif choice=='3':
            statistic.pd_dates(df)
        elif choice=='4':
            statistic.pd_levels(df)
            level=input('показать записи уровня (Enter пропустить):').strip().upper()
            if level:
                statistic.pd_filter(df,level)
        elif choice=='5':
            statistic.pd_load(df)
        elif choice=='6':
            statistic.pd_anomalies(df)
        else:
            print('такого пункта нет')
            continue
        logging.info('статистика выполнена')

def benchmark_menu():
    path=log.log_list()
    if not path:
        print('логов нету')
        return
    thread_count=validator.int_2('сколько потоков:')
    process_count=validator.int_2('сколько процессов:')
    benchmark.run(path,thread_count,process_count)
    logging.info(f'бенчмарк выполнен: {thread_count} потоков, {process_count} процессов')

def anomalies_menu():
    path=log.log_list()
    if not path:
        print('логов нету')
        return
    statistic.anomalies(path)
    logging.info('поиск аномалий выполнен')

def main():
    config.setting_file()
    config.new_folder()
    setup_log()
    server_list=servers.load_servers()
    
    while True:
        menu()
        choice=input('выбор:').strip()
        
        if choice=='1':
            menu_ser(server_list)
        elif choice=='2':
            log_menu()
        elif choice=='3':
            analyze_menu()
        elif choice=='4':
            statistic_menu()
        elif choice=='5':
            anomalies_menu()
        elif choice=='7':
            gen_sermenu()
            server_list=servers.load_servers()
        elif choice=='8':
            gen_logmenu()
        elif choice=='9':
            benchmark_menu()
        elif choice=='0':
            print('выход')
            break
        else:
            print('такого пункта пока нет') 
            
if __name__=='__main__':
    try:
        main()
    except Exception as e:
        logging.exception(f'необработаная:{e}')
        print('произошла ошибка,проверь logs/application.log')