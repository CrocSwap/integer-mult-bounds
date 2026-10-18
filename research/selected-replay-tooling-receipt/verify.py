#!/usr/bin/env python3
"""Check the selected-replay tooling overlap receipt (stdlib only).

Default mode checks the main-side facts at the receipt's base commit. With
--heads it also recomputes every per-PR fact from the exact PR head objects,
which must already be in the local object store (see README for the fetch).

Josie Elliston's donated session with Claude Code. Apache-2.0.
"""
import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]


def fail(msg):
    print('FAIL_SELECTED_REPLAY_TOOLING_RECEIPT:', msg)
    sys.exit(1)


def require(cond, msg):
    if not cond:
        fail(msg)


def git(*args, check=True):
    r = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True)
    if check and r.returncode:
        fail('git %s: %s' % (' '.join(args), r.stderr.decode(errors='replace').strip()))
    return r


def show(rev, path):
    return git('show', '%s:%s' % (rev, path)).stdout


def has_object(rev):
    return git('cat-file', '-e', rev + '^{commit}', check=False).returncode == 0


def blob(rev, path):
    r = git('rev-parse', '--verify', '-q', '%s:%s' % (rev, path), check=False)
    return r.stdout.decode().strip() if r.returncode == 0 else None


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main_side(rc):
    base = rc['base_commit']
    m = rc['main_facts']
    # Selected record moved to #1094; the #1042 record is retained as a checkpoint.
    sel = show(base, 'certificates/selected-result.json')
    ck = show(base, 'certificates/checkpoints/frontier1042.json')
    require(sha256(sel) == m['selected_record_sha256'], 'selected record differs at base')
    require(json.loads(sel)['decimal'] == m['selected_decimal'], 'selected decimal differs')
    require(sha256(ck) == m['frontier1042_checkpoint_sha256'], 'frontier1042 checkpoint differs')
    require(sha256(sel) != sha256(ck), 'selected record still equals the #1042 record')
    require(blob(base, 'certificates/checkpoints/frontier942.json') == m['frontier942_checkpoint_blob'],
            'frontier942 checkpoint blob differs')
    # Live files must equal the base for the default (registered) run.
    for p in ('certificates/selected-result.json', 'certificates/checkpoints/frontier1042.json'):
        require(sha256((ROOT / p).read_bytes()) == sha256(show(base, p)), 'live %s drifted from base' % p)
    # Cold chain 1094 -> 1042 -> 799 -> 741.
    for script, callee in m['cold_chain']:
        require(callee.encode() in show(base, script), '%s no longer runs %s' % (script, callee))
    # PR1277 premise: the --baseline1042 reuse path discards check_selected's result.
    # Every call of check_selected must be a bare statement on `ancestor`, i.e. its result unused.
    tree = ast.parse(show(base, 'scripts/verify_frontier1094.py'))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, 'id', None) == 'check_selected']
    bare = [n.value for n in ast.walk(tree) if isinstance(n, ast.Expr) and n.value in calls
            and getattr(n.value.args[0], 'id', None) == 'ancestor']
    require(len(calls) == len(bare) == m['bare_check_selected_statements'],
            'check_selected calls %d, bare on ancestor %d' % (len(calls), len(bare)))
    # PR1142's documented make target does not exist at base.
    mk = show(base, 'Makefile').decode()
    for tgt in m['absent_make_targets']:
        require(('\n%s:' % tgt) not in mk, 'make target %s now exists' % tgt)
    return ['base %s: selected %s, #1042 checkpoint retained, cold chain, PR1277 premise, '
            '%d absent make target(s)' % (base[:8], m['selected_decimal'], len(m['absent_make_targets']))]


def merge_tree(a, b):
    r = git('merge-tree', '--write-tree', '--name-only', a, b, check=False)
    lines = r.stdout.decode().splitlines()
    return r.returncode, lines[0] if lines else None, lines


def pr_facts(base, pr):
    head = pr['head']
    mb = git('merge-base', base, head).stdout.decode().strip()
    diff = git('diff', '--name-status', '--no-renames', mb, head).stdout.decode().splitlines()
    changed = sorted(tuple(x.split('\t', 1)) for x in diff)
    on_main_same = sorted(p for _, p in changed if blob(base, p) is not None and blob(base, p) == blob(head, p))
    on_main_diff = sorted(p for _, p in changed if blob(base, p) is not None and blob(base, p) != blob(head, p))
    code, _, _ = merge_tree(base, head)
    return {
        'changed': [list(c) for c in changed],
        'paths_identical_on_base': on_main_same,
        'paths_present_on_base_with_other_bytes': on_main_diff,
        'merges_cleanly_into_base': code == 0,
    }


def unexpected_shared(rc):
    c = rc['collision']
    owners = {}
    for pr in rc['prs']:
        for _, path in pr['changed']:
            owners.setdefault(path, []).append(pr['number'])
    return sorted(k for k, v in owners.items() if len(v) > 1
                  and not (k.startswith(c['path_prefix']) and v == [c['first'], c['second']]))


