#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Append the declared literal edit-list stage (edits/EDITS.json: R1_E42, R2_E7, B_586_438, B_588_440) to PR2979's rank-7 overlay source.

Edits R1_E42, R2_E7, B_586_438 and B_588_440 by dcharb78, with AI assistance, extending Stack2979 / Jeremy Kothe's (jeremykothe2, PR3015)
declared edit stage on PR2979's words (mdumitrean). Overlay/rebuild conventions are credited to PR2979/PR2942 (mdumitrean),
PR2908 (jeremydiviney) and PR2917 (mason-hale).
"""
import argparse, gzip, hashlib, json, shutil
from pathlib import Path

PARENT = '751b46364742cbb947f7db07c130ff09085b38b52c520d3b47f2dadc1e21ba80'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
def save(p, x): p.write_text(json.dumps(x, indent=2, sort_keys=True) + '\n')
def tree(p):
    assert not any(f.is_symlink() for f in p.rglob('*'))
    return {f.relative_to(p).as_posix(): sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f != p / 'MANIFEST.json'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--local-package', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    src, out, p = a.source.resolve(), a.out.resolve(), a.local_package.resolve()
    assert __debug__ and not out.exists() and not out.is_relative_to(src)
    assert sha(src / 'MANIFEST.json') == PARENT and tree(src) == read(src / 'MANIFEST.json')
    pins = read(p / 'EDIT-PINS.json')
    assert all(sha(p / n) == h for n, h in pins.items())
    shutil.copytree(src, out)
    local = out / 'new/borrow/edits'
    local.mkdir()
    shutil.copy2(p / 'edits/EDITS.json', local / 'EDITS.json')
    shutil.copy2(p / 'edits/declared_edits.py', out / 'new/borrow/declared_edits.py')
    shutil.copy2(p / 'edits/edits_review.py', out / 'new/borrow/edits_review.py')
    providers = read(src / 'new/BORROW-PROVIDERS.json')
    records = {}
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        q = out / f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'
        assert read(q) == read(p / f'data/WORD-{tag}.json.gz'), 'source word is the PR2979 word'
        shutil.copy2(q, out / f'new/borrow/inputs/RANK7-WORD-{tag}.json.gz')
        shutil.copy2(p / f'edits/FINAL-WORD-{tag}.json.gz', q)
        word = read(q)
        providers[pid]['widths'] = [len(word['helper_final'].get(str(h), [0] * 9)) - len(word['start_extra'].get(str(h), []))
                                    for h in sorted(set(range(224, 704)) - set(word['removed']))]
        providers[pid]['actual_paid_profile'] = word['report']['local_profile']
        records[tag] = {'parent_sha256': sha(p / f'data/WORD-{tag}.json.gz'), 'word_sha256': sha(q)}
    save(out / 'new/BORROW-PROVIDERS.json', providers)
    path = out / 'new/rebuild_borrow.py'
    text = path.read_text()
    anchor = "    final=json.loads(gzip.decompress(shipped.read_bytes()))"
    assert text.count(anchor) == 1
    block = """    # Declared literal edit list on PR2979's word (R1_E42, R2_E7, B_586_438, B_588_440); compensation, cut, start_extra, removed and private buffer count are unchanged.
    import declared_edits
    edit_parent=json.loads(gzip.decompress((D/'inputs'/f'RANK7-WORD-{wt}.json.gz').read_bytes()))
    assert chain[-1]==edit_parent
    edit_word,_=declared_edits.apply(chain[-1],json.loads((D/'edits/EDITS.json').read_text())['edits'][wt],json.loads((D/'edits/EDITS.json').read_text())['declared'])
    chain.append(edit_word);steps.append('declared-edit-list')
"""
    path.write_text(text.replace(anchor, block + anchor))
    path = out / 'verify.py'
    text = path.read_text()
    line = next(s for s in text.splitlines() if s.startswith("run('paired-extension-review'"))
    assert text.count(line) == 1
    review = ("run('declared-edit-review',P/'new/borrow/edits_review.py','--source-dir',P/'new/borrow',"
              "'--parent-base',P/'new/borrow/inputs/RANK7-WORD-base.json.gz','--parent-extra',P/'new/borrow/inputs/RANK7-WORD-extra.json.gz',"
              "'--candidate-base',P/'new/borrow/words/BORROW-WORD-43base.json.gz','--candidate-extra',P/'new/borrow/words/BORROW-WORD-43extra.json.gz',"
              "'--edits',P/'new/borrow/edits/EDITS.json','--out-dir',work/'declared-edit-review')")
    path.write_text(text.replace(line, line + "\n" + review))
    before, after = tree(src), tree(out)
    changes = {n: {'before': before.get(n), 'after': after.get(n)} for n in set(before) | set(after) if before.get(n) != after.get(n)}
    expected = {'new/BORROW-PROVIDERS.json', 'new/rebuild_borrow.py', 'verify.py', 'new/borrow/declared_edits.py', 'new/borrow/edits_review.py', 'new/borrow/edits/EDITS.json'}
    expected |= {f'new/borrow/words/BORROW-WORD-43{tag}.json.gz' for tag in ('base', 'extra')}
    expected |= {f'new/borrow/inputs/RANK7-WORD-{tag}.json.gz' for tag in ('base', 'extra')}
    assert set(changes) == expected and tree(src) == before
    save(out / 'MANIFEST.json', after)
    result = {'status': 'PASS_SOURCE_BOUND_DECLARED_EDIT_OVERLAY', 'parent_manifest_sha256': PARENT, 'manifest_sha256': sha(out / 'MANIFEST.json'),
              'source_file_count': len(after), 'changes': changes, 'words': records, 'builder_sha256': sha(Path(__file__))}
    save(out.parent / (out.name + '-DERIVATION.json'), result)
    print(result['status'], result['manifest_sha256'], len(after), flush=True)


if __name__ == '__main__':
    main()
