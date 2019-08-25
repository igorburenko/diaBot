import telebot

# Кнопки которые будут в боте
btn_setup = telebot.types.InlineKeyboardButton(text="\u2699 Настройки", callback_data="setup")
btn_doza = telebot.types.InlineKeyboardButton(text=u"\U0001F489 Расчет дозы", callback_data="doza")
btn_my_menus = telebot.types.InlineKeyboardButton(text=u"\U0001F4CB Моё меню", callback_data="moi_menu")
btn_delete_menu = telebot.types.InlineKeyboardButton(text=u"\U0000274C Очистить меню", callback_data="delete_my_menu")
btn_calculate = telebot.types.InlineKeyboardButton(text=u"\U0001F9EE Расчитать", callback_data="calculate")
btn_my_menu_1 = telebot.types.InlineKeyboardButton(text=u"\U0001F4D5 Меню 1", callback_data="Switch_menu, 1")
btn_my_menu_2 = telebot.types.InlineKeyboardButton(text=u"\U0001F4D7 Меню 2", callback_data="Switch_menu, 2")
btn_my_menu_3 = telebot.types.InlineKeyboardButton(text=u"\U0001F4D8 Меню 3", callback_data="Switch_menu, 3")
btn_del_prod_from_menu = telebot.types.InlineKeyboardButton(text=u"\U0000274C Удалить продукт из меню",
                                                            callback_data="delete_from_menu")
btn_baza_produktov = telebot.types.InlineKeyboardButton(text=u"\U0001F354 База продуктов",
                                                        callback_data="baza_produktov")
btn_serch_product = telebot.types.InlineKeyboardButton(text=u"\U0001F50D Поиск продукта",
                                                        callback_data="serch_in_products")
btn_add_to_base = telebot.types.InlineKeyboardButton(text=u"\U0001F195Добавить в базу"+u"\U0001F195",
                                                     callback_data="add2base")
btn_help = telebot.types.InlineKeyboardButton(text=u"\U00002753 Помощь", callback_data="help")
btn_timezone = telebot.types.InlineKeyboardButton(text=u"\U000023F0 Часовой пояс", callback_data="set_timezone")
btn_coefficients = telebot.types.InlineKeyboardButton(text=u"\U0001F374 Коэффициенты", callback_data="set_coefficients")
btn_main_menu = telebot.types.InlineKeyboardButton(text=u"\U0001F519 Стартовая", callback_data="back2main_menu")
btn_my_coeff = telebot.types.InlineKeyboardButton(text=u"\U0001F374 Мои коэффициенты", callback_data="my_coeff")
btn_set_new_coef = telebot.types.InlineKeyboardButton(text=u"\U00002795 Добавить новый", callback_data="set_new_coef")
btn_delete_coef = telebot.types.InlineKeyboardButton(text=u"\U0000274C Удалить коэфициент", callback_data="delete_coef")
btn_write_to_dev = telebot.types.InlineKeyboardButton(text=u"\U0001F4E8Написать разработчику", url="https://t.me/Burenko")
btn_how_to_use = telebot.types.InlineKeyboardButton(text=u"\U0001F4FAКак пользоваться", url="https://youtube.com")
btn_azbuka = telebot.types.InlineKeyboardButton(text=u"\U0001F4DAАзбука Диаклуба", url="https://juri.dia-club.ru")
btn_gratitude = telebot.types.InlineKeyboardButton(text=u"\U0001F64FБлагодарности", callback_data="gratitude")


emoje1 = '\U0000274C'
