"""Pin assignments and runtime tunables.
"""
HEARTBEAT_MS = 1000

# --- Button and Cap ---------------------------------------------------------
PIN_BUTTON = 15
PIN_TOUCH = 6
PIN_LED = "LED" 

# --- Screen (ST7789 1.54" 240x240, SPI1) ------------------------------------
PIN_SCREEN_SCK  = 10   # SCL on the TFT
PIN_SCREEN_MOSI = 11   # SDA on the TFT
PIN_SCREEN_CS   = 9
PIN_SCREEN_DC   = 13
PIN_SCREEN_RST  = 12
PIN_SCREEN_BL   = 14
SCREEN_SPI_BAUD = 32_000_000
SCREEN_FRAME_MS = 120  # ~8 FPS animation
READER_PATH   = "/content/reader.txt" # where the kindle lives

# --- Speaker (MAX98357A I2S, I2S0) ------------------------------------------
PIN_SPK_BCLK = 16
PIN_SPK_LRC  = 17
PIN_SPK_DIN  = 18
SPK_SAMPLE_RATE = 16000

# --- PIR motion sensor ------------------------------------------------------
PIN_PIR = 22

# --- Auto-off ---------------------------------------------------------------
AUTO_OFF_MS = 100_000   # turn screen off after this many ms with no activity

# --- Timing (milliseconds) ---------------------------------------------------
DEBOUNCE_MS = 30
LOOP_INTERVAL_MS = 5

# --- Mode switching ---------------------------------------------------------
LONG_PRESS_MS = 700  # hold cap sensor this long to switch modes

# --- Logging -----------------------------------------------------------------
DEBUG = True 
