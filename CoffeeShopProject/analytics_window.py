from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from mpt_canvas import MptCanvas


class AnalyticsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Top-Selling Items')
        self.canvas = MptCanvas(self, width=6, height=4, dpi=100)
        toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self, item_names, quantities):
        self.canvas.axes.clear()
        self.canvas.axes.bar(item_names, quantities)
        self.canvas.axes.set_xlabel('Menu Item')
        self.canvas.axes.set_ylabel('Quantity Sold')
        self.canvas.axes.set_title('Top Selling Items')
        self.canvas.figure.autofmt_xdate(rotation=45)
        self.canvas.draw()