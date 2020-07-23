
from aiogram.utils.helper import Helper,HelperMode,ListItem


class StatesTest(Helper):
    mode = HelperMode.snake_case
    
    PREPARE1 = ListItem()
    PREPARE2 = ListItem()
    CURRENCY = ListItem()
    FROM_DEAPASON = ListItem()
    TO_DEAPASON = ListItem()
    MENU = ListItem()



