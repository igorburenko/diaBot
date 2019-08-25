import telebot
import os
import re
import help
from telebot.types import Message
from db_foo import *
from calculate import *
from buttons import *
from keyboards import KeyboardEditTimeCoef, KeyboardWeight, KeyboardMyMenu
from pprint import pprint

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['test'])
def test_msg(message: Message):

    delete_answer(message.chat.id, message.message_id)



# при команде старт
@bot.message_handler(commands=['start'])
def start_msg(message: Message):
    try:
        user_in_db = check_new_user(message.chat.id)
        if user_in_db is None:
            add_new_user(message.chat.id)
            txt = 'Здравствуйте, я ДиаБот. Я умею расчитывать дозу инсулина.\nДля начала нажмите НАСТРОЙКИ!\n\n'
        elif user_in_db[0] == message.chat.id:
            txt = 'С возвращением!\nРад что мы снова вместе!\n \nДля начала нажмите НАСТРОЙКИ!\n\n'
        delete_answer(message.chat.id, message.message_id)
        main_menu(message.chat.id, txt)
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'back2main_menu' in call.data)
def back_to_main_menu(call):
    try:
        main_menu(call.message.chat.id, messageId=call.message.message_id)
    except:
        print('Somthing went wrong')


def main_menu(teleid, greeting=None, messageId=None):
    """
    основное меню бота.
    """
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(btn_doza, btn_setup)
        keyboard.add(btn_add_to_base)
        keyboard.add(btn_help)
        txt = greeting + '\n ГЛАВНОЕ МЕНЮ' if greeting is not None else 'ГЛАВНОЕ МЕНЮ'
        if greeting is not None:
            txt = greeting + '\n ГЛАВНОЕ МЕНЮ'
            bot.send_message(teleid, txt, reply_markup=keyboard)
        else:
            txt = 'ГЛАВНОЕ МЕНЮ'
            message_sender(teleid, messageId, keyboard, txt1=txt)
    except:
        print('Somthing went wrong')


def message_sender(chatId, messageId, replyMarkup, txt1='', txt2=''):
    """
    отправляет сообщение пользователю через эдит предыдущего сообщения
    """
    try:
        bot.edit_message_text(chat_id=chatId, message_id=messageId,
                          text=txt1+txt2, reply_markup=replyMarkup)
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'help' in call.data)
def help_menu(call):
    """Меню хелП"""
    text = help.text
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(btn_azbuka)
    keyboard.add(btn_how_to_use)
    keyboard.add(btn_write_to_dev)
    keyboard.add(btn_main_menu)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=text, reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: 'serch_in_products' in call.data)
def execute_button_search(call):
    """Отработчик кнопки поиска продукта"""
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(btn_doza, btn_main_menu)
        txt = 'Отправьте первые 2-4 буквы нужного продукта'
        message = bot.send_message(chat_id=call.message.chat.id, text=txt)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=message.message_id,
                              text=txt, reply_markup=keyboard)
        delete_answer(call.message.chat.id, call.message.message_id)
    except:
        print('oops')


@bot.message_handler(content_types=['text'])
def search_product_from_message(message: Message):
    """Выполняет поиск продукта по присланному сообщению"""
    try:
        serched_products = serch_product_by_name(message.text)
        delete_answer(message.chat.id, message.message_id - 1)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboards_array = prod_keyboards(serched_products, 'prod_for_calc')
        for i in range(len(keyboards_array)):
            keyboard.add(keyboards_array[i])
        keyboard.add(btn_serch_product)
        keyboard.add(btn_baza_produktov, btn_main_menu)
        bot.send_message(chat_id=message.chat.id,
                              text=f'Вот что нашел', reply_markup=keyboard)
        delete_answer(message.chat.id, message.message_id)
    except:
        print('oops')





@bot.callback_query_handler(func=lambda call: 'doza' in call.data)
def menu_rashet_doza(call):
    """Меню расчета дозы инсулина"""
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(btn_calculate, btn_my_menus)
        keyboard.add(btn_serch_product, btn_baza_produktov)
        keyboard.add(btn_main_menu)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='РАСЧЕТ ИНСУЛИНА', reply_markup=keyboard)
    except:
        print('oopp')


