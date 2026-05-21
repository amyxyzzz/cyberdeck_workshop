"""Main entry point — splash, then state machine for aquarium / cat / reader.

Inputs:
  Button (rising edge)        : toggle music play/stop
  Cap sensor short tap        : mode-specific action
                                  aquarium -> nothing
                                  cat      -> cycle blink/snuggle/kiss
                                  reader   -> turn page
  Cap sensor long press       : cycle to next mode (also turns screen on)
  PIR motion                  : wake screen if off
  Idle timeout                : auto-off after AUTO_OFF_MS
"""
from machine import Pin, SPI
import time

import config
from hardware import DebouncedInput, StatusLED

import st7789py as st7789
from aquarium import Aquarium
from cat import Cat
from reader import Reader
from music import Music
from splash import splash


MODE_AQUARIUM = 0
MODE_CAT      = 1
MODE_READER   = 2
MODES = [MODE_AQUARIUM, MODE_CAT, MODE_READER]
MODE_NAMES = {0: "aquarium", 1: "cat", 2: "reader"}


def log(msg):
    if config.DEBUG:
        print("[{:>8} ms] {}".format(time.ticks_ms(), msg))


def build_inputs():
    button = DebouncedInput(
        config.PIN_BUTTON, pull=Pin.PULL_UP,
        active_high=False, debounce_ms=config.DEBOUNCE_MS,
    )
    touch = DebouncedInput(
        config.PIN_TOUCH, pull=Pin.PULL_DOWN,
        active_high=True, debounce_ms=config.DEBOUNCE_MS,
    )
    pir = DebouncedInput(
        config.PIN_PIR, pull=None,
        active_high=True, debounce_ms=config.DEBOUNCE_MS,
    )
    led = StatusLED(config.PIN_LED)
    return button, touch, pir, led


def build_display():
    spi = SPI(
        1, baudrate=config.SCREEN_SPI_BAUD,
        sck=Pin(config.PIN_SCREEN_SCK),
        mosi=Pin(config.PIN_SCREEN_MOSI),
    )
    display = st7789.ST7789(
        spi, 240, 240,
        reset=Pin(config.PIN_SCREEN_RST, Pin.OUT),
        cs=Pin(config.PIN_SCREEN_CS, Pin.OUT),
        dc=Pin(config.PIN_SCREEN_DC, Pin.OUT),
        backlight=None,
        rotation=0,
    )
    bl = Pin(config.PIN_SCREEN_BL, Pin.OUT, value=0)
    return display, bl


def main():
    log("Boot OK. Initializing hardware...")
    button, touch, pir, led = build_inputs()
    display, bl = build_display()

    music = Music()                # not started yet — button toggles it

    # Boot splash (silent)
    splash(display, bl)

    aquarium = Aquarium(display, tick=music.tick)
    cat      = Cat(display,      tick=music.tick)
    reader   = Reader(display, config.READER_PATH, tick=music.tick)
    scenes   = [aquarium, cat, reader]

    mode = MODE_AQUARIUM
    screen_on = False
    last_activity = time.ticks_ms()
    last_frame    = time.ticks_ms()
    last_beat     = time.ticks_ms()

    # Long-press tracking
    touch_press_start = None
    touch_long_fired = False

    def turn_on():
        nonlocal screen_on
        screen_on = True
        bl.value(1)
        scenes[mode].reset()

    def turn_off():
        nonlocal screen_on
        if screen_on:
            screen_on = False
            display.fill(0)
            bl.value(0)

    log("Ready.")
    log("button=music  cap-tap=action  cap-hold={}ms=switch mode  pir=wake".format(
        config.LONG_PRESS_MS))

    try:
        while True:
            btn_rise, _ = button.update()
            tch_rise, tch_fall = touch.update()
            pir_rise, _ = pir.update()

            now = time.ticks_ms()

            music.tick()

            # --- Button: toggle music ---
            if btn_rise:
                if music.playing:
                    music.stop()
                    log("Music stopped.")
                else:
                    started = music.play("/sounds/lofi.wav", loop=True)
                    log("Music started." if started else "No /sounds/lofi.wav found.")

            # --- Cap sensor: short tap vs long press ---
            if tch_rise:
                touch_press_start = now
                touch_long_fired = False

            if (touch_press_start is not None
                    and not touch_long_fired
                    and touch.pressed
                    and time.ticks_diff(now, touch_press_start) >= config.LONG_PRESS_MS):
                # Long press fires while still held
                last_activity = now
                mode = (mode + 1) % len(MODES)
                log("Mode -> {}".format(MODE_NAMES[mode]))
                turn_on()
                touch_long_fired = True

            if tch_fall:
                last_activity = now
                if not touch_long_fired and touch_press_start is not None:
                    # Short tap: mode-specific action
                    if not screen_on:
                        turn_on()
                        log("Tap -> wake ({}).".format(MODE_NAMES[mode]))
                    elif mode == MODE_AQUARIUM:
                        log("Aquarium tap (no action).")
                    elif mode == MODE_CAT:
                        cat.touch()
                        log("Cat: {}".format(cat.state_name))
                    elif mode == MODE_READER:
                        reader.next_page()
                        log("Reader page {} / {}".format(reader.page + 1, reader.total_pages))
                touch_press_start = None
                touch_long_fired = False

            # --- PIR: wake on motion ---
            if pir_rise:
                last_activity = now
                if not screen_on:
                    turn_on()
                    log("Motion -> {}".format(MODE_NAMES[mode]))

            # --- Idle timeout ---
            if screen_on and time.ticks_diff(now, last_activity) > config.AUTO_OFF_MS:
                turn_off()
                log("Off (idle).")

            # --- Render ---
            if screen_on and time.ticks_diff(now, last_frame) >= config.SCREEN_FRAME_MS:
                scenes[mode].step()
                last_frame = now

            # --- Heartbeat ---
            if config.HEARTBEAT_MS and time.ticks_diff(now, last_beat) >= config.HEARTBEAT_MS:
                log("hb btn={} touch={} pir={} | mode={} screen={} music={}".format(
                    int(button.pressed), int(touch.pressed), int(pir.pressed),
                    MODE_NAMES[mode],
                    "on" if screen_on else "off",
                    "playing" if music.playing else "off",
                ))
                last_beat = now

            led.set(button.pressed or touch.pressed or pir.pressed)
            time.sleep_ms(config.LOOP_INTERVAL_MS)

    except KeyboardInterrupt:
        log("Interrupted.")
    finally:
        led.off()
        bl.value(0)
        music.stop()
        log("Clean shutdown.")


if __name__ == "__main__":
    main()
