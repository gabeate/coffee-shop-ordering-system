class MenuItem:
    def __init__(self, name, price):
        self.__name = name
        self.__price = price

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_price(self):
        return self.__price

    def set_price(self, price):
        self.__price = price

    def display_menu_item(self):
        print(self.__name)
        print(self.__price)

class Beverage(MenuItem):
    def __init__(self, name, price, size, temp, milk_type):
        super().__init__(name, price)
        self.__size = size
        self.__temp = temp
        self.__milk_type = milk_type

    def get_size(self):
        return self.__size

    def set_size(self, size):
        self.__size = size

    def get_temp(self):
        return self.__temp

    def set_temp(self, temp):
        self.__temp = temp

    def get_milk_type(self):
        return self.__milk_type

    def set_milk_type(self, milk_type):
        self.__milk_type = milk_type

    def display_menu_item(self):
        super().display_menu_item()
        print(self.__size)
        print(self.__temp)
        print(self.__milk_type)

class Food(MenuItem):
    def __init__(self, name, price, requires_heating):
        super().__init__(name, price)
        self.__requires_heating = requires_heating

    def get_requires_heating(self):
        return self.__requires_heating

    def set_requires_heating(self, requires_heating):
        self.__requires_heating = requires_heating

    def display_menu_item(self):
        super().display_menu_item()
        if self.__requires_heating:
            print('Heat before serving')