@bot.callback_query_handler(func=lambda call: 'calculate' in call.data)
def execute_rashet_doza(call):
    """Обработчик кнопки расчитать. Расчитывает дозу инсулина по продуктам в моем меню"""
    try:
        my_menu = load_my_menu(tele_id=call.message.chat.id)
        if my_menu == []:
            bot.answer_callback_query(call.id, show_alert=True, text=f'\U00002757\nОшибка!\nДобавьте продукт\nв ваше меню!')
            return
        bgu = calculate_bgu_from_menu(my_menu)
        massa_menu = calculate_mass_my_menu(my_menu)

        coef = smart_load_coef(call.message.chat.id)

        if coef is None:
            bot.answer_callback_query(call.id, show_alert=True,
                                      text=f'\U00002757Расчет дозы не возможен.\n'
                                      f'Установите коэфициенты К1 и К2 в настройках')
        calc = Calculator(prot=bgu[0], fat=bgu[1], carbo=bgu[2], weight=massa_menu, k1=coef[0], k2=coef[1])
        dose = calc.calculate_dose()
        bot.answer_callback_query(call.id, show_alert=True, text=f'Доза инсулина для вашего меню \n{dose} ед.\n'
                                                                 f'k1={coef[0]}, k2={coef[1]}')
    except ValueError as ex:
        bot.answer_callback_query(call.id, show_alert=True, text=f'\U00002757\nОшибка!\n{ex}')
    except TypeError:
        bot.answer_callback_query(call.id, show_alert=True, text=f'\U00002757\nОшибка!\n'
        f'Проверьте установленный вес во всех продуктах меню,\n'
        f'установлены ли коэфициенты k1, k2 и time зона в настройках бота')
    except Exception as e:
        print(f'Ошибка - {e}')


@bot.callback_query_handler(func=lambda call: 'moi_menu' in call.data)
def my_menu(call):
    """Показывает меню мои меню для расчета дозы инсулина"""
    try:
        menu = load_my_menu(call.message.chat.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        kb = KeyboardMyMenu(1,1)
        keyboards_array = kb.make(menu)
        for i in range(len(keyboards_array)):
            keyboard.add(keyboards_array[i])
        keyboard.add(btn_calculate, btn_delete_menu)
        keyboard.add(btn_baza_produktov, btn_doza)
        keyboard.add(btn_main_menu)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='МОЕ МЕНЮ', reply_markup=keyboard)
    except:
        print('oops')


@bot.callback_query_handler(func=lambda call: 'My_menu_edit' in call.data)
def edit_my_menu(call):
    """Функция ввода нового веса в редактировании Мое меню. На входе 0-вызов, 1-id продукта"""
    try:
        call_dat = call.data.split(',')
        prod_name = call_dat[2]
        keyboard = telebot.types.InlineKeyboardMarkup()
        kb = KeyboardWeight(1, 1)
        main_kb = kb.make(prod_id=call_dat[1], back_menu_flag='my_menu')
        for i in range(len(main_kb)):
            keyboard.row(*main_kb[i])
        keyboard.add(telebot.types.InlineKeyboardButton(text=u"\U0000274C Удалить продукт из меню",
                                                                callback_data=f'delete_from_menu,{call_dat[1]}'))
        keyboard.add(btn_my_menus, btn_baza_produktov)
        keyboard.add(btn_main_menu)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Вес: {prod_name}', reply_markup=keyboard)
    except:
        print('oops')


@bot.callback_query_handler(func=lambda call: 'delete_from_menu' in call.data)
def delete_product_from_menu(call):
    """удаляет продукт из моего меню. на входе [1]-айди продукта """
    try:
        call_dat = call.data.split(',')
        delete_product_from_my_menu_db(call.message.chat.id, call_dat[1])
        bot.answer_callback_query(call.id, show_alert=False, text=f'Продукт удален из меню')
        my_menu(call)
    except:
        print('oops')


