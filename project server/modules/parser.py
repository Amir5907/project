from modules import log
class log_record:
    __slots__=('date','time','server','level','message')
    def __init__(self,date,time, server, level, message):
        self.date=date
        self.time=time
        self.server=server
        self.level=level
        self.message=message
    def __str__(self):
        return f"{self.date} {self.time} {self.server} {self.level} {self.message}"
    def __repr__(self):
        return f"{self.date} {self.time} {self.server} {self.level} {self.message}"

def str_parts(lines):
    part=lines.strip().split('|')
    if len(part)!=4:
        return None
    
    date_time=part[0].split(' ')
    if len(date_time)!=2:
        return None
    date=date_time[0]
    time=date_time[1]
    server=part[1]
    level=part[2]
    message=part[3]
    
    if level in['INFO',"WARNING","CRITICAL","ERROR"]:
        return log_record(date,time,server,level,message)
    else:
        return None
    
def file_parse(path):
    lines=log.file_read(path)
    for line in lines:
        record=str_parts(line)
        if record !=None:
            yield record
            
def parse(paths):
    for path in paths:
        for record in file_parse(path):
            yield record
            
class LogIterator:
    def __init__(self,paths):
        self.paths=paths
        self.file_index=0
        self.records=None
    
    def __iter__(self):
        return self
    
    def __next__(self):
        while self.file_index<len(self.paths):
            if self.records is None:
                path=self.paths[self.file_index]
                self.records=iter(file_parse(path))
            try:
                return next(self.records)
            except StopIteration:
                self.records=None
                self.file_index+=1
        raise StopIteration    
