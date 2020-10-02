.. module:: ezdxf.render.path

Path
====

This module implements a geometrical :class:`Path` supported by several render backends,
with the goal to create such paths from LWPOLYLINE, POLYLINE and HATCH boundary paths
and send them to the render backend, see :mod:`ezdxf.addons.drawing`.

Minimum common interface:

- matplotlib: `PathPatch`_
    - matplotlib.path.Path() codes:
    - MOVETO
    - LINETO
    - CURVE4 - cubic Bèzier-curve

- PyQt: `QPainterPath`_
    - moveTo()
    - lineTo()
    - cubicTo() - cubic Bèzier-curve

- PyCairo: `Context`_
    - move_to()
    - line_to()
    - curve_to() - cubic Bèzier-curve

- SVG: `SVG-Path`_
    - "M" - absolute move to
    - "L" - absolute line to
    - "C" - absolute cubic Bèzier-curve

ARC and ELLIPSE entities are approximated by multiple cubic Bézier-curves, which are close enough
for display rendering. Non-rational SPLINES of 3rd degree can be represented exact as multiple
cubic Bézier-curves, other B-splines will be approximated.

.. class:: Path

    .. autoattribute:: start

    .. autoattribute:: end

    .. autoattribute:: is_closed

    .. automethod:: from_lwpolyline

    .. automethod:: from_polyline

    .. automethod:: from_spline

    .. automethod:: from_ellipse

    .. automethod:: from_arc

    .. automethod:: from_circle

    .. automethod:: from_hatch_boundary_path(boundary: Union[PolylinePath, EdgePath], ocs: OCS = None, elevation: float = 0) -> Path

    .. automethod:: from_hatch_polyline_path(polyline: PolylinePath, ocs: OCS = None, elevation: float = 0) -> Path

    .. automethod:: from_hatch_edge_path(edge: EdgePath, ocs: OCS = None, elevation: float = 0) -> Path

    .. automethod:: control_vertices

    .. automethod:: has_clockwise_orientation

    .. automethod:: line_to(location: Vector)

    .. automethod:: curve_to(location: Vector, ctrl1: Vector, ctrl2: Vector)

    .. automethod:: close

    .. automethod:: clone() -> Path

    .. automethod:: reversed() -> Path

    .. automethod:: clockwise() -> Path

    .. automethod:: counter_clockwise() -> Path

    .. automethod:: add_curves(curves: Iterable[Bezier4P])

    .. automethod:: add_ellipse(ellipse: ConstructionEllipse, segments=1)

    .. automethod:: add_spline(spline: BSpline, level=4)

    .. automethod:: transform(m: Matrix44) -> Path

    .. automethod:: approximate(segments: int=20) -> Iterable[Vector]

    .. automethod:: flattening(distance: float, segments: int=16) -> Iterable[Vector]

.. _PathPatch: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.PathPatch.html#matplotlib.patches.PathPatch
.. _QPainterPath: https://doc.qt.io/qtforpython/PySide2/QtGui/QPainterPath.html
.. _SVG-Path: https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths
.. _Context: https://pycairo.readthedocs.io/en/latest/reference/context.html