@bot.callback_query_handler(func=lambda call: 'delete_my_menu' in call.data)
def delete_my_menu(call):
    """стирает мое меню"""
    try:
        delete_menu_from_db(call.message.chat.id)
        bot.answer_callback_query(call.id, show_alert=False, text=f'Меню удалено')
        my_menu(call)
    except:
        print('oops')


@bot.callback_query_handler(func=lambda call: 'baza_produktov' in call.data)
def show_group_products(call):
    """загрузка групп базы продуктов"""
    try:
        group_products = load_product_groups('groups')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboards_array = products_group_keyboard(group_products, 'use_group')
        for i in range(len(keyboards_array)):
            keyboard.row(*keyboards_array[i])
        keyboard.add(btn_calculate, btn_my_menus)
        keyboard.add(btn_doza, btn_main_menu)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='ГРУППЫ ПРОДУКТОВ', reply_markup=keyboard)
    except:
        print('oops')


def products_group_keyboard(data, calb_name):
    """клавиатура выбора группы в базе продуктов"""
    try:
        keyboards_array = []
        counter = 0
        for i in range(int(len(data)/2)):
            row = []
            for b in range(2):
                row.append(telebot.types.InlineKeyboardButton(text=f'{data[counter][2]}{data[counter][1]}',
                                                              callback_data=f'{calb_name},{data[counter][1]},{data[counter][3]},{data[counter][2]}'))
                counter += 1
            keyboards_array.append(row)
        return keyboards_array
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'use_group' in call.data)
def show_products_from_group(call):
    """показывает продукты в выбранной группе"""
    try:
        call_dat = call.data.split(',')
        group_id = call_dat[2]
        group_products = load_product_groups('products', group_id)
        # pprint(group_products)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboards_array = prod_keyboards(group_products, 'prod_for_calc')
        for i in range(len(keyboards_array)):
            keyboard.add(keyboards_array[i])
        keyboard.add(btn_baza_produktov, btn_main_menu)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'{call_dat[3]}{call_dat[1]}', reply_markup=keyboard)
    except Exception as e:
        print(e)


def prod_keyboards(data, calb_name):
    """клавиатура для показа продуктов в выбранной группе"""
    try:
        keyboards_array = []
        for i in data:
            keyboards_array.append(telebot.types.InlineKeyboardButton(text=f'{i[1]} \U0001F4AA:{int(i[2])} \U0001F43D:{int(i[3])} \U0001F36D:{int(i[4])}',
                                                              callback_data=f'{calb_name}, {i[0]}, {i[1]}'))
        return keyboards_array
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'prod_for_calc' in call.data)
def add_to_menu_ask_weight(call):
    """добавляет продукт в базу меню и предлагает выбрать массу продукта получает 0-вызов, 1-айди продукта, 2-имя продукта"""
    try:
        call_dat = call.data.split(',')
        prod_id = int(call_dat[1])
        add_new_prod_to_menu(call.message.chat.id, prod_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        kb = KeyboardWeight(4, 6)
        main_kb = kb.make(prod_id=call_dat[1])
        for i in range(len(main_kb)):
            keyboard.row(*main_kb[i])
        keyboard.add(btn_baza_produktov, btn_main_menu)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Вес для {call_dat[2]}', reply_markup=keyboard)
    except:
        print('oops')


@bot.callback_query_handler(func=lambda call: 'product_weight' in call.data)
def set_weight(call):
    """Устанавливает вес продукта в меню. Получает 0-вызов, 1-вес, 2-айди продукта"""
    try:
        call_dat = call.data.split(',')
        set_weight_in_db(call.message.chat.id, call_dat[2], call_dat[1])
        bot.answer_callback_query(call.id, show_alert=False, text=f'Установлен вес {call_dat[1]} гр.')
        if call_dat[3] == 'my_menu':
            my_menu(call)
        elif call_dat[3] == 'prod_base':
            show_group_products(call)
    except:
        print('oops')


#=========Меню настроек==========

@bot.callback_query_handler(func=lambda call: 'setup' in call.data)
def setup_menu(call):
    """
    Меню настроек бота. Часовой пояс, коэфициенты.
    """
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(btn_timezone, btn_coefficients)
        keyboard.add(btn_main_menu)
        message_sender(call.message.chat.id, call.message.message_id, keyboard, txt1='НАСТРОЙКИ')
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'set_timezone' in call.data)
def setup_timezone_ui(call):
    try:
        txt = u'\U000023F0 Давайте сверим часы? ' u'\U000023F0 \nВыберете сколько сейчас\nполных часов(без минут)\nв вашей локации.'
        keyboards_array = []
        iter = 0
        for i in range(6):
            row = []
            for t in range(4):
                if iter > 0:
                  t = 4 * iter + t
                row.append(telebot.types.InlineKeyboardButton(text=f'{t}:oo', callback_data=f'timezone {t}'))
            keyboards_array.append(row)
            iter += 1
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in range(len(keyboards_array)):
            keyboard.row(*keyboards_array[i])
        keyboard.add(btn_main_menu, btn_setup)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=txt, reply_markup=keyboard)
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'timezone' in call.data)
def timezone_execute(call):
    try:
        user_time = int(re.findall(r'\w+$', call.data)[0])
        timezone = timezone_calculate(user_time, call.message.edit_date)
        sign = '+' if timezone > 0 else ''
        bot.answer_callback_query(call.id, show_alert=False, text=f'Часовой пояс {sign}{timezone}\nустановлен')
        set_timezone(call.message.chat.id, timezone)
        setup_menu(call)
    except:
        print('Somthing went wrong')


