"""Reproduce the frozen PR289 subset excluding all PR290 kernel members.

Run only as discovery, before build_selection.py and generate_pins.py.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
original = json.loads((ROOT / 'notices/PR289-extreme-selection.json').read_text())
kernel = json.loads((ROOT / 'kernel-selection.json').read_text())
members = {s for p in kernel['pairs'] for s in (p['a'], p['b'])}
members.update(s for f in kernel['families'] for s in [f['pivot']] + f['donors'])
original['entries'] = [e for e in original['entries'] if not (set(e['scalar'][:2]) & members)]
original['selected_gate_count'] = len(original['entries'])
original['status'] = 'GEN5_KERNEL_DISJOINT_EXTREME_MEET_SELECTION'
assert original['selected_gate_count'] == 65
(ROOT / 'extreme-selection.json').write_text(json.dumps(original, indent=1) + '\n')
print('selected 65 compatible gates, excluded 22 kernel conflicts')
