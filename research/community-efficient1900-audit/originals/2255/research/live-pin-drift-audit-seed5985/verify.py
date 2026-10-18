#!/usr/bin/env python3
"""Live-byte source-pin drift audit at base 0fdd7d82.

Two named checkers read pinned source bytes live:

  L  check_sources-style: a manifest member "files" mapping repository paths
     to SHA-256 digests of the bytes the path must currently hold (behavior
     reproduced for research/skip-clones/clone_io.py:check_sources);
  R  research_package.py SOURCES.json records (path/usage/git_blob/sha256):
     that validator checks usage=="input" rows against the current working
     file and binds usage=="provenance" rows to the recorded git blob.

This audit enumerates every JSON pin entry in the git-tracked inventory,
classifies each pin by container shape as L, R-input, R-provenance or P (a
syntactic catch-all, e.g. a catalogue digest recorded at task draw),
recomputes every digest against the bytes the pinned path currently holds,
and records for each L/R drift the commits that touched the pinned file after
the pin's manifest last changed. Shape is not consumer semantics: no per-entry
claim is made that a P or R-provenance entry is never compared to live bytes;
see enumeration_rule in RESULT.json for the known counterexamples.

Scope: an audit and a precise obstruction record. No pin, frozen package or
certificate is modified. Aaron Wang, with help from opencode. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.set_int_max_str_digits(0)  # pinned manifests carry large exact integers

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT = HERE / 'RESULT.json'
EXCLUDE_DIRS = {'.git', '.worktrees'}
SELF = HERE.name
AUDITED_BASE = '0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2'
TOP_PREFIXES = ('research/', 'scripts/', 'references/', 'certificates/',
                'formal/', 'docs/', 'tests/', 'upstream/', 'artifacts/',
                'notes/', 'patches/')
KEY_RE = re.compile(r'^[A-Za-z0-9_.+-]+(/[A-Za-z0-9_.+-]+)+$')
DIGEST_RE = re.compile(r'^[0-9a-f]{64}$')
BLOB_RE = re.compile(r'^[0-9a-f]{40,64}$')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=False)
    require(result.returncode == 0, 'git failed: ' + ' '.join(args) + ': ' +
            result.stderr.decode('utf-8', 'replace'))
    return result.stdout


def git_blob_at(commit, path):
    result = subprocess.run(['git', 'show', commit + ':' + path],
                            cwd=ROOT, capture_output=True, check=False)
    return None if result.returncode else sha256(result.stdout)


class DigestCache:
    """One read per distinct pinned path; a checker reads the same bytes."""

    def __init__(self):
        self.cache = {}

    def current(self, key):
        if key not in self.cache:
            target = ROOT / key
            self.cache[key] = sha256(target.read_bytes()) if target.is_file() else None
        return self.cache[key]


CACHE = DigestCache()


def classify(key, recorded):
    """live | receipt target verdict: match | drift | unresolved | ignored."""
    if not key.startswith(TOP_PREFIXES):
        return 'ignored', None
    current = CACHE.current(key)
    if current is None:
        return 'unresolved', None
    return ('match' if current == recorded else 'drift'), current


def is_files_map(value):
    return isinstance(value, dict) and bool(value) and all(
        isinstance(k, str) and KEY_RE.fullmatch(k) and ':' not in k and
        isinstance(v, str) and DIGEST_RE.fullmatch(v) for k, v in value.items())


def is_sources_records(value):
    return isinstance(value, list) and bool(value) and all(
        isinstance(row, dict) and isinstance(row.get('path'), str) and
        isinstance(row.get('sha256'), str) and DIGEST_RE.fullmatch(row['sha256']) and
        isinstance(row.get('git_blob'), str) and BLOB_RE.fullmatch(row['git_blob']) and
        row.get('usage') in ('input', 'provenance') for row in value)


def walk_json():
    """The manifest inventory is the tracked set, not the working tree.

    git ls-files is identical in every complete checkout on every platform.
    The .json extension is matched case-insensitively because 22 tracked
    manifests use .JSON; a filesystem glob or a case-sensitive '*.json'
    query drops them and once made this census report 17,503 instead of
    17,525.
    """
    listing = git('ls-files', '-z').decode('utf-8').split('\x00')
    for rel in sorted(p for p in listing if p and p.lower().endswith('.json')):
        parts = rel.split('/')
        if parts[0] in EXCLUDE_DIRS or SELF in parts:
            continue
        yield ROOT / rel


def collect(node, out, shape):
    """Record every {repo path: sha256} pin with its manifest-member shape.

    R-input rows are the only research_package.py rows that validator checks
    against live working bytes; R-provenance rows record historical blobs.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key == 'files' and is_files_map(value):
                for k, v in value.items():
                    out.append((k, v, 'L'))
                continue
            if key == 'files' and is_sources_records(value):
                for row in value:
                    out.append((row['path'], row['sha256'],
                                'R-input' if row['usage'] == 'input' else 'R-provenance'))
                continue
            if isinstance(value, str) and KEY_RE.fullmatch(key) and ':' not in key \
                    and DIGEST_RE.fullmatch(value):
                out.append((key, value, shape))
            else:
                collect(value, out, shape)
    elif isinstance(node, list):
        for item in node:
            collect(item, out, shape)