def timezone_calculate(local_user_time, gmt_unix_date):
    """вычисляет таймзону"""
    try:
        gmt_hour = hour_from_unix_time(gmt_unix_date, timezone=0)
        timezone = local_user_time - gmt_hour
        if timezone > 12:
            timezone -= 24
        elif timezone < -12:
            timezone += 24
        return timezone
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'set_coefficients' in call.data)
def my_coef_menu(call):
    """
    Меню мои коэффициенты
    """
    try:
        user_coefficients = read_all_coefficient_from_db(call.message.chat.id)
        user_coefficients.sort(key = lambda row: row[0])
        txt = 'МОИ КОЭФФИЦИЕНТЫ'
        keyboards_array = []
        marks_list = [u"\U000023F0", 'k1', 'k2', 'цеи']
        db_marks_list = ['time', 'k1', 'k2', 'k3']
        for ucRow in user_coefficients:
            row = []
            iter = 0
            for but in ucRow:
                row.append(telebot.types.InlineKeyboardButton(text=f'{marks_list[iter]}={but}',
                                                              callback_data=f'modify_coef,{ucRow[0]},{db_marks_list[iter]}'))
                iter += 1
            keyboards_array.append(row)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in range(len(keyboards_array)):
            keyboard.row(*keyboards_array[i])
        keyboard.add(btn_set_new_coef)
        keyboard.add(btn_delete_coef)
        keyboard.add(btn_setup, btn_main_menu)
        # bot.send_message(chat_id=message.chat.id, text=txt, reply_markup=keyboard)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt, reply_markup=keyboard)
    except Exception as ex:
        print(ex)


