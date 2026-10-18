"""usage: dfs_exhaustive.py LABEL LOG TL.  The orderings search (cards/B256/dfs.py) stops at its time limit and prints 'found []' either way, so a
'found []' line only counts when the search finished before the limit (time < TL): then the whole state space was visited."""
import re, sys, os
label, log, tl = sys.argv[1], sys.argv[2], float(sys.argv[3])
t = open(log, encoding='utf-8', errors='replace').read() if os.path.isfile(log) else ''
m = re.search(r"^found (\[.*?\]) deepest \[(\d+), .*\] seen (\d+) time ([0-9.]+)$", t, re.M)
rc = open(log[:-4] + '.rc').read().strip() if os.path.isfile(log[:-4] + '.rc') else '?'
if not m or rc != '0': print('FAIL %s  no result line or run exited %s' % (label, rc)); sys.exit(1)
found, deep, seen, secs = m.group(1), int(m.group(2)), int(m.group(3)), float(m.group(4))
if found != '[]': print('FAIL %s  an order was found: %s' % (label, found)); sys.exit(1)
if secs >= tl: print('FAIL %s  time limit reached (%.0fs): not exhaustive' % (label, secs)); sys.exit(1)
print('PASS %s  0 orders, exhaustive: %d states, deepest prefix %d ops' % (label, seen, deep))
