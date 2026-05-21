"""Tiny kindle-like text reader.

Loads `path` once, word-wraps the text, and shows one page at a time.
Each call to next_page() advances; wraps around at the end.
"""
import st7789py as st7789
import vga1_8x8 as font_small


# Layout
BG     = st7789.color565( 35,  30,  25)   # warm paper-ish
FG     = st7789.color565(245, 235, 215)   # cream text
ACCENT = st7789.color565(200, 170, 120)   # footer / decoration

CHAR_W = 8
LINE_H = 8
MARGIN_X = 8
MARGIN_Y = 12
LINES_PER_PAGE  = (240 - MARGIN_Y - 20) // LINE_H 
MAX_LINE_CHARS  = (240 - 2 * MARGIN_X) // CHAR_W   # = 14
FOOTER_Y = 240 - 10


def _word_wrap(text, max_chars):
    """Wrap text to max_chars per line, preserving paragraph breaks."""
    out = []
    paragraphs = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    for p in paragraphs:
        words = p.split()
        if not words:
            out.append('')
            continue
        cur = words[0]
        for w in words[1:]:
            if len(cur) + 1 + len(w) <= max_chars:
                cur += ' ' + w
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out


class Reader:
    def __init__(self, display, path, tick=None):
        self.display = display
        self.path = path
        self.tick = tick if tick else (lambda: None)
        self.lines = []
        self.page = 0
        self._load()

    def _load(self):
        try:
            with open(self.path) as f:
                text = f.read()
        except OSError:
            text = ("no text yet.\n\n"
                    "save a .txt file at\n"
                    "{}\n\n"
                    "then run make sync.").format(self.path)
        self.lines = _word_wrap(text, MAX_LINE_CHARS)

    @property
    def total_pages(self):
        return max(1, (len(self.lines) + LINES_PER_PAGE - 1) // LINES_PER_PAGE)

    def reset(self):
        self.page = 0
        self._render()

    def next_page(self):
        self.page = (self.page + 1) % self.total_pages
        self._render()

    def step(self):
        # Static page; nothing to animate.
        pass

    def _render(self):
        self.display.fill(BG)
        self.tick()
        start = self.page * LINES_PER_PAGE
        end   = min(start + LINES_PER_PAGE, len(self.lines))
        y = MARGIN_Y
        for i, line in enumerate(self.lines[start:end]):
            self.display.text(font_small, line[:MAX_LINE_CHARS],
                              MARGIN_X, y, FG, BG)
            y += LINE_H
            if i % 4 == 3:
                self.tick()
        # Footer: page number, centered
        footer = "{} / {}".format(self.page + 1, self.total_pages)
        fx = (240 - len(footer) * 8) // 2
        self.display.text(font_small, footer, fx, FOOTER_Y, ACCENT, BG)