@bot.callback_query_handler(func=lambda call: 'set_new_coef' in call.data)
def set_new_coefficient(call):
    try:
        txt = 'Выберете время (час) нового коэффициента'
        keyboards_array = []
        for i in range(6):
            row = []
            for tex in range(4):
                t = (4 * i + tex)
                row.append(telebot.types.InlineKeyboardButton(text=f'{t}:oo', callback_data=f'seting_new_coef_time {t}'))
            keyboards_array.append(row)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in range(len(keyboards_array)):
            keyboard.row(*keyboards_array[i])
        keyboard.add(btn_main_menu, btn_setup)
        keyboard.add(btn_coefficients)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=txt, reply_markup=keyboard)
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'seting_new_coef_time' in call.data)
def check_coef_in_database(call):
    """установка новой ячейки с временем для нового коэфициента"""
    try:
        times = int(re.findall(r'\w+$', call.data)[0])
        if cell_in_table(load_base_uid(call.message.chat.id), times) is None:
            add_coefficient(call.message.chat.id, times)
            bot.answer_callback_query(call.id, show_alert=False,
                                  text=f'Новое время добавлено, теперь отредактируйте коэфициенты в меню Мои Коэфициенты')
        else:
            bot.answer_callback_query(call.id, show_alert=False,
                                  text=f'На это время уже установлены коэфициенты. Редактируйте их в меню Мои Коэфициенты')
        my_coef_menu(call)
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'delete_coef' in call.data)
def delete_coeficient(call):
    """предлагает выбрать время коэфициента для удаления строки в бд"""
    try:
        txt = 'Выберете время коэфициента который хотите удалить'
        #получить все часы бд коэфициентов
        userid = load_base_uid(call.message.chat.id)
        times_in_db = load_base_coef_time(userid)
        times_in_db.sort(key = lambda row: row[0])
        keyboards_array = []
        for t in times_in_db:
            keyboards_array.append(telebot.types.InlineKeyboardButton(text=f"\U000023F0{t[0]}:oo",
                                                                      callback_data=f'delete_time,{t[0]}'))
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in range(len(keyboards_array)):
            keyboard.add(keyboards_array[i])
        keyboard.add(btn_main_menu, btn_setup)
        keyboard.add(btn_coefficients)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=txt, reply_markup=keyboard)
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'delete_time' in call.data)
def delete_coef_action(call):
    try:
        time_for_del = int(re.findall(r'\w+$', call.data)[0])
        uid = load_base_uid(call.message.chat.id)
        id_coef = cell_in_table(uid, time_for_del)
        delete_from_db(id_coef[0])
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(btn_main_menu, btn_setup)
        bot.answer_callback_query(call.id, show_alert=False, text=f'Коэфициенты для {time_for_del}:oo удалены')
        my_coef_menu(call)
    except:
        print('Somthing went wrong')


@bot.callback_query_handler(func=lambda call: 'modify_coef' in call.data)
def ask_for_new_value(call):
    try:
        data = call.data.split(',')
        keyboard = telebot.types.InlineKeyboardMarkup()

        if data[2] == 'time':
            kb = KeyboardEditTimeCoef(4, 6)
            keyboards_array = kb.make(data)
            # keyboards_array = make_keyboard(data, rows_count=4, collums_count=6, multiplier=1)
        else:
            kb = KeyboardEditTimeCoef(5, 6)
            keyboards_array = kb.make(data, 10)
            # keyboards_array = make_keyboard(data, rows_count=5, collums_count=6, multiplier=10)
        for i in range(len(keyboards_array)):
            keyboard.row(*keyboards_array[i])
        keyboard.add(btn_coefficients)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберете новое значение', reply_markup=keyboard)
    except:
        print('Somthing went wrong')

@bot.callback_query_handler(func=lambda call: 'mynewcoef' in call.data)
def modify_coefficient(call):
    try:
        co_edit = call.data.split(',')
        if co_edit[2] == 'time':
            if cell_in_table(load_base_uid(call.message.chat.id), co_edit[3]) is not None:
                bot.answer_callback_query(call.id, show_alert=True,
                                      text=f'Для времени {co_edit[3]}:oo уже существуют коэфициенты\n'
                                           f'Их можно изменить в меню Мои Коэффициенты')
                my_coef_menu(call)
                return
        bot.answer_callback_query(call.id, show_alert=False,
                                  text=f'Коэфициент {co_edit[2]} для {co_edit[1]}oo\nустановлен на {co_edit[3]}')
        add_coefficient(call.message.chat.id, co_edit[1], co_edit[2], co_edit[3])
        my_coef_menu(call)
    except:
        print('Somthing went wrong')

#============Конец меню настроек================


def delete_answer(chatid, messageid):
    try:
        bot.delete_message(chat_id=chatid, message_id=messageid)
    except:
        print('Somthing went wrong')

# @bot.callback_query_handler(func=lambda call: True)



# @bot.message_handler(content_types=['text'])
# @bot.edited_message_handler(content_types=['text'])



#     pprint(message.__dict__)
#     pprint(message.sticker.__dict__)


bot.polling(timeout=60)  # таймаут в сек для ошибок из-за скорости интернета
