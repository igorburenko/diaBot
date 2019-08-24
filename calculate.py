from db_foo import load_my_menu, load_product_properties


def map_from_arduino(x, in_min, in_max, out_min, out_max):
    """функция мап как на ардуино. возвращает одно значение нужного коэфициента"""
    if in_min > in_max:
        in_max += 24
    if x < in_min:
        x += 24
    if out_min == out_max:
        return out_min
    return ((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)


def calculate_mass_my_menu(menu):
    """Суммируем общую массу еды в меню. На входе мое меню(список кортежей), на выходе инт общая масса"""
    try:
        list = [sum(i) for i in zip(*menu)]
        return list[1]
    except:
        print('oops')


def calculate_bgu_from_menu(my_menu):
    """Расчитывает общее число БЖУ по моему меню"""
    data_for_calculate = []
    for i in my_menu:
        cell_data_calculate = []
        prod_prop = load_product_properties(i[0])  # Получаем БЖУ продуктов из базы списком кортежей
        for p in prod_prop[0]:
            bgu_v_menu_konkretnogo_producta = i[1] / 100 * p  # Расчитываем по очереди БЖУ в меню по массе продукта
            cell_data_calculate.append(
                bgu_v_menu_konkretnogo_producta)  # Добавляем в список БЖУ - в нем 3 элемента для конкр продукта
        data_for_calculate.append(cell_data_calculate)  # Добавляем в общий список[списков] расчитанных по массе БЖУ
    bgu = [sum(i) for i in zip(*data_for_calculate)]  # суммироем бжу получаем список 3 элемента[Б,Ж,У] всего меню
    return bgu


class Calculator():
    def __init__(self, prot, fat, carbo, weight, k1, k2):
        self.weight = weight
        self.prot = prot
        self.fat = fat
        self.carbo = carbo
        self.k1 = k1
        self.k2 = k2
        self.bread_unit = 10
        self.glik_index = 50

    def calculate_dose(self):
        if self.k1 is None or self.k2 is None:
            return None
        # print(self.weight)
        fast_carb_comp = self.weight * ((self.carbo / 100) * (self.glik_index / 100) / self.bread_unit) * self.k1
        slow_carb_comp = self.weight * (
                    (self.carbo / 100) * ((100 - self.glik_index) / 100) / self.bread_unit) * self.k1
        prot_comp = self.weight * (self.prot / 100) * (4.1 / 100) * self.k2
        fat_comp = self.weight * (self.fat / 100) * (9.3 / 100) * self.k2
        # print(self.k1)
        doza = fast_carb_comp + slow_carb_comp + prot_comp + fat_comp
        doza = round(doza / (self.weight / 100), 1)
        return doza
