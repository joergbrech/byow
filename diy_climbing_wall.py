#!/usr/bin/env python
# coding: utf-8

from OCC.Display.SimpleGui import init_display

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepFeat import BRepFeat_MakeCylindricalHole
from OCC.Core.gp import gp_Ax1, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec, gp_XYZ

from copy import copy as shallow_copy
from copy import deepcopy
from math import radians, sin, cos, tan


def euler_to_gp_trsf(euler_zxz=None, unit="deg"):
    
    if euler_zxz is None:
        euler_zxz = [0, 0, 0]
    if unit == "deg":  # convert angle to radians
        euler_zxz = [radians(a) for a in euler_zxz]
    
    x = gp_Ax1(gp_Pnt(), gp_Dir(1, 0, 0))
    z = gp_Ax1(gp_Pnt(), gp_Dir(0, 0, 1))

    trns = gp_Trsf()
    trns.SetRotation(z, euler_zxz[2])

    trns_next = gp_Trsf()
    trns_next.SetRotation(x, euler_zxz[1])

    trns = trns*trns_next

    trns_next = gp_Trsf()
    trns_next.SetRotation(z, euler_zxz[0])

    return trns*trns_next


def translate_part(part, vec):

    ret = shallow_copy(part)
    ret._position = deepcopy(part._position)
    ret._orientation = deepcopy(part._orientation)
    ret._parent = part

    if part._parent is not None:
        # TODO: Only transform rotation part
        trans = part._parent._shape.Location().Transformation()
        xyz = gp_XYZ(vec.X(), vec.Y(), vec.Z())
        trans.Transforms(xyz)
        mvec = gp_Vec(xyz.X(), xyz.Y(), xyz.Z())
    else:
        mvec = vec

    trns = gp_Trsf()
    trns.SetTranslation(mvec)
    brep_trns = BRepBuilderAPI_Transform(part._shape, trns, False)
    brep_trns.Build()

    ret._position[0] = vec.X()
    ret._position[1] = vec.Y()
    ret._position[2] = vec.Z()
    ret._shape = brep_trns.Shape()
    return ret   


class Part:

    def __init__(self, pos=None, ori=None, parent=None):
        if ori is None:
            ori = [0, 0, 0]
        if pos is None:
            pos = [0, 0, 0]
        self._position = deepcopy(pos)
        self._orientation = deepcopy(ori)
        self._parent = parent
        self._shape = None

    def place(self):

        assert(self._shape is not None)

        if self._parent is not None:
            trans = self._parent._shape.Location().Transformation()
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
        """
        returns the position in global coordinates
        """
        if self._parent is not None:
            return [self._position[i] + self._parent.position[i] for i in range(0, 3)]
        else:
            return deepcopy(self._position)

    @position.setter
    def position(self, value):
        self._position = value
        self.place()

    @property
    def orientation(self):
        """
        returns the orientation in local coordinates
        """
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._orientation = value
        self.place()


class Bar(Part):

    def __init__(self,
                 pos=None,
                 ori=None,
                 parent=None,
                 length=2000, 
                 section=(80, 100)):

        super().__init__(pos, ori, parent)
        self._length = length
        self._section = section

        self._shape = BRepPrimAPI_MakeBox(length, section[0], section[1]).Shape()
        self.place()
        

class Panel(Part):

    def __init__(self,
                 pos=None,
                 ori=None,
                 parent=None,
                 width=1000, 
                 height=2400,
                 thickness=21,
                 holes=None):
        super().__init__(pos, ori, parent)
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
        
        self.place()


def climbing_wall():

    bar_width = 100
    bar_height = 80
    bar_section = (bar_width, bar_height)
    
    wall_width = 2000
    wall_height = 2400
    wall_thickness = 21
    wall_angle = 25
    holes = {'x_start': 100,
             'x_dist': 200,
             'y_start': 100,
             'y_dist': 200,
             'diameter': 13}


    parts =[]

    # create horizontal bar on the left side
    horizontal_left = Bar(pos=[0, 0, 0],
                          ori=[0, 0, -90],
                          length=2000,
                          section=bar_section)
    parts.append(horizontal_left)

    # create horizontal bar on the right side
    horizontal_right = Bar(pos=[wall_width + horizontal_left._section[0], 0, 0],
                           ori=[0, 0, -90],
                           length=2000,
                           section=bar_section)
    parts.append(horizontal_right)

    # create horizontal part in the lower back
    back = Bar(pos=[horizontal_left._section[0], 0, bar_height],
               ori=[0, 0, 90],
               parent=horizontal_left,
               length=wall_width + 2*horizontal_left._section[0],
               section=bar_section)
    parts.append(back)

    # create three diagonal spars
    sina = sin(radians(wall_angle))
    cosa = cos(radians(wall_angle))
    diag1 = Bar(pos=[horizontal_left._section[0], -2*bar_width + 2*back._section[0]/cosa, back._section[1]*sina],
                ori=[-90, wall_angle-90, 0],
                parent=back,
                length=wall_height,
                section=(bar_height, bar_width))
    parts.append(diag1)

    diag2 = Bar(pos=[0, (wall_width - horizontal_left._section[1])/2, 0],
                parent=diag1,
                length=wall_height,
                section=(bar_height, bar_width))
    parts.append(diag2)

    diag3 = Bar(pos=[0, (wall_width - horizontal_left._section[1]) / 2, 0],
                parent=diag2,
                length=wall_height,
                section=(bar_height, bar_width))
    parts.append(diag3)

    # add the climbing panels
    tana = tan(radians(wall_angle))
    panel_lo = Panel(pos=[tana*diag1._section[1], 0, -wall_thickness],
                     parent=diag1,
                     width=wall_width,
                     height=wall_height/2,
                     thickness=wall_thickness,
                     holes=holes)
    parts.append(panel_lo)

    panel_lo = Panel(pos=[panel_lo._height, 0, 0],
                     parent=panel_lo,
                     width=wall_width,
                     height=wall_height / 2,
                     thickness=wall_thickness,
                     holes=holes)
    parts.append(panel_lo)

    return parts


if __name__ == '__main__':

    parts = climbing_wall()

    display, start_display, add_menu, add_function_to_menu = init_display()
    for part in parts:
        display.DisplayShape(part._shape, update=False)
    display.FitAll()
    start_display()
