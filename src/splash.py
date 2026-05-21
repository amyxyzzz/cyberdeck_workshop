"""Boot splash animation. No sound, no inputs -- runs once at startup."""
import time

import st7789py as st7789
import vga1_16x16 as font_big
import vga1_8x8 as font_small


BG   = st7789.color565(20,  15,  30)
FUR  = st7789.color565(255, 200, 130)
TEXT = st7789.color565(255, 230, 200)


def splash(display, bl, name="friend"):
    """Show the boot animation. Returns when done."""
    bl.value(1)
    display.fill(BG)

    # Cat sprite (same shape we use everywhere), centered horizontally.
    cy_top = 70  # top of the cat in pixels
    sprite_rows = ["/\\_/\\", "( o.o )", " > ^ <"]
    for i, row in enumerate(sprite_rows):
        x = (240 - len(row) * 16) // 2
        y = cy_top + i * 16
        display.text(font_big, row, x, y, FUR, BG)

    # Type out the greeting one character at a time.
    greeting = "hello, {}!".format(name)
    gx = (240 - len(greeting) * 8) // 2
    gy = cy_top + 60
    for i in range(len(greeting) + 1):
        display.text(font_small, greeting[:i], gx, gy, TEXT, BG)
        time.sleep_ms(60)