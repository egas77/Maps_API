import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow
from data.ui.ui_main import Ui_MainWindow


class Example(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.static_api_server = "http://static-maps.yandex.ru/1.x/"
        self.geocoder_server = "http://geocode-maps.yandex.ru/1.x/"
        self.geocoder_key = "40d1649f-0493-4b70-98ba-98533de7710b"

        self.toponym = None
        self.keys_move = [Qt.Key_Down, Qt.Key_Up, Qt.Key_Left, Qt.Key_Right]

        self.params_static_api = {
            "ll": "83.775671,53.347664",
            "l": "map",
            "size": "650,450",
            "z": 10
        }

        self.params_geocoder_api = {
            "apikey": self.geocoder_key,
            "geocode": None,
            "format": "json"
        }

        self.setupUi(self)
        self.load_image()

    def get_address(self, point):
        pass

    def get_toponym(self, address):
        self.params_geocoder_api["geocode"] = address
        resp = requests.get(self.geocoder_server, params=self.params_geocoder_api)
        if not resp:
            return
        toponym = resp.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        return toponym

    def get_image(self):
        resp = requests.get(self.static_api_server, params=self.params_static_api)
        if not resp:
            return
        return resp.content

    def load_image(self):
        image = self.get_image()
        if image:
            pixmap = QPixmap.fromImage(QImage.fromData(image))
            self.main_map.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            if self.params_static_api["z"] > 0:
                self.params_static_api["z"] -= 1
                self.load_image()
        elif event.key() == Qt.Key_PageUp:
            if self.params_static_api["z"] < 18:
                self.params_static_api["z"] += 1
                self.load_image()
        elif event.key() in self.keys_move:
            l1, l2 = map(float, self.params_static_api['ll'].split(','))
            ind = self.keys_move.index(event.key())
            change_l = 10 / 2 ** (self.params_static_api["z"])
            if ind == 0:
                l2 -= change_l / 2
            elif ind == 1:
                l2 += change_l / 2
            elif ind == 2:
                l1 -= change_l
            else:
                l1 += change_l
            if not (-180 < l1 <= 180):
                l1 = (l1 + 180) % 360 - 180
            if not (-90 < l2 <= 90):
                l2 = (l2 + 90) % 180 - 90
            self.params_static_api['ll'] = f'{l1},{l2}'
            self.load_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
