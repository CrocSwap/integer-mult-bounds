"""Replay the complete PR968 D/E/H coverage with both exact enumerators.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import statistics
import time
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = 'research/frame-pair-enumeration-fast-seed93/baseline.py'
BASE = 'abdc6a7002abdbcd9e21bfc5e1a795784deacfdf'
spec = importlib.util.spec_from_file_location('mask_enumerator', HERE/'fast.py')
fast = importlib.util.module_from_spec(spec); spec.loader.exec_module(fast)


def need(ok, why):
    if not ok: raise ValueError(why)


def canonical(obj):
    # JSON object keys are strings. Normalize runtime integer keys before
    # sorting, so saved and live chain dictionaries use the same order.
    return json.dumps(json.loads(json.dumps(obj, allow_nan=False)),
                      sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(obj): return hashlib.sha256(canonical(obj).encode()).hexdigest()


def check_pins(pins):
    need(pins['base_commit'] == BASE and set(pins['files']) == {REL}, 'source inventory')
    for rel, expected in pins['files'].items():
        raw = (ROOT/rel).read_bytes().replace(b'\r\n', b'\n')
        need(hashlib.sha256(raw).hexdigest() == expected, 'source digest')


def source():
    # PR968 relies on assertions. Explicit optimize=0 preserves them even if
    # this wrapper is launched with -O; no predecessor file is changed.
    module = types.ModuleType('pinned_pr968')
    module.__file__ = str(ROOT/REL)
    exec(compile((ROOT/REL).read_bytes(), str(ROOT/REL), 'exec', optimize=0), module.__dict__)
    return module


def scoped_replay(use_fast):
    m = source()
    reference = m.frame_pair_solutions
    stream = []
    rank_records = []
    original_pair = m.pair_decoder
    def enumerate_pairs(a, b):
        result = fast.frame_pair_solutions(a, b, m.IP) if use_fast else reference(a, b)
        stream.append([a, b, result])
        return result
    def pair_check(pairs, live):
        answer = original_pair(pairs, live)
        rank_records.append([pairs, live, answer])
        return answer
    m.frame_pair_solutions = enumerate_pairs
    m.pair_decoder = pair_check
    capture = io.StringIO()
    start = time.perf_counter()
    with contextlib.redirect_stdout(capture):
        frames, example, hist, kinds = m.section_d()
        chain = m.section_e(frames, example)
        m.section_h(example, frames, hist)
    elapsed = time.perf_counter() - start
    need(not m.FAILS, 'predecessor checks failed: '+str(m.FAILS))
    need(len(frames) == 1260 and len(stream) == 2520 and len(rank_records) == 7168,
         'complete D and H enumeration/rank coverage')
    receipt = {'frames': len(frames), 'enumerations': len(stream), 'decoder_rank_checks': len(rank_records),
               'term_rank_checks': sum(len(record[2][1]) for record in rank_records),
               'ordered_solution_stream_sha256': digest(stream), 'rank_stream_sha256': digest(rank_records),
               'histogram': sorted(hist.items()), 'types': sorted((str(k), v) for k,v in kinds.items()),
               'example': example, 'chain': chain, 'log': capture.getvalue().splitlines()}
    return receipt, elapsed


def controls():
    m = source(); a = list(m.FRAME0)
    frame = next(list(f) for f in m.frames_in(m.P112) if m.frame_pair_solutions(a,list(f)))
    expected = m.frame_pair_solutions(a, frame)
    need(len(expected) == 8, 'control fixture must be admissible')
    passed = []
    def rejected(name, fn):
        try: fn()
        except ValueError: passed.append(name)
        else: raise ValueError('control accepted: '+name)
    for name, changed in [('drop solution', expected[:-1]), ('reverse solution order', expected[::-1]),
                          ('duplicate solution', expected + expected[:1])]:
        rejected(name, lambda changed=changed: need(changed == expected, 'full ordered stream mismatch'))
    changed = copy.deepcopy(expected); changed[0][0] = (changed[0][0][0], changed[0][1][1])
    rejected('swap partner', lambda: need(changed == expected, 'partner mismatch'))
    for name, left, right in [('short frame', a[:-1], frame), ('duplicate frame entry', a, frame[:-1]+frame[:1]),
                             ('overlapping frames', a, a)]:
        rejected(name, lambda left=left,right=right: fast.frame_pair_solutions(left,right,m.IP))
    pins = json.loads((HERE/'SOURCES.json').read_text())
    changed = copy.deepcopy(pins); changed['files'][REL] = '0'*64
    rejected('source byte mutation', lambda: check_pins(changed))
    changed = copy.deepcopy(pins); changed['files'] = {}
    rejected('missing source binding', lambda: check_pins(changed))
    # Exercise an actual predecessor assertion under this caller's flags.
    try: m.ip((1,), (1,))
    except AssertionError: passed.append('source rejects nonintegral root pairing under optimized caller')
    else: raise ValueError('source assertions were disabled')
    return passed


def benchmark():
    m = source(); frames = m.frames_in(m.P112)
    timings = {'reference': [], 'candidate': []}; output_hash = None
    for repetition in range(3):
        # Alternate to reduce fixed-order warmup bias; every run consumes the
        # identical ordered 1260-frame input, including 364 empty outputs.
        order = ('reference','candidate') if repetition % 2 == 0 else ('candidate','reference')
        for kind in order:
            start = time.perf_counter()
            if kind == 'reference': outputs = [m.frame_pair_solutions(m.FRAME0,list(f)) for f in frames]
            else: outputs = [fast.frame_pair_solutions(m.FRAME0,list(f),m.IP) for f in frames]
            timings[kind].append(time.perf_counter()-start)
            h = digest(outputs)
            if output_hash is None: output_hash = h
            need(h == output_hash, 'benchmark changed complete ordered stream')
    medians = {k:statistics.median(v) for k,v in timings.items()}
    return {'python': platform.python_version(), 'platform': platform.platform(), 'frames': len(frames),
            'repetitions': 3, 'seconds': timings, 'median_seconds': medians,
            'median_speedup': medians['reference']/medians['candidate'], 'ordered_stream_sha256': output_hash,
            'timing_scope': 'Enumeration kernel only; unchanged downstream costs measured separately; no timing threshold determines correctness.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    parser.add_argument('--benchmark', action='store_true')
    args = parser.parse_args()
    need(canonical({1:'a',2:'b',10:'c'}) == canonical({'1':'a','2':'b','10':'c'}),
         'JSON key normalization')
    pins = json.loads((HERE/'SOURCES.json').read_text()); check_pins(pins)
    before, bt = scoped_replay(False); after, at = scoped_replay(True)
    need(canonical(before) == canonical(after), 'complete D/E/H proof-relevant receipt mismatch')
    receipt = {'status':'PASS_FRAME_PAIR_FAST_S93', 'base_commit':BASE, 'seed':93,
               'source_pins':pins, 'coverage':after, 'negative_controls':controls()}
    if args.record: (HERE/'CERTIFICATE.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    else: need(canonical(receipt) == canonical(json.loads((HERE/'CERTIFICATE.json').read_text())), 'saved certificate mismatch')
    if args.benchmark:
        bench = benchmark(); bench['D_E_H_seconds'] = {'reference':bt,'candidate':at,'speedup':bt/at}
        (HERE/'BENCHMARK.json').write_text(json.dumps(bench,indent=2,sort_keys=True)+'\n')
        print('BENCHMARK enumeration median speedup',bench['median_speedup'],'D/E/H',bt/at)
    print('PASS_FRAME_PAIR_FAST_S93 frames=1260 decoders=7168 term_ranks=57344 chain=25 inherited_controls=6 package_controls='+str(len(receipt['negative_controls'])))


if __name__ == '__main__': main()
