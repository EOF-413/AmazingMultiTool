# Download
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QPen, QColor
from PyQt5.QtCore import Qt, QRectF, QPointF, QSize


def _blank_pixmap(size):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    return pix


def make_icon(kind, size=18, color='#c9d1d9'):
    pix = _blank_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    pen = QPen(QColor(color))
    pen.setWidthF(max(1.2, size * 0.09))
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)

    if kind == 'play':
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color))
        m = size * 0.24
        path = QPainterPath()
        path.moveTo(m, size * 0.16)
        path.lineTo(size - m * 0.9, size / 2)
        path.lineTo(m, size - size * 0.16)
        path.closeSubpath()
        painter.drawPath(path)

    elif kind == 'stop':
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color))
        m = size * 0.24
        painter.drawRoundedRect(QRectF(m, m, size - 2 * m, size - 2 * m), 2, 2)

    elif kind == 'download':
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        cx = size / 2
        painter.drawLine(QPointF(cx, size * 0.15), QPointF(cx, size * 0.62))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color))
        head = QPainterPath()
        head.moveTo(cx - size * 0.22, size * 0.5)
        head.lineTo(cx + size * 0.22, size * 0.5)
        head.lineTo(cx, size * 0.75)
        head.closeSubpath()
        painter.drawPath(head)
        painter.setPen(pen)
        painter.drawLine(QPointF(size * 0.2, size * 0.86), QPointF(size * 0.8, size * 0.86))

    elif kind == 'settings':
        painter.setPen(pen)
        ys = (size * 0.28, size * 0.52, size * 0.76)
        knob_x = (size * 0.62, size * 0.38, size * 0.55)
        for y, kx in zip(ys, knob_x):
            painter.drawLine(QPointF(size * 0.12, y), QPointF(size * 0.88, y))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(color))
            painter.drawEllipse(QPointF(kx, y), size * 0.075, size * 0.075)
            painter.setPen(pen)

    elif kind == 'refresh':
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        rect = QRectF(size * 0.16, size * 0.16, size * 0.68, size * 0.68)
        painter.drawArc(rect, 40 * 16, 260 * 16)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color))
        head = QPainterPath()
        ang_x = size * 0.18
        ang_y = size * 0.28
        head.moveTo(ang_x, ang_y - size * 0.14)
        head.lineTo(ang_x + size * 0.2, ang_y)
        head.lineTo(ang_x - size * 0.02, ang_y + size * 0.18)
        head.closeSubpath()
        painter.drawPath(head)

    elif kind == 'trash':
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(QPointF(size * 0.2, size * 0.28), QPointF(size * 0.8, size * 0.28))
        painter.drawLine(QPointF(size * 0.4, size * 0.28), QPointF(size * 0.42, size * 0.16))
        painter.drawLine(QPointF(size * 0.6, size * 0.28), QPointF(size * 0.58, size * 0.16))
        painter.drawLine(QPointF(size * 0.42, size * 0.16), QPointF(size * 0.58, size * 0.16))
        body = QPainterPath()
        body.moveTo(size * 0.28, size * 0.3)
        body.lineTo(size * 0.32, size * 0.86)
        body.lineTo(size * 0.68, size * 0.86)
        body.lineTo(size * 0.72, size * 0.3)
        painter.drawPath(body)
        painter.drawLine(QPointF(size * 0.42, size * 0.4), QPointF(size * 0.43, size * 0.76))
        painter.drawLine(QPointF(size * 0.58, size * 0.4), QPointF(size * 0.57, size * 0.76))

    elif kind == 'globe':
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        rect = QRectF(size * 0.14, size * 0.14, size * 0.72, size * 0.72)
        painter.drawEllipse(rect)
        painter.drawEllipse(QRectF(size * 0.34, size * 0.14, size * 0.32, size * 0.72))
        painter.drawLine(QPointF(size * 0.16, size / 2), QPointF(size * 0.84, size / 2))

    elif kind == 'close':
        painter.setPen(pen)
        m = size * 0.26
        painter.drawLine(QPointF(m, m), QPointF(size - m, size - m))
        painter.drawLine(QPointF(size - m, m), QPointF(m, size - m))

    elif kind == 'plus':
        painter.setPen(pen)
        cx, cy = size / 2, size / 2
        painter.drawLine(QPointF(cx, size * 0.15), QPointF(cx, size * 0.85))
        painter.drawLine(QPointF(size * 0.15, cy), QPointF(size * 0.85, cy))

    painter.end()
    return QIcon(pix)


def apply_icon(button, kind, size=18, color='#c9d1d9'):
    button.setIcon(make_icon(kind, size=size, color=color))
    button.setIconSize(QSize(size, size))
    button.setText('')