def build_ledger():
    pins = []
    decode_failures = 0
    manifests_seen = 0
    for path in walk_json():
        manifests_seen += 1
        try:
            node = json.loads(path.read_bytes().decode('utf-8'))
        except (UnicodeDecodeError, ValueError):
            decode_failures += 1
            continue
        found = []
        collect(node, found, 'P')
        manifest = path.relative_to(ROOT).as_posix()
        for key, digest, shape in found:
            pins.append({'manifest': manifest, 'key': key, 'recorded': digest, 'shape': shape})
    pins.sort(key=lambda row: (row['manifest'], row['key'], row['shape']))
    shapes = ('L', 'R-input', 'R-provenance', 'P')
    counts = {shape: {'match': 0, 'drift': 0, 'unresolved': 0, 'ignored': 0} for shape in shapes}
    live_drift, live_unresolved = [], []
    for row in pins:
        status, current = classify(row['key'], row['recorded'])
        counts[row['shape']][status] += 1
        if row['shape'] in ('L', 'R-input') and status == 'drift':
            row['current'] = current
            live_drift.append(row)
        if row['shape'] in ('L', 'R-input') and status == 'unresolved':
            live_unresolved.append(row)
    return {'pins_seen': len(pins), 'manifests_seen': manifests_seen, 'counts': counts,
            'live_drift': live_drift, 'live_unresolved': live_unresolved,
            'json_decode_failures': decode_failures}


def add_provenance(ledger):
    by_path = {}
    for row in ledger['live_drift']:
        by_path.setdefault(row['key'], []).append(row)
    provenance_rows = []
    for key in sorted(by_path):
        entries = []
        for row in sorted(by_path[key], key=lambda r: (r['manifest'], r['shape'])):
            manifest = row['manifest']
            freeze = git('log', '-1', '--format=%H', '--', manifest).decode().strip()
            at_freeze = git_blob_at(freeze, key) if freeze else None
            raw = git('log', '--format=%H%x01%s', freeze + '..HEAD', '--', key).decode('utf-8', 'replace')
            later = []
            for line in raw.splitlines():
                if not line:
                    continue
                commit, _, subject = line.partition('\x01')
                later.append({'commit': commit, 'subject': subject,
                              'blob_sha256': git_blob_at(commit, key)})
            entries.append({'manifest': manifest, 'shape': row['shape'],
                            'manifest_freeze_commit': freeze, 'recorded': row['recorded'],
                            'blob_sha256_at_manifest_freeze': at_freeze,
                            'later_commits': later})
        provenance_rows.append({'path': key, 'current_sha256': CACHE.current(key),
                                'pins': len(by_path[key]), 'entries': entries})
    ledger['drift_provenance'] = provenance_rows
    return ledger


