"""Vista HTML de las capas de interfaz; no modifica los sprites originales."""
import base64
import io
from pathlib import Path
from PIL import Image
from launcher_es import BUTTON_LABELS, button_label_layout

ROOT = Path(__file__).parent

def image_uri(raw):
    return 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii')

def main():
    rows = []
    for name in BUTTON_LABELS:
        variants = []
        for suffix in ('', '_sel'):
            path = ROOT / 'runtime/resources/buttons' / f'actionBtn_{name}{suffix}.png'
            with Image.open(path) as sprite:
                width, height = sprite.size
            region, bands, label, (x, y) = button_label_layout(path)
            stream = io.BytesIO()
            label.save(stream, format='PNG')
            rects = ''.join(f'<rect x="{region[0]}" y="{a}" width="{region[2]-region[0]}" height="{b-a}" fill="{color}"/>'
                            for a, b, color in bands)
            variants.append(f'<div class="button" style="width:{width}px;height:{height}px">'
                f'<img src="{image_uri(path.read_bytes())}">'
                f'<svg width="{width}" height="{height}">{rects}</svg>'
                f'<img style="left:{x}px;top:{y}px" src="{image_uri(stream.getvalue())}"></div>')
        rows.append('<section>' + ''.join(variants) + '</section>')
    html = '<!doctype html><meta charset="utf-8"><title>Botones originales en castellano</title>'
    html += '<style>body{margin:16px;background:#101722;color:white;font:16px Arial}section{display:flex;gap:20px;margin:12px 0}.button{position:relative}.button img,.button svg{position:absolute;left:0;top:0;image-rendering:pixelated}</style>'
    html += '<p>Estado normal / Estado seleccionado — sprites originales, rótulos en castellano</p>' + ''.join(rows)
    (ROOT / 'buttons-preview.html').write_text(html, encoding='utf-8')

if __name__ == '__main__':
    main()
