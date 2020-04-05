
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeHalfSpace
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_MakeFace
from OCC.Core.BRepFeat import BRepFeat_MakeCylindricalHole
from OCC.Core.gp import gp_Ax1, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec, gp_Pln

from abc import ABC, abstractmethod
from math import radians, sin, cos, floor

from byow.util import euler_to_gp_trsf


class Part(ABC):
    """
    A rigid part that has a position and orientation.
    The position and orientation can be relative to
    a parent part
    """

    def __init__(self, pos=None, ori=None, parent=None):
        """
        initialize the part with a position, orientation and a parent

        :param pos: a 3-element list for the position of the part.
                    Default is [0, 0, 0]
        :param ori: a 3-element list with intrinsic zxz-Euler angles in degrees
                    Default is [0, 0, 0]
        :param parent: The parent part or None. In the first case, pos and ori
                       are relative to the parent part, in the latter they are
                       relative to the global coordinate system
        """

        if ori is None:
            ori = [0, 0, 0]
        if pos is None:
            pos = [0, 0, 0]

        self._position = pos
        self._orientation = ori
        self._parent = parent

        self._set_shape()
        self._place()

        self.name = ''

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def _set_shape(self):
        """adds the shape to the part. This must be implemented
           by the derived classes
        """
        pass

    def _place(self):
        """
        put the part where it belongs. This should be called
        after the shape has been initialized, so that the
        shape can be transformed
        """
        assert (self._shape is not None)

        if self._parent is not None:
            trans = self._parent.shape.Location().Transformation()
        else:
            trans = gp_Trsf()

        translation = gp_Trsf()
        translation.SetTranslation(gp_Vec(*self._position))
        trans = trans * translation

        rot = euler_to_gp_trsf(self._orientation)
        trans = trans * rot

        brep_trns = BRepBuilderAPI_Transform(self._shape, trans, False)
        brep_trns.Build()
        self._shape = brep_trns.Shape()

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self._place()

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._orientation = value
        self._place()

    @property
    def shape(self):
        """ returns the shape """
        return self._shape

    @property
    def parent(self):
        """ returns the parent """
        return self._parent


class Bar(Part):

    def __init__(self,
                 pos=None,
                 ori=None,
                 parent=None,
                 length=2000.,
                 section=(80., 100.),
                 saw_start=None,
                 saw_end=None):

        self._length = length
        self._section = section
        self._saw_start = saw_start
        self._saw_end = saw_end
        super().__init__(pos, ori, parent)

    def _set_shape(self):
        self._shape = BRepPrimAPI_MakeBox(self._length,
                                          self._section[0],
                                          self._section[1]).Shape()

        if self._saw_start is not None:
            ra = radians(self._saw_start)
            sina = sin(ra)
            cosa = cos(ra)
            if ra > 0:
                pnt = gp_Pnt(0, 0, 0)
                pln = gp_Pln(pnt, gp_Dir(-sina, 0, cosa))
                pnt_out = gp_Pnt(0, 0, self._section[1])
            else:
                pnt = gp_Pnt(0, 0, self._section[1])
                pln = gp_Pln(pnt, gp_Dir(sina, 0, -cosa))
                pnt_out = gp_Pnt(0, 0, 0)
            face = BRepBuilderAPI_MakeFace(pln).Shape()
            tool = BRepPrimAPI_MakeHalfSpace(face, pnt_out).Solid()
            self._shape = BRepAlgoAPI_Cut(self._shape, tool).Shape()

        if self._saw_end is not None:
            ra = radians(self._saw_end)
            sina = sin(ra)
            cosa = cos(ra)
            if ra > 0:
                pnt = gp_Pnt(self._length, 0, 0)
                pln = gp_Pln(pnt, gp_Dir(sina, 0, cosa))
                pnt_out = gp_Pnt(self._length, 0, self._section[1])
            else:
                pnt = gp_Pnt(self._length, 0, self._section[1])
                pln = gp_Pln(pnt, gp_Dir(-sina, 0, -cosa))
                pnt_out = gp_Pnt(self._length, 0, 0)

            face = BRepBuilderAPI_MakeFace(pln).Shape()
            tool = BRepPrimAPI_MakeHalfSpace(face, pnt_out).Solid()
            self._shape = BRepAlgoAPI_Cut(self._shape, tool).Shape()

    def __repr__(self):
        out = '# ' + self.name + '\n'
        out += ' - '
        out += (str(round(self._length)) + ' x '
                + str(round(self._section[0])) + ' x '
                + str(round(self._section[1])) + ' mm' + '\n')
        if self._saw_start:
            out += ' - left miter angle: ' + str(self._saw_start) + ' deg\n'
        if self._saw_end:
            out += ' - right miter angle: ' + str(self._saw_end) + ' deg\n'
        out += '\n'
        return out


class Panel(Part):

    def __init__(self,
                 pos=None,
                 ori=None,
                 parent=None,
                 width=1000.,
                 height=2400.,
                 thickness=21.,
                 holes=None):
        if holes is None:
            holes = {'x_start': 100,
                     'x_dist': 200,
                     'y_start': 100,
                     'y_dist': 200,
                     'diameter': 13}
        self._width = width
        self._height = height
        self._thickness = thickness
        self._holes = holes
        super().__init__(pos, ori, parent)

    def __repr__(self):
        out = '# ' + self.name + '\n'
        out += ' - '
        out += (str(round(self._width)) + ' x '
                + str(round(self._height)) + ' mm' + '\n')
        out += ' - Hole diameter: ' + str(round(self._holes['diameter'])) + ' mm\n'
        out += ' - Hole horizontal start: ' + str(round(self._holes['x_start'])) + ' mm\n'
        out += ' - Hole vertical start: ' + str(round(self._holes['y_start'])) + ' mm\n'
        out += ' - horizontal hole spacing: ' + str(round(self._holes['x_dist'])) + ' mm\n'
        out += ' - vertical hole spacing: ' + str(round(self._holes['y_dist'])) + ' mm\n'

        n_holes_x = floor((self._width-self._holes['x_start'])/self._holes['x_dist'])+1
        n_holes_y = floor((self._height - self._holes['y_start']) / self._holes['y_dist'])+1
        out += ' - Num. required drive-in nuts: ' + str(n_holes_x*n_holes_y) + '\n'
        out += '\n'
        return out

    def _set_shape(self):
        self._shape = BRepPrimAPI_MakeBox(self._height, self._width, self._thickness).Shape()
        x = self._holes['x_start']
        y = self._holes['y_start']
        while x < self._height:
            while y < self._width:
                feature_origin = gp_Ax1(gp_Pnt(x, y, 0), gp_Dir(0, 0, 1))
                feature_maker = BRepFeat_MakeCylindricalHole()
                feature_maker.Init(self._shape, feature_origin)
                feature_maker.Build()
                feature_maker.Perform(self._holes['diameter'] / 2.0)
                self._shape = feature_maker.Shape()
                y += self._holes['y_dist']
            x += self._holes['x_dist']
            y = self._holes['y_start']
