"""interfaces.py: side-by-side comparison of the unchanged ancestor (PR1319 on PR1297's words) and the pivot-566 kernel,
from one completed replay_full.py work directory (standard library).

  native     every artifact of the lineage native chain for each provider word (gauge44, extra), ancestor vs kernel:
             identical bytes, identical payload, or the JSON keys that differ;
  interface  the call interface the T74 hosting consumes from a local word (ports, centres, register count, every
             helper's entrance and end frame and width), compared exactly;
  plan       PR1319's PLAN.json vs data/PLAN.json: every differing JSON path;
  hosting    the two strict T74 replays: the independent owner audit, controller audit, invoice and assembly receipts,
             field by field, and the hosted outputs by payload hash.
usage: python3 -B interfaces.py --work W [--out OUT.json]   (W from replay_full.py; reads W/INTERFACE-INPUTS.json)"""
import argparse, gzip, hashlib, json, sys
from pathlib import Path
if not __debug__:
    raise SystemExit('interfaces.py: run without -O / PYTHONOPTIMIZE (its assert statements are the checks)')
def raw(p): return Path(p).read_bytes()
def payload(p): b = raw(p); return gzip.decompress(b) if str(p).endswith('.gz') else b
def rd(p): return json.loads(payload(p))
def h(b): return hashlib.sha256(b).hexdigest()
def role_keys(x):
    """input hashes are keyed by absolute paths, which differ between the two runs: key them by role instead."""
    if isinstance(x, dict):
        def role(k):
            if not (isinstance(k, str) and k.startswith('/')): return k
            name = k.rsplit('/', 1)[-1]
            return ('extra:' if '/native-extra/' in k else 'gauge44:' if name == 'CANONICAL-WORD.json.gz' else '') + name
        return {role(k): role_keys(v) for k, v in x.items()}
    return [role_keys(v) for v in x] if isinstance(x, list) else x
def paths_differing(a, b, prefix='', out=None, limit=200):
    """JSON paths where a and b differ. Lists of equal length are compared entrywise; when more than 8 entries differ,
    the differing fields are aggregated as [*] with their entry counts."""
    out = [] if out is None else out
    if len(out) >= limit: return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b: out.append(prefix + str(k) + (' (only kernel)' if k not in a else ' (only ancestor)'))
            elif a[k] != b[k]: paths_differing(a[k], b[k], prefix + str(k) + '.', out, limit)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        idx = [i for i in range(len(a)) if a[i] != b[i]]
        if len(idx) > 8:
            count = {}
            for i in idx:
                for p in paths_differing(a[i], b[i], '', None, limit): count[p] = count.get(p, 0) + 1
            for p, n in sorted(count.items()): out.append(prefix.rstrip('.') + '[*]' + ('' if p == '(root)' else p if p.startswith(' (') else '.' + p) + f' ({n} of {len(a)} entries)')
        else:
            for i in idx: paths_differing(a[i], b[i], prefix + f'[{i}].', out, limit)
    elif isinstance(a, list) and isinstance(b, list): out.append(prefix.rstrip('.') + f' (lengths {len(a)} and {len(b)})')
    else: out.append(prefix.rstrip('.') or '(root)')
    return out
def compare_dir(A, B):
    names = sorted({p.name for p in Path(A).iterdir() if p.is_file()} | {p.name for p in Path(B).iterdir() if p.is_file()})
    res = {}
    for n in names:
        a, b = Path(A) / n, Path(B) / n
        if not a.exists() or not b.exists(): res[n] = 'only ' + ('kernel' if not a.exists() else 'ancestor'); continue
        if raw(a) == raw(b): res[n] = 'identical bytes'; continue
        if payload(a) == payload(b): res[n] = 'identical payload'; continue
        try: res[n] = dict(differs=paths_differing(role_keys(rd(a)), role_keys(rd(b)), limit=40))
        except ValueError: res[n] = dict(differs='non-JSON payload', ancestor_sha256=h(payload(a)), kernel_sha256=h(payload(b)))
    return res
def call_interface(local):
    """what the hosting reads from a native local word: ports, centres, R, and each helper's entrance/end frames."""
    c = rd(Path(local) / 'CANONICAL-WORD.json.gz'); V = 112; F = c['frames']
    helpers = range(2 * V, 2 * V + c['R'])
    return dict(ports=c['ports'], centers=c['centers'], R=c['R'],
                entrance_frames=[F[c['start'][r]] for r in helpers], end_frames=[F[c['final'][r]] for r in helpers],
                widths=[len(F[c['final'][r]]) - len(F[c['start'][r]]) for r in helpers])
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--work', type=Path, required=True); ap.add_argument('--out', type=Path); a = ap.parse_args()
    W = a.work.resolve(); I = json.loads((W / 'INTERFACE-INPUTS.json').read_text(encoding='utf-8')); out = dict(native={}, interface={})
    for pid in ('gauge44', 'extra'):
        A, B = Path(I['native']['ancestor'][pid]) / 'local', Path(I['native']['kernel'][pid]) / 'local'
        out['native'][pid] = compare_dir(A, B)
        ia, ib = call_interface(A), call_interface(B)
        out['interface'][pid] = dict(identical=ia == ib, helpers=ia['R'], ports=len(ia['ports']), centers=len(ia['centers']),
                                     width_inventory={str(w): ia['widths'].count(w) for w in sorted(set(ia['widths']))}, differing=paths_differing(ia, ib, limit=20))
    out['plan'] = paths_differing(rd(I['plan']['ancestor']), rd(I['plan']['kernel']))
    hosting = {}
    for name in ('RESULT.json', 'ASSEMBLY.json', 'INDEPENDENT.json', 'ADMISSION-CONTROLS.json', 'BIT-CONTROLS.json'):
        hosting[name] = paths_differing(role_keys(rd(Path(I['strict']['ancestor']) / name)), role_keys(rd(Path(I['strict']['kernel']) / name)), limit=60)
    for d in ('global/audit', 'global/hosted'):
        hosting[d] = compare_dir(Path(I['strict']['ancestor']) / d, Path(I['strict']['kernel']) / d)
    out['hosting'] = hosting
    ra, rb = rd(Path(I['strict']['ancestor']) / 'RESULT.json'), rd(Path(I['strict']['kernel']) / 'RESULT.json')
    keep = ('roles', 'calls', 'prefix_bits', 'charged_prefix_bits', 'physical_row_coefficient', 'row_limit', 'live', 'deficit', 'rank_mass', 'idle', 'width_inventories', 'provider_counts', 'controls_rejected')
    out['hosting_summary'] = {k: dict(ancestor=ra['independent'].get(k), kernel=rb['independent'].get(k), equal=ra['independent'].get(k) == rb['independent'].get(k)) for k in keep}
    out['kappa'] = dict(ancestor=ra['kappa'], kernel=rb['kappa'])
    out['call_interfaces_identical'] = all(x['identical'] for x in out['interface'].values())
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if a.out: a.out.write_text(text, encoding='utf-8', newline='\n')
    print(json.dumps(dict(call_interfaces_identical=out['call_interfaces_identical'], hosting_summary={k: v['equal'] for k, v in out['hosting_summary'].items()}, kappa=out['kappa']), indent=1))
    sys.exit(0 if out['call_interfaces_identical'] else 1)
