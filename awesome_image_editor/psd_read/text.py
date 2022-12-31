from psd_tools.api.layers import TypeLayer
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor

from ..model_view.items.text import AIETextItem

DEFAULT_PSD_TEXT_FILL_COLOR_DATA = {"Type": 1, "Values": [1, 0, 0, 0]}


PSD_PARAGRAPH_JUSTIFICATION_QT_ALIGNMENT_MAP = {
    0: Qt.AlignmentFlag.AlignLeft,
    2: Qt.AlignmentFlag.AlignCenter,
}


def psd_type_layer_to_text_item(layer: TypeLayer):
    item = AIETextItem("", layer.name)
    item.setPos(layer.offset[0], layer.offset[1])
    item.setVisible(layer.visible)

    document = item.document()
    document.setUseDesignMetrics(True)
    cursor = QTextCursor(document)

    text = layer.engine_dict["Editor"]["Text"].value
    fontset = layer.resource_dict["FontSet"]
    runlength = layer.engine_dict["StyleRun"]["RunLengthArray"]
    rundata = layer.engine_dict["StyleRun"]["RunArray"]
    assert len(rundata) == len(runlength)

    index = 0
    for length, style in zip(runlength, rundata):
        substring: str = text[index : index + length]

        stylesheet = style["StyleSheet"]["StyleSheetData"]
        font = fontset[stylesheet["Font"]]
        index += length

        fill_color_data = stylesheet.get("FillColor", DEFAULT_PSD_TEXT_FILL_COLOR_DATA)
        fill_color_argb_float = fill_color_data["Values"]
        fill_color_rgba_float = (*fill_color_argb_float[1:], fill_color_argb_float[0])
        fill_color_rgba_uchar = tuple(
            map(lambda x: int(x * 255), fill_color_rgba_float)
        )

        font_family = str(font["Name"])
        font_size = stylesheet["FontSize"]

        qfont = QFont()
        assert int(font_size) == font_size
        qfont.setPixelSize(int(font_size))
        qfont.setFamily(font_family)

        char_format = QTextCharFormat()
        char_format.setFont(qfont)
        char_format.setForeground(QColor(*fill_color_rgba_uchar))

        cursor.insertText(substring, char_format)

    paragraph_rundata = layer.engine_dict["ParagraphRun"]["RunArray"]
    # paragraph_runlength = layer.engine_dict['ParagraphRun']['RunLengthArray']

    assert (document.blockCount() - 1) == len(paragraph_rundata)

    cursor.movePosition(QTextCursor.MoveOperation.Start)
    for paragraph_style in paragraph_rundata:
        block_format = QTextBlockFormat()

        alignment = PSD_PARAGRAPH_JUSTIFICATION_QT_ALIGNMENT_MAP[
            paragraph_style["ParagraphSheet"]["Properties"]["Justification"]
        ]

        block_format.setAlignment(alignment)
        cursor.setBlockFormat(block_format)

        cursor.movePosition(QTextCursor.MoveOperation.NextBlock)

    return item