def heads(rc):
    base = rc['base_commit']
    missing = [str(p['number']) for p in rc['prs'] if not has_object(p['head'])]
    require(not missing, 'missing PR head objects for %s; fetch them as in README' % ', '.join(missing))
    out = []
    for pr in rc['prs']:
        got = pr_facts(base, pr)
        for k, v in got.items():
            require(pr[k] == v, 'PR%d %s: receipt %r, recomputed %r' % (pr['number'], k, pr[k], v))
        out.append('PR%d %s: %d paths, clean=%s, retained=%d'
                   % (pr['number'], pr['head'][:8], len(got['changed']),
                      got['merges_cleanly_into_base'], len(got['paths_identical_on_base'])))
    c = rc['collision']
    a, b = (next(p for p in rc['prs'] if p['number'] == n) for n in (c['first'], c['second']))
    # Both PRs add the same package directory with different bytes.
    # Apart from the recorded collision, no two family PRs change the same path.
    require(not unexpected_shared(rc), 'unexpected shared paths %r' % unexpected_shared(rc))
    bad = json.loads(json.dumps(rc))
    bad['prs'][0]['changed'].append(['A', bad['prs'][1]['changed'][0][1]])
    require(unexpected_shared(bad), 'control: injected shared path was accepted')
    pa = {p for _, p in map(tuple, a['changed']) if p.startswith(c['path_prefix'])}
    pb = {p for _, p in map(tuple, b['changed']) if p.startswith(c['path_prefix'])}
    require(pa == pb and len(pa) == c['paths'], 'collision path set differs')
    raw = sorted(p for p in pa if blob(a['head'], p) != blob(b['head'], p))
    lf = sorted(p for p in pa if show(a['head'], p).replace(b'\r\n', b'\n') != show(b['head'], p).replace(b'\r\n', b'\n'))
    require(raw == c['differ_raw'] and lf == c['differ_after_crlf_normalization'], 'collision bytes differ: %r %r' % (raw, lf))
    # The copy in the second PR pins selected-result.json to the #942 record blob.
    src = json.loads(show(b['head'], c['path_prefix'] + 'SOURCES.json').replace(b'\r\n', b'\n'))
    files = src.get('files', src)
    pinned = files['certificates/selected-result.json']['git_blob']
    require(pinned == c['second_pins_selected_result_blob'] == rc['main_facts']['frontier942_checkpoint_blob'],
            'second copy pin %s' % pinned)
    require(blob(base, 'certificates/selected-result.json') != pinned, 'base selected record equals #942 blob')
    # Merging the first then the second conflicts (add/add).
    t = git('merge-tree', '--write-tree', base, a['head']).stdout.decode().split()[0]
    mc = git('commit-tree', t, '-p', base, '-p', a['head'], '-m', 'receipt trial merge').stdout.decode().strip()
    code, _, lines = merge_tree(mc, b['head'])
    require(code == 1 and any('CONFLICT (add/add)' in x for x in lines), 'sequential merge did not conflict')
    # PR1142's capsule audit pins the #1042 record at the path that is now #1094's.
    p = rc['capsule_pin']
    pins = json.loads(show(b['head'], p['pins_file']))
    require(pins['selected_record']['path'] == p['pinned_path'], 'capsule pin path')
    require(pins['selected_record']['sha256'] == rc['main_facts']['frontier1042_checkpoint_sha256'], 'capsule pin sha')
    out.append('collision PR%d/PR%d: %d paths, %d differ raw, %d after CRLF normalization; '
               'sequential merge add/add conflict' % (c['first'], c['second'], len(pa), len(raw), len(lf)))
    return out


def controls(rc):
    """Each mutated receipt must be rejected by the base-side checks."""
    import copy
    import contextlib
    import io
    muts = {
        'selected decimal': ('selected_decimal', '0.001672188119205421'),
        'checkpoint sha': ('frontier1042_checkpoint_sha256', '0' * 64),
        'chain callee': ('cold_chain', [['scripts/verify_frontier1094.py', 'scripts/verify_frontier890.py']]),
        'PR1277 premise': ('bare_check_selected_statements', 0),
        'existing target': ('absent_make_targets', ['frontier1094-verify']),
    }
    for name, (key, value) in muts.items():
        bad = copy.deepcopy(rc)
        bad['main_facts'][key] = value
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                main_side(bad)
        except SystemExit:
            continue
        fail('control %r was accepted' % name)
    return ['%d receipt mutation controls rejected' % len(muts)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--heads', action='store_true', help='also recompute per-PR facts from fetched heads')
    a = ap.parse_args()
    if sys.flags.optimize:
        fail('run without -O')
    rc = json.loads((PKG / 'RECEIPT.json').read_text())
    lines = main_side(rc) + controls(rc)
    if a.heads:
        lines += heads(rc)
    for line in lines:
        print(line)
    print('PASS_SELECTED_REPLAY_TOOLING_RECEIPT', 'heads' if a.heads else 'base-only')


if __name__ == '__main__':
    main()
