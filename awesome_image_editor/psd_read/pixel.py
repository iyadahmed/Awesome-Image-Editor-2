from psd_tools.api.layers import PixelLayer

from ..model_view.items.image import AIEImageItem


def psd_pixel_layer_to_image_item(layer: PixelLayer):
    assert layer.kind == "pixel"

    pil_image = layer.topil()
    if pil_image is None:
        return

    image = pil_image.toqimage()
    left, top = layer.offset
    image_name = layer.name
    item = AIEImageItem(image, image_name)
    item.setPos(left, top)
    item.setVisible(layer.visible)

    return item
