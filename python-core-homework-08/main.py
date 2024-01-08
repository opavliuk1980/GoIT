'''
Home work #8
'''
from datetime import datetime, date, timedelta
from functools import reduce
import sys

TODAY: date
PERIOD_START_DATE: date
PERIOD_END_DATE: date

def init_globals() -> None:
    '''
    Global constants initialization:
       TODAY - date of the day we collect the birthdays around
       [PERIOD_START_DATE, PERIOD_END_DATE] - 1 week period we 
       collect the birthdays fore
    '''
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
    '''
    check id the date occured during the special period
    '''
    return PERIOD_START_DATE <= dt <= PERIOD_END_DATE

def set_biirthday_date(u:dict, year) -> dict:
    '''
    calculates this year dates of users birthdays
    '''
    birth_date = u["birthday"]
    year_birthday_date = datetime(year=year, month=birth_date.month, day=birth_date.day).date()
    u["this_birtday_date"] = year_birthday_date
    return u

def has_birthday(u:dict) -> bool:
    """
    True if usr has his birhtday during the dates-range
    """
    return is_in_darte_range(u["this_birtday_date"])

def put_user(bd:dict, u:dict):
    """
    put user nane to the results' dictionary
    """
    week_day = u["this_birtday_date"].strftime("%A")
    day_users:list = bd.get(week_day, [])
    day_users.append(u["name"])
    bd.update({week_day: day_users})
    return bd

def update_year_birthdays_per_weekday(users_details:dict, year:int, dict_to_update:dict) -> dict:
    """
        Adds more usrs to the results dictionary
    """
    users_details = list(map(lambda u: set_biirthday_date(u, year), users_details))
    affected_users = list(filter(has_birthday, users_details))
    birthdays_diary = reduce(lambda bd,u: put_user(bd, u), affected_users, dict_to_update)
    return birthdays_diary

def get_birthdays_per_week(users_details):
    """
    collect users whos birthday occcured this week
    """
    init_globals()
    birthdays_diary = update_year_birthdays_per_weekday(users_details, PERIOD_START_DATE.year, {})
    if PERIOD_START_DATE.year != PERIOD_END_DATE.year:
        birthdays_diary = update_year_birthdays_per_weekday(
            users_details,
            PERIOD_END_DATE.year,
            birthdays_diary
            )
    monday_birthdays:list = birthdays_diary.get("Monday", [])
    for d in ['Sunday', "Saturday"]:
        d_birthdays = birthdays_diary.pop(d, [])
        d_birthdays.extend(monday_birthdays)
        monday_birthdays = d_birthdays
    if monday_birthdays:
        birthdays_diary.update({"Monday":monday_birthdays})
    return birthdays_diary

if __name__ == "__main__":
    users = [
        {"name": "Lesyk F.", "birthday": datetime(year=2017, month=12,day= 29).date()},
    ]
    result = get_birthdays_per_week(users)
    for day_name, names in result.items():
        print(f"{day_name}: {', '.join(names)}")
    sys.exit(0)
