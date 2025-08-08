from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QFileDialog
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from pyproj import Transformer
from PyQt5 import QtWebEngineWidgets
import sys
import io
import folium

# coordinate transform
transformer_from_EOV = Transformer.from_crs("epsg:23700", "epsg:4326")
transformer_from_KML = Transformer.from_crs("epsg:4326", "epsg:23700")


class Ui_Dialog(object):
    
    def setupUi(self, Dialog):
        # Javítás: super().__init__() eltávolítása, mert ez nem egy QWidget osztály
        # super().__init__()  # Ezt eltávolítottuk
        
        # create message window
        self.message_box = QMessageBox()
        self.message_box.setIcon(QMessageBox.Critical)
        self.message_box.setWindowTitle("Error")

        # create Folium Map     
        coordinate = (47.504105491592426, 19.046773410517797)
        map = folium.Map(
            tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr = 'Esri',
            name = 'Esri Satellite',
            zoom_start=13,
            location=coordinate
        ) 

        map.add_child(folium.ClickForMarker())
        data = io.BytesIO()
        map.save(data, close_file=False)

        # create GUI 
        Dialog.setObjectName("Dialog")
        Dialog.setWhatsThis("Nézd meg a videót :)")
        Dialog.resize(1600, 800)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_6.addWidget(self.label_2)
        self.eovy_input = QtWidgets.QLineEdit(self.groupBox)
        self.eovy_input.setObjectName("eovy_input")
        self.eovy_input.setPlaceholderText("pl.: 650000")
        self.horizontalLayout_6.addWidget(self.eovy_input)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_5.addWidget(self.label)
        self.eovx_input = QtWidgets.QLineEdit(self.groupBox)
        self.eovx_input.setObjectName("eovx_input")
        self.eovx_input.setPlaceholderText("pl.: 240000")
        self.horizontalLayout_5.addWidget(self.eovx_input)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.eovtowgs_button = QtWidgets.QPushButton(self.groupBox)
        self.eovtowgs_button.setObjectName("eovtowgs_button")
        self.horizontalLayout_9.addWidget(self.eovtowgs_button)
        self.eovtowgs_button.clicked.connect(self.button_clicked_eovtowgsmap)
        self.eovtowgs_button_google = QtWidgets.QPushButton(self.groupBox)
        self.eovtowgs_button_google.setObjectName("eovtowgs_button_google")
        self.horizontalLayout_9.addWidget(self.eovtowgs_button_google)
        self.verticalLayout_2.addLayout(self.horizontalLayout_9)
        self.eovtowgs_button_google.clicked.connect(self.button_clicked_eovtogoogle)
        self.eovtowgs_output = QtWidgets.QLineEdit(self.groupBox)
        self.eovtowgs_output.setObjectName("eovtowgs_output")
        self.verticalLayout_2.addWidget(self.eovtowgs_output)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_6.addWidget(self.groupBox)    
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_8.addWidget(self.label_3)
        self.wgsinput = QtWidgets.QLineEdit(self.groupBox_2)
        self.wgsinput.setObjectName("wgsinput")
        self.wgsinput.setPlaceholderText("pl.: 47.50393208, 19.0474447")
        self.horizontalLayout_8.addWidget(self.wgsinput)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.wgstoeov_button = QtWidgets.QPushButton(self.groupBox_2)
        self.wgstoeov_button.setObjectName("wgstoeov_button")
        self.wgstoeov_button.clicked.connect(self.button_simple_convert_to_eov)
        self.verticalLayout_3.addWidget(self.wgstoeov_button)
        self.wgstoeov_output = QtWidgets.QLineEdit(self.groupBox_2)
        self.wgstoeov_output.setObjectName("wgstoeov_output")
        self.verticalLayout_3.addWidget(self.wgstoeov_output)
        self.horizontalLayout_7.addLayout(self.verticalLayout_3)
        self.verticalLayout_6.addWidget(self.groupBox_2)
        self.horizontalLayout_4.addLayout(self.verticalLayout_6)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_3 = QtWidgets.QGroupBox(Dialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.widget = QtWebEngineWidgets.QWebEngineView(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setHtml(data.getvalue().decode())
        self.widget.setObjectName("widget")
        self.verticalLayout_5.addWidget(self.widget)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.lineEdit_printscreen = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_printscreen.setObjectName("lineEdit_printscreen")
        self.horizontalLayout_3.addWidget(self.lineEdit_printscreen)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.pushButton = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.click_handler)
        self.verticalLayout_5.addWidget(self.pushButton)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "EOV-WGS"))
        self.groupBox.setTitle(_translate("Dialog", "EOV-ból WGS"))
        self.label_2.setText(_translate("Dialog", "EOVy:"))
        self.label.setText(_translate("Dialog", "EOVx:"))
        self.eovtowgs_button.setText(_translate("Dialog", "Mutasd a térképen"))
        self.eovtowgs_button_google.setText(_translate("Dialog", "Mutasd Google map-on"))
        self.groupBox_2.setTitle(_translate("Dialog", "WGS-ból EOV"))
        self.label_3.setText(_translate("Dialog", "WGS from google:"))
        self.wgstoeov_button.setText(_translate("Dialog", "WGS to EOV"))
        self.groupBox_3.setTitle(_translate("Dialog", ""))
        self.label_4.setText(_translate("Dialog", "Képernyőmentés neve:"))
        self.pushButton.setText(_translate("Dialog", "Képernyőfotó"))
    
    def validate_coordinates(self, y_input, x_input):
        """Koordináták validálása - új metódus"""
        if not y_input:
            self.message_box.setText("EOVy koordinátát ki kell tölteni")
            self.message_box.show()
            return False

        if "," in y_input:
            self.message_box.setText("tizedes pontot kell használni nem vesszőt")
            self.message_box.show()
            return False

        if not x_input:
            self.message_box.setText("EOVx koordinátát ki kell tölteni")
            self.message_box.show()
            return False

        if "," in x_input:
            self.message_box.setText("tizedes pontot kell használni nem vesszőt")
            self.message_box.show()
            return False
            
        try:
            float(y_input)
            float(x_input)
        except ValueError:
            self.message_box.setText("Érvénytelen koordináták")
            self.message_box.show()
            return False
            
        return True
    
    def button_clicked_eovtowgsmap(self):
        """EOV koordináták konvertálása és térképen megjelenítése - javított verzió"""
        y_input = self.eovy_input.text()
        x_input = self.eovx_input.text()
        
        if not self.validate_coordinates(y_input, x_input):
            return
        
        try:
            input_data_y = float(y_input)
            input_data_x = float(x_input)
            coords = transformer_from_EOV.transform(input_data_y, input_data_x)

            wgs84y = coords[0]
            wgs84x = coords[1]
            
            str_output_data = f"WGS84 coords: {coords}"
            self.eovtowgs_output.setText(str_output_data)

            coordinate = (wgs84y, wgs84x)
            map = folium.Map(
                tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr = 'Esri',
                name = 'Esri Satellite',
                zoom_start=13,
                location=coordinate
            ) 
            
            eovyfloat = float(coords[0])
            eovyfinal = '%.5f' % eovyfloat
            eovxfloat = float(coords[1])
            eovxfinal = '%.5f' % eovxfloat

            tooltip = f"{eovyfinal}, {eovxfinal}"
            popup = f"<b>EOVY: {input_data_y}<br>EOVX: {input_data_x}</b>"

            folium.Marker([wgs84y, wgs84x], popup=popup, tooltip=tooltip).add_to(map)
            map.add_child(folium.ClickForMarker())
            
            data = io.BytesIO()
            map.save(data, close_file=False)
            
            self.widget.setHtml(data.getvalue().decode())
            
        except Exception as e:
            self.message_box.setText(f"Hiba történt: {str(e)}")
            self.message_box.show()

    def button_clicked_eovtogoogle(self):
        """EOV koordináták konvertálása és Google Maps megnyitása - javított verzió"""
        y_input = self.eovy_input.text()
        x_input = self.eovx_input.text()
        
        if not self.validate_coordinates(y_input, x_input):
            return
        
        try:
            input_data_y = float(y_input)
            input_data_x = float(x_input)
            coords = transformer_from_EOV.transform(input_data_y, input_data_x)

            wgs84y = coords[0]
            wgs84x = coords[1]
            
            str_output_data = f"WGS84 coords: {coords}"
            self.eovtowgs_output.setText(str_output_data)
            
            wgsurl = f"https://www.google.hu/maps/?q=loc:{wgs84y},{wgs84x}&t=k&hl=hu&z=100"
            QDesktopServices.openUrl(QUrl(wgsurl))
            
        except Exception as e:
            self.message_box.setText(f"Hiba történt: {str(e)}")
            self.message_box.show()
    
    def button_simple_convert_to_eov(self):
        """WGS koordináták konvertálása EOV-ra - javított verzió"""
        if not self.wgsinput.text():
            self.message_box.setText("Koordinátákat ki kell tölteni")
            self.message_box.show()
            return

        try:
            input_data = self.wgsinput.text().replace(" ", "").split(",")
            
            if len(input_data) != 2:
                self.message_box.setText("Érvénytelen koordináta formátum")
                self.message_box.show()
                return
                
            lat = float(input_data[0])
            lon = float(input_data[1])
            
            eov_coords = transformer_from_KML.transform(lat, lon)
            eovyfloat = float(eov_coords[0])
            eovyfinal = '%.2f' % eovyfloat
            eovxfloat = float(eov_coords[1])
            eovxfinal = '%.2f' % eovxfloat
            
            finalcoords = f"EOV koordinátak Y,X: {eovyfinal},{eovxfinal}"
            self.wgstoeov_output.setText(finalcoords)
            
        except ValueError:
            self.message_box.setText("Érvénytelen koordináták")
            self.message_box.show()
        except Exception as e:
            self.message_box.setText(f"Hiba történt: {str(e)}")
            self.message_box.show()
    
    def click_handler(self):
        """Képernyőfotó készítése - javított verzió"""
        try:
            widget = QApplication.instance().activeWindow().findChild(QWidget, "widget")
            if widget:
                # Take a screenshot of the widget
                pixmap = widget.grab()
                # Save the screenshot to a file
                input_printscreen = self.lineEdit_printscreen.text()
                if not input_printscreen:
                    self.message_box.setText("Adja meg a képernyőfotó nevét")
                    self.message_box.show()
                    return
                    
                filename, _ = QFileDialog.getSaveFileName(
                    widget, 
                    "Képernyőfotó mentése", 
                    f"{input_printscreen}", 
                    "Png files (*.png)"
                )
                
                if filename:
                    pixmap.save(filename, "")
                    self.lineEdit_printscreen.clear()
                    self.message_box.setIcon(QMessageBox.Information)
                    self.message_box.setText("Képernyőfotó sikeresen mentve!")
                    self.message_box.show()
            else:
                self.message_box.setText("Nem található a térkép widget")
                self.message_box.show()
                
        except Exception as e:
            self.message_box.setText(f"Hiba történt: {str(e)}")
            self.message_box.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.setStyleSheet("""
    border-style: ridge;
    border-width: 2px;
    border-radius: 10px;
    """)
    Dialog.show()
    sys.exit(app.exec_())
