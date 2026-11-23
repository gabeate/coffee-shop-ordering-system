import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit, QGridLayout, QVBoxLayout,
    QMessageBox, QCheckBox
)

from admin_window import AdminWindow
from login_window import LoginWindow
from add_item_dialog import AddItemDialog
from MenuItem import Beverage, Food
from Order import Order
from db_config import get_connection
from update_order_dialog import UpdateOrderDialog


class MainWindow(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.setWindowTitle(f'The Bean - Order ({role.capitalize()})')
        self.setMinimumWidth(400)
        self.order_number = self.get_next_order_number()
        self.current_order = None
        self.managed_order_number = None
        self.logout_requested = False

        # Widgets
        self.header1L = QLabel('CREATE ORDER')
        self.header1L.setFont(QFont('Arial', 16, QFont.Weight.Bold))

        self.itemL = QLabel('Menu Item:')
        self.itemCB = QComboBox()

        self.sizeL = QLabel('Size:')
        self.sizeCB = QComboBox()
        self.sizeCB.addItems(['Small', 'Medium', 'Large'])

        self.quantityL = QLabel('Quantity:')
        self.quantityLE = QLineEdit()

        self.tempL = QLabel('Temperature:')
        self.tempCB = QComboBox()
        self.tempCB.addItems(['Hot', 'Cold'])

        self.milkL = QLabel('Milk:')
        self.milkCB = QComboBox()
        self.milkCB.addItems(['None', 'Regular', 'Oat', 'Lactose-Free'])

        self.heatingL = QLabel('Heat this item:')
        self.heatingCheckBox = QCheckBox('Yes')
        self.heatingCheckBox.setEnabled(False)

        self.addB = QPushButton('Add to Order')
        self.resetB = QPushButton('Reset')
        self.finishOrderB = QPushButton('Finish Order')
        self.logoutB = QPushButton('Logout')

        self.orderDisplayTE = QTextEdit()
        self.orderDisplayTE.setReadOnly(True)

        self.beverage_menu, self.food_menu = load_menu()

        beverage_names = list(self.beverage_menu.keys())
        food_names = list(self.food_menu.keys())
        self.itemCB.addItems(beverage_names + food_names)

        self.updateOrderB = QPushButton('Update/Delete Order')

        # Button Connections
        self.itemCB.currentTextChanged.connect(self.update_size_state)
        self.addB.clicked.connect(self.add_to_order)
        self.resetB.clicked.connect(self.reset_fields)
        self.finishOrderB.clicked.connect(self.finish_order)
        self.updateOrderB.clicked.connect(self.open_update_order_form)
        self.logoutB.clicked.connect(self.logout)

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.header1L, 0, 0)
        grid.addWidget(self.itemL, 1, 0)
        grid.addWidget(self.itemCB, 1, 1)
        grid.addWidget(self.sizeL, 2, 0)
        grid.addWidget(self.sizeCB, 2, 1)
        grid.addWidget(self.quantityL, 3, 0)
        grid.addWidget(self.quantityLE, 3, 1)
        grid.addWidget(self.tempL, 4, 0)
        grid.addWidget(self.tempCB, 4, 1)
        grid.addWidget(self.milkL, 5, 0)
        grid.addWidget(self.milkCB, 5, 1)
        grid.addWidget(self.heatingL, 6, 0)
        grid.addWidget(self.heatingCheckBox, 6, 1)
        grid.addWidget(self.addB, 7, 0)
        grid.addWidget(self.resetB, 7, 1)
        grid.addWidget(self.finishOrderB, 8, 0, 1, 2)

        # Outer Vertical Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(grid)
        main_layout.addWidget(QLabel('Current Order:'))
        main_layout.addWidget(self.orderDisplayTE)
        main_layout.addWidget(self.updateOrderB)
        main_layout.addWidget(self.logoutB)

        if self.role == 'admin':
            self.adminL = QLabel('ADMIN FUNCTIONS')
            self.adminL.setFont(QFont('Arial', 16, QFont.Weight.Bold))
            self.reportsB = QPushButton('Reports')
            self.addItemB = QPushButton('Add Menu Item')
            self.reportsB.clicked.connect(self.open_reports)
            self.addItemB.clicked.connect(self.open_add_item_form)
            main_layout.addWidget(self.adminL)
            main_layout.addWidget(self.reportsB)
            main_layout.addWidget(self.addItemB)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def update_size_state(self, selected_item):
        is_beverage = selected_item in self.beverage_menu
        self.sizeCB.setEnabled(is_beverage)
        self.tempCB.setEnabled(is_beverage)
        self.milkCB.setEnabled(is_beverage)

        is_food = selected_item in self.food_menu
        self.heatingCheckBox.setEnabled(is_food)
        if is_food:
            self.heatingCheckBox.setChecked(self.food_menu[selected_item].get_requires_heating())
        else:
            self.heatingCheckBox.setChecked(False)

    def get_next_order_number(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT MAX(order_number) FROM orders')
        result = cursor.fetchone()
        connection.close()
        max_order = result[0]
        return (max_order + 1) if max_order else 1

    def add_to_order(self):
        item_name = self.itemCB.currentText()
        quantity_text = self.quantityLE.text().strip()

        if not quantity_text.isdigit() or int(quantity_text) <= 0:
            QMessageBox.warning(self, 'Error', 'Please enter a valid quantity.')
            return
        quantity = int(quantity_text)

        if item_name in self.beverage_menu:
            size = self.sizeCB.currentText()
            temp = self.tempCB.currentText()
            milk = self.milkCB.currentText()
            menu_entry = self.beverage_menu[item_name][size]
            chosen_item = Beverage(menu_entry.get_name(), menu_entry.get_price(), size, temp, milk)
            note = ''
        else:
            heating_choice = self.heatingCheckBox.isChecked()
            menu_entry = self.food_menu[item_name]
            chosen_item = Food(menu_entry.get_name(), menu_entry.get_price(), heating_choice)
            note = ' (heated)' if heating_choice else ' (not heated)'

        if self.current_order is None:
            self.current_order = Order(self.order_number)

        self.current_order.add_item(chosen_item, quantity)
        self.orderDisplayTE.append(f'Added {quantity} x {item_name}{note}: ${chosen_item.get_price():.2f}')

    def finish_order(self):
        if self.current_order is None or not self.current_order.get_items():
            QMessageBox.warning(self, 'Error', 'No items added to the order yet.')
            return

        total = self.current_order.calculate_tot_bill()
        order_number = self.current_order.get_order_number()

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO orders (order_number) VALUES (%s)', (order_number,))

        for item, quantity in self.current_order.get_items():
            if isinstance(item, Beverage):
                cursor.execute(
                    'INSERT INTO order_items (order_number, item_type, item_name, size, temp, milk, quantity, total, heated) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (order_number, 'Beverage', item.get_name(), item.get_size(), item.get_temp(),
                     item.get_milk_type(), quantity, item.get_price() * quantity, None)
                )
            else:
                cursor.execute(
                    'INSERT INTO order_items (order_number, item_type, item_name, size, temp, milk, quantity, total, heated) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (order_number, 'Food', item.get_name(), '', '', '', quantity, item.get_price() * quantity,
                     item.get_requires_heating())
                )

        connection.commit()
        connection.close()

        self.orderDisplayTE.append(f'\nOrder #{order_number} finalized — Total (incl. tax): ${total:.2f}\n')
        self.order_number += 1
        self.current_order = None

    def open_reports(self):
        self.reports_window = AdminWindow()
        self.reports_window.show()

    def open_add_item_form(self):
        dialog = AddItemDialog()
        dialog.exec()

    def open_update_order_form(self):
        dialog = UpdateOrderDialog()
        dialog.exec()

    def reset_fields(self):
        self.itemCB.setCurrentIndex(0)
        self.sizeCB.setCurrentIndex(0)
        self.quantityLE.clear()
        self.tempCB.setCurrentIndex(0)
        self.milkCB.setCurrentIndex(0)
        self.update_size_state(self.itemCB.currentText())

    def logout(self):
        self.logout_requested = True
        self.close()

def load_menu():
    beverage_menu = {}
    food_menu = {}

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT name, price, size FROM beverages')
    for name, price, size in cursor.fetchall():
        if name not in beverage_menu:
            beverage_menu[name] = {}
        beverage_menu[name][size] = Beverage(name, float(price), size, '', '')

    cursor.execute('SELECT name, price, requires_heating FROM food_items')
    for name, price, requires_heating in cursor.fetchall():
        food_menu[name] = Food(name, float(price), bool(requires_heating))

    connection.close()
    return beverage_menu, food_menu


def main():
    app = QApplication(sys.argv)

    while True:
        login_dialog = LoginWindow()
        result = login_dialog.exec()

        if not login_dialog.logged_in:
            break

        window = MainWindow(login_dialog.role)
        window.show()
        app.exec()

        if not window.logout_requested:
            break

    sys.exit()


main()