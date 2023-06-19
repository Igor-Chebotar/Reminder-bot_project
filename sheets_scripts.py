import gspread


async def add_new_line_into_google_sheets(users_data):
    gs = gspread.service_account(filename='credits_key.json')  # подключаем файл с ключами и пр.
    sh = gs.open_by_key('1rPyN7V0g2RYgONSekpBOhAaHxwqCq85yboO0oc_XQ1Q')  # подключаем таблицу по ID
    worksheet = sh.sheet1  # получаем первый лист
    worksheet.append_row([users_data['username'], users_data['question'], users_data['answer']])
