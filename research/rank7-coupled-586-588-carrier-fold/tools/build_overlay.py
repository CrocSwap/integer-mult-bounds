# SPDX-License-Identifier: Apache-2.0
"""Build a source-bound overlay for a literal word edit on top of PR2917's derived source (manifest 98d57c82..., 632 files).
Stage '<stage>' (default rank7-joint-endframes): new/borrow/inputs/wordedit_43{base,extra}.json (exact spec PR2917 word -> candidate
word) applied by new/borrow/wordedit.py (pure producer, re-derives cleanup from helper_final). The shipped words must equal
apply_spec(previous, spec) exactly. Allowed changed sections: warps (B positions only; lender, frames and count fixed), A, B, restore,
compensation, start_extra, report, cleanup, initial_corrections, helper_final (new restored endpoints = extra private buffers; every
inherited endpoint retained or lowered to a subspace of its old end frame); removed is fixed (408 live helpers). The same guards are
patched into the source's own rebuild chain (new/rebuild_borrow.py), which the admission release reruns.
Overlay/rebuild conventions follow Jeremy Diviney's PR2908 builder and Mason Hale's PR2917 build_extension.py; generalized from our
PR2942 tools/build_overlay.py. Marius-Paul Dumitrean, with substantial AI assistance (Claude Code).
Usage: build_overlay.py --source PR2917_DERIVED_SOURCE --candidate-dir DIR_WITH_WORD-{base,extra}.json.gz --out OUT [--stage-name NAME]
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter
import argparse, gzip, hashlib, json, shutil, types
UPSTREAM_MANIFEST = '98d57c82a1c7318be3c330c3b66897844d57232f0aaeaea88fb4bebd0a1bedf1'   # PR2917 derived overlay (632 files)
UPSTREAM_FILES = 632
ALLOWED = {'warps', 'A', 'B', 'restore', 'compensation', 'start_extra', 'report', 'cleanup', 'initial_corrections', 'helper_final'}
def need(ok, why):
    if not ok: raise ValueError(why)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sem(v): return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def read(p):
    p = Path(p); b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
def write(p, v): p.write_text(json.dumps(v, sort_keys=True, indent=2) + '\n')
def tree(p):
    need(not list(p.rglob('__pycache__')) and not list(p.rglob('*.pyc')), 'no source bytecode or cache folders')
    out = {}
    for f in sorted(p.rglob('*')):
        need(not f.is_symlink(), 'no source symlinks')
        if f.is_file() and f != p / 'MANIFEST.json': out[f.relative_to(p).as_posix()] = sha(f)
    return out
def find_word(d, tag):
    c = [p for p in sorted(Path(d).glob('*.json.gz')) if p.name.endswith('-' + tag + '.json.gz') or p.name == f'WORD-{tag}.json.gz']
    need(len(c) == 1, f'exactly one candidate word for {tag} in {d}: {c}'); return c[0]
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--source', type=Path, required=True); ap.add_argument('--candidate-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True); ap.add_argument('--producer', type=Path, default=Path(__file__).resolve().parent / 'wordedit.py')
    ap.add_argument('--stage-name', default='rank7-joint-endframes'); a = ap.parse_args()
    need(not sys.flags.optimize, 'assertions required'); source = a.source.resolve(); out = a.out.resolve()
    need(sha(source / 'MANIFEST.json') == UPSTREAM_MANIFEST and tree(source) == read(source / 'MANIFEST.json') and len(read(source / 'MANIFEST.json')) == UPSTREAM_FILES, 'exact PR2917 derived overlay inventory')
    need(not out.exists() and not out.is_relative_to(source), 'fresh external overlay'); shutil.copytree(source, out)
    # producer module inside the overlay: plain import of word_patch from its own directory (new/borrow); no scratchpad paths
    prod = a.producer.read_text()
    head, sep, tail = prod.partition('try:\n    import word_patch as WP')
    need(sep, 'producer import block'); tail = tail.split('    import word_patch as WP\n', 1)[1]
    prod = head + 'import word_patch as WP  # PR2833 helpers (derive_cleanup), found next to this file inside the overlay\n' + tail
    need('/scratchpad/' not in prod and 'import word_patch as WP' in prod, 'producer path relocation'); compile(prod, 'wordedit.py', 'exec')
    (out / 'new/borrow/wordedit.py').write_text(prod); PRODUCER_SHA = sha(out / 'new/borrow/wordedit.py')
    sys.path.insert(0, str(out / 'new/borrow'))
    gen = types.ModuleType('wordedit'); gen.__file__ = str(out / 'new/borrow/wordedit.py'); exec(compile(prod, str(out / 'new/borrow/wordedit.py'), 'exec'), gen.__dict__)
    providers = read(source / 'new/BORROW-PROVIDERS.json'); records = {}; buffers = set()
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        src = source / ('new/borrow/words/BORROW-WORD-43' + tag + '.json.gz'); target = find_word(a.candidate_dir, tag); old = read(src); new = read(target)
        need(old != new, 'candidate word differs from the PR2917 word ' + tag)
        spec = gen.make_spec(old, new); derived = gen.apply_spec(old, spec)
        need(derived == new, 'complete producer reconstruction ' + tag)
        changed = set(k for k in old if old[k] != new[k]); need(changed <= ALLOWED, 'exact changed sections ' + str(changed))
        need(new['removed'] == old['removed'] and len(new['warps']) == len(old['warps']), 'removed set and warp count unchanged')
        need([x[1:] for x in new['warps']] == [x[1:] for x in old['warps']], 'warps: only their B positions may move')
        def _span(b):
            out = {0}
            for v in b: out |= {x ^ v for x in out}
            return out
        need(all(h in new['helper_final'] and _span(new['helper_final'][h]) <= _span(U) for h, U in old['helper_final'].items()), 'every inherited restored endpoint retained or LOWERED to a subspace')
        need(new['cleanup'] == gen.derive_cleanup(new), 'cleanup is the derived inverse of the word with buffers for every endpoint')
        live = sorted(set(range(224, 704)) - set(new['removed'])); need(len(live) == 408, 'unchanged helper identities')
        widths = [len(new['helper_final'].get(str(h), [0] * 9)) - len(new['start_extra'].get(str(h), [])) for h in live]
        need({str(k): v for k, v in Counter(widths).items()} == new['report']['width_inventory'], 'report inventory equals derived widths')
        buffers.add(len(new['helper_final']))
        providers[pid] = {'widths': widths, 'actual_paid_profile': new['report']['local_profile']}
        shutil.copy2(target, out / ('new/borrow/words/BORROW-WORD-43' + tag + '.json.gz'))
        shutil.copy2(src, out / ('new/borrow/inputs/PR2917-WORD-' + tag + '.json.gz'))
        rec = dict(stage=a.stage_name, source_word_sha256=sha(src), source_canonical_sha256=sem(old), candidate_word_sha256=sha(target), candidate_canonical_sha256=sem(new),
                   producer_sha256=PRODUCER_SHA, changed_sections=sorted(changed), buffers=len(new['helper_final']), spec=spec)
        write(out / ('new/borrow/inputs/wordedit_43' + tag + '.json'), rec); records[tag] = dict(rec, spec='(see file)')
    need(len(buffers) == 1, 'both providers charge the same private buffer count'); B = buffers.pop()
    write(out / 'new/BORROW-PROVIDERS.json', providers)
    patches = []
    def patch(name, old, new):
        p = out / name; before = sha(p); body = p.read_text(); need(body.count(old) == 1, 'exact overlay preimage ' + name); p.write_text(body.replace(old, new))
        patches.append(dict(path=name, before_sha256=before, after_sha256=sha(p), old=old, new=new))
    anchor = '    final=json.loads(gzip.decompress(shipped.read_bytes()))'
    block = '''    # Recorded exact word edit (here: rank-7 joint end frames, five paired extractions, fourteen declared rewrites); pure producer, cleanup re-derived from helper_final. Every previous state stays in the audit chain.
    we_=D/'inputs'/f'wordedit_43{wt}.json'
    if we_.exists():
        import wordedit
        we_patch=json.loads(we_.read_text());previous_we=chain[-1]
        canonical=lambda z:hashlib.sha256(json.dumps(z,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert canonical(previous_we)==we_patch['source_canonical_sha256']
        we_word=wordedit.apply_spec(previous_we,we_patch['spec'])
        assert canonical(we_word)==we_patch['candidate_canonical_sha256']
        assert set(k_ for k_ in previous_we if previous_we[k_]!=we_word[k_])<={'A','B','restore','compensation','start_extra','report','cleanup','initial_corrections','helper_final','warps'}
        assert [x_[1:] for x_ in we_word['warps']]==[x_[1:] for x_ in previous_we['warps']]   # warps: only their B positions may move
        assert we_word['cleanup']==wordedit.derive_cleanup(we_word)
        assert we_word['removed']==previous_we['removed'] and len(we_word['warps'])==len(previous_we['warps'])
        def _we_span(b_):
            o_={0}
            for v_ in b_: o_|={x_^v_ for x_ in o_}
            return o_
        assert all(h_ in we_word['helper_final'] and _we_span(we_word['helper_final'][h_])<=_we_span(U_) for h_,U_ in previous_we['helper_final'].items())
        assert len(we_word['helper_final'])==we_patch['buffers']
        chain.append(we_word);steps.append(we_patch['stage'])
''' + anchor
    patch('new/rebuild_borrow.py', anchor, block)
    # PR2917's and PR2908's independent reviews read their own data/ copies; the shared-kernel and preload-move reviews read inputs/ copies: no redirect needed.
    before = read(source / 'MANIFEST.json'); after = tree(out); write(out / 'MANIFEST.json', after)
    change = {p: dict(before_sha256=before.get(p), after_sha256=after.get(p)) for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)}
    expected = {'new/borrow/words/BORROW-WORD-43base.json.gz', 'new/borrow/words/BORROW-WORD-43extra.json.gz', 'new/borrow/inputs/PR2917-WORD-base.json.gz', 'new/borrow/inputs/PR2917-WORD-extra.json.gz',
                'new/borrow/inputs/wordedit_43base.json', 'new/borrow/inputs/wordedit_43extra.json', 'new/borrow/wordedit.py', 'new/rebuild_borrow.py'}
    optional = {'new/BORROW-PROVIDERS.json'}   # unchanged when the edit keeps every width and the local profile (same-cost word edit)
    need(expected <= set(change) <= expected | optional, 'exact overlay change allowlist ' + str(set(change) ^ expected)); need(tree(source) == before, 'original source remained byte-exact')
    receipt = dict(status='PASS_SOURCE_BOUND_WORDEDIT_OVERLAY_DERIVATION', stage=a.stage_name, upstream_manifest_sha256=UPSTREAM_MANIFEST, derived_manifest_sha256=sha(out / 'MANIFEST.json'),
                   source_file_count=len(after), buffers=B, builder_sha256=sha(Path(__file__)), producer_sha256=PRODUCER_SHA, changes=change, patches=patches, words=records)
    write(out.parent / (out.name + '-DERIVATION.json'), receipt); print(json.dumps({k: receipt[k] for k in ['status', 'derived_manifest_sha256', 'source_file_count', 'buffers']}, sort_keys=True))
if __name__ == '__main__': main()
