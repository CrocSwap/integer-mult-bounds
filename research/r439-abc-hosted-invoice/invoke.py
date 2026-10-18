#!/usr/bin/env python3
"""Inventory reads while running an unchanged Python entry point.

Matthieu Pascal, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import atexit
import importlib.util
import json
from pathlib import Path
import runpy
import sys

root, destination, script = map(lambda x: Path(x).resolve(), sys.argv[1:4])
args = sys.argv[4:]
seen = set()


def audit(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes)):
        return
    path = Path(args[0].decode() if isinstance(args[0], bytes) else args[0])
    if path.suffix == '.pyc':
        try:
            path = Path(importlib.util.source_from_cache(str(path)))
        except ValueError:
            return
    path = path.resolve()
    if path.is_relative_to(root) and path.is_file():
        seen.add(path.relative_to(root).as_posix())


atexit.register(lambda: destination.write_text(json.dumps(sorted(seen), indent=2) + '\n'))
sys.addaudithook(audit)
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name='__main__')
