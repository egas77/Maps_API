import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui_main import Ui_MainWindow


class Example(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.static_api_server = "http://static-maps.yandex.ru/1.x/"
        self.geocoder_server = "http://geocode-maps.yandex.ru/1.x/"
        self.geocoder_key = "40d1649f-0493-4b70-98ba-98533de7710b"

        self.initUI()

    def get_address(self, point):
        pass

    def get_toponym(self, address):
        params = {
            "apikey": self.geocoder_key,
            "geocode": address,
            "format": "json"
        }
        resp = requests.get(self.geocoder_server, params=params)
        if not resp:
            return
        toponym = resp.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        return toponym

    def get_image(self, params):
        resp = requests.get(self.static_api_server, params=params)
        if not resp:
            return
        return resp.content

    def initUI(self):
        self.setupUi(self)

        toponym = self.get_toponym("Барнаул, Ленина, 61")
        if toponym:
            image = self.get_image({
                "ll": toponym['Point']['pos'].replace(' ', ','),
                "spn": '0.003,0.003',
                "l": "map",
                "size": "650,450"
            })
            pixmap = QPixmap.fromImage(QImage.fromData(image))
            pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio)
            self.main_map.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
