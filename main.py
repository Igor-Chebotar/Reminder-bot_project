from aiogram import Bot, Dispatcher, executor, types
from secret_data import REMINDER_TOKEN
from sheets_scripts import add_new_line_into_google_sheets
from utils import reminder_date, reminder_datetime, write_notification_time_to_json, open_db_and_check_remind_time, \
    hours_replit_delta
import logging
import asyncio
from louder import Start
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

bot = Bot(token=REMINDER_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
questions = {'1': 'Что было сделано на прошлой неделе?',
             '2': 'Какой план на следующую неделю?'
             }
tasks_book = {}


@dp.message_handler(commands=['help'], state='*')
async def help_command(message: types.Message):
    await bot.send_message(message.from_user.id,
                           text='Для того, чтобы отписаться по готовым проектам, нужно:\n'

'1) Вызвать команду /start_record n\n'
'2) В качестве n указать номер вопроса, на который будет ответом список задач/дел\n'
'1 - Что было сделано на прошлой неделе?\n'
'2 - Какой план на следующую неделю?\n'
'(Например, /start_record 1)\n'
'Отвечать можно несколькими сообщениями, если сделанные задачи слишком большие\n\n' 

'3) Чтобы завершить ответ, введи команду /stop\n\n'

'Важно: команду /stop нужно нажимать после того, как записал/а все задачи для вопроса 1 или 2 (нельзя записать ответ на оба пункта сразу)\n\n'

'Например:\n'
'/start_record 1\n'
'Отправил питчдек \n'
'Проанализировал конкурентов\n'
'/stop\n'
'/start_record 2\n'
'Созвонюсь с аналитиками\n'
'Подумаю о будущем\n'
'/stop\n\n'

'Еще бот может сам напоминать тебе о том, что нужно отписаться по задачам на этой неделе:\n'
'1) введи команду /set_remind d %H:%M\n\n'

'd — номер дня недели, на который хочешь поставить уведомление (ПН - 1 ... ВС - 7)\n'
'Например, /set_remind 2 17:30')


@dp.message_handler(commands=['start'], state='*')
async def help_command(message: types.Message):
    await bot.send_message(message.from_user.id,
                           text='Здравствуйте! Я бот-ассисстент, созданный чтобы помочь вам составлять отчётность о Ваших сделанных делах и планах, чтобы узнать что я умею воспользуйтесь командой /help')


@dp.message_handler(commands=['start_record'], state=None)
async def start_message(message: types.Message):
    user_id = message.from_user.id
    number_of_question = message.text.split()[-1]
    logging.info(f'{user_id} start_record')
    if number_of_question not in questions:
        await bot.send_message(message.from_user.id,
                               text='Пожалуйста, повторите ввод, корректно указав вопрос, на который хотите написать ответ')
    else:
        if user_id not in tasks_book:
            tasks_book[user_id] = ['', number_of_question]
        await bot.send_message(message.from_user.id, text='Какие дела записываем?')
        await Start.memory_loop.set()


@dp.message_handler(state=Start.memory_loop)
async def task_memorization(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text != '/stop':
        task = message.text
        logging.info(f'{user_id} record task')
        if user_id in tasks_book:
            tasks_book[user_id][0] += task + '\n' * 2
        await bot.send_message(user_id, text='Запомнил')
        await Start.memory_loop.set()
    else:
        logging.info(f'{user_id} stop and start remember')
        await state.reset_state()
        answer = tasks_book[message.from_user.id][0]
        user_full_name = message.from_user.full_name
        number_of_question = tasks_book[message.from_user.id][1]
        data = {
            'username': user_full_name,
            'question': questions[number_of_question],
            'answer': answer.rstrip(),
        }
        await bot.send_message(user_id, text=f'Ваш ответ на вопрос {questions[number_of_question]} '
                                             f'был успешно записан в данном виде \n\n'
                                             f'{answer.rstrip()}')
        tasks_book.pop(user_id, None)

        await add_new_line_into_google_sheets(data)  # Функция, формирующая и отправляющая ответ в гугл таблицы


@dp.message_handler(commands=['set_remind'], state="*")
async def set_remind(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    date = args[1]
    time = args[2].split(':')
    logging.info(f'{user_id} set_remind')
    try:
        remind_date = reminder_date(target_day=int(date))
        remind_datetime = reminder_datetime(remind_date, time)
        users_id_time = {
            'id': user_id,
            'time': remind_datetime - hours_replit_delta
        }
        write_notification_time_to_json(users_id_time)
        await bot.send_message(message.from_user.id,
                               text=f'Уведомление установлено на {remind_datetime} ')
    except Exception:
        await bot.send_message(message.from_user.id,
                               text=f'Что-то пошло не так, пожалуйста, повторите попытку установки напоминания')


async def send_notifications():
    while True:
        approach_remind = open_db_and_check_remind_time()
        for remind in approach_remind:
            user_id, time = remind
            await bot.send_message(user_id,
                                   text=f'Время записать что вы успели сделать за эту неделю и какие планы на следующую')
        await asyncio.sleep(60)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_notifications())

    executor.start_polling(dp, skip_updates=True)
