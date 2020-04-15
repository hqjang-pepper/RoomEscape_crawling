import datetime

def reserve_date_list(days):
    result=[]
    today = datetime.datetime.today()
    for i in range(days):
        result.append(today.strftime('%Y%m%d'))
        today += datetime.timedelta(+1)
    return result

def day_list(days):
    result=[]
    today=datetime.date.today()
    for _ in range(days):
        result.append(today.day)
        today += datetime.timedelta(+1)
    return result

def reserve_date_list_hyphen(days):
    result=[]
    today = datetime.datetime.today()
    for i in range(days):
        result.append(today.strftime('%Y-%m-%d'))
        today += datetime.timedelta(+1)
    return result

def reserve_date_list_slash(days):
    result=[]
    today = datetime.datetime.today()
    for i in range(days):
        result.append(today.strftime('%Y/%m/%d'))
        today += datetime.timedelta(+1)
    return result
