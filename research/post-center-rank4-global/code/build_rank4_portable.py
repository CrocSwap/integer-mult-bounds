"""Replay the frozen SAME504 post-gauge/rank-four entrance construction.

Prepared for icekylinx with GPT-6 Astra assistance. Apache-2.0.

This is a deterministic replay, with no candidate search.  The inherited
gk_word/gk_common response and kernel primitives are by DreamingOfClouds,
prepared with Claude Opus 5.5 (Anthropic), PR484, and retain their notices.
The input SAME504 scalar word retains its own source and construction credits.

The new order is: original static40 kernels and A; center cut; 112 gauge
compensations; 56 rank-four pivot injections; native B; full-frame cleanup.
Every pivot is removed from the post-gauge set.  A gauge donor receives new
pivot dirt only after its own initial dirt has been compensated.
"""
import argparse
import copy
import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path


def normalize_gzip_header(result):
    # Frozen artifact header: 1f8b0800000000000203.  With mtime=0,
    # Python 3.11 can inherit zlib's OS byte (3 on this build), whereas
    # Python 3.14 writes 255.  This byte is metadata, outside the deflate
    # payload and its CRC.  Fix only that byte to the frozen value; retain
    # strict checks of both the entire compressed file and decoded content.
    assert result[:9] == bytes.fromhex('1f8b08000000000002'), 'gzip header'
    assert len(result) >= 18, 'gzip size'
    return result[:9] + bytes([3]) + result[10:]


