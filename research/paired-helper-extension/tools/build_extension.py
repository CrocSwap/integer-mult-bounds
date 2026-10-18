#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Append the declared nine-extraction stage to immutable PR2908 source.

Overlay/rebuild conventions are credited to Jeremy Diviney's PR2908 builder.
"""
import argparse
import gzip
import hashlib
import json
import shutil
from pathlib import Path

PARENT = '56cf455752722051d598a7da1e5ee700637fbaef09189f534413dbe6e0525a83'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def save(p, x):
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + '\n')


def tree(p):
    assert not any(f.is_symlink() for f in p.rglob('*'))
    return {f.relative_to(p).as_posix(): sha(f) for f in sorted(p.rglob('*'))
            if f.is_file() and f != p / 'MANIFEST.json'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--local-package', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    src, out, p = a.source.resolve(), a.out.resolve(), a.local_package.resolve()
    assert __debug__ and not out.exists() and not out.is_relative_to(src)
    assert sha(src / 'MANIFEST.json') == PARENT and tree(src) == read(src / 'MANIFEST.json')
    pins = read(p / 'PINS.json')
    assert all(sha(p / n) == h for n, h in pins.items())
    shutil.copytree(src, out)
    local = out / 'new/borrow/paired-extension'
    local.mkdir()
    copied = ['PINS.json', 'verify.py', 'producer.py', 'structure.py', *pins]
    for n in copied:
        dest = local / n
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p / n, dest)
    shutil.copy2(p / 'producer.py', out / 'new/borrow/paired_extension.py')
    providers = read(src / 'new/BORROW-PROVIDERS.json')
    records = {}
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        q = out / f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'
        assert q.read_bytes() == (p / f'data/PARENT-{tag}.json.gz').read_bytes()
        shutil.copy2(q, out / f'new/borrow/inputs/CHANNEL408-WORD-{tag}.json.gz')
        shutil.copy2(p / f'data/WORD-{tag}.json.gz', q)
        word = read(q)
        helpers = sorted(set(range(224, 704)) - set(word['removed']))
        providers[pid] = {'widths': [len(word['helper_final'].get(str(h), [0] * 9)) -
                                    len(word['start_extra'].get(str(h), [])) for h in helpers],
                          'actual_paid_profile': word['report']['local_profile']}
        records[tag] = {'parent_sha256': sha(p / f'data/PARENT-{tag}.json.gz'), 'word_sha256': sha(q)}
    save(out / 'new/BORROW-PROVIDERS.json', providers)
    path = out / 'new/rebuild_borrow.py'
    text = path.read_text()
    anchor = '    final=json.loads(gzip.decompress(shipped.read_bytes()))'
    assert text.count(anchor) == 1
    block = """    # Nine additional paired directions; all82 cold buffers are charged.
    import paired_extension
    extension_parent=json.loads(gzip.decompress((D/'inputs'/f'CHANNEL408-WORD-{wt}.json.gz').read_bytes()))
    assert chain[-1]==extension_parent
    extension_transforms=[json.loads((D/'paired-extension/data'/f'TRANSFORM-{h}.json').read_text()) for h in paired_extension.HELPERS]
    extension_word=paired_extension.apply(chain[-1],extension_transforms)
    assert set(k_ for k_ in chain[-1] if chain[-1][k_]!=extension_word[k_])==paired_extension.ALLOWED
    chain.append(extension_word);steps.append('nine-additional-paired-extractions')
"""
    path.write_text(text.replace(anchor, block + anchor))
    path = out / 'verify.py'
    text = path.read_text()
    line = next(s for s in text.splitlines() if s.startswith("run('two-sided-helper408-review'"))
    assert text.count(line) == 1
    path.write_text(text.replace(line, line + "\nrun('paired-extension-review',P/'new/borrow/paired-extension/verify.py','--work',work/'paired-extension-review')"))
    before, after = tree(src), tree(out)
    changes = {n: {'before': before.get(n), 'after': after.get(n)} for n in set(before) | set(after)
               if before.get(n) != after.get(n)}
    expected = {'new/BORROW-PROVIDERS.json', 'new/rebuild_borrow.py', 'verify.py', 'new/borrow/paired_extension.py'}
    expected |= {f'new/borrow/words/BORROW-WORD-43{tag}.json.gz' for tag in ('base', 'extra')}
    expected |= {f'new/borrow/inputs/CHANNEL408-WORD-{tag}.json.gz' for tag in ('base', 'extra')}
    expected |= {'new/borrow/paired-extension/' + n for n in copied}
    assert set(changes) == expected and tree(src) == before
    save(out / 'MANIFEST.json', after)
    result = {'status': 'PASS_SOURCE_BOUND_PAIRED_EXTENSION_OVERLAY', 'parent_manifest_sha256': PARENT,
              'manifest_sha256': sha(out / 'MANIFEST.json'), 'source_file_count': len(after),
              'changes': changes, 'words': records, 'builder_sha256': sha(Path(__file__))}
    save(out.parent / (out.name + '-DERIVATION.json'), result)
    print(result['status'], result['manifest_sha256'], len(after), flush=True)


if __name__ == '__main__':
    main()
