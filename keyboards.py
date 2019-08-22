import telebot
import db_foo
import buttons

class Keyboard():
    def __init__(self, rows, collums):
        self.rows = rows
        self.collums = collums




class KeyboardEditTimeCoef(Keyboard):
    def make(self, data, multiplier: int = 1):
        keyboards_array = []
        for i in range(self.rows):
            row = []
            for t in range(self.collums):
                t = (self.collums * i + t) / multiplier
                t = int(t) if multiplier == 1 else t
                minutes = ':oo' if data[2] == 'time' else ''
                row.append(telebot.types.InlineKeyboardButton(text=f'{t}{minutes}',
                                                              callback_data=f'mynewcoef,{data[1]},{data[2]},{t}'))
            keyboards_array.append(row)
        return keyboards_array


class KeyboardWeight(Keyboard):
    """клавиатура для выбора веса"""
    lst = [[5, 10, 15, 20, 25, 30, 35, 40],
           [45, 50, 55, 60, 65, 70, 75, 80],
           [90, 100, 110, 120, 130, 140, 150],
           [160, 170, 180, 190, 200],
           [225, 250, 275, 300, 325, 350, 375],
           [400, 450, 500, 550, 600, 650, 700],
           [750, 800, 850, 900, 950, 1000]]

    def make(self, calb_name='product_weight', prod_id=0, back_menu_flag='prod_base'):
        keyboards_array = []
        for i in KeyboardWeight.lst:
            row = []
            for p in i:
                row.append(telebot.types.InlineKeyboardButton(text=f'{p}',
                                                   callback_data=f'{calb_name},{p},{prod_id},{back_menu_flag}'))
            keyboards_array.append(row)

        return keyboards_array


class KeyboardMyMenu(Keyboard):
    """Клавиатура для показа меню 'Мое меню' """
    def make(self, menu):
        keyboards_array= []
        for i in menu:
            prod_name = db_foo.load_product_name_from_product_id(i[0])
            keyboards_array.append(telebot.types.InlineKeyboardButton(text=f"{prod_name} - {i[1]} гр.",
                                                                      callback_data=f'My_menu_edit, {i[0]}, {prod_name}'))
        return keyboards_array
