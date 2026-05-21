"""Runs once at power-on, before main.py.

Use this for low-level setup (network bring-up, garbage-collect tuning,
disabling the REPL on UART, etc). Keep it minimal -- if it crashes,
you may need BOOTSEL to recover.
"""
import gc
gc.collect()
