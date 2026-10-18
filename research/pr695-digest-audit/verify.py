#!/usr/bin/env python3
"""Trace three selected #626 provenance digests by whole-file hash substitution.

This reconstructs downstream bytes after substituting four provider hashes and
invoice key order. It does not prove that the substituted files differ only in
seconds: historical CI payloads and some non-timing semantics remain unverified.
Rohan Guliani (@Rohansguliani), with Anthropic Claude assistance. Apache-2.0.
Maintainer clarification by Douglas Colkitt with OpenAI Codex assistance.
"""
import argparse
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
COMMITTED = ROOT / 'research/community-k492-audit/pr626/replay'
PROVIDERS = ('ck', 'jp8')
TIMED = ('CLIFFORD-REVIEW.json', 'SCALAR-FRAME-AUDIT.json')
DIFFERING = {('template_sha256',), ('input_sha256', 'owner_audit'),
             ('input_sha256', 'fresh_invoice')}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def leaf_differences(a, b, path=()):
    if isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b):
        out = set()
        for key in a:
            out |= leaf_differences(a[key], b[key], path + (key,))
        return out
    return set() if a == b else {path}


def substitute(data, table):
    for old, new in table.items():
        data = data.replace(old.encode(), new.encode())
    return data


def explain(local, committed):
    """local/committed: dicts of name -> bytes for the complex replay files."""
    read = lambda side, name: json.loads(side[name])
    differing = leaf_differences(read(local, 'ASSEMBLY.json'), read(committed, 'ASSEMBLY.json'))
    require(differing == DIFFERING, 'Assembly differs outside the three provenance digests: %s' % sorted(differing))

    audit_l, audit_c = read(local, 'audit/ASYNC-AUDIT.json'), read(committed, 'audit/ASYNC-AUDIT.json')
    for key in ('provider_phase_semantic_sha256', 'provider_artifact_semantic_sha256'):
        require(audit_l[key] == audit_c[key], 'Timing-stripped provider semantics differ: ' + key)

    inv_l, inv_c = read(local, 'audit/PREFIX-AND-INVOICE.json'), read(committed, 'audit/PREFIX-AND-INVOICE.json')
    table = {}
    for pid in PROVIDERS:
        art_l, art_c = inv_l['providers'][pid]['artifacts'], inv_c['providers'][pid]['artifacts']
        require(set(art_l) == set(art_c), 'Provider artifact inventory differs: ' + pid)
        changed = {name for name in art_l if art_l[name] != art_c[name]}
        require(changed == set(TIMED), 'Unexplained provider artifact digest change: %s %s' % (pid, sorted(changed)))
        for name in TIMED:
            timed = read(local, 'base/providers/%s/%s' % (pid, name))
            require(isinstance(timed.get('seconds'), float), 'No wall-clock field in ' + name)
            require(digest(local['base/providers/%s/%s' % (pid, name)]) == art_l[name], 'Stale local digest')
            table[art_l[name]] = art_c[name]

    # The template embeds sha256(PLAN.json); PLAN.json embeds the CLIFFORD-REVIEW digests.
    raw = gzip.decompress(local['hosted/GLOBAL-TEMPLATE.json.gz'])
    template = json.loads(raw)
    require(json.dumps(template, sort_keys=True, separators=(',', ':')).encode() == raw, 'Template is not canonical JSON')
    plan = local['PLAN.json']
    require(digest(plan.replace(b'\r\n', b'\n')) == template['async_schedule']['source_plan_sha256'], 'Template/PLAN link broken')
    template['async_schedule']['source_plan_sha256'] = digest(substitute(plan, table).replace(b'\r\n', b'\n'))
    template_c = read(committed, 'hosted/HOSTED.json')['template_sha256']
    template_l = digest(raw)
    require(digest(json.dumps(template, sort_keys=True, separators=(',', ':')).encode()) == template_c,
            'Committed template_sha256 not reproduced from timing digests')
    table[template_l] = template_c

    chain = {}
    for name in ('audit/ASYNC-AUDIT.json', 'audit/OWNERS-AND-PROFILE.json', 'hosted/HOSTED.json'):
        rebuilt = substitute(local[name], table)
        require(rebuilt == committed[name], 'Not reproduced: ' + name)
        table[digest(local[name])] = digest(committed[name])
        chain[name] = [digest(local[name]), digest(committed[name])]

    # invoice_allcold.py: artifacts={f.name:... for f in local_dir.iterdir()} -> filesystem order.
    invoice = json.loads(substitute(local['audit/PREFIX-AND-INVOICE.json'], table))
    for pid in PROVIDERS:
        art = invoice['providers'][pid]['artifacts']
        invoice['providers'][pid]['artifacts'] = {k: art[k] for k in inv_c['providers'][pid]['artifacts']}
    rebuilt = (json.dumps(invoice, indent=2) + '\n').encode()
    require(rebuilt == committed['audit/PREFIX-AND-INVOICE.json'], 'Committed invoice not reproduced')
    pair = [digest(local['audit/PREFIX-AND-INVOICE.json']), digest(committed['audit/PREFIX-AND-INVOICE.json'])]
    table[pair[0]] = pair[1]
    chain['audit/PREFIX-AND-INVOICE.json'] = pair

    require(substitute(local['ASSEMBLY.json'], table) == committed['ASSEMBLY.json'],
            'Committed ASSEMBLY.json not reproduced')
    return dict(status='PASS_PR695_DIGEST_SUBSTITUTION_TRACE',
                template_sha256=[template_l, template_c], chain=chain,
                timed_artifacts=len(TIMED) * len(PROVIDERS), kappa=read(local, 'ASSEMBLY.json')['kappa'])


