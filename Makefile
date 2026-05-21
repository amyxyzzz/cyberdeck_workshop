# Pico MicroPython project — mpremote shortcuts.
# Usage: `make help`

SRC := src
PORT ?= auto

MP := mpremote connect $(PORT)

.PHONY: help sync run repl reset ls clean wipe du \
        test-button test-button-cap test-speaker \
        test-screen-colors test-screen-aquarium test-all
help:
	@echo "Targets:"
	@echo "  make sync   Copy src/ -> Pico filesystem and soft-reset"
	@echo "  make run    Run src/main.py once without saving (fast iteration)"
	@echo "  make test-screen  Run src/test_screen.py once (smoke test)"
	@echo "  make repl   Live REPL on the Pico   (Ctrl-X to exit)"
	@echo "  make reset  Soft reset the Pico"
	@echo "  make ls     List files on the Pico"
	@echo "  make wipe   Delete all .py files on the Pico  (be careful)"
	@echo ""
	@echo "Override the port with: make sync PORT=/dev/tty.usbmodem1101"

sync:
	$(MP) fs cp -r $(SRC)/. :
	$(MP) reset

run:
	$(MP) run $(SRC)/main.py

test-button:
	$(MP) run tests/test_button.py

test-button-cap:
	$(MP) run tests/test_button_and_cap.py

test-speaker:
	$(MP) run tests/test_speaker.py

test-screen-colors:
	$(MP) run tests/test_screen_colors.py

test-screen-aquarium:
	$(MP) run tests/test_screen_aquarium.py

test-all: test-button test-button-cap test-screen-colors test-speaker
	@echo "All tests run. test-screen-aquarium separately if you want to watch fish."
	
repl:
	$(MP) repl

reset:
	$(MP) reset

ls:
	$(MP) fs ls

wipe:
	$(MP) exec "import os; [os.remove(f) for f in os.listdir() if f.endswith('.py')]"
