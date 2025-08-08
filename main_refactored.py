"""
EOV-WGS Konverter - Refaktorált verzió
=====================================

Ez a modul egy koordináta konverter alkalmazást tartalmaz,
amely EOV és WGS84 koordináta rendszerek között konvertál.

Author: Refaktorált verzió
Version: 2.0.0
"""

import sys
import io
import os
import logging
from typing import Tuple, Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMessageBox, QFileDialog, 
    QProgressBar, QStatusBar, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QDesktopServices, QFont, QPixmap
from PyQt5.QtCore import QUrl, pyqtSignal, QThread, QTimer
from PyQt5 import QtWebEngineWidgets

from pyproj import Transformer
import folium

# Logging konfiguráció
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MapConfig:
    """Térkép konfigurációs beállítások"""
    DEFAULT_ZOOM: int = 13
    DEFAULT_LOCATION: Tuple[float, float] = (47.504105491592426, 19.046773410517797)
    TILE_URL: str = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    TILE_ATTR: str = 'Esri'
    TILE_NAME: str = 'Esri Satellite'


@dataclass
class CoordinateConfig:
    """Koordináta konfigurációs beállítások"""
    EOV_CRS: str = "epsg:23700"
    WGS84_CRS: str = "epsg:4326"
    COORDINATE_PRECISION: int = 5
    EOV_PRECISION: int = 2


class CoordinateValidator:
    """Koordináta validáció osztály"""
    
    @staticmethod
    def validate_eov_coordinates(y_input: str, x_input: str) -> Tuple[bool, str]:
        """
        EOV koordináták validálása
        
        Args:
            y_input: EOVy koordináta
            x_input: EOVx koordináta
            
        Returns:
            Tuple[bool, str]: (érvényes-e, hibaüzenet)
        """
        if not y_input or y_input == "pl.: 650000":
            return False, "EOVy koordinátát ki kell tölteni"
            
        if "," in y_input:
            return False, "tizedes pontot kell használni nem vesszőt"
            
        if not x_input or x_input == "pl.: 240000":
            return False, "EOVx koordinátát ki kell tölteni"
            
        if "," in x_input:
            return False, "tizedes pontot kell használni nem vesszőt"
            
        try:
            float(y_input)
            float(x_input)
        except ValueError:
            return False, "Érvénytelen koordináták"
            
        return True, ""
    
    @staticmethod
    def validate_wgs_coordinates(wgs_input: str) -> Tuple[bool, str, Optional[Tuple[float, float]]]:
        """
        WGS koordináták validálása
        
        Args:
            wgs_input: WGS koordináta string
            
        Returns:
            Tuple[bool, str, Optional[Tuple[float, float]]]: (érvényes-e, hibaüzenet, koordináták)
        """
        if not wgs_input or wgs_input == "pl.: 47.50393208, 19.0474447":
            return False, "Koordinátákat ki kell tölteni", None
            
        try:
            input_data = wgs_input.replace(" ", "").split(",")
            
            if len(input_data) != 2:
                return False, "Érvénytelen koordináta formátum", None
                
            lat = float(input_data[0])
            lon = float(input_data[1])
            
            return True, "", (lat, lon)
            
        except ValueError:
            return False, "Érvénytelen koordináták", None


