import sys
import requests

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow
from data.ui.ui_main import Ui_MainWindow


class Example(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.static_api_server = "http://static-maps.yandex.ru/1.x/"
        self.geocoder_server = "http://geocode-maps.yandex.ru/1.x/"
        self.geocoder_key = "40d1649f-0493-4b70-98ba-98533de7710b"

        self.toponym = None
        self.keys_move = [Qt.Key_Down, Qt.Key_Up, Qt.Key_Left, Qt.Key_Right]

        self.params_static_api = {
            "ll": "83.775671,53.347664",
            "l": "map",
            "size": "650,450",
            "z": 10,
            "pt": ""
        }

        self.params_geocoder_api = {
            "apikey": self.geocoder_key,
            "geocode": None,
            "format": "json"
        }

        self.map_btn.clicked.connect(self.set_map_mode)
        self.sat_btn.clicked.connect(self.set_sat_mode)
        self.hybrid_btn.clicked.connect(self.set_hybrid_mode)
        self.search_btn.clicked.connect(self.search)
        self.reset_search_btn.clicked.connect(self.reset_search)

        self.load_image()

    def show_address(self, obj=None):
        if not obj:
            self.address_text.setText('')
            return
        address = obj['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        self.address_text.setText(address)

    def search(self):
        text = self.search_line_edit.text()  # Адресс поиска
        if not text:
            return
        geo_obj = self.get_toponym(text)
        if not geo_obj:
            return
        self.show_address(geo_obj)
        point = geo_obj["Point"]["pos"].replace(" ", ",")
        self.params_static_api["ll"] = point
        self.params_static_api["pt"] = f'{point},comma'
        self.load_image()

    def reset_search(self):
        self.params_static_api["pt"] = ""
        self.search_line_edit.setText("")
        self.show_address()
        self.load_image()

    def set_map_mode(self):
        self.params_static_api["l"] = "map"
        self.load_image()

    def set_sat_mode(self):
        self.params_static_api["l"] = "sat"
        self.load_image()

    def set_hybrid_mode(self):
        self.params_static_api["l"] = "sat,skl"
        self.load_image()

    def get_address(self, point):
        pass

    def get_toponym(self, geocode):
        self.params_geocoder_api["geocode"] = geocode
        resp = requests.get(self.geocoder_server, params=self.params_geocoder_api)
        if not resp:
            return
        json_resp = resp.json()['response']
        if json_resp['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData'][
            'found'] == '0':  # В случае если звпрос успешен, но результатов нет
            return
        toponym = json_resp["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        return toponym

    def get_image(self):
        resp = requests.get(self.static_api_server, params=self.params_static_api)
        if not resp:
            return
        return resp.content

    def load_image(self):
        image = self.get_image()
        self.main_map.setFocus()
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
