import sys
from math import floor, ceil

import qdarkstyle

from diy_climbing_wall import climbing_wall

from OCC.Display.backend import load_any_qt_backend, get_qt_modules

load_any_qt_backend()
QtCore, QtGui, QtWidgets, QtOpenGL = get_qt_modules()
from OCC.Display.qtDisplay import qtViewer3d


class Controller(QtWidgets.QFrame):

    def __init__(self, label_text, unit_text, keys, min, max, *args):
        super().__init__(*args)

        self.dial = QtWidgets.QDial()
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.label = QtWidgets.QLabel()
        self.label.setText(label_text)

        app = QtWidgets.QApplication.instance()
        self.setMinimum(min)
        self.setMaximum(max)
        self.keys = keys
        self.setValue()

        self.setLayout(QtWidgets.QVBoxLayout())
        frame = QtWidgets.QWidget()
        frame.setLayout(QtWidgets.QHBoxLayout())
        frame.layout().addWidget(self.spinbox)
        frame.layout().addWidget(QtWidgets.QLabel(unit_text))
        self.layout().addWidget(self.label)
        self.layout().addWidget(frame)
        self.layout().addWidget(self.dial)

        # connect signals and slots
        self.dial.valueChanged.connect(self.spinbox.setValue)
        self.spinbox.valueChanged.connect(self.dial.setValue)
        self.spinbox.valueChanged.connect(self.update_wall)

        self.spinbox.editingFinished.connect(app.viewer.trigger_redraw)
        self.dial.sliderReleased.connect(app.viewer.trigger_redraw)

        # set size policies and style
        self.dial.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Expanding, )
        self.spinbox.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Minimum)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                           QtWidgets.QSizePolicy.Minimum)

        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Raised)
        self.setLineWidth(2)
        self.setStyleSheet("#base_frame {border: 1px solid rgb(255,255,255)}")

    def setMinimum(self, val):
        self.dial.setMinimum(val)
        self.spinbox.setMinimum(val)

    def setMaximum(self, val):
        self.dial.setMaximum(val)
        self.spinbox.setMaximum(val)

    def setValue(self):

        app = QtWidgets.QApplication.instance()
        dict = app.wall
        for i in range(0, len(self.keys)-1):
            dict = app.wall[self.keys[i]]

        self.dial.setValue(dict[self.keys[-1]])
        self.spinbox.setValue(dict[self.keys[-1]])

    def update_wall(self):

        app = QtWidgets.QApplication.instance()
        dict = app.wall
        for i in range(0, len(self.keys) - 1):
            dict = app.wall[self.keys[i]]
        dict[self.keys[-1]] = self.dial.value()
        app.viewer.needs_redraw=True


class ControllerTab(QtWidgets.QWidget):

    def __init__(self, *args):
        super().__init__(*args)
        self.ndials = 0
        self.setLayout(QtWidgets.QGridLayout())

    def append(self, controller):
        i = floor(self.ndials / 2.)
        j = ceil(self.ndials / 2. - i)
        self.layout().addWidget(controller, i, j)
        self.ndials += 1


class Viewer3d(qtViewer3d):

    def __init__(self, *args):
        super().__init__(*args)
        self.needs_redraw = True
        self.InitDriver()

    def trigger_redraw(self):
        if self.needs_redraw:
            self._redraw()

    def _redraw(self):
        app = QtWidgets.QApplication.instance()
        self._display.EraseAll()
        parts = climbing_wall(**app.wall)
        for part in parts:
            self._display.DisplayShape(part._shape, update=False)
        self._display.FitAll()
        self.needs_redraw = False


class MainWindow(QtWidgets.QMainWindow):
    """
    Main Windows of the BYOW GUI
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setAcceptDrops(True)

        self.frame = QtWidgets.QFrame()
        self.setCentralWidget(self.frame)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(self.layout)

        self.splitter = QtWidgets.QSplitter(self.frame)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        app = QtWidgets.QApplication.instance()
        self.splitter.addWidget(app.viewer)

        self.tabs = QtWidgets.QTabWidget()
        self.splitter.addWidget(self.tabs)

        self.wall_parameters = ControllerTab()
        self.panel_parameters = ControllerTab()
        self.tabs.addTab(self.wall_parameters, "Wall Parameters")
        self.tabs.addTab(self.panel_parameters, "Panel Parameters")

        self.width_controller = Controller("Width",
                                           "mm",
                                           ["wall_width", ],
                                           200,
                                           8000)
        self.wall_parameters.append(self.width_controller)

        self.height_controller = Controller("Height",
                                            "mm",
                                            ["wall_height", ],
                                            200,
                                            8000)
        self.wall_parameters.append(self.height_controller)

        self.angle_controller = Controller("Overhang angle",
                                           "degrees",
                                           ["wall_angle", ],
                                           0,
                                           85)
        self.wall_parameters.append(self.angle_controller)

        self.gap_controller = Controller("Gap",
                                         "mm",
                                         ["gap", ],
                                         0,
                                         2000)
        self.wall_parameters.append(self.gap_controller)

        self.safety_controller = Controller("Foot Length",
                                            "mm",
                                            ["safety", ],
                                            0,
                                            8000)
        self.wall_parameters.append(self.safety_controller)

        self.thickness_controller = Controller("Thickness",
                                               "mm",
                                               ["wall_thickness", ],
                                               2,
                                               100)
        self.panel_parameters.append(self.thickness_controller)

        self.diameter_controller = Controller("Hole Diameter",
                                              "mm",
                                              ["holes", "diameter"],
                                              1,
                                              50)
        self.panel_parameters.append(self.diameter_controller)

        self.x_start_controller = Controller("Hole Start x-direction",
                                             "mm",
                                             ["holes", "x_start"],
                                             1,
                                             1000)
        self.panel_parameters.append(self.x_start_controller)

        self.y_start_controller = Controller("Hole Start y-direction",
                                             "mm",
                                             ["holes", "y_start"],
                                             1,
                                             1000)
        self.panel_parameters.append(self.y_start_controller)

        self.x_dist_controller = Controller("Hole distance x-direction",
                                            "mm",
                                            ["holes", "x_dist"],
                                            1,
                                            1000)
        self.panel_parameters.append(self.x_dist_controller)

        self.y_dist_controller = Controller("Hole distance y-direction",
                                            "mm",
                                            ["holes", "y_dist"],
                                            1,
                                            1000)
        self.panel_parameters.append(self.y_dist_controller)

        self.showMaximized()


class BYOWApp(QtWidgets.QApplication):

    def __init__(self, args):
        super(BYOWApp, self).__init__(args)
        self.setApplicationDisplayName('Build Your Own Wall')
        self.setStyleSheet(qdarkstyle.load_stylesheet())

        self._wall = {'wall_width': 2000,
                      'wall_height': 2400,
                      'wall_thickness': 21,
                      'wall_angle': 25,
                      'gap': 100,
                      'safety': 500,
                      'holes': {
                          'x_start': 100.,
                          'x_dist': 200.,
                          'y_start': 100.,
                          'y_dist': 200.,
                          'diameter': 13.
                      }
                      }

        self.viewer = Viewer3d()
        self.window = MainWindow()
        self.setActiveWindow(self.window)

    @property
    def wall(self):
        return self._wall

    @wall.setter
    def wall(self, value):
        if value != self._wall:
            self.viewer.needs_redraw = True
        self._wall = value

    def run(self):
        self.exec_()


def gui():
    # start app and open main window
    BYOWApp(sys.argv).run()


if __name__ == '__main__':

    # start app and open main window
    app = BYOWApp(sys.argv)
    app.viewer.trigger_redraw()
    app.run()
