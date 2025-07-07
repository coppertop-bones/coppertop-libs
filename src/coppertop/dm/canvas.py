# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

# https://ipycanvas.readthedocs.io/en/latest/installation.html
# conda install -c conda-forge ipycanvas
# jupyter labextension install @jupyter-widgets/jupyterlab-manager ipycanvas

# https://blog.jupyter.org/ipycanvas-a-python-canvas-for-jupyter-bbb51e4777f7
# https://github.com/martinRenou/ipycanvas

#
# with hold_canvas(c):
#     # Perform drawings...


# https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Drawing_text

# x = 10;y = 70; ctx.font = '32px sans-serif'; ctx.textAlign = 'start';
# ctx.textBaseline = "hanging";
# var t = 'Why hello world?';
# var text = ctx.measureText(t);
# asc = text.actualBoundingBoxAscent; desc = text.actualBoundingBoxDescent;
#
# l = text.actualBoundingBoxLeft; r = text.actualBoundingBoxRight;
#
# ctx.fillText(t, x, y); ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(x, y); ctx.moveTo(x+l, y-asc); ctx.lineTo(x+l, y+desc);
# ctx.lineTo(x+r, y+desc); ctx.lineTo(x+r, y-asc); ctx.lineTo(x+l, y-asc); ctx.stroke();
# ctx.font = '18pt sans-serif'; ctx.textAlign = 'start';
# ctx.fillText(asc, 0, y+60);ctx.fillText(desc, 0, y+90);ctx.fillText(asc+desc, 0, y+120);



from ipycanvas import Canvas, RoughCanvas, hold_canvas
from coppertop.pipe import *
from coppertop.dm.core.types import num, tvfloat, index, num, txt
from bones.ts.metatypes import BType, BTAtom

__all__ = [
    'canvas', 'rough', 'fill', 'clear', 'outline', 'style', 'line', 'text', 'save', 'restore', 'clip',
    'relative', 'toFile'
]


def _newCanvas(*args, **kwargs):
    c = Canvas(**kwargs)
    c._t = BType('canvas')
    c._v = c
    return c

def _newRough(*args, **kwargs):
    c = RoughCanvas(**kwargs)
    c._t = BType('rough')
    c._v = c
    return c

canvas = BType('canvas: atom in mem').setConstructor(_newCanvas)

# MUSTDO fleshout the rough stuff
rough = BType('rough: atom in mem').setConstructor(_newRough)

relative = num['canvas.relative'].setCoercer(tvfloat)

@coppertop
def fill(c:canvas+rough, x1, y1, x2, y2) -> canvas+rough:
    x1 -= 1;
    y1 -= 1
    w, h = x2 - x1, y2 - y1
    c.fill_rect(x1, c.height - y1 - h, w, h)
    return c

@coppertop
def fill(c:canvas+rough, x1:index+num, y1:index+num, x2:relative, y2:relative) -> canvas+rough:
    x1 -= 1;
    y1 -= 1
    x2 = x1 + x2
    y2 = y1 + y2
    w, h = x2 - x1, y2 - y1
    c.fill_rect(x1, c.height - y1 - h, w, h)
    return c


@coppertop
def clear(c:canvas+rough, x1, y1, x2, y2) -> canvas+rough:
    x1 -= 1;
    y1 -= 1
    w, h = x2 - x1, y2 - y1
    c.clear_rect(x1, c.height - y1 - h, w, h)
    return c


@coppertop
def outline(c:canvas+rough, x1, y1, x2, y2) -> canvas+rough:
    x1 -= 1;
    y1 -= 1
    w, h = x2 - x1, y2 - y1
    c.stroke_rect(x1, c.height - y1 - h, w, h)
    return c

@coppertop
def outline(c:canvas+rough, x1:index+num, y1:index+num, x2:relative, y2:relative) -> canvas+rough:
    x1 -= 1;
    y1 -= 1
    x2 = x1 + x2
    y2 = y1 + y2
    w, h = x2 - x1, y2 - y1
    c.stroke_rect(x1, c.height - y1 - h, w, h)
    return c


@coppertop
def text(c:canvas+rough, x, y, s:txt) -> canvas+rough:
    x -= 1; y -= 1
    h = 0
    c.fill_text(s, x, c.height - y - h)
    return c


@coppertop
def clip(c:canvas+rough, x1, y1, x2, y2) -> canvas+rough:
    x1 -= 1; y1 -= 1; x2 -= 1; y2 -= 1
    y1 = c.height - y1
    y2 = c.height - y2
    c.move_to(x1, y1)
    c.begin_path()
    c.line_to(x2, y1)
    c.line_to(x2, y2)
    c.line_to(x1, y2)
    c.line_to(x1, y1)
    c.clip()
    return c


@coppertop
def save(c:canvas+rough) -> canvas+rough:
    c.save()
    return c


@coppertop
def restore(c:canvas+rough) -> canvas+rough:
    c.restore()
    return c


@coppertop
def style(c:canvas+rough, **kwargs) -> canvas+rough:
    for k, v in kwargs.items():
        if k == 'fill':
            c.fill_style = v
        elif k == 'stroke':
            c.stroke_style = v
        elif k == 'width':
            c.line_width = v
        elif k == 'alpha':
            c.global_alpha = v
        elif k == 'font':
            # https://www.w3schools.com/tags/canvas_font.asp
            # https://www.w3schools.com/cssref/pr_font_font.asp
            c.font = v
        elif k == 'align':
            c.text_align = v
        elif k == 'baseline':
            c.text_baseline = v
        elif k == 'direction':
            c.direction = v
        else:
            raise TypeError(f'Unknown style type - {k}')
    return c


@coppertop
def line(c:canvas+rough, x1, y1, x2, y2) -> canvas+rough:
    x1 -= 1;
    y1 -= 1;
    x2 -= 1;
    y2 -= 1
    c.stroke_line(x1, c.height - y1, x2, c.height - y2)
    return c


@coppertop
def line(c:canvas+rough, x1:index+num, y1:index+num, x2:relative, y2:relative) -> canvas+rough:
    x1 -= 1;
    y1 -= 1;
    x2 = x1 + x2;
    y2 = y1 + y2
    c.stroke_line(x1, c.height - y1, x2, c.height - y2)
    return c

@coppertop
def toFile(c:canvas+rough, pfn:txt) -> canvas+rough:
    c.to_file(pfn)
    return c



