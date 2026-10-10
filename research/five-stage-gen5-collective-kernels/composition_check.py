"""Check the exact kernel-disjoint subset of PR289 before composing with PR290.

Prepared with OpenAI Codex assistance. Apache-2.0; inherited mechanisms
and selections are credited in COMPOSITION-PROOF.md.
"""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def validate(selected, original, kernel):
    members = {s for p in kernel['pairs'] for s in (p['a'], p['b'])}
    members.update(s for f in kernel['families'] for s in [f['pivot']] + f['donors'])
    expected = [e for e in original['entries'] if not (set(e['scalar'][:2]) & members)]
    assert len(original['entries']) == original['selected_gate_count'] == 87
    assert selected['entries'] == expected, 'selection must be the exact kernel-disjoint subset'
    assert len(expected) == selected['selected_gate_count'] == 65
    for key in ('input_raw_sha256', 'input_scalar_sha256', 'source_record_count'):
        assert selected[key] == original[key], 'retiming input binding differs'
    operands = [s for e in expected for s in e['scalar'][:2]]
    assert len(operands) == len(set(operands)) == 130
    assert not (set(operands) & members)
    return members

def run():
    selected = json.loads((HERE / 'extreme-selection.json').read_text())
    original_path = HERE / 'notices/PR289-extreme-selection.json'
    original = json.loads(original_path.read_text())
    kernel = json.loads((HERE / 'kernel-selection.json').read_text())
    members = validate(selected, original, kernel)
    controls = []
    collision = next(e for e in original['entries'] if set(e['scalar'][:2]) & members)
    bad_cases = []
    bad = copy.deepcopy(selected); bad['entries'].append(collision); bad['selected_gate_count'] += 1
    bad_cases.append(('conflicting retiming included', bad))
    bad = copy.deepcopy(selected); bad['entries'].pop(); bad['selected_gate_count'] -= 1
    bad_cases.append(('compatible retiming omitted', bad))
    bad = copy.deepcopy(selected); bad['entries'][0]['new_basis'][0][0] += 1
    bad_cases.append(('retiming basis changed', bad))
    bad = copy.deepcopy(selected); bad['input_raw_sha256'] = '0' * 64
    bad_cases.append(('retiming input binding changed', bad))
    for name, bad in bad_cases:
        try:
            validate(bad, original, kernel)
        except AssertionError:
            controls.append(name)
        else:
            raise AssertionError('invalid composition admitted: ' + name)
    return dict(status='PASS_EXACT_KERNEL_DISJOINT_RETIMING_COMPOSITION',
                upstream_pr289_selection_sha256=hashlib.sha256(original_path.read_bytes()).hexdigest(),
                selected_gates=65, excluded_conflicting_gates=22,
                affected_operands=130, kernel_members=len(members), controls=controls)
