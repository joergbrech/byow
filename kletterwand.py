#!/usr/bin/env python
# coding: utf-8



from OCC.Display.SimpleGui import init_display

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepFeat import BRepFeat_MakeCylindricalHole
from OCC.Core.gp import gp_Ax1, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec

from math import radians, sin, cos


x_axis = gp_Ax1(gp_Pnt(), gp_Dir(1,0,0))
y_axis = gp_Ax1(gp_Pnt(), gp_Dir(0,1,0))
z_axis = gp_Ax1(gp_Pnt(), gp_Dir(0,0,1))


display, start_display, add_menu, add_function_to_menu = init_display()


def rotate_shape(shape, axis, angle, unite="deg"):
    """ Rotate a shape around an axis, with a given angle.
    @param shape : the shape to rotate
    @point : the origin of the axis
    @vector : the axis direction
    @angle : the value of the rotation
    @return: the rotated shape.
    """
    if unite == "deg":  # convert angle to radians
        angle = radians(angle)
    trns = gp_Trsf()
    trns.SetRotation(axis, angle)
    brep_trns = BRepBuilderAPI_Transform(shape, trns, False)
    brep_trns.Build()
    shp = brep_trns.Shape()
    return shp



def translate_shp(shp, vec, copy=False):
    trns = gp_Trsf()
    trns.SetTranslation(vec)
    brep_trns = BRepBuilderAPI_Transform(shp, trns, copy)
    brep_trns.Build()
    return brep_trns.Shape()



# inputs
w = 2000
h = 2400
a = 25
raster = 200



# other parameters
kh_w = 80
kh_h = 100
thickness = 21

dy = h*sin(radians(a))
dz = h*cos(radians(a))

z_gap = kh_w-kh_h*sin(radians(a))
#y_gap = (kh_h-kh_h*cos(radians(a)))

lower_back = BRepPrimAPI_MakeBox(w+2*kh_h, kh_h, kh_w).Shape()
lower_back = translate_shp(lower_back, gp_Vec(-kh_h, 0, 0))
display.DisplayShape(lower_back, update=False)

diag1 = BRepPrimAPI_MakeBox(kh_w, kh_h, h).Shape()
diag1 = rotate_shape(diag1, x_axis, a)
diag1 = translate_shp(diag1, gp_Vec(0, 0, z_gap))
display.DisplayShape(diag1, update=False)

diag2 = translate_shp(diag1, gp_Vec(w-kh_w, 0, 0), copy=True)
display.DisplayShape(diag2, update=False)

lower_side1 = BRepPrimAPI_MakeBox(kh_h, dy+kh_h, kh_w).Shape()
lower_side1 = translate_shp(lower_side1, gp_Vec(-kh_h, -dy, -kh_w))
display.DisplayShape(lower_side1, update=False)

lower_side2 = translate_shp(lower_side1, gp_Vec(w+kh_h, 0, 0), copy=True)
display.DisplayShape(lower_side2, update=False)

side1 = BRepPrimAPI_MakeBox(kh_h, kh_w, dz+kh_w+z_gap).Shape()
side1 = translate_shp(side1, gp_Vec(-kh_h, -kh_w-dy, -kh_w))
display.DisplayShape(side1, update=False)

side2 = translate_shp(side1, gp_Vec(w+kh_h, 0, 0))
display.DisplayShape(side2, update=False)

top = BRepPrimAPI_MakeBox(w+2*kh_h, kh_w, kh_h).Shape()
top = translate_shp(top, gp_Vec(-kh_h,-dy-kh_w,dz+z_gap))
display.DisplayShape(top, update=False)



def paneel(h,w,thickness, raster):
    p = BRepPrimAPI_MakeBox(w, thickness, h).Shape()
    
    feature_diameter = 13
    origin_x = raster/2
    origin_z = raster/2
    while origin_x < w:
        while origin_z < h:
            feature_origin = gp_Ax1(gp_Pnt(origin_x, 0, origin_z), gp_Dir(0, 1, 0))
            feature_maker = BRepFeat_MakeCylindricalHole()
            feature_maker.Init(p, feature_origin)
            feature_maker.Build()
            feature_maker.Perform(feature_diameter / 2.0)
            p = feature_maker.Shape()
            origin_z += raster
        origin_x += raster
        origin_z = raster/2
    
    return p



lower_paneel = paneel(h/2, w, thickness, raster)
lower_paneel = translate_shp(lower_paneel, gp_Vec(0, -thickness, 0))
lower_paneel = rotate_shape(lower_paneel, x_axis, a)
lower_paneel = translate_shp(lower_paneel, gp_Vec(0, 0, kh_w-kh_h*sin(radians(a))))
display.DisplayShape(lower_paneel, update=False)

upper_paneel = translate_shp(lower_paneel, gp_Vec(0, -dy/2, dz/2), copy=True)
display.DisplayShape(upper_paneel)

#middle_bar = BRepPrimAPI_MakeBox(w-2*kh_w, kh_w, kh_h).Shape()
#middle_bar = rotate_shape(middle_bar, x_axis, a)
#ddy = (h/2-kh_h/2)*sin(radians(a))
#ddz = (h/2-kh_h/2)*cos(radians(a))+kh_w-kh_h*sin(radians(a))
#middle_bar = translate_shp(middle_bar, gp_Vec(kh_w, -ddy, ddz), copy=True)
#display.DisplayShape(middle_bar)



start_display()




