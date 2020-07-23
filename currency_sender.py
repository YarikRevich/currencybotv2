import asyncio
from currancy_data import DB
from pymysql.err import IntegrityError



async def cheker(bot,types):
    while True:
        await asyncio.sleep(3)
        all_users_data = DB().get_all_tracked_user_data()
        current_currency = DB().get_current_data()
        for elem in all_users_data:
            if float(current_currency[elem[1]]) >= float(elem[2]) and float(current_currency[elem[1]]) <= float(elem[3]):
                DB().del_tracked_user(elem[0])

                markup = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(callback_data="want",text="Зробити новий трекер")
                markup.add(button)

                await bot.send_message(elem[0],"❗️❗️❗️Курс опинився у заданому тобою діапазоні",reply_markup=markup)
            else:
                pass
            await asyncio.sleep(2)
        await asyncio.sleep(3)

