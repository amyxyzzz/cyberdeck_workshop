"""I2S audio for the MAX98357A speaker breakout.

Two playback paths:
  - tone() / chime()  : synthesize sine waves on the fly, no file needed
  - play_wav(path)    : stream a 16-bit PCM mono WAV from flash

All playback is "fire and (mostly) forget" -- short clips fit in I2S's
internal buffer and write() returns quickly. Long clips block while the
buffer drains, which will pause animation; chunk in the main loop if
that matters to you.
"""
from machine import Pin, I2S
import math
import struct

import config


_i2s = None
_current_rate = None


def _open_i2s(rate):
    """Open or reopen I2S at the given sample rate."""
    global _i2s, _current_rate
    if _i2s is not None and _current_rate == rate:
        return _i2s
    if _i2s is not None:
        _i2s.deinit()
    _i2s = I2S(
        0,
        sck=Pin(config.PIN_SPK_BCLK),
        ws=Pin(config.PIN_SPK_LRC),
        sd=Pin(config.PIN_SPK_DIN),
        mode=I2S.TX,
        bits=16,
        format=I2S.MONO,
        rate=rate,
        ibuf=8000,            # ~0.25 s of audio buffered internally
    )
    _current_rate = rate
    return _i2s


def init(rate=None):
    return _open_i2s(rate or config.SPK_SAMPLE_RATE)


def deinit():
    global _i2s, _current_rate
    if _i2s is not None:
        _i2s.deinit()
        _i2s = None
        _current_rate = None


def tone(freq, duration_ms, volume=0.3):
    """Play a sine wave at `freq` Hz for `duration_ms` ms."""
    rate = config.SPK_SAMPLE_RATE
    i2s = _open_i2s(rate)
    n = int(rate * duration_ms / 1000)
    amp = int(32767 * max(0.0, min(1.0, volume)))
    buf = bytearray(n * 2)
    k = 2 * math.pi * freq / rate
    for i in range(n):
        s = int(amp * math.sin(k * i))
        buf[i * 2]     = s & 0xFF
        buf[i * 2 + 1] = (s >> 8) & 0xFF
    i2s.write(buf)


def chime(notes, volume=0.3):
    """Play a sequence of (freq_hz, duration_ms) tuples. freq=0 is a rest."""
    rate = config.SPK_SAMPLE_RATE
    i2s = _open_i2s(rate)
    for freq, dur in notes:
        if freq <= 0:
            # silence
            n = int(rate * dur / 1000)
            i2s.write(bytearray(n * 2))
        else:
            tone(freq, dur, volume=volume)


def play_wav(path):
    """Stream a 16-bit PCM mono WAV from flash to the speaker.

    Convert files on your Mac with:
        ffmpeg -i input.mp3 -ac 1 -ar 16000 -sample_fmt s16 output.wav

    The WAV must be 16-bit mono. Sample rate is read from the file header
    and I2S is reconfigured to match.
    """
    with open(path, "rb") as f:
        riff = f.read(12)
        if riff[:4] != b"RIFF" or riff[8:12] != b"WAVE":
            raise ValueError("Not a WAV: " + path)
        rate = bits = channels = None
        # Walk chunks until 'data'
        while True:
            hdr = f.read(8)
            if len(hdr) < 8:
                raise ValueError("WAV truncated; no data chunk")
            chunk_id = hdr[:4]
            chunk_size = struct.unpack("<I", hdr[4:8])[0]
            if chunk_id == b"fmt ":
                fmt = f.read(chunk_size)
                channels = struct.unpack("<H", fmt[2:4])[0]
                rate     = struct.unpack("<I", fmt[4:8])[0]
                bits     = struct.unpack("<H", fmt[14:16])[0]
            elif chunk_id == b"data":
                break
            else:
                f.read(chunk_size)

        if bits != 16 or channels != 1:
            raise ValueError("Need 16-bit mono WAV; got bits={} ch={}".format(bits, channels))

        i2s = _open_i2s(rate)
        buf = bytearray(2048)
        while True:
            n = f.readinto(buf)
            if not n:
                break
            i2s.write(buf if n == len(buf) else buf[:n])
