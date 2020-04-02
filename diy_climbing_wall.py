#!/usr/bin/env python
# coding: utf-8

from OCC.Display.SimpleGui import init_display
from math import radians, sin, cos, tan
from parts import Bar, Panel

from util import get_boundingbox, get_boundingbox_shape, make_compound


def climbing_wall(wall_width=2000.,
                  wall_height=2400.,
                  wall_thickness=21.,
                  wall_angle=25.,
                  gap=100.,
                  safety=500.,
                  holes=None):
    """
    create a free standing climbing wall

    :param wall_width: the width of the climbable surface
    :param wall_height: the height of the climbable surface
    :param wall_thickness: the thickness of the plywood
    :param wall_angle: the angle of overhang
    :param gap: the desired gap between the top part of
           the climbable surface and the horizontal top bar
    :param safety: extra length of the left and right floor
           bars to prevent tilting
    :param holes: the holes dict for defining the panels
           of the climbable surface

    :return: a list of parts that make up the climbing wall
    """

    # holes definition used for the plywood panels
    if holes is None:
        holes = {'x_start': 100.,
                 'x_dist': 200.,
                 'y_start': 100.,
                 'y_dist': 200.,
                 'diameter': 13.}

    # cross section of the bars for the rear construction
    # and for the front construction
    back_section = (100, 80)
    front_section = (100, 100)

    # some auxiliary variables
    ra = radians(wall_angle)
    sina = sin(ra)
    cosa = cos(ra)
    tana = tan(ra)

    parts = []

    # create horizontal bar on the left side
    l = back_section[0] + front_section[0] + (wall_height + gap) * sina + safety - front_section[0]
    horizontal_left = Bar(pos=[0, 0, 0],
                          ori=[0, 0, -90],
                          length=l,
                          section=back_section)
    horizontal_left.name = "horizontal, left"
    parts.append(horizontal_left)

    # create horizontal bar on the right side
    horizontal_right = Bar(pos=[0, wall_width + horizontal_left._section[0], 0],
                           parent=horizontal_left,
                           length=l,
                           section=back_section)
    horizontal_right.name = "horizontal, right"
    parts.append(horizontal_right)

    # create horizontal part in the lower back
    back = Bar(pos=[horizontal_left._section[0], 0, back_section[1]],
               ori=[0, 0, 90],
               parent=horizontal_left,
               length=wall_width + 2*horizontal_left._section[0],
               section=back_section)
    back.name = "back bar"
    parts.append(back)


    # create the three diagonal bars
    dz = back._section[1] - back._section[0] * sina
    dy = back._section[0] * sina * tana
    l = wall_height + back_section[0]*tana + gap
    kwargs = {
        'pos': [horizontal_left._section[0], dy, dz],
        'ori': [-90, wall_angle-90, 0],
        'parent': back,
        'length': l,
        'section': (back_section[1], back_section[0]),
        'saw_start': wall_angle-90,
        'saw_end': 90-wall_angle
    }
    diag1 = Bar(**kwargs)
    diag1.name = "diagonal bar 1"
    parts.append(diag1)

    kwargs['pos'] = [0, (wall_width - horizontal_left._section[1])/2, 0]
    kwargs['ori'] = [0, 0, 0]
    kwargs['parent'] = diag1
    diag2 = Bar(**kwargs)
    diag2.name = "diagonal bar 2"
    parts.append(diag2)

    kwargs['pos'] = [0, (wall_width - horizontal_left._section[1])/2, 0]
    kwargs['parent'] = diag2
    diag3 = Bar(**kwargs)
    diag3.name = "diagonal bar 3"
    parts.append(diag3)

    # add the climbing panels
    panel_lo = Panel(pos=[tana*diag1._section[1], 0, -wall_thickness],
                     parent=diag1,
                     width=wall_width,
                     height=wall_height/2,
                     thickness=wall_thickness,
                     holes=holes)
    panel_lo.name = "lower plywood panel"
    parts.append(panel_lo)

    panel_hi = Panel(pos=[panel_lo._height, 0, 0],
                     parent=panel_lo,
                     width=wall_width,
                     height=wall_height / 2,
                     thickness=wall_thickness,
                     holes=holes)
    panel_hi.name = "upper plywood panel"
    parts.append(panel_hi)

    # add vertical bars
    dx = 2 * back_section[0] + (wall_height + gap) * sina - front_section[0]
    dz = back_section[1]
    l = (wall_height + gap) * cosa + back_section[1]
    vertical_left = Bar(pos=[dx, 0, dz],
                        ori=[90, 90, -90],
                        length=l,
                        parent=horizontal_left,
                        section=front_section)
    vertical_left.name = "left vertical bar"
    parts.append(vertical_left)

    vertical_right = Bar(pos=[dx, 0, dz],
                         ori=[90, 90, -90],
                         length=l,
                         parent=horizontal_right,
                         section=front_section)
    vertical_right.name = "right vertical bar"
    parts.append(vertical_right)

    dx = back_section[1] + front_section[0] + (wall_height + gap) * cosa
    top = Bar(pos=[dx, 0, 0],
              ori=[90, 0, 0],
              length=wall_width + 2*back_section[0],
              parent=vertical_left,
              section=front_section)
    top.name = "top bar"
    parts.append(top)

    return parts


if __name__ == '__main__':

    wall = {'wall_width': 2000,
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

    parts = climbing_wall(**wall)

    for part in parts:
        print(part)

    wall_compound = make_compound(parts)
    bb = get_boundingbox(wall_compound, use_mesh=False)
    bb_box = get_boundingbox_shape(bb)

    display, start_display, add_menu, add_function_to_menu = init_display()
    for part in parts:
        display.DisplayShape(part._shape, update=False)
    display.DisplayShape(bb_box, color='red', update=False)
    display.FitAll()
    start_display()

    # TO DO
    # add options for diagonal bar mount
    #   mount_upper = [side, bottom] (default for wall_angle >= 45: side, default for wall_angle < 45: bottom)
    #   mount_lower = [side, top] (default for wall_angle >= 45: side, default for wall_angle < 45: top)
    #   overlap_upper = [+, -] (- means away from climber, - is default)
    #   overlap_lower = [+, -] (- means away from climber, - is default)
    # support pretty print in gui
    # export to step, stl
    # make conda package
