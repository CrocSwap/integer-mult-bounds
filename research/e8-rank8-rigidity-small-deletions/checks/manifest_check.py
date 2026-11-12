# Step 0 of verify.sh: every line of MANIFEST.sha256 ("<sha256>  <relative path>") must match the file; the manifest must list every file of the package except itself.
import hashlib, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
listed = {}
for l in open(os.path.join(root, 'MANIFEST.sha256')):
    h, p = l.rstrip('\n').split('  ', 1); listed[p] = h
bad = [p for p, h in listed.items() if not os.path.isfile(os.path.join(root, p)) or hashlib.sha256(open(os.path.join(root, p), 'rb').read()).hexdigest() != h]
allf = {os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs if '__pycache__' not in d and f != 'MANIFEST.sha256' and not f.endswith('.pyc')}
extra = sorted(allf - set(listed))
print(('FAIL' if bad else 'PASS') + ' manifest: %d files hash-checked, %d mismatching %s' % (len(listed), len(bad), bad[:3]))
print(('FAIL' if extra else 'PASS') + ' manifest lists every package file (%d unlisted %s)' % (len(extra), extra[:3]))
sys.exit(1 if bad or extra else 0)
