from PyQt6.QtWidgets import QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QMessageBox
from db_config import get_connection
from analytics_window import AnalyticsWindow

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('The Bean - Reports')

        self.viewOrdersB = QPushButton('View All Orders')
        self.viewOrdersB.clicked.connect(self.show_all_orders)

        self.viewMenuB = QPushButton('View All Menu Items')
        self.viewMenuB.clicked.connect(self.show_all_menu_items)

        self.reportDisplayTE = QTextEdit()
        self.reportDisplayTE.setReadOnly(True)

        self.topItemsB = QPushButton('View Top-Selling Items')
        self.topItemsB.clicked.connect(self.show_top_items)

        self.revenueB = QPushButton('Total Revenue')
        self.revenueB.clicked.connect(self.show_total_revenue)

        layout = QVBoxLayout()
        layout.addWidget(self.viewOrdersB)
        layout.addWidget(self.viewMenuB)
        layout.addWidget(self.reportDisplayTE)
        layout.addWidget(self.topItemsB)
        layout.addWidget(self.revenueB)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.resize(500,600)

    def show_all_orders(self):
        self.reportDisplayTE.clear()

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT order_number, item_type, item_name, size, temp, milk, quantity, total, heated
            FROM order_items ORDER BY order_number
        ''')
        rows = cursor.fetchall()
        connection.close()

        if not rows:
            self.reportDisplayTE.append('No orders found')
            return

        orders = {}
        for order_number, item_type, item_name, size, temp, milk, quantity, total, heated in rows:
            orders.setdefault(order_number, []).append((item_type, item_name, size, temp, milk, quantity, total, heated))

        for order_number, item_lines in orders.items():
            self.reportDisplayTE.append(f'\nOrder #{order_number}:')
            order_subtotal = 0.0
            for item_type, item_name, size, temp, milk, quantity, total, heated in item_lines:
                order_subtotal += float(total)
                if item_type == 'Beverage':
                    self.reportDisplayTE.append(
                        f'  {quantity} x {size} {temp} {item_name} ({milk} milk) - ${float(total):.2f}')
                else:
                    if heated is None:
                        heating_note = ''
                    elif heated:
                        heating_note = ' (heated)'
                    else:
                        heating_note = ' (not heated)'
                    self.reportDisplayTE.append(f'  {quantity} x {item_name}{heating_note} - ${float(total):.2f}')
            tax = order_subtotal * (0.0975 + 0.05)
            self.reportDisplayTE.append(f'  Order Total (with Tax): ${order_subtotal + tax:.2f}')

    def show_all_menu_items(self):
        self.reportDisplayTE.clear()

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT name, price, size FROM beverages')
        beverages = cursor.fetchall()
        cursor.execute('SELECT name, price, requires_heating FROM food_items')
        foods = cursor.fetchall()
        connection.close()

        if not beverages and not foods:
            self.reportDisplayTE.append('No menu items found')
            return

        for name, price, size in beverages:
            self.reportDisplayTE.append(f'{name} ({size}) - ${float(price):.2f}')
        for name, price, requires_heating in foods:
            heating_note = ' (requires heating)' if requires_heating else ''
            self.reportDisplayTE.append(f'{name}{heating_note} - ${float(price):.2f}')

    def show_total_revenue(self):
        self.reportDisplayTE.clear()

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT item_type, SUM(total) AS subtotal 
            FROM order_items 
            GROUP BY item_type
        ''')
        rows = cursor.fetchall()
        connection.close()

        if not rows:
            self.reportDisplayTE.append('No orders found')
            return

        grand_subtotal = 0.0
        self.reportDisplayTE.append('Revenue by Category (Before Tax):')
        for item_type, subtotal in rows:
            subtotal = float(subtotal)
            grand_subtotal += subtotal
            self.reportDisplayTE.append(f'  {item_type} - ${subtotal:.2f}')

        tax = grand_subtotal * (0.0975 + 0.05)
        self.reportDisplayTE.append(f'\nTotal Revenue (Before Tax): ${grand_subtotal:.2f}')
        self.reportDisplayTE.append(f'Total Tax Collected: ${tax:.2f}')
        self.reportDisplayTE.append(f'Total Collected (incl. tax): ${grand_subtotal + tax:.2f}')

    def show_top_items(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT item_name, SUM(quantity) AS total_quantity
            FROM order_items
            GROUP BY item_name
            ORDER BY total_quantity DESC
            LIMIT 10
        ''')
        rows = cursor.fetchall()
        connection.close()

        if not rows:
            QMessageBox.information(self, 'No Data', 'No order data available yet.')
            return

        item_names = [row[0] for row in rows]
        quantities = [row[1] for row in rows]

        self.analytics_window = AnalyticsWindow()
        self.analytics_window.plot(item_names, quantities)
        self.analytics_window.show()
