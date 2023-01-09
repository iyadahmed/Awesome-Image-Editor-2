from psd_tools.api.layers import ShapeLayer
from psd_tools.api.shape import Subpath
from psd_tools.psd.vector import Knot
from PyQt6.QtGui import QPainterPath

from ..model_view.items.shape import AIEShapeItem


def _connect_knots_cubic(
    qpath: QPainterPath, k1: Knot, k2: Knot, psd_width: int, psd_height: int
):
    start_y, start_x = k1.anchor
    start_x *= psd_width
    start_y *= psd_height

    end_y, end_x = k2.anchor
    end_x *= psd_width
    end_y *= psd_height

    control_point_1_y, control_point_1_x = k1.leaving
    control_point_1_x *= psd_width
    control_point_1_y *= psd_height

    control_point_2_y, control_point_2_x = k2.preceding
    control_point_2_x *= psd_width
    control_point_2_y *= psd_height

    qpath.cubicTo(
        control_point_1_x,
        control_point_1_y,
        control_point_2_x,
        control_point_2_y,
        end_x,
        end_y,
    )


def psd_shape_layer_to_shape_item(layer: ShapeLayer, psd_width: int, psd_height: int):
    # What mainly helped:
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths#b%C3%A9zier_curves
    # https://doc.qt.io/qt-5/qpainterpath.html
    # https://psd-tools.readthedocs.io/en/latest/reference/psd_tools.api.shape.html#psd_tools.api.shape.VectorMask.paths

    if layer.vector_mask is None:
        return

    left, top = layer.offset
    layer_name = layer.name

    subpath: Subpath

    items = []

    # Iterate over all subpaths in the layer.vector_mask.paths list
    for subpath in layer.vector_mask.paths:
        num_knots = len(subpath)
        if num_knots == 0:
            continue

        qpath = QPainterPath()
        qpath.moveTo(
            subpath[0].anchor[1] * psd_width, subpath[0].anchor[0] * psd_height
        )

        for i in range(num_knots - 1):
            current_knot = subpath[i]
            next_knot = subpath[i + 1]
            _connect_knots_cubic(qpath, current_knot, next_knot, psd_width, psd_height)

        if subpath.is_closed():
            _connect_knots_cubic(qpath, subpath[-1], subpath[0], psd_width, psd_height)

        item = AIEShapeItem(qpath, layer_name)
        item.setVisible(layer.visible)

        # Append the item to the list of items
        items.append(item)

    # Return the list of items
    return items
