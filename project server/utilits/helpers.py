def number(message):
    digits=''
    for ch in message.split()[-1]:
        if ch.isdigit():
            digits+=ch
        elif digits:
            break
    if not digits:
        return None
    return int(digits)
