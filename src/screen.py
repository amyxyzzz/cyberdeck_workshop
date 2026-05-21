"""Minimal ST7789 240x240 driver for 1.54" panels.

Pure MicroPython, no extra modules. Handles init, address window,
and pushing a framebuffer-shaped byte array. Designed to be just
enough to back a `framebuf.FrameBuffer` in RGB565.

If your panel shows a 0,0 offset garbage strip or wrong colors,
tweak _OFFSET_X / _OFFSET_Y or comment the _INVON line below.
"""
from machine import Pin
import time
import struct

# --- ST7789 commands we use -------------------------------------------------
_SWRESET = b"\x01"
_SLPOUT  = b"\x11"
_NORON   = b"\x13"
_INVON   = b"\x21"
_DISPON  = b"\x29"
_CASET   = b"\x2A"
_RASET   = b"\x2B"
_RAMWR   = b"\x2C"
_COLMOD  = b"\x3A"
_MADCTL  = b"\x36"

# Most no-name 1.54" 240x240 ST7789 panels need (0, 0). If yours has a
# few-pixel border of garbage, try (0, 80) or (35, 0).
_OFFSET_X = 0
_OFFSET_Y = 0


def color565(r, g, b):
    """Pack 8-bit RGB into a 16-bit RGB565 value (big-endian on the wire)."""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


class ST7789:
    def __init__(self, spi, *, cs, dc, rst, bl=None, width=240, height=240):
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.dc = Pin(dc, Pin.OUT, value=0)
        self.rst = Pin(rst, Pin.OUT, value=1)
        self.bl = Pin(bl, Pin.OUT, value=1) if bl is not None else None
        self.width = width
        self.height = height
        self._init_display()

    # --- low-level command/data helpers ------------------------------------
    def _cmd(self, cmd):
        self.cs.value(0); self.dc.value(0)
        self.spi.write(cmd)
        self.cs.value(1)

    def _data(self, data):
        self.cs.value(0); self.dc.value(1)
        self.spi.write(data)
        self.cs.value(1)

    def _init_display(self):
        # Hardware reset
        self.rst.value(1); time.sleep_ms(10)
        self.rst.value(0); time.sleep_ms(10)
        self.rst.value(1); time.sleep_ms(120)

        self._cmd(_SWRESET); time.sleep_ms(150)
        self._cmd(_SLPOUT);  time.sleep_ms(10)
        self._cmd(_COLMOD);  self._data(b"\x55")  # 16-bit RGB565
        self._cmd(_MADCTL);  self._data(b"\x00")  # default orientation
        self._cmd(_INVON)                         # most 1.54" panels need this
        self._cmd(_NORON);   time.sleep_ms(10)
        self._cmd(_DISPON);  time.sleep_ms(100)

    # --- public API --------------------------------------------------------
    def set_window(self, x0, y0, x1, y1):
        x0 += _OFFSET_X; x1 += _OFFSET_X
        y0 += _OFFSET_Y; y1 += _OFFSET_Y
        self._cmd(_CASET); self._data(struct.pack(">HH", x0, x1))
        self._cmd(_RASET); self._data(struct.pack(">HH", y0, y1))
        self._cmd(_RAMWR)

    def blit_buffer(self, buf, x, y, w, h):
        """Push a raw RGB565 byte buffer to the panel."""
        self.set_window(x, y, x + w - 1, y + h - 1)
        self.cs.value(0); self.dc.value(1)
        self.spi.write(buf)
        self.cs.value(1)

    def fill(self, color):
        """Solid color fill across the whole screen."""
        self.set_window(0, 0, self.width - 1, self.height - 1)
        line = bytes((color >> 8, color & 0xFF)) * self.width
        self.cs.value(0); self.dc.value(1)
        for _ in range(self.height):
            self.spi.write(line)
        self.cs.value(1)

    def backlight(self, on):
        if self.bl is not None:
            self.bl.value(1 if on else 0)
