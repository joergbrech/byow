
from OCC.Core.TopoDS import TopoDS_Compound, topods
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRep import BRep_Builder
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.gp import gp_Ax1, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.Addons import text_to_brep, Font_FontAspect_Bold
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone

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


def get_boundingbox(shape, tol=1e-6, use_mesh=True):
    """ return the bounding box of the TopoDS_Shape `shape`
    Parameters
    ----------
    shape : TopoDS_Shape or a subclass such as TopoDS_Face
        the shape to compute the bounding box from
    tol: float
        tolerance of the computed boundingbox
    use_mesh : bool
        a flag that tells whether or not the shape has first to be meshed before the bbox
        computation. This produces more accurate results
    """
    bbox = Bnd_Box()
    bbox.SetGap(tol)
    if use_mesh:
        mesh = BRepMesh_IncrementalMesh()
        mesh.SetParallelDefault(True)
        mesh.SetShape(shape)
        mesh.Perform()
        if not mesh.IsDone():
            raise AssertionError("Mesh not done.")
    brepbndlib_Add(shape, bbox, use_mesh)

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    return {'xmin': xmin,
            'ymin': ymin,
            'zmin': zmin,
            'dx': xmax-xmin,
            'dy': ymax-ymin,
            'dz': zmax-zmin
            }


def get_boundingbox_shape(bb):
    """
    Given the dict returned by `get_boundingbox`, this
    function creates a TopoDS_Compound to visualize
    the bounding box, including annotations

    :param bb: dict returned by `get_boundingbox`

    :return: a TopoDS_Compound to visualize the bounding box
    """
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)

    bb_box = BRepPrimAPI_MakeBox(bb['dx'], bb['dy'], bb['dz']).Shape()
    translation = gp_Trsf()
    translation.SetTranslation(gp_Vec(bb['xmin'], bb['ymin'], bb['zmin']))
    brep_trns = BRepBuilderAPI_Transform(bb_box, translation, False)
    brep_trns.Build()
    bb_box = brep_trns.Shape()
    anEdgeExplorer = TopExp_Explorer(bb_box, TopAbs_EDGE)
    while anEdgeExplorer.More():
        anEdge = topods.Edge(anEdgeExplorer.Current())
        builder.Add(compound, anEdge)
        anEdgeExplorer.Next()

    dx_string = text_to_brep(str(round(bb['dx'])) + " mm", "Arial", Font_FontAspect_Bold, 120., True)
    transformation = gp_Trsf()
    transformation.SetTranslation(gp_Vec(bb['xmin'] + 120, bb['ymin'] - 120, 0))
    brep_trns = BRepBuilderAPI_Transform(dx_string, transformation, False)
    brep_trns.Build()
    dx_string = brep_trns.Shape()
    builder.Add(compound, dx_string)

    dy_string = text_to_brep(str(round(bb['dy'])) + " mm", "Arial", Font_FontAspect_Bold, 120., True)
    t1 = gp_Trsf()
    z = gp_Ax1(gp_Pnt(), gp_Dir(0, 0, 1))
    t1.SetRotation(z, radians(90))
    t2 = gp_Trsf()
    t2.SetTranslation(gp_Vec(bb['xmin'] - 25, bb['ymin'] + 120, 0))
    brep_trns = BRepBuilderAPI_Transform(dy_string, t2 * t1, False)
    brep_trns.Build()
    dy_string = brep_trns.Shape()
    builder.Add(compound, dy_string)

    dz_string = text_to_brep(str(round(bb['dz'])) + " mm", "Arial", Font_FontAspect_Bold, 120., True)
    x = gp_Ax1(gp_Pnt(), gp_Dir(1, 0, 0))
    y = gp_Ax1(gp_Pnt(), gp_Dir(0, 1, 0))
    z = gp_Ax1(gp_Pnt(), gp_Dir(0, 0, 1))
    t1 = gp_Trsf()
    t1.SetRotation(z, radians(90))
    t2 = gp_Trsf()
    t2.SetRotation(y, radians(90))
    t3 = gp_Trsf()
    t3.SetRotation(x, radians(90))
    t4 = gp_Trsf()
    t4.SetTranslation(gp_Vec(bb['xmin'], bb['ymin'] - 25, 120))
    brep_trns = BRepBuilderAPI_Transform(dz_string, t4 * t3 * t2 * t1, False)
    brep_trns.Build()
    dz_string = brep_trns.Shape()
    builder.Add(compound, dz_string)

    return compound


def make_compound(parts):
    """
    Takes a list of parts and returns a TopoDS_Compound
    from the parts' shapes.

    :param parts: A list of Part instances

    :return: a TopoDS_Compound from all of the parts' shapes
    """
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    for part in parts:
        builder.Add(compound, part._shape)
    return compound


def export_to_step(filename, parts):
    """
    Export all the parts' shapes to a STEP file

    :param filename: The output STEP file
    :param parts: a list of Part instances

    :return: None
    """
    compound = make_compound(parts)
    step_writer = STEPControl_Writer()
    Interface_Static_SetCVal("write.step.schema", "AP203")
    step_writer.Transfer(compound, STEPControl_AsIs)
    status = step_writer.Write(filename)

    if status != IFSelect_RetDone:
        raise AssertionError("load failed")
