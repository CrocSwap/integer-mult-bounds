import json, sys, gzip, collections
base = json.load(open(sys.argv[1])); cen = json.load(open(sys.argv[2])); half = json.load(open(sys.argv[3])); OUT = sys.argv[4]
used = {r for z in base for r in z['roles']}
chosen = sorted(cen['chosen'], key=lambda z: z['gain'])
# half-overlap free helpers
free_half = set()
for z in half:
    pass
S_base = sum(z['dim'] for z in base); items = []
for z in chosen:
    assert not any(h in used for h in z['members'])
    used |= set(z['members'])
    items.append(dict(pivot=z['pivot'], a=z['pivot'], roles=list(z['members']), partners=[h for h in z['members'] if h != z['pivot']], dim=z['e'], E_dimension=z['e'], basis=[[str(x) for x in r] for r in z['basis']], cut=z['cut'], approx_slack_delta=z['gain'], kind='%s, e=%d, residual census at cut %d (excluding 851 helpers)' % (z['kind'], z['e'], z['cut']), round='headroom-2'))
S = S_base + sum(z['dim'] for z in items)
while S % 3:
    for j in range(len(items)-1, -1, -1):
        if items[j]['dim'] == 1: print('drop weakest dim-1', items[j]['roles'], items[j]['approx_slack_delta']); S -= 1; items.pop(j); break
    else: raise SystemExit('cannot normalize mod 3')
merged = base + items
print('added', len(items), 'families; entrance rank', S, 'by cut', collections.Counter(z['cut'] for z in items), 'by e', collections.Counter(z['dim'] for z in items), 'gain', round(sum(z['approx_slack_delta'] for z in items), 2))
json.dump(merged, open(OUT, 'w'), indent=1); open(OUT + '.gz', 'wb').write(gzip.compress(json.dumps(merged, indent=1).encode(), mtime=0))
