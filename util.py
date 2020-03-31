
from OCC.Core.gp import gp_Ax1, gp_Pnt, gp_Dir, gp_Trsf

from math import radians


def euler_to_gp_trsf(euler_zxz=None, unit="deg"):
    """
    returns a rotation-only gp_Trsf given Euler angles

    :param euler_zxz: a list of three intrinsic Euler angles
                      in zxz-convention
    :param unit: If "deg", the euler angles are in degrees,
                 otherwise radians

    :return: A rotation-only gp_Trsf
    """

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

    trns = trns *trns_next

    trns_next = gp_Trsf()
    trns_next.SetRotation(z, euler_zxz[0])

    return trns *trns_next