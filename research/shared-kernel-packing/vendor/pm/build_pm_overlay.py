# SPDX-License-Identifier: Apache-2.0
"""Compose the declared preload-move stage onto the derived PR2857 four-kernel source overlay.

Preload re-synthesis by Jeremy Kothe (jeremykothe2), with AI assistance, on the PR2857
(Lyy-iiis) overlay builder, which is run unchanged first. This tool copies the derived overlay
to a fresh directory, ships the PR2857 shared-kernel words as the audited parent state,
replaces the supplier words by the preload-move words, makes the source chain
rebuild them from the declared patch inputs, and adds the independent reviewer to verify.py.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, gzip, hashlib, json, shutil, types
SHARED_MANIFEST = '54dc42f25c1d8b85adcf593c4bf6c0f83f7351388af857812790b8a0b4c3d869'
SHARED_FILES = 547
PINS = {'preload_move.py': 'c8fda4674644fcd5cbf39b6645ce148a21daa90a998b678cbe51f970b78b0044',
        'preload_move_review.py': 'cf9f2f8d2b4f04a9e9bd6b7cd1aa777fa3f352b6a7fa97e3fd210b2c2ce2fb72',
        'patch-base.json': 'a7424d157e6df5c11a182d16253b3d9da84df1c17bb6db303f8d4e15095ef644',
        'patch-extra.json': '1979934ed1c75f6789f37fabe9addf674fa367ff18b7cab4dd0442efe8d547df',
        'words/WORD-PM-base.json.gz': 'c20a470aec0f3e61833cb41fe190639eb358f58017143d2336c55c80fba265eb',
        'words/WORD-PM-extra.json.gz': 'db34e39876241087b581ed9374c53e9cd393e3e86ef6103bfb54f3077c3d2761'}
def need(ok, why):
    if not ok: raise ValueError(why)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    p = Path(p); b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
def write(p, v): p.write_text(json.dumps(v, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')
def tree(p):
    need(not list(p.rglob('__pycache__')) and not list(p.rglob('*.pyc')), 'no source bytecode or cache folders')
    out = {}
    for f in sorted(p.rglob('*')):
        need(not f.is_symlink(), 'no source symlinks')
        if f.is_file() and f != p / 'MANIFEST.json': out[f.relative_to(p).as_posix()] = sha(f)
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--overlay', type=Path, required=True); ap.add_argument('--pm-dir', type=Path, required=True); ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    need(not sys.flags.optimize, 'assertions required'); src = a.overlay.resolve(); pm = a.pm_dir.resolve(); out = a.out.resolve()
    need(sha(src / 'MANIFEST.json') == SHARED_MANIFEST and len(read(src / 'MANIFEST.json')) == SHARED_FILES and tree(src) == read(src / 'MANIFEST.json'), 'exact PR2857 four-kernel overlay')
    need(all(sha(pm / n) == h for n, h in PINS.items()), 'pinned preload-move inputs')
    need(not out.exists() and not out.is_relative_to(src) and not src.is_relative_to(out), 'fresh external output')
    shutil.copytree(src, out)
    mod = types.ModuleType('preload_move'); exec(compile((pm / 'preload_move.py').read_bytes(), 'preload_move.py', 'exec'), mod.__dict__)
    providers = read(out / 'new/BORROW-PROVIDERS.json'); aud = types.ModuleType('independent_frames'); ap_ = out / 'new/borrow/audit_local.py'; exec(compile(ap_.read_bytes(), str(ap_), 'exec'), aud.__dict__)
    records = {}
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        shared_path = out / ('new/borrow/words/BORROW-WORD-43' + tag + '.json.gz'); shared = read(shared_path); patch = read(pm / ('patch-' + tag + '.json')); target = pm / 'words' / ('WORD-PM-' + tag + '.json.gz'); new = read(target)
        derived, ledger = mod.apply(shared, patch); need(derived == new, 'complete declared-stage reconstruction ' + tag)
        need(new['report']['local_profile'] == {'1': 2404, '2': 642, '3': 262, '4': 128, '5': 26, '8': 8} and new['report']['width_inventory'] == {'4': 26, '5': 2, '7': 62, '8': 86, '9': 232}, 'complete paid profile and helper inventory')
        live = sorted(set(range(224, 704)) - set(new['removed'])); need(len(live) == 408, 'unchanged helper identities')
        widths = []
        for r in live:
            end = aud.basis(new['helper_final'].get(str(r), [256, 128, 64, 32, 16, 8, 4, 2, 1])); start = aud.basis(new['start_extra'].get(str(r), [])); widths.append(len(end) - len(start))
        providers[pid] = dict(widths=widths, actual_paid_profile=new['report']['local_profile'])
        shutil.copy2(shared_path, out / ('new/borrow/inputs/SHARED-WORD-' + tag + '.json.gz')); shutil.copy2(target, shared_path)
        write(out / ('new/borrow/inputs/preload_move_43' + tag + '.json'), patch)
        records[tag] = dict(shared_word_sha256=sha(out / ('new/borrow/inputs/SHARED-WORD-' + tag + '.json.gz')), candidate_word_sha256=sha(shared_path), patch_sha256=sha(out / ('new/borrow/inputs/preload_move_43' + tag + '.json')), ledger=ledger)
    shutil.copy2(pm / 'preload_move.py', out / 'new/borrow/preload_move.py'); shutil.copy2(pm / 'preload_move_review.py', out / 'new/borrow/preload_move_review.py'); write(out / 'new/BORROW-PROVIDERS.json', providers)
    patches = []
    def patch(name, old, new):
        p = out / name; before = sha(p); body = p.read_text(encoding='utf-8'); need(body.count(old) == 1, 'exact overlay preimage ' + name)
        p.write_text(body.replace(old, new), encoding='utf-8', newline='\n'); patches.append(dict(path=name, before_sha256=before, after_sha256=sha(p), old=old, new=new))
    anchor = "        chain.append(shared_word);steps.append('shared-four-kernel')\n"
    block = anchor + '''    # Declared preload-move stage: two more staged quartets, after the four-kernel stage.
    pm_f=D/'inputs'/f'preload_move_43{wt}.json'
    if pm_f.exists():
        import preload_move
        pm_patch=json.loads(pm_f.read_text());previous_pm=chain[-1]
        canonical_pm=lambda z:hashlib.sha256(json.dumps(z,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert canonical_pm(previous_pm)==pm_patch['source_canonical_sha256']
        pm_word,pm_ledger=preload_move.apply(previous_pm,pm_patch)
        assert canonical_pm(pm_word)==pm_patch['candidate_canonical_sha256']
        assert set(k_ for k_ in previous_pm if previous_pm[k_]!=pm_word[k_])<={'A','B','compensation','start_extra','report','cleanup'}
        chain.append(pm_word);steps.append('preload-move')
'''
    patch('new/rebuild_borrow.py', anchor, block)
    old_review = "run('shared-kernel-independent-review',P/'new/borrow/shared_kernel_review.py','--source-dir',P/'new/borrow','--source-base',P/'new/borrow/inputs/PR2833-WORD-base.json.gz','--source-extra',P/'new/borrow/inputs/PR2833-WORD-extra.json.gz','--candidate-base',P/'new/borrow/words/BORROW-WORD-43base.json.gz','--candidate-extra',P/'new/borrow/words/BORROW-WORD-43extra.json.gz','--out-dir',work/'shared-kernel-independent-review')"
    new_review = old_review.replace("P/'new/borrow/words/BORROW-WORD-43base.json.gz'", "P/'new/borrow/inputs/SHARED-WORD-base.json.gz'").replace("P/'new/borrow/words/BORROW-WORD-43extra.json.gz'", "P/'new/borrow/inputs/SHARED-WORD-extra.json.gz'") + "\nrun('preload-move-independent-review',P/'new/borrow/preload_move_review.py','--source-dir',P/'new/borrow','--shared-base',P/'new/borrow/inputs/SHARED-WORD-base.json.gz','--shared-extra',P/'new/borrow/inputs/SHARED-WORD-extra.json.gz','--candidate-base',P/'new/borrow/words/BORROW-WORD-43base.json.gz','--candidate-extra',P/'new/borrow/words/BORROW-WORD-43extra.json.gz','--patch-base',P/'new/borrow/inputs/preload_move_43base.json','--patch-extra',P/'new/borrow/inputs/preload_move_43extra.json','--out-dir',work/'preload-move-independent-review')"
    patch('verify.py', old_review, new_review)
    before = read(src / 'MANIFEST.json'); after = tree(out); write(out / 'MANIFEST.json', after)
    change = {p: dict(before_sha256=before.get(p), after_sha256=after.get(p)) for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)}
    expected = {'new/borrow/words/BORROW-WORD-43base.json.gz', 'new/borrow/words/BORROW-WORD-43extra.json.gz', 'new/borrow/inputs/SHARED-WORD-base.json.gz', 'new/borrow/inputs/SHARED-WORD-extra.json.gz', 'new/borrow/inputs/preload_move_43base.json', 'new/borrow/inputs/preload_move_43extra.json', 'new/borrow/preload_move.py', 'new/borrow/preload_move_review.py', 'new/BORROW-PROVIDERS.json', 'new/rebuild_borrow.py', 'verify.py'}
    need(set(change) == expected, 'exact overlay change allowlist'); need(tree(src) == before, 'four-kernel overlay stayed byte-exact')
    receipt = dict(status='PASS_SOURCE_BOUND_PRELOAD_MOVE_OVERLAY_DERIVATION', parent_manifest_sha256=SHARED_MANIFEST, derived_manifest_sha256=sha(out / 'MANIFEST.json'), source_file_count=len(after), builder_sha256=sha(Path(__file__)), changes=change, patches=patches, words=records, pins=PINS,
                   scope='Exact source overlay construction only. The declared stage is rebuilt by the source chain; native, owner, controller and outer admission and every inherited validator remain separate.')
    write(out.parent / (out.name + '-DERIVATION.json'), receipt); print(json.dumps({k: receipt[k] for k in ['status', 'derived_manifest_sha256', 'source_file_count']}, sort_keys=True))
if __name__ == '__main__': main()
