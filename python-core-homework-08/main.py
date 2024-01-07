from datetime import datetime, date, timedelta
from functools import reduce

TODAY: date
PERIOD_START_DATE: date
PERIOD_END_DATE: date

def init_globals():
    global TODAY 
    TODAY = date.today()
    
    global PERIOD_START_DATE
    weekday = TODAY.weekday()
    match weekday:
        case 0:
            PERIOD_START_DATE = TODAY - timedelta(days=2) 
        case 6:
            PERIOD_START_DATE = TODAY - timedelta(days=1)
        case _:
            PERIOD_START_DATE = TODAY
    
    global PERIOD_END_DATE
    PERIOD_END_DATE = PERIOD_START_DATE + timedelta(days=6)
    

def is_in_darte_range(dt:datetime) -> bool:
    return PERIOD_START_DATE <= dt and dt <= PERIOD_END_DATE

def set_biirthday_date(u:dict, year):
    birth_date = u["birthday"];
    year_birthday_date = datetime(year=year, month=birth_date.month, day=birth_date.day).date()
    u["this_birtday_date"] = year_birthday_date
    return u

def has_birthday(u:dict):
    return is_in_darte_range(u["this_birtday_date"])

def put_user(bd:dict, u:dict):
    week_day = u["this_birtday_date"].strftime("%A")
    day_users:list = bd.get(week_day, [])
    day_users.append(u["name"])
    bd.update({week_day: day_users})
    return bd
    
def update_year_birthdays_per_weekday(users, year, dict):
    users = list(map(lambda u: set_biirthday_date(u, year), users))
    affected_users = list(filter(has_birthday, users))
    birthdays_diary = reduce(lambda bd,u: put_user(bd, u), affected_users, dict)
    return birthdays_diary

def get_birthdays_per_week(users):
    init_globals()
    
    birthdays_diary = update_year_birthdays_per_weekday(users, PERIOD_START_DATE.year, {})
    if PERIOD_START_DATE.year != PERIOD_END_DATE.year:
        birthdays_diary = update_year_birthdays_per_weekday(users, PERIOD_END_DATE.year, birthdays_diary)
    
    monday_birthdays:list = birthdays_diary.get("Monday", [])
    for d in ['Sunday', "Saturday"]:
        d_birthdays = birthdays_diary.pop(d, [])
        d_birthdays.extend(monday_birthdays)
        monday_birthdays = d_birthdays
    if monday_birthdays:
        birthdays_diary.update({"Monday":monday_birthdays})    
        
    return birthdays_diary

def date_to_str(dat):
    return dat.strftime("%A %d %B %Y")
    
if __name__ == "__main__":
    users = [
        {"name": "Lesyk F.", "birthday":     datetime(year=2017, month=12,day= 29).date()},
        # {"name": "Oleh Z.",  "birthday":     datetime(year=1976, month=1, day=1).date()},
        # {"name": "Olena P.", "birthday":     datetime(year=1980, month=1, day=3).date()},
        # {"name": "Serg. Z.", "birthday":     datetime(year=1986, month=1, day=5).date()},
        # {"name": "Vlad. M.", "birthday":     datetime(year=1998, month=1, day=6).date()},
        # {"name": "Andrea V.", "birthday":    datetime(year=1988, month=1, day=3).date()},
        {"name": "Anastasia Z.", "birthday": datetime(year=2007, month=12,day=30).date()},
    ]
    result = get_birthdays_per_week(users)
    
    print(f'\ntoday: {date_to_str(TODAY):>30} \nstart: {date_to_str(PERIOD_START_DATE):>30}\n  end: {date_to_str(PERIOD_END_DATE):>30}')
    print("\nThe users are:")
    for u in users:
        print(f' * {u["name"]:>15} : {str(u["birthday"])}')
    
    print("\nNext 7 days birthdays:")
    for day_name, names in result.items():
        print(f"{day_name}: {', '.join(names)}")