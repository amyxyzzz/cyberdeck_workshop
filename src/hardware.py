"""Hardware abstraction layer.

Wraps `machine.Pin` with debouncing and edge detection so the main
loop can ask 'did this just become pressed?' instead of polling
raw pin values and getting bouncy reads.
"""
from machine import Pin
import time


class DebouncedInput:
    """A digital input with software debounce and rising/falling edges.

    Args:
        pin_num: GPIO number (or "LED" etc).
        pull: Pin.PULL_UP, Pin.PULL_DOWN, or None.
        active_high: True if logical "pressed" == pin HIGH.
                     For a button to GND with pull-up, pass False.
        debounce_ms: Ignore changes shorter than this.
    """

    def __init__(self, pin_num, pull=None, active_high=True, debounce_ms=30):
        if pull is None:
            self.pin = Pin(pin_num, Pin.IN)
        else:
            self.pin = Pin(pin_num, Pin.IN, pull)
        self.active_high = active_high
        self.debounce_ms = debounce_ms

        initial = self._read_raw()
        self._last_raw = initial
        self._stable = initial
        self._prev_stable = initial
        self._last_change = time.ticks_ms()

    def _read_raw(self):
        v = bool(self.pin.value())
        return v if self.active_high else not v

    def update(self):
        """Sample the pin. Returns (rising, falling) bools for this tick."""
        now = time.ticks_ms()
        raw = self._read_raw()

        if raw != self._last_raw:
            # Saw a change; reset the debounce timer.
            self._last_raw = raw
            self._last_change = now
        elif time.ticks_diff(now, self._last_change) >= self.debounce_ms:
            # Reading has been steady long enough to trust it.
            self._stable = raw

        rising = self._stable and not self._prev_stable
        falling = (not self._stable) and self._prev_stable
        self._prev_stable = self._stable
        return rising, falling

    @property
    def pressed(self):
        return self._stable


    @property
    def raw(self):
        """Current un-debounced reading. Useful for wiring diagnostics."""
        return self._read_raw()
    
class StatusLED:
    """Onboard LED wrapper with a few convenience helpers."""

    def __init__(self, pin_id="LED"):
        self.pin = Pin(pin_id, Pin.OUT)
        self._state = False

    def on(self):
        self.pin.on()
        self._state = True

    def off(self):
        self.pin.off()
        self._state = False

    def toggle(self):
        self.pin.toggle()
        self._state = not self._state

    def set(self, on):
        self.on() if on else self.off()

    @property
    def state(self):
        return self._state
    
    
