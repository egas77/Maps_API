import sys
import requests

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow
from data.ui.ui_main import Ui_MainWindow

import math

from math import *


class Example(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.static_api_server = "http://static-maps.yandex.ru/1.x/"
        self.geocoder_server = "http://geocode-maps.yandex.ru/1.x/"
        self.geocoder_key = "40d1649f-0493-4b70-98ba-98533de7710b"

        self.keys_move = [Qt.Key_Down, Qt.Key_Up, Qt.Key_Left, Qt.Key_Right]
        self.last_searched_address = None

        self.longitude_on_one_px = 360 / 256  # Градусов на 1 пикселей долготы
        self.latitude_on_one_px = 180 / 256  # Градусов на 1 пикселей широты

        self.params_static_api = {
            "ll": "0,0",
            "l": "map",
            "size": "650,450",
            "z": 0,
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
        self.check_index.toggled.connect(self.show_address)

        self.load_image()

    def show_address(self, obj=None):
        if not isinstance(obj, dict) and not self.last_searched_address:
            self.address_text.setText('')
            return
        if isinstance(obj, dict):
            # если поступил новый запрос обновляем последний найденный адрес
            self.last_searched_address = [
                obj['metaDataProperty']['GeocoderMetaData']['Address']['formatted'],
                obj['metaDataProperty']['GeocoderMetaData']['Address'].get('postal_code')
            ]
        if self.check_index.isChecked() and self.last_searched_address[1]:
            # если у объекта существует почтовый индекс и поставлена соответствующая галочка
            self.address_text.setText(', '.join(self.last_searched_address))
        else:
            self.address_text.setText(self.last_searched_address[0])

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

    def click_on_object(self, coords):
        point = ','.join(list(map(str, coords)))
        geo_obj = self.get_toponym(point)
        if not geo_obj:
            return
        self.show_address(geo_obj)
        self.params_static_api["pt"] = f'{point},comma'
        self.load_image()

    def reset_search(self):
        self.params_static_api["pt"] = ""
        self.search_line_edit.setText("")
        self.last_searched_address = None
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cur_longitude, cur_latitude = list(map(float, self.params_static_api['ll'].split(',')))
            print(cur_longitude, cur_latitude)
            X, Y = self.convert_on_mercator(cur_longitude, cur_latitude)
            print(X, Y)
            Long, Lat = self.convert_on_long_lat(X, Y)
            print(Long, Lat)

    def convert_on_long_lat(self, marcator_x, mercator_y):
        Y = mercator_y
        X = marcator_x
        a = 6378137
        b = 6356752.314
        f = (a - b) / a
        e = sqrt(2 * f - f ** 2)
        pih = pi / 2
        ts = exp(-Y / a)
        phi = pih - 2 * atan(ts)
        i = 0
        dphi = 1
        while fabs(dphi) > 0.000000000001 and i < 1500:
            con = e * sin(phi)
            dphi = pih - 2 * atan(ts * (1 - con) / (1 + con) ** e) - phi
            phi = phi + dphi
        rLong = X / a
        rLat = phi
        Long = rLong * 180 / pi
        Lat = rLat * 180 / pi

        return Long, Lat

    def convert_on_mercator(self, long, lat):
        Lat = lat
        Long = long
        rLat = Lat * pi / 180
        rLong = Long * pi / 180
        a = 6378137
        b = 6356752.3142
        f = (a - b) / a
        e = sqrt(2 * f - f ** 2)
        X = a * rLong
        Y = a * log(tan(pi / 4 + rLat / 2) * ((1 - e * sin(rLat)) / (1 + e * sin(rLat))) ** (e / 2))
        return X, Y


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
