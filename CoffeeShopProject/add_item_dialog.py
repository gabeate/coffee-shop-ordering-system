from PyQt6.QtWidgets import QLineEdit, QLabel, QComboBox, QCheckBox, QPushButton, QGridLayout, QMessageBox, QDialog
from db_config import get_connection


class AddItemDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Add Menu Item')

        self.nameL = QLabel('Name:')
        self.nameLE = QLineEdit()

        self.priceL = QLabel('Price:')
        self.priceLE = QLineEdit()

        self.typeL = QLabel('Type:')
        self.typeCB = QComboBox()
        self.typeCB.addItems(['Beverage', 'Food'])

        self.sizeL = QLabel('Size:')
        self.sizeCB = QComboBox()
        self.sizeCB.addItems(['Small', 'Medium', 'Large'])

        self.heatingCB = QCheckBox('Requires heating')
        self.heatingCB.setEnabled(False)

        self.typeCB.currentTextChanged.connect(self.update_type_fields)

        self.saveB = QPushButton('Save Item')
        self.cancelB = QPushButton('Cancel')

        self.saveB.clicked.connect(self.save_item)
        self.cancelB.clicked.connect(self.reject)

        grid = QGridLayout()
        grid.addWidget(self.nameL, 0, 0)
        grid.addWidget(self.nameLE, 0, 1)
        grid.addWidget(self.priceL, 1, 0)
        grid.addWidget(self.priceLE, 1, 1)
        grid.addWidget(self.typeL, 2, 0)
        grid.addWidget(self.typeCB, 2, 1)
        grid.addWidget(self.sizeL, 3, 0)
        grid.addWidget(self.sizeCB, 3, 1)
        grid.addWidget(self.heatingCB, 4, 0, 1, 2)
        grid.addWidget(self.saveB, 5, 0)
        grid.addWidget(self.cancelB, 5, 1)
        self.setLayout(grid)

    def update_type_fields(self, selected_type):
        is_beverage = selected_type == 'Beverage'
        self.sizeCB.setEnabled(is_beverage)
        self.heatingCB.setEnabled(not is_beverage)

    def save_item(self):
        name = self.nameLE.text().strip()
        price_text = self.priceLE.text().strip()

        if not name:
            QMessageBox.warning(self, 'Error', 'Please enter a name')
            return

        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please enter a valid price')
            return

        item_type = self.typeCB.currentText()

        connection = get_connection()
        cursor = connection.cursor()

        if item_type == 'Beverage':
            size = self.sizeCB.currentText()
            cursor.execute(
                'INSERT INTO beverages (name, price, size) VALUES (%s, %s, %s)',
                (name, price, size)
            )
        else:
            requires_heating = self.heatingCB.isChecked()
            cursor.execute(
                'INSERT INTO food_items (name, price, requires_heating) VALUES (%s, %s, %s)',
                (name, price, requires_heating)
            )

        connection.commit()
        connection.close()

        QMessageBox.information(self, 'Saved', f'{name} added to menu.')
        self.accept()