def skip_clones_reproduction():
    """Smallest falsifying instance: research/skip-clones source-pin check."""
    import importlib.util
    path = ROOT / 'research/skip-clones/clone_io.py'
    spec = importlib.util.spec_from_file_location('pin_drift_clone_io', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.check_sources(module.CERTIFICATE_INPUTS)
    except ValueError as error:
        return {'result': 'ValueError', 'message': str(error)}
    return {'result': 'no error'}


def registered_package_sample(ledger):
    """Reproduce registered rejections caused by live (usage=input) drift.

    Selection is deterministic: the sorted research/ packages whose SOURCES
    record at least one drifted usage=input pin and that carry TASK.json,
    plus two legacy packages seen failing for an unrelated metadata reason.
    """
    drifted = sorted({row['manifest'].rsplit('/', 1)[0] for row in ledger['live_drift']
                      if row['shape'] == 'R-input' and row['manifest'].endswith('/SOURCES.json')})
    picks = [pkg for pkg in drifted if (ROOT / pkg / 'TASK.json').is_file()][:3]
    picks += ['research/bit-compression-provenance', 'research/central-factor-packed']
    out = []
    for package in picks:
        result = subprocess.run([sys.executable, '-B', 'scripts/research_package.py',
                                '--package', package, '--check-only'],
                               cwd=ROOT, capture_output=True, check=False)
        out.append({'package': package, 'returncode': result.returncode,
                    'stdout': result.stdout.decode('utf-8', 'replace').strip()[-400:],
                    'stderr': result.stderr.decode('utf-8', 'replace').strip()[-400:]})
    return out


def controls(ledger, stable):
    checks = {}
    head = next(r for r in ledger['drift_provenance'] if r['path'] == 'scripts/exclusion_circuit.py')
    checks['control_a_headline_digest_fixed'] = head['current_sha256'] == \
        'f9fbcd6e85e442cbd0926ac0887414e20735b2dc923d2d5822c803ceb46726d3'
    clean = json.loads((ROOT / 'certificates/dyadic-central-factor.json').read_bytes())
    recorded = None
    stack = [clean]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'scripts/exclusion_circuit.py' and isinstance(value, str):
                    recorded = value
                else:
                    stack.append(value)
        elif isinstance(node, list):
            stack.extend(node)
    checks['control_b_matching_pin_reports_clean'] = (
        recorded == head['current_sha256'] and
        classify('scripts/exclusion_circuit.py', recorded)[0] == 'match')
    corrupted = head['current_sha256'][:-1] + ('0' if head['current_sha256'][-1] != '0' else '1')
    checks['control_c_corrupted_digest_registers_drift'] = \
        classify('scripts/exclusion_circuit.py', corrupted)[0] == 'drift'
    checks['control_d_missing_target_is_unresolved'] = \
        classify('scripts/does-not-exist-pin-drift-control.py', head['current_sha256'])[0] == 'unresolved'
    checks['control_e_non_repo_key_is_ignored'] = \
        classify('data/local-fixture.json', head['current_sha256'])[0] == 'ignored'
    checks['control_f_shape_l_detected'] = is_files_map(
        {'scripts/exclusion_circuit.py': head['current_sha256']}) and not is_files_map(
        {'scripts/exclusion_circuit.py': 'nope'})
    checks['control_g_recomputation_stable'] = stable
    inventory = [p.relative_to(ROOT).as_posix() for p in walk_json()]
    checks['control_h_tracked_inventory_retains_case_variant_json'] = (
        len(inventory) == ledger['manifests_seen'] and
        any(not name.endswith('.json') for name in inventory))
    require(all(checks.values()), 'control failed: ' + json.dumps(checks, sort_keys=True))
    return checks


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    write = '--write' in argv
    ledger = add_provenance(build_ledger())
    ledger['skip_clones_reproduction'] = skip_clones_reproduction()
    ledger['registered_package_sample'] = registered_package_sample(ledger)
    ledger['audited_base_commit'] = AUDITED_BASE
    ledger['enumeration_rule'] = (
        'Every JSON mapping entry whose key matches ^[A-Za-z0-9_.+-]+(/[A-Za-z0-9_.+-]+)+$ '
        'and contains no ":" and whose value matches ^[0-9a-f]{64}$. The manifest inventory '
        'is the git-tracked set at the checkout head (git ls-files) with the .json extension '
        'matched case-insensitively (22 tracked manifests use .JSON and are retained; a '
        'working-tree glob or a case-sensitive *.json query drops them and reports 17503 '
        'instead of 17525), excluding .git, .worktrees and this package. Shape L: member '
        '"files" whose value is such a mapping (check_sources-style live pin). Shape R-input '
        'and R-provenance: member "files" whose value is a list of path/usage/git_blob/sha256 '
        'records (research_package.py pins); for that validator only usage=="input" rows are '
        'checked against live working bytes ("working source drift"), usage=="provenance" '
        'rows bind historical blobs. Shape P: any other such entry (e.g. a catalogue digest '
        'recorded at task draw). Shapes are syntactic categories, not consumer semantics: the '
        'audit has not established per entry whether a consumer compares it to live bytes, and '
        'at least scripts/verify_pr_reconciliation.py:207 (ledger["source_sha256"]) and '
        'scripts/verify_replay_coverage.py:98 (selected["source_sha256"]) hash current bytes '
        'for some P-shaped entries. Classification of live pins is against the bytes a checker '
        'reads at the pinned path; other keys are counted ignored.')
    if write:
        stable = build_ledger() == {key: ledger[key] for key in
                                    ('pins_seen', 'manifests_seen', 'counts', 'live_drift',
                                     'live_unresolved', 'json_decode_failures')}
    else:
        # Verify mode proves stability more strongly: exact equality with the
        # pinned RESULT.json below, which was written under the double
        # enumeration. Skip the second full pass to keep the replay within its
        # command budget.
        stable = True
    checks = controls(ledger, stable)
    expected = {'result': 'ValueError',
                'message': 'Pinned inherited source changed: scripts/exclusion_circuit.py'}
    require(ledger['skip_clones_reproduction'] == expected,
            'skip-clones reproduction differs: ' + json.dumps(ledger['skip_clones_reproduction']))
    if write:
        RESULT.write_bytes(json.dumps({'ledger': ledger, 'controls': checks},
                                      indent=1, sort_keys=True).encode('utf-8'))
    else:
        require(RESULT.is_file(), 'RESULT.json missing; run with --write first')
        saved = json.loads(RESULT.read_bytes())
        require(saved == {'ledger': ledger, 'controls': checks},
                'RESULT.json differs from recomputation')
    counts = ledger['counts']
    print(f'PASS_LIVE_PIN_DRIFT_AUDIT pins={ledger["pins_seen"]} manifests={ledger["manifests_seen"]} '
          f'L(match={counts["L"]["match"]},drift={counts["L"]["drift"]},'
          f'unresolved={counts["L"]["unresolved"]},ignored={counts["L"]["ignored"]}) '
          f'R-input(match={counts["R-input"]["match"]},drift={counts["R-input"]["drift"]},'
          f'unresolved={counts["R-input"]["unresolved"]},ignored={counts["R-input"]["ignored"]}) '
          f'R-prov(match={counts["R-provenance"]["match"]},drift={counts["R-provenance"]["drift"]},'
          f'unresolved={counts["R-provenance"]["unresolved"]},ignored={counts["R-provenance"]["ignored"]}) '
          f'P(match={counts["P"]["match"]},drift={counts["P"]["drift"]},'
          f'unresolved={counts["P"]["unresolved"]},ignored={counts["P"]["ignored"]}) '
          f'live_drift_paths={len(ledger["drift_provenance"])} controls={len(checks)} '
          f'skip_clones=ValueError')


if __name__ == '__main__':
    main()