def controls(local, committed):
    passed = []

    def reject(name, mutate, message):
        changed = deepcopy(local)
        mutate(changed)
        try:
            explain(changed, committed)
        except ValueError as error:
            require(message in str(error), name + ': wrong rejection: ' + str(error))
            passed.append(name)
        else:
            raise ValueError('Accepted mutated replay: ' + name)

    def margin(files):
        a = json.loads(files['ASSEMBLY.json'])
        a['outer'][next(iter(a['outer']))] = '1'
        files['ASSEMBLY.json'] = (json.dumps(a, indent=2) + '\n').encode()

    def plan(files):
        files['PLAN.json'] = files['PLAN.json'].replace(b'"order"', b'"order" ', 1)

    reject('changed_outer_margin', margin, 'outside the three')
    reject('changed_plan_bytes', plan, 'Template/PLAN link')
    return passed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True,
                        help='replay directory; created by a cold replay if it does not exist')
    work = parser.parse_args().work.resolve()
    if not (work / 'complex/ASSEMBLY.json').is_file():
        require(not work.exists(), 'Work directory exists without a completed replay')
        subprocess.run([sys.executable, '-B', 'scripts/verify_frontier626.py', '--work', str(work)],
                       cwd=ROOT, check=True)
    mixed = ['hosted/GLOBAL-TEMPLATE.json.gz', 'hosted/HOSTED.json', 'PLAN.json', 'audit/ASYNC-AUDIT.json',
             'audit/OWNERS-AND-PROFILE.json', 'audit/PREFIX-AND-INVOICE.json']
    mixed += ['base/providers/%s/%s' % (p, n) for p in PROVIDERS for n in TIMED]
    local = {n: (work / 'complex/mixed-global' / n).read_bytes() for n in mixed}
    local['ASSEMBLY.json'] = (work / 'complex/ASSEMBLY.json').read_bytes()
    committed = {n: (COMMITTED / 'mixed-global' / n).read_bytes()
                 for n in mixed if n.startswith(('hosted/HOSTED', 'audit/'))}
    committed['ASSEMBLY.json'] = (COMMITTED / 'ASSEMBLY.json').read_bytes()
    report = explain(local, committed)
    report['controls'] = controls(local, committed)
    print(json.dumps(report, indent=2))
    print(report['status'], '3 digests reproduced,', len(report['controls']), 'rejection controls')


if __name__ == '__main__':
    main()
