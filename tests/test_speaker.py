"""Speaker smoke test — plays a C major scale up and back down.

Run with:
    make test-speaker

If you hear nothing: check VIN to VBUS (5V), BCLK/LRC/DIN to GP16/17/18,
and that the speaker is connected to the amp output, not the Pico.
"""
import time

from sound import tone, deinit


# One octave of C major (Hz): C D E F G A B C
SCALE = [262, 294, 330, 349, 392, 440, 494, 523]
NOTE_NAMES = ["C", "D", "E", "F", "G", "A", "B", "C'"]
NOTE_MS = 300


def main():
    print("[test_speaker] Playing C major scale, ascending then descending.")
    try:
        for hz, name in zip(SCALE, NOTE_NAMES):
            print("[test_speaker]   {:>2}  {} Hz".format(name, hz))
            tone(hz, NOTE_MS, volume=0.3)
        time.sleep_ms(200)
        for hz, name in zip(reversed(SCALE), reversed(NOTE_NAMES)):
            print("[test_speaker]   {:>2}  {} Hz".format(name, hz))
            tone(hz, NOTE_MS, volume=0.3)
        print("[test_speaker] Done.")
    except KeyboardInterrupt:
        print("[test_speaker] Interrupted.")
    finally:
        deinit()


if __name__ == "__main__":
    main()
