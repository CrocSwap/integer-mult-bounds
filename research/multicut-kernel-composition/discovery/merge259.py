import json, sys, gzip
c259 = json.load(open(sys.argv[1])); mine = json.load(open(sys.argv[2]))['candidates']; free = {tuple(p) for p in json.load(open(sys.argv[3]))['free']}; OUT = sys.argv[4]
used = set()
for z in c259: used |= set(z['roles'])
added = []
for z in mine:
    if (z['a'], z['b']) not in free: continue
    assert z['a'] not in used and z['b'] not in used
    item = dict(pivot=z['a'], a=z['a'], roles=[z['a'], z['b']], partners=[z['b']], dim=1, E_dimension=1, basis=z['basis'], cut=676559, first_frames=[z['first_a'], z['first_b']], approx_slack_delta=z['approx_slack_delta'], kind='early-cut equal-response pair (u sum 0, norm %d)' % sum(int(x)**2 for x in z['basis'][0]), round='union-early-cut')
    added.append(item); used |= {z['a'], z['b']}
merged = c259 + added
S = sum(z['dim'] for z in merged); print('merged candidates', len(merged), 'added', len(added), 'entrance rank sum', S, 'mod 3 =', S % 3)
json.dump(merged, open(OUT, 'w'), indent=1); open(OUT + '.gz', 'wb').write(gzip.compress(json.dumps(merged, indent=1).encode(), mtime=0))
