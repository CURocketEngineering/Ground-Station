import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load('Ground-Station\cure_ground\gui\GUI\GUIContent\Screen01.ui.qml')

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())