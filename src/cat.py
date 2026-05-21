"""Cute cat — bigger sprite with per-state text labels.

The cat itself is rendered in 16x16 font for visibility; the line of
text below it is in 8x8. Edit LABELS below to change what the cat says.
"""
import st7789py as st7789
import vga1_16x16 as font_big
import vga1_8x8 as font_small


# ----- 16x16 cell grid for the cat -----------------------------------------
CAT_CELL = 16
CAT_COLS = 240 // CAT_CELL    # 15
CAT_ROWS = 240 // CAT_CELL    # 15

# ----- Palette --------------------------------------------------------------
BG    = st7789.color565(25,  18,  35)
FUR   = st7789.color565(255, 200, 130)
EYE   = st7789.color565(120, 220, 255)
MOUTH = st7789.color565(255, 140, 180)
HEART = st7789.color565(255, 90,  130)
ZZZ   = st7789.color565(170, 200, 255)
TEXT  = st7789.color565(255, 230, 200)

# ----- States ---------------------------------------------------------------
IDLE    = 0
BLINK   = 1
SNUGGLE = 2
KISS    = 3
CYCLE = [BLINK, SNUGGLE, KISS]
STATE_NAMES = {IDLE: "idle", BLINK: "blink", SNUGGLE: "snuggle", KISS: "kiss"}

# ===== EDIT ME: text shown under the cat for each state =====================
# Keep them short-ish (under ~30 chars) so they fit on one line at 8x8.
# '<3' renders as two characters.
LABELS = {
    IDLE:    "hi friend!",
    BLINK:   "<3",
    SNUGGLE: "welcome back",
    KISS:    "love you",
}
# ============================================================================

# Cat sprite is 7 cells wide x 3 cells tall, centered horizontally.
SPRITE_W = 7
SPRITE_H = 3
BASE_COL = (CAT_COLS - SPRITE_W) // 2    # 4
BASE_ROW = 4                              # leave some top margin

# Label sits in pixel coords near the bottom of the screen.
LABEL_Y_PX = 180


class Cat:
    def __init__(self, display, tick=None):
        self.display = display
        self.state = IDLE
        self.state_frame = 0
        self.idle_frame = 0
        self.cycle_idx = 0
        self._dirty = []
        self._label_text = ""
        self.tick = tick if tick else (lambda: None)

    # ----- public API -------------------------------------------------------
    def reset(self):
        self.display.fill(BG)
        self.tick()
        self.state = IDLE
        self.state_frame = 0
        self.idle_frame = 0
        self.cycle_idx = 0
        self._dirty = []
        self._label_text = ""
        self._render()

    def touch(self):
        """Advance to the next cute animation."""
        self.state = CYCLE[self.cycle_idx % len(CYCLE)]
        self.state_frame = 0
        self.cycle_idx += 1
        self._render()

    def step(self):
        self.state_frame += 1
        if self.state == IDLE:
            self.idle_frame += 1
        elif self._anim_done():
            self.state = IDLE
            self.state_frame = 0
        self._render()

    @property
    def state_name(self):
        return STATE_NAMES.get(self.state, "?")

    # ----- internals --------------------------------------------------------
    def _anim_done(self):
        if self.state == BLINK:   return self.state_frame > 4
        if self.state == SNUGGLE: return self.state_frame > 22
        if self.state == KISS:    return self.state_frame > 18
        return True

    def _erase_dirty(self):
        for col, row, length in self._dirty:
            self.display.fill_rect(col * CAT_CELL, row * CAT_CELL,
                                   length * CAT_CELL, CAT_CELL, BG)
        self._dirty = []

    def _draw(self, col, row, text, color):
        if not text or col >= CAT_COLS or row < 0 or row >= CAT_ROWS:
            return
        s, c = text, col
        if c < 0:
            s = s[-c:]
            c = 0
        if c + len(s) > CAT_COLS:
            s = s[: CAT_COLS - c]
        if not s:
            return
        self.display.text(font_big, s, c * CAT_CELL, row * CAT_CELL, color, BG)
        self._dirty.append((c, row, len(s)))

    def _render(self):
        self._erase_dirty()
        self.tick()

        # Idle sway
        sway = 0
        if self.state == IDLE:
            sway = (-1, 0, 1, 0)[(self.idle_frame // 6) % 4]
        col = BASE_COL + sway
        row = BASE_ROW

        # Ears
        self._draw(col + 1, row, "/\\_/\\", FUR)
        # Face row
        self._draw(col,     row + 1, "(", FUR)
        self._draw(col + 6, row + 1, ")", FUR)
        self._draw(col + 2, row + 1, self._eyes(), EYE)
        # Mouth row
        self._draw(col + 1, row + 2, ">", FUR)
        self._draw(col + 5, row + 2, "<", FUR)
        mouth, mc = self._mouth()
        self._draw(col + 3, row + 2, mouth, mc)

        # State-specific accents
        if self.state == SNUGGLE:
            self._render_snuggle(col, row)
        elif self.state == KISS:
            self._render_kiss(col, row)

        # Update the text label
        self._render_label()

    def _eyes(self):
        if self.state == BLINK:   return "-.-"
        if self.state == SNUGGLE: return "^.^"
        if self.state == KISS:
            return "-.o" if self.state_frame % 8 < 4 else "o.o"
        return "o.o"

    def _mouth(self):
        if self.state == SNUGGLE: return ("w", MOUTH)
        if self.state == KISS:    return ("3", MOUTH)
        return ("^", FUR)

    def _render_snuggle(self, col, row):
        if (self.state_frame // 3) % 2 == 0:
            self._draw(col - 2, row + 1, "<3", HEART)
            self._draw(col + 7, row + 1, "<3", HEART)
        zphase = (self.state_frame // 4) % 4
        for i in range(zphase):
            self._draw(col + 8 + i, max(0, row - i), "z", ZZZ)

    def _render_kiss(self, col, row):
        for i in range(3):
            t = self.state_frame + i * 4
            offset = (t // 2) % 7
            hx = col + 7 + offset
            hy = row + 2 - offset // 3
            self._draw(hx, hy, "<3", HEART)

    def _render_label(self):
        new_label = LABELS.get(self.state, "")
        if new_label == self._label_text:
            return  # no change, skip the SPI traffic
        # Erase the whole label strip (full width, one 8-px row)
        self.display.fill_rect(0, LABEL_Y_PX, 240, 16, BG)
        if new_label:
            x_px = (240 - len(new_label) * 16) // 2
            self.display.text(font_big, new_label, x_px, LABEL_Y_PX,
                              TEXT, BG)
        self._label_text = new_label
