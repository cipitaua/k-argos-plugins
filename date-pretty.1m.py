#!/usr/bin/env python
# install LunarCalendar: https://github.com/wolfhong/LunarCalendar
# if you install LunarCalendar from pypi, you should use
# LunarCalendar.converter replace lunarcalendar.converter below

import datetime
import calendar
from lunarcalendar.converter import Converter, Solar, Lunar
import os.path
import pickle
from itertools import cycle


today = datetime.datetime.today()
today_date = today.date()
year = today.year

def pstatus_bar():
    '''print status bar'''
    bitbar="|font=mononoki size=14 color=black dropdown=false"
    birthdays = {"0102": "Som"}
    gap_numbers = {0: "!", 1: "'", 2: "╎", 3: "┆", 4: "┊"}
    is_birthday = False
    is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
    solar = Solar.from_date(today.date())
    lunar_year = Converter.Solar2Lunar(solar).year
    days_this_year = 366 if is_leap else 365
    for lunar_date in birthdays.keys():
        month, day = int(lunar_date[-4:-2]), int(lunar_date[-2:])
        lunar = Lunar(lunar_year, month, day, is_leap)
        solar = Converter.Lunar2Solar(lunar)
        gap = (datetime.date(solar.year, solar.month, solar.day) - today_date).days % days_this_year
        if gap <= 4:
            print(f"{birthdays[lunar_date]}🎂{gap_numbers[gap]}{today.hour:02d}:{today.minute:02d}{bitbar}")
            if not is_birthday:
                is_birthday = True
    if not is_birthday:
        print(f"{list(calendar.day_abbr)[today.weekday()]}{today.day}⸾{today.hour:02d}:{today.minute:02d}{bitbar}")


def pdropdown():
    '''print dropdown'''
    cache_name = ".lunardate.cache"
    month = today.month
    cal = calendar.Calendar()
    cal.setfirstweekday(calendar.SUNDAY)
    to_show = []

    # print("<u>星期.7&nbsp;星期.1&nbsp;星期.2&nbsp;星期.3&nbsp;星期.4&nbsp;星期.5&nbsp;星期.6</u>" + bitbar)
    # print("－－~~~"*6 + "－－~~" + bitbar)
    to_show.append("<u>星期.7&nbsp;星期.1&nbsp;星期.2&nbsp;星期.3&nbsp;星期.4&nbsp;星期.5&nbsp;星期.6</u>")

    if os.path.exists(cache_name):
        with open(cache_name, 'rb') as handle:
            solar2fest = pickle.load(handle)
        if month != solar2fest['month']:
            solar2fest = get_festival(month, cache_name)
    else:
        solar2fest = get_festival(month, cache_name)

    s = ""
    c_day = ("","初一","初二","初三","初四","初五",
           "初六","初七","初八","初九","初十",
           "十一","十二","十三","十四","十五",
           "十六","十七","十八","十九","二十",
           "廿一","廿二","廿三","廿四","廿五",
           "廿六","廿七","廿八","廿九","三十"
          )
    c_mon = ("","正","二","三","四","五","六","七","八","九","十","十一","腊")
    for weekday, day, date in zip(cycle(cal.iterweekdays()), cal.itermonthdays(year, month), cal.itermonthdates(year, month)):
        if date in solar2fest:
            lunar_calendar_info = solar2fest[date][0][:2]
            s += f"{day:02d}{lunar_calendar_info}&nbsp;"
        else:
            solar = Solar.from_date(date)
            lunar = Converter.Solar2Lunar(solar)
            if lunar.day == 1:
                lunar_calendar_info = c_mon[lunar.month]
            else:
                lunar_calendar_info = c_day[lunar.day]
            if day == today.day:
                lunar_year = lunar.year
                lunar_month = lunar.month
                lunar_day = lunar.day
                s += f"<font color=\"blue\">{day:02d}{lunar_calendar_info}</font>&nbsp;"
            elif day == 0:
                s += f"<font color=\"gray\">{date.day:02d}{lunar_calendar_info}</font>&nbsp;"
            else:
                s += f"{day:02d}{lunar_calendar_info}&nbsp;"

        if weekday == calendar.SATURDAY:
           # s += bitbar
           # print(s)
           to_show.append(s)
           s = ""

    bitbar = "| font='FiraMono' size=6 color=black"
    print(bitbar)
    bitbar = "| font='FiraMono' size=12 color=black"
    print("\\n".join(to_show) + bitbar)
    print(bitbar)
    bitbar = "| font='FiraMono' size=14 color=black"

    if today_date in solar2fest:
        today_festival = "╎".join(solar2fest[today_date])
        print(f"{year}-{month:02d}-{today.day:02d}╎农历{get_lunar_year_name(lunar_year)}年{c_mon[lunar_month]}月{c_day[lunar_day]}╎{today_festival}{bitbar}")
    else:
        print(f"{year}-{month:02d}-{today.day:02d}╎农历{get_lunar_year_name(lunar_year)}年{c_mon[lunar_month]}月{c_day[lunar_day]}{bitbar}")


def get_lunar_year_name(lunar_year):
    """return Heavenly Stem and Earthly Branch of this year"""
    tiangan = "甲乙丙丁戊己庚辛壬癸"
    dizhi = "子丑寅卯辰巳午未申酉戌亥"
    # 公元4年是一个甲子年
    # -4表示从甲子年又过了ly个年头，ly%10：表示从天干上算过了几个天干，如果为0表示天干还是甲，如果为1表示到了乙
    ly = (lunar_year - 4) % 60
    return tiangan[ly % 10] + dizhi[ly % 12]


def get_festival(month, cache_name):
    """return lunar festivals"""
    from lunarcalendar.festival import zh_festivals
    from lunarcalendar.solarterm import zh_solarterms
    sol2fes = {}

    for fest in zh_festivals + zh_solarterms:
        solar_date = fest(year)
        if solar_date.month == month:
            if solar_date in sol2fes:
                sol2fes[solar_date].append(fest.get_lang('zh_hans'))
            else:
                sol2fes[solar_date] = [fest.get_lang('zh_hans')]

    sol2fes['month'] = month

    with open(cache_name, 'wb') as handle:
        pickle.dump(sol2fes, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return sol2fes


if __name__ == "__main__":
    print('---')
    pstatus_bar()
    pdropdown()
