from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.logged_in = False
        self.role = None

        self.welcomeL = QLabel("Welcome to The Bean's Ordering System!")
        self.welcomeL.setFont(QFont('Arial', 20, QFont.Weight.Bold))

        self.adminUserL = QLabel('Admin Username:')
        self.adminUserLE = QLineEdit()

        self.employeeUserL = QLabel('Employee Username:')
        self.employeeUserLE = QLineEdit()

        self.passwordL = QLabel('Password:')
        self.passwordLE = QLineEdit()

        self.loginB = QPushButton('Login')
        self.loginB.clicked.connect(self.check_credentials)

        self.cancelB = QPushButton('Cancel')
        self.cancelB.clicked.connect(self.reject)

        grid = QGridLayout()
        grid.addWidget(self.welcomeL, 0, 0, 1, 2)
        grid.addWidget(self.adminUserL, 1, 0)
        grid.addWidget(self.adminUserLE, 1, 1)
        grid.addWidget(self.employeeUserL, 2, 0)
        grid.addWidget(self.employeeUserLE, 2, 1)
        grid.addWidget(self.passwordL, 3, 0)
        grid.addWidget(self.passwordLE, 3, 1)
        grid.addWidget(self.loginB, 4, 0)
        grid.addWidget(self.cancelB, 4, 1)
        self.setLayout(grid)

    def verify(self, username, password, filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    stored_username, stored_password = line.strip().split(',')
                    if username == stored_username and password == stored_password:
                        return True
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', f'{filename} not found.')
        return False

    def check_credentials(self):
        admin_username = self.adminUserLE.text().strip()
        employee_username = self.employeeUserLE.text().strip()
        password = self.passwordLE.text().strip()

        if admin_username and employee_username:
            QMessageBox.warning(self, 'Error', 'Please fill in only one username field.')
            return

        if not admin_username and not employee_username:
            QMessageBox.warning(self, 'Error', 'Please enter a username.')
            return

        if not password:
            QMessageBox.warning(self, 'Error', 'Please enter a password.')
            return

        if admin_username:
            if self.verify(admin_username, password, 'admin_credentials.txt'):
                self.role = 'admin'
                self.logged_in = True
                self.accept()
                return
        else:
            if self.verify(employee_username, password, 'employee_credentials.txt'):
                self.role = 'employee'
                self.logged_in = True
                self.accept()
                return

        QMessageBox.warning(self, 'Error', 'Invalid username or password.')
