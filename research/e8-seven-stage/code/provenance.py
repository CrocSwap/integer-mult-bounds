"""Check that every file listed as inherited unchanged from PR #352 has the git blob id recorded in SOURCE-pr352.json
(the ids of PR #352's tree at the recorded commit; compare with `git ls-tree -r <commit> -- research/w3-p10b-e8-complex`)."""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = json.load(open(os.path.join(HERE, 'SOURCE-pr352.json')))
bad = [rel for rel, want in src['identical'].items()
       if (lambda b: hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest())(open(os.path.join(HERE, rel), 'rb').read()) != want]
if bad: sys.exit('files differ from PR #352 at %s: %s' % (src['commit'][:7], bad))
print('   %d files byte-identical to PR #352 at %s (git blob ids); %d edited' % (len(src['identical']), src['commit'][:7], len(src['changed'])))
