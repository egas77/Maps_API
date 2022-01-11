import sys
import requests

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow
from data.ui.ui_main import Ui_MainWindow

import math

from math import *


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


class Example(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.static_api_server = "http://static-maps.yandex.ru/1.x/"
        self.search_api_server = "https://search-maps.yandex.ru/v1/"
        self.search_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
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

        self.search_params = {
            "apikey": self.search_key,
            "text": "",
            "lang": "ru_RU",
            "type": "biz",
            "ll": "0, 0",
            'results': 1
        }

        self.map_btn.clicked.connect(self.set_map_mode)
        self.sat_btn.clicked.connect(self.set_sat_mode)
        self.hybrid_btn.clicked.connect(self.set_hybrid_mode)
        self.search_btn.clicked.connect(self.search)
        self.reset_search_btn.clicked.connect(self.reset_search)
        self.check_index.toggled.connect(self.show_address)

        self.load_image()

    def show_address(self, obj=None, name_organization=None):
        if not isinstance(obj, dict) and not self.last_searched_address:
            self.address_text.setText('')
            return
        if isinstance(obj, dict):
            # если поступил новый запрос обновляем последний найденный адрес
            self.last_searched_address = [
                obj['metaDataProperty']['GeocoderMetaData']['Address']['formatted']]
            if name_organization:
                self.last_searched_address.append(name_organization)
            postal_code = obj['metaDataProperty']['GeocoderMetaData']['Address'].get('postal_code',
                                                                                     ' ')
            self.last_searched_address.append(postal_code)
        if self.last_searched_address:
            if self.check_index.isChecked():
                self.address_text.setText(', '.join(self.last_searched_address))
            else:
                self.address_text.setText(
                    ','.join(self.last_searched_address[:len(self.last_searched_address) - 1]))

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

    def left_click_on_object(self, coords):
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

    def get_biz(self, point, address):
        self.search_params['ll'] = point
        self.search_params['text'] = address
        resp = requests.get(self.search_api_server, params=self.search_params)
        if not resp:
            return
        json_resp = resp.json()
        organizations = json_resp["features"]
        if not organizations:
            return
        organization = organizations[0]
        point_org = tuple(organization["geometry"]["coordinates"])
        name_organization = organization['properties']['name']
        if lonlat_distance(tuple(map(float, point.split(','))), point_org) > 50:
            return None, None
        return point_org, name_organization

    def right_click_on_object(self, coords):
        point = ','.join(list(map(str, coords)))
        obj = self.get_toponym(point)
        if not obj:
            return
        address = obj['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        biz_obj, name_organization = self.get_biz(point, address)
        if not biz_obj:
            return
        point = ','.join(list(map(str, biz_obj)))
        geo_obj = self.get_toponym(point)
        self.show_address(geo_obj, name_organization=name_organization)
        self.params_static_api["pt"] = f'{point},comma'
        self.load_image()

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
            change_l = 360 / 2 ** (self.params_static_api["z"])
            if ind == 0:
                l2 -= change_l / 8
            elif ind == 1:
                l2 += change_l / 8
            elif ind == 2:
                l1 -= change_l / 4
            else:
                l1 += change_l / 4
            if not (-180 < l1 <= 180):
                l1 = (l1 + 180) % 360 - 180
            if not (-90 < l2 <= 90):
                l2 = (l2 + 90) % 180 - 90
            self.params_static_api['ll'] = f'{l1},{l2}'
            self.load_image()

    def mousePressEvent(self, event):
        if event.button() in (Qt.LeftButton, Qt.RightButton):
            cur_longitude, cur_latitude = list(map(float, self.params_static_api['ll'].split(',')))
            mouse_pox_x, mouse_pox_y = event.x() - self.main_map.x(), event.y() - self.main_map.y()
            dx = mouse_pox_x - self.main_map.width() / 2
            dy = mouse_pox_y - self.main_map.height() / 2

            find_lon = (dx * (self.longitude_on_one_px / (2 ** self.params_static_api["z"])) +
                        cur_longitude)
            find_lat = (-dy *
                        (self.latitude_on_one_px / (2 ** self.params_static_api["z"])) * 1.25 +
                        cur_latitude)
            if event.button() == Qt.LeftButton:
                self.left_click_on_object((find_lon, find_lat))
            else:
                self.right_click_on_object((find_lon, find_lat))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
