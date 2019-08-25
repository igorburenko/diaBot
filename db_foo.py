import psycopg2
from contextlib import closing
import time
from pprint import pprint
import os


DB = os.getenv("DATABASE")
DATABASE = DB.split(',')
db_conn_data = dict(dbname=str(DATABASE[0]),
                    user=str(DATABASE[1]),
                    password=str(DATABASE[2]),
                    host=str(DATABASE[3]))


def add_new_user(userid):
    """
    Добавляет нового юзера в базу данных
    """
    action = "INSERT INTO users (teleuserid) VALUES ({})".format(str(userid))
    connect_to_db_and_action(action, False)


def check_new_user(userid):
    """
    Проверяет наличие юзера в базе данных на вход получает id  юзера
    """
    action = " SELECT teleuserid FROM users WHERE teleuserid = {}" .format(userid)
    result  = connect_to_db_and_action(action, True)
    if result == []:
        return None
    else:
        return result[0]


def load_base_uid(userid):
    """
    На вход получает chatId telegram возвращает UID локальной базы данных
    """
    action = 'SELECT id FROM users WHERE teleuserid = {}'.format(userid)
    answer = connect_to_db_and_action(action, True)[0]
    return answer[0]


def load_base_coef_time(userid):
    """
    На вход получает chatId telegram возвращает все часы(записи) юзера в таблице коэф.
    """
    action = 'SELECT time FROM coefficients WHERE userid = {}'.format(userid)
    answer = connect_to_db_and_action(action, True)
    return answer


def load_timezone_from_db(tele_uid):
    """Загружает текущую таймзону из базы данных. На входе телеграм ИД, на выходе таймзона"""
    action = 'SELECT timezone FROM users WHERE teleuserid = {}'.format(tele_uid)
    answer = connect_to_db_and_action(action, True)
    return answer[0][0]


def set_timezone(userid, timezone):
    """
    Получает на вход телеграмм Юзер айди и временнУю зону устанавливает их в базу данных
    """
    db_uid = load_base_uid(userid)
    action = "UPDATE users SET timezone = {} WHERE id = {}" .format(timezone, db_uid)
    connect_to_db_and_action(action, False)


def connect_to_db_and_action(action: str, retn: bool = False):
    """
    Получает на вход строку обновления или добавления в БД и исполняет ее
    """
    try:
        with closing(psycopg2.connect(**db_conn_data)) as connection:
            with connection.cursor() as cursor:
                cursor.execute(action)
                connection.commit()
                answer = cursor.fetchall() if retn else None
        return answer
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into table", error)


def delete_from_db(id_coef):
    """На  вход - id коэфициента в базе данных
    Удаляет всю строку записи в БД"""
    action = "DELETE FROM coefficients WHERE id_coef = {}".format(id_coef)
    connect_to_db_and_action(action, False)


def add_coefficient(tele_id, coef_time, coef_name='k1', coef_val='NULL'):
    """
    На вход получает юзерайди, время, имя и значение коэффициента и добавляет его в базу данных
    """
    uid = load_base_uid(tele_id)
    cit = cell_in_table(uid, coef_time)
    if cit is None:
        coef_id = None
    else:
        coef_id = cit[0]
    if coef_id is None:
        action = "INSERT INTO coefficients ({}, userid, time) VALUES ({}, {}, {})".format(coef_name, coef_val, uid, coef_time)
    else:
        action = "UPDATE coefficients SET {} = {} WHERE id_coef = {}" .format(coef_name, coef_val, str(coef_id))
    connect_to_db_and_action(action, False)
    return coef_id


def read_all_coefficient_from_db(teleid):
    """
    для расчета дозы
    На вход получает id пользователя в телеге
    Возвращает кортеж коэфициентов (k1, k2, цеи, time)
    используется для настройки коэффициентов кнопками
    """
    userid = load_base_uid(teleid)
    action = 'SELECT time, k1, k2, k3 FROM coefficients WHERE userid = {}'.format(userid)
    answer = connect_to_db_and_action(action, True)
    return answer


def cell_in_table(uid, coef_time):
    """
    Проверяет есть ли у данного юзера запись(строка) на определенное время
    На входе ДБ айди и время у коэфициента
    Если строка есть, возвращает ее айди, если нет Ноне
    используется для проверки в момент ввода нового коэфициента
    и для удаления строки коэф в бд
    """
    action = " SELECT id_coef FROM coefficients WHERE userid = {} AND time = {}" .format(uid, coef_time)
    coef_id = connect_to_db_and_action(action, True)
    return None if coef_id == [] else coef_id[0]


def hour_from_unix_time(unix_time, timezone=3):
    """Получает на вход время юникс эпохи и временную зону
        Возвращает часы по гринвичу
    """
    message_time = time.gmtime(unix_time)[3] + timezone
    if message_time >= 24:
        message_time = message_time - 24
    elif message_time < 0:
        message_time = message_time + 24
    return message_time


