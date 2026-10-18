"""Assertion helper of verify.sh.  usage: expect.py LABEL LOG [--has REGEX]... [--count REGEX N]... [--absent REGEX]...
Prints one 'PASS LABEL  detail' or 'FAIL LABEL  reason' line.  Also FAILS if LOG.rc exists and is not 0 (the run itself failed)."""
import re, sys, os
label, log = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
txt = open(log, encoding='utf-8', errors='replace').read() if os.path.isfile(log) else None
bad = []
if txt is None:
    bad.append('missing log ' + os.path.basename(log))
else:
    rc = log[:-4] + '.rc' if log.endswith('.log') else None
    if rc and os.path.isfile(rc) and open(rc).read().strip() != '0':
        bad.append('run exited %s' % open(rc).read().strip())
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--has':
            if not re.search(args[i + 1], txt, re.M): bad.append('missing: ' + args[i + 1])
            i += 2
        elif a == '--absent':
            if re.search(args[i + 1], txt, re.M): bad.append('unexpected: ' + args[i + 1])
            i += 2
        elif a == '--count':
            n = len(re.findall(args[i + 1], txt, re.M))
            if n != int(args[i + 2]): bad.append('count of %r is %d, want %s' % (args[i + 1], n, args[i + 2]))
            i += 3
        else:
            bad.append('bad option ' + a); i += 1
if bad:
    print('FAIL %s  %s' % (label, '; '.join(bad))); sys.exit(1)
print('PASS %s' % label)
