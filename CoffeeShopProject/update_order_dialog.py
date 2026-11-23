from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QListWidget, QGridLayout, QVBoxLayout, QMessageBox
)
from db_config import get_connection


class UpdateOrderDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Update / Delete Order')
        self.setMinimumWidth(400)

        self.orderNumberL = QLabel('Order Number:')
        self.orderNumberLE = QLineEdit()
        self.findB = QPushButton('Find Order')
        self.findB.clicked.connect(self.find_order)

        self.itemsLW = QListWidget()

        self.newQuantityL = QLabel('New Quantity:')
        self.newQuantityLE = QLineEdit()
        self.updateQtyB = QPushButton('Update Quantity')
        self.updateQtyB.clicked.connect(self.update_quantity)
        self.deleteItemB = QPushButton('Remove Selected Item')
        self.deleteItemB.clicked.connect(self.delete_item)
        self.deleteOrderB = QPushButton('Delete Order')
        self.deleteOrderB.clicked.connect(self.delete_order)
        self.closeB = QPushButton('Close')
        self.closeB.clicked.connect(self.accept)

        top_layout = QGridLayout()
        top_layout.addWidget(self.orderNumberL, 0, 0)
        top_layout.addWidget(self.orderNumberLE, 0, 1)
        top_layout.addWidget(self.findB, 0, 2)

        bottom_layout = QGridLayout()
        bottom_layout.addWidget(self.newQuantityL, 0, 0)
        bottom_layout.addWidget(self.newQuantityLE, 0, 1)
        bottom_layout.addWidget(self.updateQtyB, 0, 2)
        bottom_layout.addWidget(self.deleteItemB, 1, 0, 1, 3)
        bottom_layout.addWidget(self.deleteOrderB, 2, 0, 1, 3)
        bottom_layout.addWidget(self.closeB, 3, 0, 1, 3)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.itemsLW)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

        self.current_order_number = None

    def find_order(self):
        order_number_text = self.orderNumberLE.text().strip()
        if not order_number_text.isdigit():
            QMessageBox.warning(self, 'Error', 'Please enter a valid order number.')
            return

        self.current_order_number = int(order_number_text)
        self.itemsLW.clear()

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            'SELECT order_item_id, item_type, item_name, size, temp, milk, quantity, total '
            'FROM order_items WHERE order_number = %s',
            (self.current_order_number,)
        )
        rows = cursor.fetchall()
        connection.close()

        if not rows:
            QMessageBox.information(self, 'Not Found', f'No order found with number {self.current_order_number}.')
            return

        for order_item_id, item_type, item_name, size, temp, milk, quantity, total in rows:
            if item_type == 'Beverage':
                label = f'{quantity} x {size} {temp} {item_name} ({milk} milk) - ${float(total):.2f}'
            else:
                label = f'{quantity} x {item_name} - ${float(total):.2f}'
            self.itemsLW.addItem(label)
            self.itemsLW.item(self.itemsLW.count() - 1).setData(Qt.ItemDataRole.UserRole, order_item_id)

    def update_quantity(self):
        selected = self.itemsLW.currentItem()
        if selected is None:
            QMessageBox.warning(self, 'Error', 'Please select an item first.')
            return

        new_quantity_text = self.newQuantityLE.text().strip()
        if not new_quantity_text.isdigit() or int(new_quantity_text) <= 0:
            QMessageBox.warning(self, 'Error', 'Please enter a valid quantity.')
            return
        new_quantity = int(new_quantity_text)

        order_item_id = selected.data(Qt.ItemDataRole.UserRole)

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT quantity, total FROM order_items WHERE order_item_id = %s', (order_item_id,))
        old_quantity, old_total = cursor.fetchone()
        unit_price = float(old_total) / old_quantity
        new_total = unit_price * new_quantity

        cursor.execute(
            'UPDATE order_items SET quantity = %s, total = %s WHERE order_item_id = %s',
            (new_quantity, new_total, order_item_id)
        )
        connection.commit()
        connection.close()

        QMessageBox.information(self, 'Updated', 'Quantity updated.')
        self.find_order()

    def delete_item(self):
        selected = self.itemsLW.currentItem()
        if selected is None:
            QMessageBox.warning(self, 'Error', 'Please select an item first.')
            return

        order_item_id = selected.data(Qt.ItemDataRole.UserRole)

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM order_items WHERE order_item_id = %s', (order_item_id,))

        cursor.execute('SELECT COUNT(*) FROM order_items WHERE order_number = %s', (self.current_order_number,))
        remaining = cursor.fetchone()[0]
        if remaining == 0:
            cursor.execute('DELETE FROM orders WHERE order_number = %s', (self.current_order_number,))

        connection.commit()
        connection.close()

        QMessageBox.information(self, 'Removed', 'Item removed.')
        self.find_order()

    def delete_order(self):
        if self.current_order_number is None:
            QMessageBox.warning(self, 'Error', 'Please find an order first.')
            return

        confirm = QMessageBox.question(
            self, 'Confirm Delete', f'Delete order #{self.current_order_number} entirely?'
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM order_items WHERE order_number = %s', (self.current_order_number,))
        cursor.execute('DELETE FROM orders WHERE order_number = %s', (self.current_order_number,))
        connection.commit()
        connection.close()

        QMessageBox.information(self, 'Deleted', f'Order #{self.current_order_number} deleted.')
        self.itemsLW.clear()
        self.current_order_number = None