from db_foo import load_my_menu

def coef_selection_from_time(coef:list, cur_time:int):
    """Выбирает время ближайшего коэфициента"""
    # print(coef, cur_time)
    try:
            best_time = 25
            for i in coef:
                first = abs(i[0] - cur_time)
                second = abs(best_time - cur_time)
                if first > 12:
                    first = abs(first - 24)
                if second > 12:
                    second = abs(second - 24)
                if first < second:
                    best_time = i[0]
                    coef = i
            if best_time > 23:
                best_time -= 24

            # print(coef)
            return coef
            # print(best_time)
    except:
        print('oops')






def calculate_mass_my_menu(menu):
    """Суммируем общую массу еды в меню. На входе мое меню(список кортежей), на выходе инт общая масса"""
    try:
        list = [sum(i) for i in zip(*menu)]
        return list[1]
    except:
        print('oops')


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
        fast_carb_comp = self.weight * ((self.carbo / 100) * (self.glik_index / 100) / self.bread_unit) * self.k1
        slow_carb_comp = self.weight * (
                    (self.carbo / 100) * ((100 - self.glik_index) / 100) / self.bread_unit) * self.k1
        prot_comp = self.weight * (self.prot / 100) * (4.1 / 100) * self.k2
        fat_comp = self.weight * (self.fat / 100) * (9.3 / 100) * self.k2
        doza = fast_carb_comp + slow_carb_comp + prot_comp + fat_comp
        return doza
