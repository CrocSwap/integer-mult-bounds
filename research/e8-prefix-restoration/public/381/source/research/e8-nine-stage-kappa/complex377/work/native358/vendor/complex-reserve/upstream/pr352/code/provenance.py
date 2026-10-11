"""Check that every file this package lists as inherited unchanged from PR #346 has the git blob id recorded in
SOURCE-pr346.json (the ids are those of PR #346's tree at the recorded commit; a reviewer can compare them with
`git ls-tree -r <commit> -- research/w3-p10b-complex-p10`). No network or git checkout of PR #346 is needed."""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = json.load(open(os.path.join(HERE, 'SOURCE-pr346.json')))
bad = []
for rel, want in src['identical'].items():
    b = open(os.path.join(HERE, rel), 'rb').read()
    if hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest() != want:
        bad.append(rel)
if bad:
    sys.exit('files differ from PR #346 at %s: %s' % (src['commit'][:7], bad))
print('   %d files byte-identical to PR #346 at %s (git blob ids); %d edited, %d not carried over'
      % (len(src['identical']), src['commit'][:7], len(src['changed']), len(src['removed'])))
