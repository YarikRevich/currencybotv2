import os
import redis
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import currency_sender
import currancy_data
from db import DB
from config import StatesTest
from config import currency_storage_euro,currency_storage_usd
from validators import validators
import currency_sender


TOKEN = os.getenv("TOKEN")

data = DB()

redis_ = redis.Redis("127.0.0.1",6379)
bot = Bot(TOKEN)
dp = Dispatcher(bot,storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())





@dp.message_handler(state="*",commands=["start"])
async def start_func(message: types.Message):

    """
    This one works when you write /start command 

    """
    if data.check_tracked_user(message.from_user.id)[0]:

        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="yes",text="Так")
        button2 = types.InlineKeyboardButton(callback_data="no",text="Ні")
        markup.add(button1,button2)

        await message.answer("❗️Ти вже маєш активний трекер.Хочеш видалити його?",reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("➕")
        markup.add(button1)
        
        #Change current state to "PREPARE1"
        current = dp.current_state(user=message.from_user.id)
        await current.set_state(StatesTest.all()[0])

        await message.answer("😀Привіт,тебе вітає бот для трекінку курсу,щоб задати налаштування трекінгу,натисни плюсик внизу",reply_markup=markup)
    

@dp.message_handler(lambda message: (message.text == "➕"),state=StatesTest.all()[0])
async def preparing_func(message: types.Message):

    """
    This func does some preparations before the setting of some
    user's data
    
    """

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    button = types.KeyboardButton("Розпочати заповнення")
    markup.add(button)

    
    await message.answer(
        "✅Воу,тепер тобі треба заповнити такі данні:\n\n1)Курс якої валюти ти хочеш відслідковувати.\n" + 
        "2)Діапазон курсу(від)\n" +
        "3)Діапазон курсу(до)\n\n" +
        "👌І вуаля,ти отримаєш повідомлення коли курс тієї чи іншої валюти" +
        "опинеться у вказаному тобою проміжку.\n\n" +
        "Ну що?!Поїхалиииии!!!🚗",
        reply_markup=markup
        ) 
    
    #Change state to PREPARE2
    current = dp.current_state(user=message.from_user.id)
    await current.set_state(StatesTest.all()[1])



@dp.message_handler(lambda message: (message.text == "Розпочати заповнення"),state = StatesTest.all()[1])
async def set_currency_func(message: types.Message):



    """ 
    This func works when the user tries to set currency 
    he wants to check

    """

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(callback_data="doll",text="USD")
    button2 = types.InlineKeyboardButton(callback_data="euro",text="EUR")
    markup.add(button1,button2)


    await message.answer("🤑Введіть валюту яку ви хочете внести?",reply_markup=markup)


@dp.message_handler(state=StatesTest.all()[3])
async def diapason_from_set_func(message: types.Message):

    """
    This func valids and sets diapason(from) to redis

    """
        
    if len(message.text) <= 4 and validators.isfloat(message.text):
        previous_entry = redis_.append(str(message.from_user.id),","+message.text)
        if float(message.text) < 25:
            await message.answer("😢Ехх,думаю такого щастя вже не трапиться:(\nТепер маєш вказати діапазон(до)")
        else:          
            await message.answer("👍Ок,перейдемо до діапазону(до)! Думаю,що вже знаєш як писать,ти ж кодер)")

        #Change state to TO_DEAPASON
        current = dp.current_state(user=message.from_user.id)
        await current.set_state(StatesTest.all()[4])
    else:
        await message.answer("❗️Перевірте введений діапазон,бо щось не так")


@dp.message_handler(state=StatesTest.all()[4])
async def diapason_to_set_func(message: types.Message):

    """
    This func valids and sets diapason(to) to redis

    """

    if len(message.text) <= 4 and validators.isfloat(message.text):

        range_from = redis_.get(str(message.from_user.id)).decode("utf-8").split(",")[1]

        if validators.isappropriate(range_from,message.text):
            previous_entry = redis_.append(str(message.from_user.id),","+message.text)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton(text="💤Відслідковування")
            button2 = types.KeyboardButton(text="🔍Інформація")

            markup.add(button1,button2)

            user_data = redis_.get(str(message.from_user.id)).decode("utf-8").split(",")

            if data.check_tracked_user(message.from_user.id)[0]:
                data.update_tracked_user_data(
                    str(message.from_user.id),
                    user_data[0],
                    user_data[1],
                    user_data[2],
                    )
            else:
                data.write_track_currancy(
                    str(message.from_user.id),
                    user_data[0],
                    user_data[1],
                    user_data[2],
                    )

            #Change state to MENU
            current = dp.current_state(user=message.from_user.id)
            await current.set_state(StatesTest.all()[5])

            await message.answer("✅Ось і все,тепер,коли курс буде в межах данних значень,ти отримаєш повідомлення\nА поки можеш ознайомитися з меню:)",reply_markup=markup)
        else:
            await message.answer("❗️Діапазон(до) не може бути відповідним діапазону(від),або ж бути меншим за нього\nВкажіть правильний!")
    else:
        await message.answer("❗️Переврте введений діапазон,бо щось не так")


@dp.message_handler(lambda message: (message.text == "🔍Інформація"),state=StatesTest.all()[5])
async def info_menu(message: types.Message):

    """
    This func answers user on his query made by pressing the button "Info"

    """

    await message.answer("👌Воу,ти у пункті 'Інформація'\nТут нема нічого такого цікавого,окрім того,що ти можеше побачити ім'я самої високості Ярослава,окрім посади короля,займаючий посаду розробника сія чуда")



@dp.message_handler(lambda message: (message.text == "💤Відслідковування"),state=StatesTest.all()[5])
async def status_menu(message: types.Message):

    """
    This func answers user on his query made by pressing button "Tracks"

    """
    if DB().tracked_user_data(str(message.from_user.id)):
        currency,curr_from,curr_to = DB().tracked_user_data(str(message.from_user.id))[0]
    
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="delete",text="⛔️Видалити трек")
        markup.add(button1)

        await message.answer(f"Ти маєш ось такий трек:\nВалюта - {currency}\nДіапазон(від) - {curr_from}\nДіапазон(до) - {curr_to}",reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(callback_data="want",text="Хочу!")

        markup.add(button1)

        await message.answer("Схоже,що у тебе вже немає треків,якщо хочеш створити новий⁉️",reply_markup=markup)

@dp.message_handler(state="*")
async def not_handled_message(message: types.Message):

    """
    This func can be handled when your message is not good for others

    """

    await message.answer("❗️Виберіть пункт з меню")



@dp.callback_query_handler(lambda callback: (True),state="*")
async def agree_func(callback: types.CallbackQuery):

    """
    This func answers user on his queries made by pressing inline buttons 

    """

    def _create_track_make_keyboard():

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("➕")
        markup.add(button1)

        return markup

    if callback.data == "yes":

        #Change state to PREPARE1
        current = dp.current_state(user=callback.from_user.id)
        await current.set_state(StatesTest.all()[0])

        keyboard = _create_track_make_keyboard()

        await bot.send_message(callback.message.chat.id,"😌Ок,тепер натисни плюсик знизу",reply_markup=keyboard)
        
    elif callback.data == "no":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton(text="💤Відслідковування")
        button2 = types.KeyboardButton(text="🔍Інформація")

        #Chnage state to MENU
        current = dp.current_state(user=callback.from_user.id)
        await current.set_state(StatesTest.all()[5])

        markup.add(button1,button2)
        await bot.send_message(callback.message.chat.id,"🤣Ну добре!Заходь у меню)",reply_markup=markup)

    elif callback.data == "delete":

        data.del_tracked_user(callback.from_user.id)

        #Change state to PREPARE1
        current = dp.current_state(user=callback.from_user.id)
        await current.set_state(StatesTest.all()[0])

        keyboard = _create_track_make_keyboard()

        await bot.send_message(callback.message.chat.id,"✅Трек видалено,тепер виконай інструкції нижче.А насамперед натисну плюсик знизу",reply_markup=keyboard)

    elif callback.data == "want":

        current = dp.current_state(user=callback.from_user.id)
        await current.set_state(StatesTest.all()[0])

        keyboard = _create_track_make_keyboard()

        await bot.send_message(callback.message.chat.id,"😜Роби все по інструкції нижче",reply_markup=keyboard)

    elif callback.data == "doll":

        #Change state to FROM_DEAPASON
        current = dp.current_state(user=callback.from_user.id)
        await current.set_state(StatesTest.all()[3])

        redis_.set(str(callback.from_user.id),"USD")
        await bot.send_message(callback.message.chat.id,"🙌Добре,ну що,давай тепер заповнимо діапазон(від)!\nНапишіть по прикладу нижче\n'27.3'")
        

    elif callback.data == "euro":

        #Change state to FROM_DEAPASON
        current = dp.current_state(user=callback.from_user.id)
        await current.set_state(StatesTest.all()[3])

        redis_.set(str(callback.from_user.id),"EUR")
        await bot.send_message(callback.message.chat.id,"🙌Добре,ну що,давай тепер заповнимо діапазон(від)!\nНапишіть по прикладу нижче\n'27.3'")
        

if __name__ == "__main__":

    #Make loop on three tasks (controllers,currency_data,currency_sender)

    loop = asyncio.get_event_loop()
    loop.create_task(currency_sender.cheker(bot,types))
    loop.create_task(currancy_data.get_data())
    executor.start_polling(dp,skip_updates=True,loop=loop)
    
