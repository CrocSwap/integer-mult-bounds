"""Build the two-fusion word from #1148's joint-entrance word with a checked literal patch.

Standard library only. RECIPE.json pins the decompressed base payload and lists, for each list section of the word, the
operations of a sequence diff: [tag, base_start, base_end, [new elements]] with tag 'replace', 'delete' or 'insert', each
carrying the base elements it removes (checked before applying). Dictionary sections must be unchanged. The output payload
is pinned. The scalar meaning of the edits is described in PROOF.md.
usage: python -B build_word.py --base ../k8-joint-entrances/FULL-WORD.json.gz --out FULL-WORD.json.gz"""
import argparse, gzip, hashlib, json
from pathlib import Path
P = Path(__file__).resolve().parent
def apply_section(old, ops):
    out, pos = [], 0
    for tag, i1, i2, removed, added in ops:
        assert i1 >= pos and old[i1:i2] == removed, ('base mismatch', tag, i1, i2)
        out += old[pos:i1]; out += added; pos = i2
    return out + old[pos:]
def build(base, rc):
    w = json.loads(json.dumps(base))
    for sec, ops in rc['sections'].items(): w[sec] = apply_section(base[sec], ops)
    for k in rc['unchanged']: assert w[k] == base[k], ('unchanged section differs', k)
    w['report'] = rc['report']
    return w
if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', type=Path, default=P.parent / 'k8-joint-entrances/FULL-WORD.json.gz'); ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    raw = gzip.decompress(a.base.read_bytes()); rc = json.loads((P / 'RECIPE.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == rc['base_content_sha256'], 'base word pin'
    data = json.dumps(build(json.loads(raw), rc), separators=(',', ':')).encode()
    assert hashlib.sha256(data).hexdigest() == rc['output_content_sha256'], 'output word pin'
    a.out.write_bytes(gzip.compress(data, mtime=0)); print('PASS build', rc['output_content_sha256'][:16])
