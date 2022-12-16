A következó link bemutatja a program használatát:

https://youtu.be/0nZd4pVh-Bk

modulok installálása:

pip install -r requirements.txt

Ha exe-t akarsz csinálni a következő parancsot használd:
pyinstaller --onefile --windowed --copy-metadata pyproj  .\eov-wgs.py

A lenti leírást https://chat.openai.com/chat adta a programról.

"Ez a kód egy EOV alapú pontok átváltására szolgál WGS'84 rendszerbe és térképen megjeleníti azokat.

A kód első része a szükséges importokat tartalmazza:


Ez a program egy PyQt5 alapú GUI-t hoz létre, amely lehetővé teszi a felhasználó számára, hogy kétféle koordináta-rendszerben, az EOV és a WGS'84 koordináta-rendszerben megadja egy adott hely koordinátáit, és azt kattintásra középpontban megjelenítse egy  térképen. A program használja a PyQt5, QDesktopServices és QUrl modulokat is, valamint a folium, pyproj és QtWebEngineWidgets csomagokat. A program létrehozza az Ui_Dialog osztályt is, amelyben létrejön a GUI, valamint egy QMessageBox ablakot, amely hibákat jelenít meg, és egy folium térképet, amelyen kattintásra megjeleníthetők a koordináták. A GUI létrehoz egy QGroupBox-ot, amelyben megtalálhatók az EOV és WGS'84 koordinátákat bekérő mezők, valamint a koordináták átalakításához és megjelenítéséhez használt gombok. A program továbbá lehetővé teszi a felhasználónak, hogy KML formátumú fájlt töltsön be és mentsen el a térképen lévő koordinátákkal.
"

