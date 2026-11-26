"""Shared drawing primitives and colours for Lecture 03."""
from build_lecture import CORAL, INK, LIGHT, MUTED, NAVY, PAPER, TEAL, WHITE


def write(c, text, x, y, size, color=INK, face='Sans', align='left'):
    c.setFont(face, size)
    c.setFillColor(color)
    {'left': c.drawString, 'center': c.drawCentredString,
     'right': c.drawRightString}[align](x, y, text)


def box(c, x, y, w, h, color, radius=6):
    c.setFillColor(color)
    c.roundRect(x, y, w, h, radius, stroke=0, fill=1)
