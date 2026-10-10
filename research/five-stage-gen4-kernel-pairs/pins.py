"""Recomputed pinned values for the kernel stage (expected/kernel-pins.json).

Every count, hash or bound that #276 pinned as a literal and that the kernel
rewrite changes is re-pinned here from a fresh replay (discovery/generate_pins.py)
and asserted by the checkers through pin(). A missing or different value fails.
"""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
PINS=json.loads((HERE/'expected/kernel-pins.json').read_text())
RECORD=None   # discovery/generate_pins.py sets a dict here to record fresh values; verify.py never does

def pin(name,value):
    if RECORD is not None:RECORD[name]={str(k):v for k,v in value.items()}if isinstance(value,dict)else value;return value
    assert name in PINS,'unpinned kernel value: '+name
    expected=PINS[name]
    if isinstance(expected,dict):value={str(k):v for k,v in value.items()}
    assert value==expected,('pinned value differs',name,value,expected)
    return value
