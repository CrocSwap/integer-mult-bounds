#!/usr/bin/env python3
"""Complete check of the served bit word, its 34 terminal sinks and its paid moment.

Counterpart of PR200's bit/prove.py: same formal columns (F2 identity and the integer defining decoder), the
same adverse controls plus one for the served operations, PR200's terminal-sink compiler (served fork), PR200's
paid-moment certification (imported unchanged) and PR200's prime witnesses (every frame used here is one of
PR200's witnessed frames; no new frame is introduced). Prints one JSON record. Usage:

    python3 served_prove.py PR200_PACKAGE_DIR SERVED_DIR
"""
from fractions import Fraction as Q
from pathlib import Path
import contextlib, gzip, importlib.util, json, sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
from served_word import Candidate, need


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def used_frames(word):
    used = set(word.opframe) | set(word.w['source_frame']) | set(word.w['root_frame']) | {word.w['full_frame']}
    used.update(z['frame'] for z in word.w['gauges'])
    for e in word.k['entries']:
        used.update((e['mix_frame'], e['deliver_frame']))
        used.update(e['passive_chain'])
    return used


def prove(pr200, served):
    pr200, served = Path(pr200), Path(served)
    pr200_prove = load('pr200_prove', pr200 / 'bit/prove.py')     # certify() and js() are used unchanged
    word = Candidate(pr200, served); word.exact_frames(); row = word.row()
    need(row['reused_registers'] == len(word.pairs), 'physical aliases counted')
    formal = [word.formal(r) for r in (2, 0)]
    controls = []
    for tamper in ('omit_compensation', 'missing_partner', 'stale', 'served_from_carrier'):
        try:
            word.formal(2, tamper)
        except ValueError:
            controls.append(tamper)
        else:
            raise ValueError('Adverse word control accepted: ' + tamper)
    i = word.changed_frames[0]; old = word.opframe[i]; word.opframe[i] = word.register([])
    try:
        word.exact_frames()
    except ValueError:
        controls.append('zero_operation_frame')
    else:
        raise ValueError('Zero frame accepted')
    word.opframe[i] = old
    # a served passive chain that skips its served frame must fail the chain checks
    e = next(e for e in word.k['entries'] if e.get('early'))
    saved = e['passive_chain']; e['passive_chain'] = [saved[0], saved[1], saved[3]]
    try:
        word.C.chains()
    except ValueError:
        controls.append('served_passive_chain_without_stop')
    else:
        raise ValueError('Served chain without its stop accepted')
    e['passive_chain'] = saved
    e['early'] = False
    try:
        word.C.chains()
    except ValueError:
        controls.append('served_pair_without_early_mix')
    else:
        raise ValueError('Served pair without early mix accepted')
    e['early'] = True
    terminal_module = load('served_terminal', HERE / 'served_terminal.py')
    selection = json.loads((pr200 / 'selected/bit/sinks.json').read_text())
    with contextlib.redirect_stdout(sys.stderr):
        terminal = terminal_module.prove(word, selection)
    terminal.pop('seconds'); terminal.pop('maxrss')
    unsunk = row; row = terminal['profile']
    row['child_histogram'] = {int(k): n for k, n in row['child_histogram'].items()}
    need(row['terminal_sinks'] == len(selection) and terminal['scalar_addition_delta'] <= 0, 'terminal sink count and retained scalar bill')
    need(row['W_per_vertex'] == unsunk['W_per_vertex'] - len(selection) and row['R'] == unsunk['R'] - len(selection), 'terminal removals reduce stock by the sink count')
    coarse = pr200_prove.certify(row)
    witnesses = json.loads(gzip.decompress((pr200 / 'bit/prime-witnesses.json.gz').read_bytes()))
    witnessed = {f for rec in witnesses['frame_witnesses'] for f in rec['frame_ids']}
    used = used_frames(word)
    need(used <= witnessed, 'every used frame carries a PR200 prime witness')
    return pr200_prove.js(dict(status='PASS', profile=row, unsunk_profile=unsunk, terminal=terminal, formal=formal,
                               coarse=coarse, word_controls=controls, served_operations=len(word.served),
                               used_frames=len(used), used_frames_witnessed_by_pr200=True,
                               scope='Complete F2 identity, integer defining decoder, exact physical frame geometry; '
                                     'retained weighted-compiler contracts.'))


def main():
    need(not sys.flags.optimize, 'assertions enabled')
    print(json.dumps(prove(sys.argv[1], sys.argv[2]), sort_keys=True))


if __name__ == '__main__':
    main()
