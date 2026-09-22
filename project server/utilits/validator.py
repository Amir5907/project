def int_val(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
    
def int_2(string2):
    while True:
        vvod=input(string2)
        if int_val(vvod):
            return int(vvod)
        print("Ошибка: введите целое число")