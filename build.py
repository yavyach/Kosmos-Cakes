#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка всего проекта: калькуляторы + страницы сайта.

  python build.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    scripts = (
        ROOT / "site" / "build_site_pages.py",
        ROOT / "site" / "_build_tilda_embed.py",
    )
    for script in scripts:
        print(f"\n=== {script.relative_to(ROOT)} ===")
        subprocess.run([sys.executable, str(script)], check=True, cwd=str(ROOT))
    print("\nГотово.")


if __name__ == "__main__":
    main()
