#!/usr/bin/env python3
"""providers_from_words.py -- derive PROVIDERS.json from the two provider words exactly as PR2917's check_allocation.py does:
helpers = sorted(range(224,704) - removed); width = len(helper_final.get(h, [0]*9)) - len(start_extra.get(h, []));
actual_paid_profile = frame_report(word) profile (= report.local_profile, asserted, via PR2917's vendored preload_move.py);
cleanup buffers {r >= 704} == {704 + h : h in helper_final}, count = --buffers.  Output: json.dumps(indent=2, sort_keys=True), no newline
(PR2917's byte format).  Usage: python -I -B providers_from_words.py BASE.json.gz EXTRA.json.gz OUT.json --buffers 86 [--compare REF]"""
import sys, json, gzip, hashlib, types, pathlib, argparse
from collections import Counter
PKG17 = pathlib.Path('S/r13/vendor/pr2917/research/paired-helper-extension')
ap = argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('extra'); ap.add_argument('out'); ap.add_argument('--buffers', type=int, required=True); ap.add_argument('--compare')
a = ap.parse_args()
def read(p):
    b = pathlib.Path(p).read_bytes(); return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)
frames = types.ModuleType('frames'); frames.__file__ = str(PKG17 / 'vendor/preload_move.py'); sys.modules['frames'] = frames
exec(compile((PKG17 / 'vendor/preload_move.py').read_bytes(), str(PKG17 / 'vendor/preload_move.py'), 'exec'), frames.__dict__)
providers, info = {}, {}
for path, pid in [(a.base, 'gauge44'), (a.extra, 'extra')]:
    word = read(path)
    profile, inventory = frames.frame_report(word)
    assert profile == word['report']['local_profile'] and inventory == word['report']['width_inventory'], 'frame_report != report'
    helpers = sorted(set(range(224, 704)) - set(word['removed']))
    widths = [len(word['helper_final'].get(str(h), [0] * 9)) - len(word['start_extra'].get(str(h), [])) for h in helpers]
    assert len(helpers) == 408 and len(word['centers']) == 8, 'helpers/centres'
    buffers = {r for gate in word['cleanup'] for r in (gate[1:3] if gate[0] == 'add' else gate[1:2]) if r >= 704}
    assert buffers == {704 + int(h) for h in word['helper_final']}, 'cleanup buffer / end-point bijection'
    assert len(buffers) == a.buffers, 'buffer count %d != %d' % (len(buffers), a.buffers)
    prof = {int(k): v for k, v in profile.items()}
    assert sum(r * n for r, n in prof.items()) - sum(widths) == 1856, 'local mass - width mass != 1856'
    assert dict(Counter(widths)) == {int(k): v for k, v in inventory.items()}, 'width list vs inventory'
    providers[pid] = {'actual_paid_profile': {str(k): prof[k] for k in sorted(prof)}, 'widths': widths}
    info[pid] = dict(word_sha256=hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest(), local=prof, inventory=dict(sorted(Counter(widths).items())), buffers=len(buffers),
                     narrowed_vs_9=[h for h, w in zip(helpers, widths) if w == 8 and str(h) in word['helper_final']][:200])
text = json.dumps(providers, indent=2, sort_keys=True)
pathlib.Path(a.out).write_text(text)
print('wrote', a.out, 'sha256', hashlib.sha256(text.encode()).hexdigest())
for pid, d in info.items():
    print(pid, 'word', d['word_sha256'][:16], 'local', d['local'], 'inventory', d['inventory'], 'buffers', d['buffers'])
print('identical widths/profile across providers:', providers['gauge44'] == providers['extra'])
if a.compare:
    ref = pathlib.Path(a.compare).read_bytes()
    print('byte-identical to', a.compare, ':', ref == text.encode(), '| content-equal:', json.loads(ref) == providers)
