"""Bind inputs, exhaust the finite cost domain, and check the frozen witness."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def same(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def module(name):
    spec = importlib.util.spec_from_file_location('scale_' + name, HERE / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def bind_sources():
    for path, pin in read(HERE / 'SOURCES.json')['files'].items():
        raw = (ROOT / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source changed: ' + path)
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        need(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'blob changed: ' + path)
        if 'payload_sha256' in pin:
            need(hashlib.sha256(gzip.decompress(raw)).hexdigest() == pin['payload_sha256'],
                 'payload changed: ' + path)


def elide(word, initially_zero):
    """Remove only known-zero W clears; preserve each nonunit cleanup."""
    zero, result = initially_zero, []
    for primitive in word:
        if tuple(primitive[1]) == ('W', 0):
            if primitive[0] == 'clear':
                if zero:
                    continue
                zero = True
            elif primitive[0] in ('copy', 'add', 'subtract'):
                zero = False
        result.append(primitive)
    return result


def shared_cost(ops, lower):
    """PR755's exact adjacent equal-source, equal-nonunit-magnitude class."""
    from fractions import Fraction as Q
    total, i = 0, 0
    while i < len(ops):
        op = ops[i]
        if op[0] != 'add' or abs(Q(op[3], op[4])) == 1:
            total += len(lower(op))
            i += 1
            continue
        end = i + 1
        while end < len(ops):
            other = ops[end]
            if (other[0] != 'add' or other[2] != op[2]
                    or abs(Q(other[3], other[4])) != abs(Q(op[3], op[4]))):
                break
            end += 1
        total += (len(lower(op)) - 2) + (end - i) + 1
        i = end
    return total


def main():
    bind_sources()
    search = module('search')
    programs = json.load(gzip.open(ROOT / search.INPUT, 'rt'))
    expected = read(HERE / 'CENSUS.json')
    blocks = read(HERE / 'BLOCKS.json')
    receipt = {}
    for direction, events in programs.items():
        actual = search.census(events)
        need(same(actual, expected[direction]), 'census drift: ' + direction)
        candidate = actual['best']
        ops = [event[1] for event in events[candidate['start']:candidate['stop']]]
        baseline = [p for op in ops for p in search.lower(op)]
        word = search.materialize(events, candidate)
        generated = {**candidate, 'ops': ops, 'baseline_word': baseline, 'word': word,
                     'baseline_length': len(baseline), 'length': len(word)}
        canonical = json.loads(json.dumps(generated))
        need(same(canonical, blocks[direction]), 'frozen word drift: ' + direction)
        need(len(word) - len(baseline) == candidate['delta'], 'underpriced witness')
        receipt[direction] = {
            'raw': [len(baseline), len(word)],
            'dirty_work_clear_elided': [len(elide(baseline, False)), len(elide(word, False))],
            'zero_work_clear_elided': [len(elide(baseline, True)), len(elide(word, True))],
            'pr755_baseline_cost': shared_cost(ops, search.lower),
        }
        r, h = tuple(candidate['register']), candidate['h']
        from fractions import Fraction as Q
        need(candidate['mode'] == 'flush' and Q(ops[0][2], ops[0][3]) > 0,
             'shared composition requires a positive initial scale and flush')
        revised = [search.adjusted(op, r, h) for op in ops[1:]]
        q = search.shift(h)
        revised.append(['scale', list(r), q.numerator, q.denominator])
        shared_before = search.share_power_runs(ops, direction == 'backward')
        shared_after = search.share_power_runs(revised, direction == 'backward')
        grouped = {**generated, 'baseline_word': shared_before, 'word': shared_after,
                   'baseline_length': len(shared_before), 'length': len(shared_after),
                   'delta': len(shared_after) - len(shared_before)}
        need(same(json.loads(json.dumps(grouped)), blocks[direction + '-shared']),
             'shared witness drift: ' + direction)
        receipt[direction]['shared_raw'] = [len(shared_before), len(shared_after)]
        receipt[direction]['shared_zero_work'] = [
            len(elide(shared_before, True)), len(elide(shared_after, True))]
    independent = module('independent')
    audit = independent.main()
    need(same(audit, read(HERE / 'AUDIT.json')), 'independent receipt drift')
    # independent.py itself checks the exact endpoints and rejects mutations.
    need(receipt['backward']['raw'] == [230, 174], 'raw bill drift')
    need(receipt['backward']['zero_work_clear_elided'] == [223, 150], 'fair bill drift')
    need(receipt['forward']['pr755_baseline_cost'] == 142, 'predecessor comparison drift')
    need(receipt['backward']['pr755_baseline_cost'] == 230, 'backward overlap drift')
    need(receipt['backward']['shared_zero_work'] == [135, 102], 'shared fair bill drift')
    print(json.dumps(receipt, sort_keys=True))
    print('PASS_JP8_SCALE_INTERVALS starts=221 intervals=557559_per_orientation '
          'backward_real_saving=66_beyond_equal_magnitude_fanin no_new_kappa')


if __name__ == '__main__':
    main()
