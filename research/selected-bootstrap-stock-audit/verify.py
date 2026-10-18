#!/usr/bin/env python3
"""Independent integer-pair audit of selected bootstrap stock thresholds.

No predecessor checker, Fraction, numerical log/exp, or float is used.
The stock coefficient itself is unknown; thresholds are sufficient conditions.
ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_COMMIT = '4d3248d6d52f8ddfe612e8508b74a36acb67fbe3'
PENDING_HEAD = 'c9819a94f9c630f8b42ff5c3027965c4ba451653'
SELECTED = 'certificates/selected-result.json'
ASSEMBLY = 'research/community-frontier1094-audit/ASSEMBLY.json'
FBA = 'research/five-stage-source527-banks/proof/FINITE_BIT_ACCOUNTING.md'
ROWS = 'research/five-stage-source527-banks/proof/three-stage-cover-rows.tex'
PR387 = 'research/bootstrap-depth-audit/sources/pr387/PROOF.md'
PR185 = 'research/bootstrap-depth-audit/sources/pr387/bootstrap-sources/research/community-round8-audit/pr185-proof-reviewed.md'
TARBALL = 'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'
BRANCHES = (('bootstrap', 'complex_lower'), ('conservative_bootstrap', 'conservative_complex_lower'))


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


class R:
    """Reduced integer rational; comparisons use integer cross products."""
    __slots__ = ('p', 'q')

    def __init__(self, p, q=1):
        require(type(p) is int and type(q) is int and q != 0, 'rational integer domain')
        if q < 0:
            p, q = -p, -q
        g = math.gcd(p, q)
        self.p, self.q = p // g, q // g

    @staticmethod
    def of(x):
        if isinstance(x, R):
            return x
        if type(x) is int:
            return R(x)
        require(type(x) is str, 'rational string domain')
        fields = x.split('/')
        require(len(fields) in (1, 2), 'rational serialization')
        return R(*(int(a) for a in fields))

    def __add__(self, x):
        x = R.of(x)
        return R(self.p*x.q+x.p*self.q, self.q*x.q)

    __radd__ = __add__

    def __neg__(self):
        return R(-self.p, self.q)

    def __sub__(self, x):
        return self + -R.of(x)

    def __rsub__(self, x):
        return R.of(x) - self

    def __mul__(self, x):
        x = R.of(x)
        return R(self.p*x.p, self.q*x.q)

    __rmul__ = __mul__

    def __truediv__(self, x):
        x = R.of(x)
        require(x.p != 0, 'nonzero rational divisor')
        return R(self.p*x.q, self.q*x.p)

    def __lt__(self, x):
        x = R.of(x)
        return self.p*x.q < x.p*self.q

    def __le__(self, x):
        x = R.of(x)
        return self.p*x.q <= x.p*self.q

    def __eq__(self, x):
        if not isinstance(x, R) and type(x) not in (int, str):
            return False
        x = R.of(x)
        return self.p == x.p and self.q == x.q

    def __str__(self):
        return str(self.p) if self.q == 1 else f'{self.p}/{self.q}'

    def floor(self):
        return self.p // self.q

    def ceil(self):
        return -(-self.p // self.q)


def fit_guard(L, delta, ell):
    require(type(L) is int and type(ell) is int, 'integer cutoff and headroom')
    delta = R.of(delta)
    return R(0) < delta and L >= 2 and R(36) <= L*delta*delta and R(2*(4+ell)) <= L*delta


def analyze_branch(record, name, side):
    s = min(R.of(record['bit_lower']), (1-R(1, 10**24))*R.of(record[side])) - R(1, 10**27)
    require(R(0) < s < R(1, 2), 'positive common saving below one half')
    old = R(384599, 10**10)
    require(type(record[name]) is list and len(record[name]) == 7, 'seven bootstrap stages')
    result = []
    for j, item in enumerate(record[name], 1):
        new = (1-s)*s+s*old
        gaps = dict(atom=s-new, borrowing=1-new-s, remainder=1-new-s*(1-old), stock=1-s)
        require(all(R(0) < g for g in gaps.values()), 'positive four gaps')
        delta = min(gaps.values())
        require(R.of(item['exponent']) == new, 'recorded stage exponent')
        require(R.of(item['gap']) == delta, 'recorded minimum gap')
        require(type(item['cutoff_log2']) is str and item['cutoff_log2'].isdigit(), 'recorded integer cutoff')
        L = int(item['cutoff_log2'])
        expected_L = max((R(36)/(delta*delta)).ceil(), (R(1032)/delta).ceil())
        require(L == expected_L, 'recorded fixed-512 cutoff')
        require(fit_guard(L, delta, 512), 'fixed-512 sufficient guard')
        H = (L*delta/R(2)).floor()-4
        require(fit_guard(L, delta, H) and not fit_guard(L, delta, H+1), 'maximal integer guard headroom')
        require(delta <= gaps['stock'], 'gap covers stock exponent')
        require(L >= 3, 'relaxed fit domain e at least eight')
        require(not fit_guard(L, delta, H+4), 'relaxed fit cap must not pass old guard')
        result.append(dict(stage=j, old=str(old), exponent=str(new), gaps={k: str(v) for k, v in gaps.items()}, gap=str(delta), cutoff_log2=str(L), stock_headroom_log2=H, original_guard_cap_exp=H-3, relaxed_fit_cap_exp=H+1, relaxed_fit_factor=16, fit_requires_e_ge=8, actual_stock_coefficient=None))
        old = new
    return dict(common_saving=str(s), stages=result)


def analyze(record):
    return {name: analyze_branch(record, name, side) for name, side in BRANCHES}


def typed(value):
    """Comparison key distinguishes booleans, integers, strings and null."""
    if type(value) is dict:
        return ('dict', tuple((k, typed(v)) for k, v in sorted(value.items())))
    if type(value) is list:
        return ('list', tuple(typed(v) for v in value))
    require(type(value) in (str, int, bool, type(None)), 'JSON exact types')
    return type(value).__name__, value


def load_json(raw):
    def pairs(items):
        out = {}
        for k, v in items:
            require(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    obj = json.loads(raw, object_pairs_hook=pairs)
    typed(obj)
    return obj


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob_sha(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def load_sources():
    manifest = load_json((HERE/'SOURCES.json').read_bytes())
    require(type(manifest['schema_version']) is int and manifest['schema_version'] == 1 and manifest['base_commit'] == BASE_COMMIT, 'fixed source schema and base')
    raw = {}
    paths = set()
    for f in manifest['files']:
        require(f['path'] not in paths, 'unique repository source path')
        paths.add(f['path'])
        if f['path'] == 'docs/research/agent-task-catalog.json':
            require(f['usage'] == 'provenance', 'catalogue is historical provenance only')
            continue
        require(f['usage'] == 'input', 'consumed source usage')
        path = (ROOT/f['path']).resolve()
        require(path.is_relative_to(ROOT), 'repository source path')
        data = path.read_bytes()
        require(sha(data) == f['sha256'] and blob_sha(data) == f['git_blob'], 'source SHA256/Git blob: '+f['path'])
        raw[f['path']] = data
    require({SELECTED, ASSEMBLY, FBA, ROWS, PR387, PR185, TARBALL} == set(raw), 'complete consumed source set')
    require(set(raw) | {'docs/research/agent-task-catalog.json'} == paths, 'complete source inventory')
    pending = manifest['pending_sources']
    require(len(pending) == 1 and type(pending[0]['pr']) is int and pending[0]['pr'] == 1965 and pending[0]['repository'] == 'CrocSwap/integer-mult-bounds' and pending[0]['head'] == PENDING_HEAD, 'fixed unique pending PR1965 identity')
    vendor = {}
    paths = set()
    for f in pending[0]['files']:
        require(f['path'] not in paths, 'unique pending source path')
        paths.add(f['path'])
        path = (HERE/f['path']).resolve()
        require(path.is_relative_to(HERE), 'pending source path')
        data = path.read_bytes()
        require(sha(data) == f['sha256'] and blob_sha(data) == f['git_blob'], 'pending source SHA256/Git blob: '+f['path'])
        vendor[path.name] = data
    require(paths == {'sources/pr1965/README.md', 'sources/pr1965/RESULT.json'}, 'PR1965 text and receipt paths')
    return raw, vendor, pending[0]['head']


def source_boundary(raw):
    fba, rows, pr387 = (raw[p].decode() for p in (FBA, ROWS, PR387))
    for needle in ('m=120, W=23,683', 'four levels halve', '14400w+1', '57,604w*ceil(log2(max(2,n)))', 'Add the\ninherited old-leaf reserve'):
        require(needle in fba, 'historical stock source anchor: '+needle)
    for needle in (r'\log_qS(e,w)=O(w\log e)', 'logarithmic reserve', 'original width $e$', 'Small widths use the retained supplier directly'):
        require(needle in rows, 'row contract source anchor: '+needle)
    require('previous ordinary constants' in pr387 and 'previous ordinary constants' in fba, 'inherited cutoff wording')
    reviewed = raw[PR185].decode()
    for needle in ('new ordinary leaves need no *external* extra stock', '252 is not asserted to be the new leaf\'s actual internal reserve', 'additional externally supplied stock is zero'):
        require(needle in reviewed, 'completed leaf source anchor: '+needle)
    with tarfile.open(fileobj=io.BytesIO(raw[TARBALL])) as archive:
        producer = archive.extractfile('code/assemble.py').read().decode()
    require(sha(producer.encode()) == '15f6986a476bac76bcdc0bfcf51da115389b46f1950d2766b6822f757888b13a', 'selected producer member SHA256')
    for needle in ('chain=[Q(384599,10**10)]', 'for _ in range(7)', 'cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap))', "check_moment('complex',H,73"):
        require(needle in producer, 'selected producer source anchor: '+needle)
    return dict(status='NOT_ESTABLISHED', historical_candidate=dict(m=120, halving_levels=4, new_stock_coefficient=57604), selected_candidate=dict(m=73), selected_additive_57604_recurrence='NOT_ESTABLISHED', actual_stage_stock_coefficients=None, inherited_old_leaf_reserve_coefficient=None, completed_inner_leaf_external_extra_stock=0, external_252_is_actual_internal_reserve=False, guard_necessity='NOT_ESTABLISHED', established_scope='Exact sufficient fit thresholds under PR1965 H3; no actual selected stock or quantitative reserve recurrence.')


def validate_claim(result):
    boundary = result['source_boundary']
    require(boundary['status'] == 'NOT_ESTABLISHED' and boundary['selected_additive_57604_recurrence'] == 'NOT_ESTABLISHED', 'selected stock recurrence remains unproved')
    require(boundary['actual_stage_stock_coefficients'] is None and boundary['inherited_old_leaf_reserve_coefficient'] is None, 'actual stock coefficients remain unknown')
    require(all(s['actual_stock_coefficient'] is None for b in result['branches'].values() for s in b['stages']), 'no unproved numerical stage stock')


def semantic_controls(record, branches, boundary):
    import copy
    controls = []
    for name, field in (('wrong gap', 'gap'), ('wrong exponent', 'exponent'), ('cutoff minus one', 'cutoff_log2')):
        changed = copy.deepcopy(record)
        old = changed['bootstrap'][0][field]
        changed['bootstrap'][0][field] = str(R.of(old)+R(1, 10**100)) if field != 'cutoff_log2' else str(int(old)-1)
        try:
            analyze(changed)
        except AuditError as error:
            controls.append(dict(name=name, rejected=True, predicate=str(error)))
        else:
            raise AuditError('semantic mutation was accepted: '+name)
    st = branches['bootstrap']['stages'][1]
    prev = branches['bootstrap']['stages'][0]
    carried = R.of(prev['cutoff_log2'])*(R.of(prev['exponent'])-R.of(prev['old']))
    require(not fit_guard(int(st['cutoff_log2']), st['gap'], carried.ceil()), 'time constant exceeds fit guard headroom')
    controls.append(dict(name='time-space confusion arithmetic guard', rejected=True, predicate='carried time lower bound fails fit guard; it is not an actual stock coefficient', stage=2, carried_log2_lower=str(carried)))
    require(not fit_guard(int(st['cutoff_log2']), st['gap'], st['stock_headroom_log2']+4), 'false relaxed-cap guard acceptance')
    controls.append(dict(name='relaxed fit cap declared old-guard accepted', rejected=True, predicate='H+4 fails maximal old guard', stage=2))
    for name, field, value in (('blanket selected 57604 recurrence', 'selected_additive_57604_recurrence', 'ESTABLISHED'), ('unproved actual stock coefficient', 'actual_stage_stock_coefficients', [57604]*7)):
        changed = dict(source_boundary=copy.deepcopy(boundary), branches=branches)
        changed['source_boundary'][field] = value
        try:
            validate_claim(changed)
        except AuditError as error:
            controls.append(dict(name=name, rejected=True, predicate=str(error)))
        else:
            raise AuditError('unproved stock claim was accepted: '+name)
    return controls


def compute():
    raw, vendor, head = load_sources()
    selected, record = load_json(raw[SELECTED]), load_json(raw[ASSEMBLY])
    require(selected['certificate'] == ASSEMBLY and selected['certificate_sha256'] == sha(raw[ASSEMBLY]), 'selected assembly binding')
    require(selected['kappa'] == record['kappa'], 'unchanged selected kappa')
    branches = analyze(record)
    predecessor = load_json(vendor['RESULT.json'])
    for name, _ in BRANCHES:
        require(typed([r['stock_headroom_log2'] for r in branches[name]['stages']]) == typed(predecessor[name]['stock_headroom_log2']), 'independent PR1965 headroom corroboration')
    text = vendor['README.md'].decode()
    require('valid exactly when every' in text and 'σ_j ≤ 2^(H_j−3)' in text, 'pinned overstrong necessity wording')
    require('not computed here' in text, 'predecessor actual-stock limitation')
    boundary = source_boundary(raw)
    result = dict(status='PASS_SELECTED_BOOTSTRAP_STOCK_AUDIT', selected_kappa=record['kappa'], cutoff_count=14, predecessor_pr=1965, predecessor_head=head, branches=branches, source_boundary=boundary, relaxed_fit=dict(factor=16, cap='sigma_j <= 2^(H_j+1)', fit_requires_e_ge=8, still_conditional_on_H3=True, sharp_maximum_claim=False), controls=semantic_controls(record, branches, boundary), scope='Independent exact selected threshold audit and sufficient factor16 fit extension; actual stock, H1/H2/H3 and physical compiler are not discharged.')
    validate_claim(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    if args.write_result is not None:
        require(not args.write_result.exists(), 'fresh result output only')
        require(not args.write_result.resolve().is_relative_to(ROOT), 'fresh result output must be external')
    result = compute()
    if args.write_result is None:
        require(typed(load_json((HERE/'RESULT.json').read_bytes())) == typed(result), 'committed RESULT equality')
    else:
        with args.write_result.open('x') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], 'cutoffs=14', 'factor16_fit=14', 'actual_stock=NOT_ESTABLISHED')


if __name__ == '__main__':
    main()