def load_product_groups(act_string, group=None):
    """
    Загружает из базы данных группы и продукты в выбранной группе.
    act_string указывает что загружаем группы или продукты
    """
    if act_string == 'groups':
        action = 'SELECT sort_id, group_name, emoji, group_id  FROM groups'
    elif act_string == 'products':
        action = 'SELECT id_prod, prod_name, prot, fats, carb FROM products WHERE group_id = {}' .format(group)
    answer = connect_to_db_and_action(action, True)
    answer.sort(key = lambda row: row[0])
    return answer


def load_product_properties(prod_id):
    """Загружает БЖУ продукта из базы данных. На входе продукт айди. Отдает БЖУ"""
    action = 'SELECT prot, fats, carb FROM products WHERE id_prod = {}'.format(prod_id)
    answer = connect_to_db_and_action(action, True)
    return answer


def add_new_prod_to_menu(tele_id, prod_id, menu_id=1):
    """Добавляет в БД-меню продукт, """
    uid = load_base_uid(tele_id)
    if is_product_in_menu(uid, prod_id):
        return
    else:
        action = "INSERT INTO menu_allusers (id_user, id_prod, id_menu) VALUES ({}, {}, {})".format(uid, prod_id, menu_id)
        connect_to_db_and_action(action, False)


def is_product_in_menu(uid, prod_id):
    """Проверяет есть ли в меню продукт"""
    action = 'SELECT id_prod FROM menu_allusers WHERE id_user = {}'.format(uid)
    answer = connect_to_db_and_action(action, True)
    for i in answer:
        if i[0] == prod_id:
            return True
    return False


def set_weight_in_db(tele_id, product_id, weight):
    """Добавляет(обновляет) вес в меню подсчета"""
    userid = load_base_uid(tele_id)
    action = "UPDATE menu_allusers SET weight = {} WHERE id_user = {} AND id_prod = {}".format(weight, userid, product_id)
    connect_to_db_and_action(action, False)


def load_my_menu(tele_id, menu_id='1'):
    """Загружает мои меню из базы данных, возвращает список кортежей - продукт ИД, вес"""
    userid = load_base_uid(tele_id)
    action = 'SELECT id_prod, weight FROM menu_allusers WHERE id_user = {} AND id_menu = {}'.format(userid, menu_id)
    answer = connect_to_db_and_action(action, True)
    if answer == []:
        raise ValueError('Меню пустое.\nДобавьте хотя бы один продукт\nв ваше меню!')
    return answer


def load_product_name_from_product_id(product_id):
    """Возвращает имя продукта по его ИД в базе"""
    action = 'SELECT prod_name FROM products WHERE id_prod = {}'.format(product_id)
    answer = connect_to_db_and_action(action, True)
    return answer[0][0]


def delete_menu_from_db(tele_id, menu_id='1'):
    """Удаляет мое меню конкретного юзера в базе данных"""
    userid = load_base_uid(tele_id)
    action = "DELETE FROM menu_allusers WHERE id_user = {} AND id_menu = {}".format(userid, menu_id)
    connect_to_db_and_action(action, False)


def delete_product_from_my_menu_db(tele_id, prod_id, menu_id='1'):
    """Удаляет продукт из моего меню"""
    userid = load_base_uid(tele_id)
    action = "DELETE FROM menu_allusers WHERE id_user = {} AND id_menu = {} AND id_prod = {}".format(userid,
                                                                                                     menu_id, prod_id)
    connect_to_db_and_action(action, False)


def serch_product_by_name(request):
    """Поиск продукта в базе данных по имени"""
    req = "'%{}%'".format(request)
    action = "SELECT id_prod, prod_name, prot, fats, carb FROM products WHERE prod_name ILIKE {}".format(req)
    answer = connect_to_db_and_action(action, True)
    answer.sort(key = lambda row: row[1])
    return answer


def load_coef_smart_time_from_db(tele_id, cur_time):
        """
        Подбирает пару ближайших коэфициентов по текущему времени смарт
        """
        userid = load_base_uid(tele_id)
        high_time = load_coef_from_db_for_calculate(userid, cur_time, True)
        low_time = load_coef_from_db_for_calculate(userid, cur_time, False)
        if high_time == []:
            cur_time -= 24
            high_time = load_coef_from_db_for_calculate(userid, cur_time, True)
        elif low_time == []:
            cur_time += 24
            low_time = load_coef_from_db_for_calculate(userid, cur_time, False)
        high_time.append(low_time[0])
        return high_time


def load_coef_from_db_for_calculate(userid, cur_time, flag_high):
    if flag_high:
        action1 = 'SELECT time, k1, k2 FROM coefficients WHERE userid = {} AND time >= {} ' \
                  'ORDER BY time ASC LIMIT 1'.format(userid, cur_time)
        coef = connect_to_db_and_action(action1, True)
    else:
        action2 = 'SELECT time, k1, k2 FROM coefficients WHERE userid = {} AND time <= {} ' \
                  'ORDER BY time DESC LIMIT 1'.format(userid, cur_time)
        coef = connect_to_db_and_action(action2, True)
    return coef

