"""Exact data installation and declared candidate-specific checker pins.

Apache-2.0. Marius-Paul Dumitrean with substantial OpenAI Codex assistance.
Target, centre and negative-control adaptations follow Mason Hale's PR2696.
The frozen predecessor packages are never edited.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil

CANDIDATE_MANIFEST = 'f9b8b8cbed9e55b32d821c50ab76fef0afb1466f29d11204254fb50d2533e680'
REFERENCE_HEAD = '5a42add713e09a8798a84d0be7a8276626d9e785'
TARGETS = {'23':[30], '34':[30], '50':[30], '108':[30],
           '14':[45], '41':[45], '43':[45], '52':[45],
           '78':[45], '99':[45], '104':[45], '106':[45]}
PROFILE = {'1':2370, '2':646, '3':297, '4':120, '5':26, '7':4, '8':4}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(candidate, reference):
    need(sha(candidate/'MANIFEST.json') == CANDIDATE_MANIFEST, 'Frozen combined input manifest')
    pins = read(candidate/'MANIFEST.json')
    actual = {p.relative_to(candidate).as_posix() for p in candidate.rglob('*')
              if p.is_file() and p.name != 'MANIFEST.json'}
    need(actual == set(pins), 'Exact combined input file set')
    for name, digest in pins.items():
        need(sha(candidate/name) == digest, 'Combined input: '+name)
    reference_pins = read(candidate/'PR2696-SOURCES.json')
    actual = {p.relative_to(reference).as_posix() for p in reference.rglob('*') if p.is_file()}
    need(actual == set(reference_pins) and len(reference_pins) == 100, 'Exact PR2696 file set')
    for name, digest in reference_pins.items():
        need(sha(reference/name) == digest, 'PR2696 source: '+name)
    return reference_pins


def install(package, candidate):
    """Install exact words/patches; adapt only three explicit candidate pins."""
    for tag in ('base', 'extra'):
        word = read(candidate/f'words/{tag}.json.gz')
        need(word['target_levels'] == TARGETS, 'Exact twelve-target map '+tag)
        need({str(k):v for k,v in word['report']['local_profile'].items()} == PROFILE,
             'Actual combined paid profile '+tag)
        shutil.copy2(candidate/f'words/{tag}.json.gz',
                     package/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz')
        for kind in ('alias8', 'prelife', 'refit563', 'alias1'):
            name = f'{kind}_43{tag}.json'
            shutil.copy2(candidate/'patches'/name, package/'new/borrow/inputs'/name)
    shutil.copy2(candidate/'PROVIDERS.json', package/'new/BORROW-PROVIDERS.json')
    changes = {}

    def replace(name, edits):
        path = package/name
        original = sha(path)
        # Preserve the frozen file's newline convention in the derivative.
        raw = path.read_bytes()
        ending = '\r\n' if b'\r\n' in raw else '\n'
        text = raw.decode().replace('\r\n', '\n')
        for before, after in edits:
            need(text.count(before) == 1, 'Unique adaptation boundary: '+name)
            text = text.replace(before, after)
        path.write_bytes(text.replace('\n', ending).encode())
        changes[name] = {'source_sha256':original, 'adapted_sha256':sha(path),
                         'replacements':[{'before':a, 'after':b} for a,b in edits]}

    replace('independent_core.py', [(
        "    require(set(levels) == {11,23,29,32,34,35,45,48,50,59,63,71,73,76,81,84,87,90,92,108}, 'twenty source-partner target offsets')\n"
        "    require(all(frames[f] in ((30,), (45,)) for f in levels.values()), 'target line30')",
        "    require({str(t): list(frames[f]) for t, f in levels.items()} == "+repr(TARGETS)+", 'candidate exact source-partner target frames')"), (
        "    require(Counter(e[4] for e in forward) == {1:8, 7:8}, 'sixteen centre children')",
        "    require(Counter(e[4] for e in forward) == {1:4, 7:4, 8:4}, 'candidate twelve centre children')")])
    replace('audit_mixed.py', [(
        "str(_e)=='target line30'",
        "str(_e)=='candidate exact source-partner target frames'")])
    replace('new/borrow/lowfour_controls.py', [(
        "    m=mut();m['A'][ia][1],m['A'][ia+1][1]=m['A'][ia+1][1],m['A'][ia][1];expect('prelude correction targets swapped',m)",
        "    # PR2696: choose distinct additions so the swap is not an identity.\n"
        "    jb=next(j for j,e in enumerate(pre) if e[0]=='add' and e[1]!=pre[ia][1] and e[2:]!=pre[ia][2:] and e[-1]==pre[ia][-1])\n"
        "    m=mut();m['A'][ia][1],m['A'][jb][1]=m['A'][jb][1],m['A'][ia][1];expect('prelude correction targets swapped',m)")])
    need(set(changes) == {'independent_core.py', 'audit_mixed.py',
                          'new/borrow/lowfour_controls.py'}, 'Declared checker adaptations only')
    return changes