class CoordinateConverter:
    """Koordináta konverter osztály"""
    
    def __init__(self):
        """Inicializálja a transformer-eket"""
        self.transformer_from_EOV = Transformer.from_crs(
            CoordinateConfig.EOV_CRS, 
            CoordinateConfig.WGS84_CRS
        )
        self.transformer_from_KML = Transformer.from_crs(
            CoordinateConfig.WGS84_CRS, 
            CoordinateConfig.EOV_CRS
        )
        logger.info("Koordináta converter inicializálva")
    
    def eov_to_wgs(self, eov_y: float, eov_x: float) -> Tuple[float, float]:
        """
        EOV koordináták konvertálása WGS84-re
        
        Args:
            eov_y: EOVy koordináta
            eov_x: EOVx koordináta
            
        Returns:
            Tuple[float, float]: (latitude, longitude)
        """
        try:
            coords = self.transformer_from_EOV.transform(eov_y, eov_x)
            logger.info(f"EOV ({eov_y}, {eov_x}) -> WGS84 {coords}")
            return coords
        except Exception as e:
            logger.error(f"Hiba EOV->WGS84 konverzióban: {e}")
            raise
    
    def wgs_to_eov(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        WGS84 koordináták konvertálása EOV-ra
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Tuple[float, float]: (EOVy, EOVx)
        """
        try:
            coords = self.transformer_from_KML.transform(lat, lon)
            logger.info(f"WGS84 ({lat}, {lon}) -> EOV {coords}")
            return coords
        except Exception as e:
            logger.error(f"Hiba WGS84->EOV konverzióban: {e}")
            raise


class MapManager:
    """Térkép kezelő osztály"""
    
    def __init__(self):
        """Inicializálja a térkép kezelőt"""
        self.current_map_file: Optional[str] = None
        self.markers: List[Dict[str, Any]] = []  # Marker lista tárolása
        logger.info("Térkép kezelő inicializálva")
    
    def create_map(self, location: Tuple[float, float], zoom: int = None) -> folium.Map:
        """
        Térkép létrehozása
        
        Args:
            location: Térkép középpontja
            zoom: Nagyítás szintje
            
        Returns:
            folium.Map: Létrehozott térkép
        """
        zoom = zoom or MapConfig.DEFAULT_ZOOM
        
        map_obj = folium.Map(
            tiles=MapConfig.TILE_URL,
            attr=MapConfig.TILE_ATTR,
            name=MapConfig.TILE_NAME,
            zoom_start=zoom,
            location=location
        )
        
        map_obj.add_child(folium.ClickForMarker())
        logger.info(f"Térkép létrehozva: {location}, zoom: {zoom}")
        return map_obj
    
    def add_marker(self, map_obj: folium.Map, location: Tuple[float, float], 
                   popup: str, tooltip: str) -> None:
        """
        Markert ad a térképhez
        
        Args:
            map_obj: Térkép objektum
            location: Marker pozíciója
            popup: Popup szöveg
            tooltip: Tooltip szöveg
        """
        folium.Marker(location, popup=popup, tooltip=tooltip).add_to(map_obj)
        logger.info(f"Marker hozzáadva: {location}")
    
    def add_marker_with_name(self, map_obj: folium.Map, location: Tuple[float, float], 
                            popup: str, tooltip: str, point_name: str) -> None:
        """
        Markert ad a térképhez pontnévvel
        
        Args:
            map_obj: Térkép objektum
            location: Marker pozíciója
            popup: Popup szöveg
            tooltip: Tooltip szöveg
            point_name: Pont neve (opcionális)
        """
        # Marker adatok tárolása
        marker_data = {
            'location': location,
            'popup': popup,
            'tooltip': tooltip,
            'point_name': point_name
        }
        self.markers.append(marker_data)
        
        if point_name:
            # Ha van pontnév, akkor egyedi ikont használunk és a nevet megjelenítjük
            icon = folium.Icon(color='red', icon='info-sign')
            marker = folium.Marker(
                location, 
                popup=popup, 
                tooltip=tooltip,
                icon=icon
            ).add_to(map_obj)
            
            # Pontnév megjelenítése a marker felett
            folium.map.Marker(
                location,
                popup=point_name,
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 12pt; color: black; background-color: white; padding: 2px; border: 1px solid black; border-radius: 3px;">{point_name}</div>',
                    icon_size=(100, 20),
                    icon_anchor=(50, -30)
                )
            ).add_to(map_obj)
        else:
            # Ha nincs pontnév, akkor normál marker
            folium.Marker(location, popup=popup, tooltip=tooltip).add_to(map_obj)
        
        logger.info(f"Marker hozzáadva: {location}, pontnév: {point_name}")
    
    def add_all_markers_to_map(self, map_obj: folium.Map) -> None:
        """
        Az összes tárolt markert hozzáadja a térképhez
        
        Args:
            map_obj: Térkép objektum
        """
        for marker_data in self.markers:
            location = marker_data['location']
            popup = marker_data['popup']
            tooltip = marker_data['tooltip']
            point_name = marker_data['point_name']
            
            if point_name:
                # Ha van pontnév, akkor egyedi ikont használunk és a nevet megjelenítjük
                icon = folium.Icon(color='red', icon='info-sign')
                marker = folium.Marker(
                    location, 
                    popup=popup, 
                    tooltip=tooltip,
                    icon=icon
                ).add_to(map_obj)
                
                # Pontnév megjelenítése a marker felett
                folium.map.Marker(
                    location,
                    popup=point_name,
                    icon=folium.DivIcon(
                        html=f'<div style="font-size: 12pt; color: black; background-color: white; padding: 2px; border: 1px solid black; border-radius: 3px;">{point_name}</div>',
                        icon_size=(100, 20),
                        icon_anchor=(50, -30)
                    )
                ).add_to(map_obj)
            else:
                # Ha nincs pontnév, akkor normál marker
                folium.Marker(location, popup=popup, tooltip=tooltip).add_to(map_obj)
        
        logger.info(f"Összes marker hozzáadva: {len(self.markers)} db")
    
    def clear_all_markers(self) -> None:
        """Az összes markert törli"""
        self.markers.clear()
        logger.info("Összes marker törölve")
    
    def save_map_to_html(self, map_obj: folium.Map) -> str:
        """
        Térkép mentése HTML fájlba
        
        Args:
            map_obj: Térkép objektum
            
        Returns:
            str: HTML tartalom
        """
        data = io.BytesIO()
        map_obj.save(data, close_file=False)
        html_content = data.getvalue().decode()
        logger.info("Térkép mentve HTML formátumban")
        return html_content


class EOVWGSConverterDialog(QtWidgets.QDialog):
    """Fő alkalmazás ablak"""
    
    # Signal-ok
    map_updated = pyqtSignal(str)  # HTML tartalom
    conversion_completed = pyqtSignal(str)  # Eredmény üzenet
    
    def __init__(self):
        """Inicializálja az alkalmazást"""
        super().__init__()
        
        # Komponensek inicializálása
        self.coordinate_converter = CoordinateConverter()
        self.map_manager = MapManager()
        self.validator = CoordinateValidator()
        
        # UI komponensek
        self.message_box = QMessageBox()
        self.message_box.setIcon(QMessageBox.Critical)
        self.message_box.setWindowTitle("Hiba")
        
        # UI létrehozása
        self.setup_ui()
        self.setup_connections()
        self.create_initial_map()
        
        logger.info("EOV-WGS Konverter alkalmazás elindítva")
    
    def setup_ui(self):
        """UI létrehozása"""
        self.setObjectName("EOVWGSConverterDialog")
        self.setWhatsThis("EOV-WGS Koordináta Konverter")
        self.resize(800, 800)
        
        # Fő layout
        main_layout = QHBoxLayout(self)
        
        # Bal oldali panel - kisebb helyet foglal
        left_panel = self.create_left_panel()
        main_layout.addLayout(left_panel, 1)  # 1-es súly
        
        # Jobb oldali panel (térkép) - több helyet kap
        right_panel = self.create_right_panel()
        main_layout.addLayout(right_panel, 3)  # 3-as súly - 3x több hely
        
        self.retranslate_ui()
    
    def create_left_panel(self) -> QVBoxLayout:
        """Bal oldali panel létrehozása"""
        left_layout = QVBoxLayout()
        
        # EOV-ból WGS csoport
        eov_group = self.create_eov_to_wgs_group()
        left_layout.addWidget(eov_group)
        
        # WGS-ból EOV csoport
        wgs_group = self.create_wgs_to_eov_group()
        left_layout.addWidget(wgs_group)
        

        
        # Pontok törlése gomb
        clear_markers_button = QtWidgets.QPushButton("Összes pont törlése")
        clear_markers_button.setMaximumWidth(120)
        clear_markers_button.clicked.connect(self.clear_all_markers)
        left_layout.addWidget(clear_markers_button)
        
        # KML export gomb
        export_kml_button = QtWidgets.QPushButton("KML export")
        export_kml_button.setMaximumWidth(120)
        export_kml_button.clicked.connect(self.export_to_kml)
        left_layout.addWidget(export_kml_button)
        
        # Rugalmas tér a status bar előtt
        left_layout.addStretch()
        
        # Status bar a bal oldali panel alján - kompaktabb
        self.status_bar = QStatusBar()
        self.status_bar.setMaximumHeight(20)
        self.status_bar.setStyleSheet("QStatusBar { font-size: 10px; }")
        left_layout.addWidget(self.status_bar)
        
        return left_layout
    
    def create_eov_to_wgs_group(self) -> QWidget:
        """EOV-ból WGS konverziós csoport"""
        group = QtWidgets.QGroupBox("EOV-ból WGS")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        group.setFont(font)
        
        layout = QVBoxLayout(group)
        
        # Pontnév input (opcionális)
        name_layout = QHBoxLayout()
        name_label = QtWidgets.QLabel("Pontnév:")
        self.point_name_input = QtWidgets.QLineEdit()
        self.point_name_input.setPlaceholderText("pl.: xyz")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.point_name_input)
        layout.addLayout(name_layout)
        
        # EOVy input
        y_layout = QHBoxLayout()
        y_label = QtWidgets.QLabel("EOVy:")
        self.eovy_input = QtWidgets.QLineEdit()
        self.eovy_input.setPlaceholderText("pl.: 650000")
        y_layout.addWidget(y_label)
        y_layout.addWidget(self.eovy_input)
        layout.addLayout(y_layout)
        
        # EOVx input
        x_layout = QHBoxLayout()
        x_label = QtWidgets.QLabel("EOVx:")
        self.eovx_input = QtWidgets.QLineEdit()
        self.eovx_input.setPlaceholderText("pl.: 240000")
        x_layout.addWidget(x_label)
        x_layout.addWidget(self.eovx_input)
        layout.addLayout(x_layout)
        
        # Gombok
        button_layout = QHBoxLayout()
        self.eovtowgs_button = QtWidgets.QPushButton("Mutasd a térképen")
        self.eovtowgs_button_google = QtWidgets.QPushButton("Mutasd Google map-on")
        button_layout.addWidget(self.eovtowgs_button)
        button_layout.addWidget(self.eovtowgs_button_google)
        layout.addLayout(button_layout)
        
        # Output
        self.eovtowgs_output = QtWidgets.QLineEdit()
        self.eovtowgs_output.setReadOnly(True)
        layout.addWidget(self.eovtowgs_output)
        
        return group
    
    def create_wgs_to_eov_group(self) -> QWidget:
        """WGS-ból EOV konverziós csoport"""
        group = QtWidgets.QGroupBox("WGS-ból EOV")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        group.setFont(font)
        
        layout = QVBoxLayout(group)
        
        # WGS input
        wgs_layout = QHBoxLayout()
        wgs_label = QtWidgets.QLabel("WGS from google:")
        self.wgsinput = QtWidgets.QLineEdit()
        self.wgsinput.setPlaceholderText("pl.: 47.50393208, 19.0474447")
        wgs_layout.addWidget(wgs_label)
        wgs_layout.addWidget(self.wgsinput)
        layout.addLayout(wgs_layout)
        
        # Gomb
        self.wgstoeov_button = QtWidgets.QPushButton("WGS to EOV")
        layout.addWidget(self.wgstoeov_button)
        
        # Output
        self.wgstoeov_output = QtWidgets.QLineEdit()
        self.wgstoeov_output.setReadOnly(True)
        layout.addWidget(self.wgstoeov_output)
        
        return group
    
    def create_right_panel(self) -> QVBoxLayout:
        """Jobb oldali panel létrehozása (térkép)"""
        right_layout = QVBoxLayout()
        
        # Térkép csoport
        map_group = QtWidgets.QGroupBox("Térkép")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        map_group.setFont(font)
        
        map_layout = QVBoxLayout(map_group)
        
        # Térkép widget - nagyobb helyet kap
        self.map_widget = QtWebEngineWidgets.QWebEngineView()
        self.map_widget.setMinimumHeight(600)  # Minimum magasság beállítása
        map_layout.addWidget(self.map_widget)
        
        # Képernyőfotó funkció - kompaktabb
        screenshot_layout = QHBoxLayout()
        screenshot_label = QtWidgets.QLabel("Képernyőmentés:")
        self.lineEdit_printscreen = QtWidgets.QLineEdit()
        self.lineEdit_printscreen.setMaximumWidth(150)
        self.pushButton = QtWidgets.QPushButton("Képernyőfotó")
        self.pushButton.setMaximumWidth(120)
        screenshot_layout.addWidget(screenshot_label)
        screenshot_layout.addWidget(self.lineEdit_printscreen)
        screenshot_layout.addWidget(self.pushButton)
        screenshot_layout.addStretch()  # Rugalmas tér a jobb oldalon
        map_layout.addLayout(screenshot_layout)
        
        right_layout.addWidget(map_group)
        return right_layout
    
    def setup_connections(self):
        """Signal-slot kapcsolatok beállítása"""
        self.eovtowgs_button.clicked.connect(self.convert_eov_to_wgs_and_show_map)
        self.eovtowgs_button_google.clicked.connect(self.convert_eov_to_wgs_and_open_google)
        self.wgstoeov_button.clicked.connect(self.convert_wgs_to_eov)
        self.pushButton.clicked.connect(self.take_screenshot)
        
        # Signal kapcsolatok
        self.map_updated.connect(self.update_map_display)
        self.conversion_completed.connect(self.show_status_message)
    
    def retranslate_ui(self):
        """UI szövegek beállítása"""
        self.setWindowTitle("EOV-WGS Konverter")
    
    def create_initial_map(self):
        """Kezdeti térkép létrehozása"""
        try:
            map_obj = self.map_manager.create_map(MapConfig.DEFAULT_LOCATION)
            html_content = self.map_manager.save_map_to_html(map_obj)
            self.map_updated.emit(html_content)
            self.status_bar.showMessage("Kezdeti térkép betöltve")
        except Exception as e:
            logger.error(f"Hiba a kezdeti térkép létrehozásában: {e}")
            self.show_error("Hiba a kezdeti térkép létrehozásában")
    
    def convert_eov_to_wgs_and_show_map(self):
        """EOV koordináták konvertálása és térképen megjelenítése"""
        try:
            # Validáció
            y_input = self.eovy_input.text()
            x_input = self.eovx_input.text()
            
            is_valid, error_msg = self.validator.validate_eov_coordinates(y_input, x_input)
            if not is_valid:
                self.show_error(error_msg)
                return
            
            # Konverzió
            input_data_y = float(y_input)
            input_data_x = float(x_input)
            coords = self.coordinate_converter.eov_to_wgs(input_data_y, input_data_x)
            
            # Eredmény megjelenítése
            str_output_data = f"WGS84 coords: {coords}"
            self.eovtowgs_output.setText(str_output_data)
            
            # Térkép létrehozása
            map_obj = self.map_manager.create_map(coords)
            
            # Marker hozzáadása
            eovyfinal = f'{coords[0]:.{CoordinateConfig.COORDINATE_PRECISION}f}'
            eovxfinal = f'{coords[1]:.{CoordinateConfig.COORDINATE_PRECISION}f}'
            
            # Pontnév kezelése (opcionális)
            point_name = self.point_name_input.text().strip()
            if point_name:
                tooltip = f"{point_name}<br>{eovyfinal}, {eovxfinal}"
                popup = f"<b>{point_name}</b><br>EOVY: {input_data_y}<br>EOVX: {input_data_x}"
            else:
                tooltip = f"{eovyfinal}, {eovxfinal}"
                popup = f"<b>EOVY: {input_data_y}<br>EOVX: {input_data_x}</b>"
            
            # Marker létrehozása a pontnévvel
            self.map_manager.add_marker_with_name(map_obj, coords, popup, tooltip, point_name)
            
            # Összes korábbi marker hozzáadása
            self.map_manager.add_all_markers_to_map(map_obj)
            
            # Térkép frissítése
            html_content = self.map_manager.save_map_to_html(map_obj)
            self.map_updated.emit(html_content)
            
            self.conversion_completed.emit("EOV->WGS konverzió sikeres")
            
        except Exception as e:
            logger.error(f"Hiba EOV->WGS konverzióban: {e}")
            self.show_error(f"Hiba történt: {str(e)}")
    
    def convert_eov_to_wgs_and_open_google(self):
        """EOV koordináták konvertálása és Google Maps megnyitása"""
        try:
            # Validáció
            y_input = self.eovy_input.text()
            x_input = self.eovx_input.text()
            
            is_valid, error_msg = self.validator.validate_eov_coordinates(y_input, x_input)
            if not is_valid:
                self.show_error(error_msg)
                return
            
            # Konverzió
            input_data_y = float(y_input)
            input_data_x = float(x_input)
            coords = self.coordinate_converter.eov_to_wgs(input_data_y, input_data_x)
            
            # Eredmény megjelenítése
            str_output_data = f"WGS84 coords: {coords}"
            self.eovtowgs_output.setText(str_output_data)
            
            # Google Maps megnyitása
            point_name = self.point_name_input.text().strip()
            if point_name:
                # Ha van pontnév, akkor azt is használjuk a Google Maps URL-ben
                wgsurl = f"https://www.google.hu/maps/?q={point_name}@{coords[0]},{coords[1]}&t=k&hl=hu&z=100"
            else:
                wgsurl = f"https://www.google.hu/maps/?q=loc:{coords[0]},{coords[1]}&t=k&hl=hu&z=100"
            QDesktopServices.openUrl(QUrl(wgsurl))
            
            self.conversion_completed.emit("Google Maps megnyitva")
            
        except Exception as e:
            logger.error(f"Hiba Google Maps megnyitásában: {e}")
            self.show_error(f"Hiba történt: {str(e)}")
    
    def convert_wgs_to_eov(self):
        """WGS koordináták konvertálása EOV-ra"""
        try:
            # Validáció
            wgs_input = self.wgsinput.text()
            is_valid, error_msg, coords = self.validator.validate_wgs_coordinates(wgs_input)
            if not is_valid:
                self.show_error(error_msg)
                return
            
            # Konverzió
            lat, lon = coords
            eov_coords = self.coordinate_converter.wgs_to_eov(lat, lon)
            
            # Eredmény formázása
            eovyfinal = f'{eov_coords[0]:.{CoordinateConfig.EOV_PRECISION}f}'
            eovxfinal = f'{eov_coords[1]:.{CoordinateConfig.EOV_PRECISION}f}'
            finalcoords = f"EOV koordinátak Y,X: {eovyfinal},{eovxfinal}"
            
            self.wgstoeov_output.setText(finalcoords)
            
            self.conversion_completed.emit("WGS->EOV konverzió sikeres")
            
        except Exception as e:
            logger.error(f"Hiba WGS->EOV konverzióban: {e}")
            self.show_error(f"Hiba történt: {str(e)}")
    
    def take_screenshot(self):
        """Képernyőfotó készítése"""
        try:
            input_printscreen = self.lineEdit_printscreen.text()
            if not input_printscreen:
                self.show_error("Adja meg a képernyőfotó nevét")
                return
                
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Képernyőfotó mentése", 
                f"{input_printscreen}.png", 
                "Png files (*.png)"
            )
            
            if filename:
                # Tényleges képernyőfotó készítése
                try:
                    # Teljes ablak képernyőfotója
                    screenshot = self.grab()
                    if screenshot and not screenshot.isNull():
                        if screenshot.save(filename, "PNG"):
                            self.show_info(f"Képernyőfotó sikeresen mentve: {filename}")
                            self.lineEdit_printscreen.clear()
                            logger.info(f"Képernyőfotó mentve: {filename}")
                        else:
                            self.show_error("Hiba történt a képernyőfotó mentése során")
                            logger.error(f"Nem sikerült menteni a képernyőfotót: {filename}")
                    else:
                        self.show_error("Nem sikerült létrehozni a képernyőfotót")
                        logger.error("A képernyőfotó objektum null vagy érvénytelen")
                except Exception as save_error:
                    self.show_error(f"Hiba a képernyőfotó mentése során: {str(save_error)}")
                    logger.error(f"Hiba a képernyőfotó mentése során: {save_error}")
                
        except Exception as e:
            logger.error(f"Hiba képernyőfotó készítésében: {e}")
            self.show_error(f"Hiba történt: {str(e)}")
    
    def update_map_display(self, html_content: str):
        """Térkép megjelenítésének frissítése"""
        try:
            self.map_widget.setHtml(html_content)
            logger.info("Térkép frissítve")
        except Exception as e:
            logger.error(f"Hiba a térkép frissítésében: {e}")
    
    def show_error(self, message: str):
        """Hiba üzenet megjelenítése"""
        self.message_box.setText(message)
        self.message_box.show()
        logger.error(f"Felhasználói hiba: {message}")
    
    def show_info(self, message: str):
        """Információs üzenet megjelenítése"""
        info_box = QMessageBox()
        info_box.setIcon(QMessageBox.Information)
        info_box.setText(message)
        info_box.show()
        logger.info(f"Felhasználói információ: {message}")
    
    def show_status_message(self, message: str):
        """Státusz üzenet megjelenítése"""
        self.status_bar.showMessage(message)
        logger.info(f"Státusz: {message}")
    

    
    def clear_all_markers(self):
        """Összes pont törlése"""
        self.map_manager.clear_all_markers()
        self.status_bar.showMessage("Összes pont törölve")
        logger.info("Összes pont törölve")
        
        # Térkép frissítése üres állapotban
        try:
            map_obj = self.map_manager.create_map(MapConfig.DEFAULT_LOCATION)
            html_content = self.map_manager.save_map_to_html(map_obj)
            self.map_updated.emit(html_content)
            self.conversion_completed.emit("Térkép frissítve - pontok törölve")
        except Exception as e:
            logger.error(f"Hiba a térkép frissítésében: {e}")
            self.show_error("Hiba a térkép frissítésében")
    
    def export_to_kml(self):
        """Összes pont exportálása KML formátumban"""
        try:
            if not self.map_manager.markers:
                self.show_error("Nincsenek pontok az exportáláshoz")
                return
            
            # Fájl mentés dialógus
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "KML fájl mentése", 
                "pontok.kml", 
                "KML files (*.kml)"
            )
            
            if filename:
                # KML tartalom generálása
                kml_content = self.generate_kml_content()
                
                # Fájl mentése
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(kml_content)
                
                self.show_info(f"KML fájl sikeresen mentve: {filename}")
                self.status_bar.showMessage(f"KML export: {len(self.map_manager.markers)} pont")
                logger.info(f"KML fájl mentve: {filename}, {len(self.map_manager.markers)} pont")
                
        except Exception as e:
            logger.error(f"Hiba KML exportálásban: {e}")
            self.show_error(f"Hiba történt: {str(e)}")
    
    def generate_kml_content(self) -> str:
        """KML tartalom generálása az összes pontból"""
        kml_header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>EOV-WGS Konverter Pontok</name>
    <description>Exportált pontok az EOV-WGS Konverter alkalmazásból</description>
"""
        
        kml_footer = """
</Document>
</kml>"""
        
        placemarks = []
        for i, marker_data in enumerate(self.map_manager.markers):
            location = marker_data['location']
            point_name = marker_data['point_name']
            popup = marker_data['popup']
            
            # Pontnév vagy alapértelmezett név
            name = point_name if point_name else f"Pont {i+1}"
            
            # Koordináták (WGS84 formátumban)
            lat, lon = location
            
            # HTML entitások tisztítása a KML-hez
            clean_popup = popup.replace('<b>', '').replace('</b>', '').replace('<br>', '\n')
            
            placemark = f"""    <Placemark>
        <name>{name}</name>
        <description>{clean_popup}</description>
        <Point>
            <coordinates>{lon},{lat},0</coordinates>
        </Point>
    </Placemark>"""
            
            placemarks.append(placemark)
        
        return kml_header + "\n".join(placemarks) + kml_footer


def main():
    """Fő alkalmazás indítása"""
    try:
        app = QApplication(sys.argv)
        
        # Stílus beállítása
        app.setStyleSheet("""
        QDialog {
            border-style: ridge;
            border-width: 2px;
            border-radius: 10px;
        }
        QGroupBox {
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        """)
        
        dialog = EOVWGSConverterDialog()
        dialog.show()
        
        logger.info("Alkalmazás sikeresen elindítva")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical(f"Kritikus hiba az alkalmazás indításában: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
