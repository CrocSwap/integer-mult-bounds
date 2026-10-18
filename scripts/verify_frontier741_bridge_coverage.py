#!/usr/bin/env python3
"""PR851 bridge identity checks, composed with the immutable PR741 binding.
Credit Adem Vessell (@AdemVessell), PR851; external adapter by Douglas Colkitt with Codex.
Apache-2.0. This preserves the historical proof-supplement hashes.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_frontier741_bindings import check as historical_check, read, require

EXPECTED_BRIDGE_IDS = frozenset(range(18))


def require_bridge_controls(value):
    require(isinstance(value, list) and len(value) == 18,
            'Bit bridge controls')
    seen = []
    for control in value:
        require(isinstance(control, dict), 'Bit bridge control record')
        bridge_id = control.get('omit_bridge')
        require(type(bridge_id) is int and bridge_id in EXPECTED_BRIDGE_IDS,
                'Bit bridge control ID')
        require(type(control.get('rejected')) is bool and control['rejected'] is True,
                'Bit bridge control rejection')
        seen.append(bridge_id)
    require(set(seen) == EXPECTED_BRIDGE_IDS, 'Bit bridge control coverage')


def check(bit, complex_dir):
    require_bridge_controls(read(bit / 'cout/columns_k4.json')['negative_controls'])
    return historical_check(bit, complex_dir)
