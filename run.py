#!/usr/bin/env python3
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

from fomtan.app.main import run_live_mode

if __name__ == "__main__":
    run_live_mode()
