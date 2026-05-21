"""Background music streamer.

Plays a 16-bit mono WAV from flash without blocking the main loop.
Chunks are pushed to I2S one at a time, paced by the chunk's playback
duration so write() never blocks.

Usage:
    music = Music()
    music.play("/sounds/lofi.wav", loop=True)

    while True:
        ...
        music.tick()        # call every loop iteration
        ...
"""
from machine import Pin, I2S
import time
import struct

import config


CHUNK_BYTES = 2048      # 64 ms of audio at 16 kHz mono 16-bit
IBUF_BYTES  = 16000     # ~0.5 s of headroom inside the I2S driver


class Music:
    def __init__(self):
        self.file = None
        self.i2s = None
        self.buf = bytearray(CHUNK_BYTES)
        self.loop = False
        self.playing = False
        self.data_start = 0
        self.rate = 0
        self.chunk_ms = 60
        self.next_write_at = 0

    def play(self, path, loop=True):
        """Open a WAV and start streaming. Returns True on success."""
        self.stop()
        import gc
        gc.collect() 
        try:
            f = open(path, "rb")
        except OSError:
            return False

        riff = f.read(12)
        if riff[:4] != b"RIFF" or riff[8:12] != b"WAVE":
            f.close()
            raise ValueError("Not a WAV: " + path)

        rate = bits = channels = None
        while True:
            hdr = f.read(8)
            if len(hdr) < 8:
                f.close()
                raise ValueError("WAV truncated; no data chunk")
            chunk_id = hdr[:4]
            chunk_size = struct.unpack("<I", hdr[4:8])[0]
            if chunk_id == b"fmt ":
                fmt = f.read(chunk_size)
                channels = struct.unpack("<H", fmt[2:4])[0]
                rate     = struct.unpack("<I", fmt[4:8])[0]
                bits     = struct.unpack("<H", fmt[14:16])[0]
            elif chunk_id == b"data":
                self.data_start = f.tell()
                break
            else:
                f.read(chunk_size)

        if bits != 16 or channels != 1:
            f.close()
            raise ValueError(
                "Need 16-bit mono WAV; got bits={} ch={}".format(bits, channels))

        self.file = f
        self.loop = loop
        self.rate = rate
        self.chunk_ms = (CHUNK_BYTES // 2) * 1000 // rate

        self.i2s = I2S(
            0,
            sck=Pin(config.PIN_SPK_BCLK),
            ws=Pin(config.PIN_SPK_LRC),
            sd=Pin(config.PIN_SPK_DIN),
            mode=I2S.TX,
            bits=16,
            format=I2S.MONO,
            rate=rate,
            ibuf=IBUF_BYTES,
        )

        # Preload a few chunks so we have buffer headroom from the start.
        for _ in range(12):
            n = self.file.readinto(self.buf)
            if n == 0:
                break
            self.i2s.write(self.buf if n == CHUNK_BYTES else self.buf[:n])

        self.playing = True
        self.next_write_at = time.ticks_add(time.ticks_ms(), self.chunk_ms * 3)
        return True

    def stop(self):
        self.playing = False
        if self.file is not None:
            self.file.close()
            self.file = None
        if self.i2s is not None:
            self.i2s.deinit()
            self.i2s = None

    def tick(self):
        """Stream one chunk if the buffer needs more, otherwise return fast."""
        if not self.playing:
            return
        now = time.ticks_ms()
        if time.ticks_diff(now, self.next_write_at) < 0:
            return

        n = self.file.readinto(self.buf)
        if n == 0:
            if self.loop:
                self.file.seek(self.data_start)
                n = self.file.readinto(self.buf)
            else:
                self.stop()
                return

        self.i2s.write(self.buf if n == CHUNK_BYTES else self.buf[:n])
        # Next write a hair before this chunk plays out, to keep buffer full.
        self.next_write_at = time.ticks_add(now, self.chunk_ms - 10)
