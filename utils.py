import datetime
import json

hours_replit_delta = datetime.timedelta(hours=3)


def reminder_date(target_day=0):
    now = datetime.datetime.now()  # текущие дата и время
    delta = datetime.timedelta(days=7)
    if target_day in range(1, 8):
        day_today = datetime.datetime.isoweekday(now)  # текущий день - его номер
        days_to_wait = (target_day - day_today + 6) % 7 + 1
        delta = datetime.timedelta(days=days_to_wait)

    return now + delta


def reminder_datetime(date, time):
    res = datetime.datetime(date.year, date.month, date.day, int(time[0]), int(time[1]))
    return res


def write_notification_time_to_json(users_id_time):
    try:
        with open('data.json', encoding='utf8') as all_json_data:  # Открываем файл
            data = json.load(all_json_data)  # Получае все данные из файла
        data['users_notification_time'][users_id_time['id']] = str(users_id_time['time'])
        with open('data.json', 'w', encoding='utf8') as outfile:  # Открываем файл для записи
            json.dump(data, outfile, ensure_ascii=False,
                      indent=2)  # Добавляем данные (все, что было ДО добавления данных + добавленные данные)
    except Exception as e:
        if e.args[0] == 2:
            data = {'users_notification_time': {
                users_id_time['id']: str(users_id_time['time'])
            }
            }
            with open("data.json", "w") as json_file:
                json.dump(data, json_file)


def delite_notification_from_json(json_data, reminds_arg):
    for remind in reminds_arg:
        week_delta = datetime.timedelta(days=7)
        #json_data['users_notification_time'].pop(remind[0], None)
        json_data['users_notification_time'][remind[0]] = str(remind[1] + week_delta)
    with open('data.json', 'w', encoding='utf8') as outfile:  # Открываем файл для записи
        json.dump(json_data, outfile, ensure_ascii=False,
                  indent=2)


def open_db_and_check_remind_time():
    with open('data.json', encoding='utf8') as all_json_data:  # Открываем файл
        data = json.load(all_json_data)  # Получае все данные из файла
        now = datetime.datetime.now()
        reminds = []
        for user_id in data["users_notification_time"]:
            remind_string_time = data["users_notification_time"][user_id]
            remind_time = datetime.datetime.strptime(remind_string_time, '%Y-%m-%d %H:%M:%S')
            if remind_time - now < datetime.timedelta(minutes=1):
                reminds.append((user_id, remind_time))

        delite_notification_from_json(data, reminds)
        return reminds


open_db_and_check_remind_time()
