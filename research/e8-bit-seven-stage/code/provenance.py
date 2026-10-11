"""Check that every file listed as inherited unchanged from PR #370 (the E8 bit word) or PR #363 (the seven-stage E8
complex unit) has the git blob id recorded in SOURCE-pr370.json / SOURCE-pr363.json (compare with
`git ls-tree -r <commit> -- <source_root>`)."""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def blob(rel):
    b = open(os.path.join(HERE, rel), 'rb').read(); return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()
for name in ('SOURCE-pr370.json', 'SOURCE-pr363.json'):
    src = json.load(open(os.path.join(HERE, name)))
    bad = [rel for rel, want in src['identical'].items() if blob(rel) != want]
    if bad: sys.exit('files differ from %s at %s: %s' % (src['source'], src['commit'][:7], bad))
    print('   %d files byte-identical to %s at %s (git blob ids); %d edited' % (
        len(src['identical']), src['source'].replace('https://github.com/CrocSwap/integer-mult-bounds/pull/', 'PR #'), src['commit'][:7], len(src['changed'])))
