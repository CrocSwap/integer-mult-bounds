"""Check that every file listed as inherited unchanged in a SOURCE-pr*.json (PR #370's E8 bit word, PR #363's bridged.py,
PR #373 and PR #375's seven-stage checkers, PR #377's nine-stage complex component) has the git blob id recorded
there (compare with `git ls-tree -r <commit> -- <source_root>`; package paths carry the recorded prefix)."""
import glob, hashlib, json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def blob(rel):
    b = open(os.path.join(HERE, rel), 'rb').read(); return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()
for name in sorted(glob.glob(os.path.join(HERE, 'SOURCE-pr*.json'))):
    src = json.load(open(name))
    bad = [rel for rel, want in src['identical'].items() if blob(rel) != want]
    if bad: sys.exit('files differ from %s at %s: %s' % (src['source'], src['commit'][:7], bad))
    print('   %d files byte-identical to %s at %s (git blob ids); %d edited' % (
        len(src['identical']), src['source'].replace('https://github.com/CrocSwap/integer-mult-bounds/pull/', 'PR #'), src['commit'][:7], len(src['changed'])))
