#!/usr/bin/env python3
"""Derive the served bit word from PR200's frozen physical bit word (deterministic; standard library only).

A partner pair (carrier c, passive d) is mixed on its two source data registers at its 2-dim mix frame.
PR200's word also forms the same sum x_c + x_d in auxiliary registers: operation i = (a, b, n) with node n the
partner diagonal. When the destination a holds x_c and the control b is a pure copy of x_d (created by one copy
operation and used only at i), this patch

  * deletes b and its copy operation;
  * reads x_d at operation i from the passive data register instead of from b;
  * moves that pair's partner XOR to the start of the word (right after the injections), so the passive
    register's chain line -> mix -> F_i -> full stays ascending, where F_i is operation i's frame.

Every other operation, frame, gauge, pair, read, root and terminal sink is kept. Roles and operations are
renumbered compactly; read positions follow the removed operations. Usage:

    python3 patch.py PR200_PACKAGE_DIR OUT_DIR
"""
import gzip, json, sys
from collections import defaultdict
from pathlib import Path


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def dumps(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n'


def exact_subset(pkg):
    """PR200's own exact frame algebra (its retained PR168 v4 integer backend): sub(f, g) is f inside g."""
    sys.path.insert(0, str(pkg / 'bit'))
    import word as pr200_word
    cand = pr200_word.Candidate()
    return cand.C.sub


def patch(pkg):
    sel = pkg / 'selected/bit'
    g = read(sel / 'graph_p12.json')
    w = read(sel / 'word_p12.json')
    k = read(sel / 'kchron_p12.json')
    prof = read(sel / 'profile_p12.json')
    sub = exact_subset(pkg)
    v, args, ops = g['v'], g['args'], w['ops']
    R = prof['R']
    phase = set(w['phase1'])
    order = sorted(phase) + [i for i in range(len(ops)) if i not in phase]
    role_ops = defaultdict(list)
    for i in order:
        a, b, n = ops[i]
        role_ops[a].append(i)
        role_ops[b].append(i)
    sources = {int(x): s for x, s in w['sources'].items()}
    content = defaultdict(int)
    for x, s in sources.items():
        content[s] = 1 << x
    before = {}
    for i in order:
        a, b, n = ops[i]
        before[i] = (content[a], content[b])
        content[a] |= content[b]
    special = set(w['rootroles']) | {z['role'] for z in w['gauges']} | set(sources.values())
    special |= {x for p in w['pairs'] for x in p}
    entry = {}
    for e in k['entries']:
        entry[frozenset((e['carrier'], e['passive']))] = e
    served, dead_roles, dead_ops = {}, set(), set()
    for i, (a, b, n) in enumerate(ops):
        pair = args[n]
        if pair is None or len(pair) != 2 or not all(x < v for x in pair) or frozenset(pair) not in entry:
            continue
        e = entry[frozenset(pair)]
        c, d = e['carrier'], e['passive']
        ca, cb = before[i]
        if ca != 1 << c or cb != 1 << d or b in special:
            continue
        if len(role_ops[b]) != 2 or role_ops[b][1] != i:
            continue
        j = role_ops[b][0]
        ja, jb, jn = ops[j]
        if ja != b or args[jn] is not None or jn != d:
            continue
        if not sub(e['mix_frame'], w['op_frame'][i]):
            continue
        served[i] = dict(passive=d, carrier=c, frame=w['op_frame'][i])
        dead_roles.add(b)
        dead_ops.add(j)
    # compact renumbering of roles and operations
    keep_roles = [s for s in range(R) if s not in dead_roles]
    rmap = {s: t for t, s in enumerate(keep_roles)}
    keep_ops = [i for i in range(len(ops)) if i not in dead_ops]
    omap = {i: t for t, i in enumerate(keep_ops)}
    new_ops = []
    for i in keep_ops:
        a, b, n = ops[i]
        if i in served:
            new_ops.append([rmap[a], -1 - served[i]['passive'], n])     # negative control: passive data register
        else:
            new_ops.append([rmap[a], rmap[b], n])
    # execution positions: reads count positions in phase1 + rest order
    old_pos = {i: p for p, i in enumerate(order)}
    kept_before = []
    count = 0
    for i in order:
        kept_before.append(count)
        if i not in dead_ops:
            count += 1
    kept_before.append(count)
    nw = dict(w)
    nw['ops'] = new_ops
    nw['op_frame'] = [w['op_frame'][i] for i in keep_ops]
    nw['phase1'] = sorted(omap[i] for i in w['phase1'] if i not in dead_ops)
    nw['sources'] = {x: rmap[s] for x, s in w['sources'].items()}
    nw['rootroles'] = [rmap[s] for s in w['rootroles']]
    nw['gauges'] = [dict(z, role=rmap[z['role']]) for z in w['gauges']]
    nw['pairs'] = [[rmap[a], rmap[b]] for a, b in w['pairs']]
    nw['reads'] = {str(rmap[int(s)]): kept_before[p] for s, p in w['reads'].items()}
    nw['served'] = sorted([omap[i], z['passive'], z['frame']] for i, z in served.items())
    nw['served_schedule'] = ('served operation [i, d, F]: ops[i] = [a, -1-d, n] adds the passive source data register '
                             'x_d into a at frame F (op_frame[i]); that pair\'s partner XOR runs right after the '
                             'injections (kchron early), and the passive chain is line -> mix -> F -> full')
    nk = dict(k)
    nk['entries'] = []
    by_passive = {z['passive']: z for z in served.values()}
    for e in k['entries']:
        e = dict(e)
        z = by_passive.get(e['passive'])
        if z is not None:
            e['early'] = True
            line, mix, full = e['passive_chain']
            e['passive_chain'] = [line, mix, z['frame'], full]
            e['passive_ranks'] = None   # recomputed by the verifier from the exact frames
        nk['entries'].append(e)
    nprof = dict(prof)
    nprof['R'] = R - len(dead_roles)
    nprof['served_note'] = 'R counts logical roles after deleting the served pure-copy controls'
    return dict(word=nw, kchron=nk, profile=nprof, served=len(served), deleted_roles=len(dead_roles),
                deleted_ops=len(dead_ops))


def main():
    pkg, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    r = patch(pkg)
    (out / 'word_p12.json.gz').write_bytes(gzip.compress(dumps(r['word']).encode(), mtime=0))
    (out / 'kchron_p12.json').write_bytes(dumps(r['kchron']).encode())
    (out / 'profile_p12.json').write_bytes(dumps(r['profile']).encode())
    print(json.dumps(dict(served=r['served'], deleted_roles=r['deleted_roles'], deleted_ops=r['deleted_ops'])))


if __name__ == '__main__':
    main()
