class Order:
    PROV_TAX = 0.0975
    FED_TAX = 0.05

    def __init__(self, order_number):
        self.__order_number = order_number
        self.__items = []   # list of (menu_item, quantity) tuples

    def get_order_number(self):
        return self.__order_number

    def add_item(self, menu_item, quantity):
        self.__items.append((menu_item, quantity))

    def get_items(self):
        return self.__items

    def calculate_subtotal(self):
        return sum(item.get_price() * quantity for item, quantity in self.__items)

    def calculate_tot_bill(self):
        subtotal = self.calculate_subtotal()
        return subtotal + (subtotal * Order.PROV_TAX) + (subtotal * Order.FED_TAX)
