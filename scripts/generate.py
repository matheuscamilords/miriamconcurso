#!/usr/bin/env python3
"""Regenera o currículo aprofundado de 47 datas, não a edição legada curta."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('rebuild_complete.py')),run_name='__main__')