def main():
    # An assert alone would itself disappear under -O, so reject optimized
    # execution explicitly before relying on the proof checks below.
    if not __debug__:
        raise RuntimeError('Proof replay requires Python without -O or -OO.')
    assert __debug__, 'proof assertions must remain enabled'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-word', type=Path, required=True)
    ap.add_argument('--recipe', type=Path, required=True)
    ap.add_argument('--gk-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True,
                    help='New output directory; writes FULL-WORD.json.gz and REPLAY.json.')
    a = ap.parse_args()
    sys.path.insert(0, str(a.gk_dir.resolve()))
    import gk_word as g
    import gk_common as common
    g.V = common.V = 112
    common.DATA = 7168
    source = a.base_word.read_bytes()
    recipe = json.loads(a.recipe.read_text())
    assert hashlib.sha256(source).hexdigest() == recipe['source_sha256'], 'source hash'
    raw = json.loads(gzip.decompress(source))
    assert len(raw['ports']) == 112 and raw['report']['R'] == 504
    assert raw['report']['h'] == len(g.FULL) == 9
    sel = copy.deepcopy(recipe['selection'])
    groups = recipe['rank4_groups']
    gauges = {int(h): g.basis(E) for h,E in sel['gauge'].items()}
    pivots = {p for cl in groups for p in cl['pivots']}
    donors = {d for cl in groups for d in cl['donors']}
    assert len(groups) == 14 and len(pivots) == len(donors) == 56
    assert not pivots & donors and not pivots & set(gauges)
    assert pivots | donors == set(range(392,504))
    assert len(gauges) == 112 and donors <= set(gauges)
    assert sum(len(cl['pivots'])+len(cl['donors']) for cl in groups) == 112
    static = {h for cl in sel['kernel'] for h in cl['pivots']+cl['donors']}
    assert not static & (set(gauges)|pivots)
    assert sum(len(cl['pivots']) for cl in sel['kernel']) == 40
    touched = {r for e in raw['A']+raw['cut']
               for r in (e[1:3] if e[0]=='add' else e[1:2])}
    assert not {224+h for h in set(gauges)|pivots} & touched
    for e in raw['A']+raw['cut']:
        if 112 <= e[1] < 224:
            assert e[0]=='add' and not 112 <= e[2] < 224

    cols = g.responses(raw)
    first = g.first_frames(raw)
    w = g.build(raw, {'kernel':sel['kernel']}, check=False)
    prefix = []
    for h,E in sorted(gauges.items()):
        w['start_extra'][str(224+h)] = list(E)
        for t,q in sorted(cols[h].items()):
            prefix.append(['add',112+t,224+h,-q.numerator,q.denominator,list(E)])
    assert len(prefix) == recipe['rank4_anchor_after_post_gauge_additions'] == 320
    injections = []
    for cl in groups:
        E = g.basis(cl['E'])
        assert len(E) == 4
        for h in cl['pivots']+cl['donors']:
            assert g.span(E) <= g.span(first[h])
        for d in cl['donors']:
            assert g.span(gauges[d]) <= g.span(E)
        for p in cl['pivots']:
            rel = g.solve_relation(cols, cl['donors'], p)
            frozen = {int(d):Q(q) for d,q in cl['relations'][str(p)].items()}
            assert rel == frozen, ('frozen relation',p)
            w['start_extra'][str(224+p)] = list(E)
            for d,q in sorted(rel.items()):
                assert q.denominator & (q.denominator-1) == 0
                injections.append(['add',224+d,224+p,-q.numerator,q.denominator,list(E)])
    w['B'] = prefix+injections+w['B']
    w['cleanup'] = [g.inverse(e,g.FULL) for e in reversed(w['A']+w['B'])
                    if not 112 <= e[1] < 224]
    H = g.profile(w)
    widths = [9-len(w['start_extra'].get(str(224+h),[])) for h in range(504)]
    mass = sum(r*z for r,z in H.items())
    entering = sum(x<9 for x in widths)
    rank = sum(9-x for x in widths)
    assert Counter(widths) == Counter({5:56,8:152,9:296})
    assert mass == 6016 and rank == 376 and entering == 208
    w['report'].update(local_profile=dict(sorted(H.items())),
                      local_rank_mass=mass,
                      width_inventory=dict(sorted(Counter(widths).items())),
                      post_center_gauges=len(gauges),
                      post_center_compensation_additions=len(prefix),
                      entrance_rank=rank, entering_helpers=entering,
                      rank4_kernel_groups=len(groups),
                      rank4_kernel_pivots=len(pivots),
                      rank4_kernel_additions=len(injections),
                      post_gauge_kernel_anchor=len(prefix),
                      status='EXACT_RELATIONS_AND_FRAMES_PENDING_INDEPENDENT_REPLAY')
    for key in ('global_profile','live','complex_coarse_float','gain_percent_float'):
        w['report'].pop(key,None)
    # Normalize JSON keys before comparing the frozen report: profile indices
    # are integer keys in memory, and JSON object keys are strings on disk.
    assert json.loads(json.dumps(w['report'])) == recipe['report'], 'frozen report'
    result = normalize_gzip_header(g.dump(w))
    compressed_hash = hashlib.sha256(result).hexdigest()
    content_hash = hashlib.sha256(gzip.decompress(result)).hexdigest()
    assert compressed_hash == recipe['output_sha256'], 'frozen compressed word'
    assert content_hash == recipe['output_uncompressed_sha256'], 'frozen content'
    receipt = dict(status='PASS_FROZEN_RANK4_REPLAY',
                   source_sha256=recipe['source_sha256'],
                   recipe_sha256=hashlib.sha256(a.recipe.read_bytes()).hexdigest(),
                   output_sha256=compressed_hash,
                   output_uncompressed_sha256=content_hash,
                   local_profile=dict(sorted(H.items())),
                   width_inventory=dict(sorted(Counter(widths).items())),
                   local_rank_mass=mass, entrance_rank=rank,
                   independent_scalar_replay_performed=False,
                   scope='Exact frozen relations, native frame/profile replay and byte-identical reconstruction only; the separate selected-word receipt supplies the independent scalar audit.')
    a.out.mkdir(parents=True,exist_ok=False)
    (a.out/'FULL-WORD.json.gz').write_bytes(result)
    (a.out/'REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True))


if __name__ == '__main__':
    main()
