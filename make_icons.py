"""SVG → PNG 아이콘 생성 (Pillow 없이 순수 Python)"""
import struct, zlib, os

def make_png(size, bg, text_char='水'):
    """단색 배경 + 텍스트 아이콘을 PNG로 반환 (간단한 solid color PNG)"""
    # 단색 PNG만 생성 (텍스트 렌더링은 PIL 필요)
    w = h = size
    r, g, b = bg

    def chunk(name, data):
        c = struct.pack('>I', len(data)) + name + data
        return c + struct.pack('>I', zlib.crc32(name + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)

    raw = b''
    for y in range(h):
        raw += b'\x00'  # filter
        for x in range(w):
            # Rounded corner mask (simple)
            raw += bytes([r, g, b])

    idat = zlib.compress(raw)

    png = (
        b'\x89PNG\r\n\x1a\n' +
        chunk(b'IHDR', ihdr) +
        chunk(b'IDAT', idat) +
        chunk(b'IEND', b'')
    )
    return png

base = os.path.dirname(os.path.abspath(__file__))

for size in [192, 512]:
    data = make_png(size, (15, 23, 42))  # #0f172a
    path = os.path.join(base, f'icon-{size}.png')
    with open(path, 'wb') as f:
        f.write(data)
    print(f'Created icon-{size}.png')

# favicon (16x16)
data = make_png(16, (15, 23, 42))
with open(os.path.join(base, 'favicon.ico'), 'wb') as f:
    f.write(data)
print('Created favicon.ico')
