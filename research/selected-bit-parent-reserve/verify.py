#!/usr/bin/env python3
"""Selected BIT parent-reserve implication; stdlib only, no predecessor execution.

Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import math
from pathlib import Path
import tarfile
from fractions import Fraction as Q

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BIT = 'research/e8-bit-p111-tuned/tune/EXPECTED.json'
ASSEMBLY = 'research/community-frontier1094-audit/ASSEMBLY.json'
ARCHIVE = 'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'
ARCHIVE_SOURCE = 'research/complex-t16-rare-pattern-exchanges/SOURCE.json'
PRICER = 'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/code/assemble9.py'
ADAPT = 'research/e8-bit-p111-tuned/code/adapt9p.py'
EMITTER = ('research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/'
           'e8-r715-eleven-stage-whole/code/emit_k.py')


class Rejected(ValueError):
    """A source, semantic premise or certificate failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Rejected(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def authenticate(data: bytes, pin: dict) -> bytes:
    require(sha(data) == pin['sha256'], 'source SHA256: ' + pin['path'])
    require(blob(data) == pin['git_blob'], 'source Git blob: ' + pin['path'])
    return data


def inputs() -> dict[str, bytes]:
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    require(manifest['base_commit'] == '564148b82ae9df72163f22106f15e73efca8aff2',
            'scientific base')
    return {p['path']: authenticate((ROOT / p['path']).read_bytes(), p)
            for p in manifest['files'] if p['usage'] == 'input'}


def assignment(tree: ast.AST, name: str) -> ast.expr:
    matches = [node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)]
    require(len(matches) == 1, 'unique source assignment: ' + name)
    return matches[0]


def expression(tree: ast.AST, name: str, expected: str) -> None:
    actual = ast.dump(assignment(tree, name), include_attributes=False)
    want = ast.dump(ast.parse(expected, mode='eval').body, include_attributes=False)
    require(actual == want, 'source expression: ' + name)


def archive_member(data: dict[str, bytes], name: str) -> bytes:
    pins = json.loads(data[ARCHIVE_SOURCE])['files']
    with tarfile.open(fileobj=io.BytesIO(data[ARCHIVE]), mode='r:gz') as archive:
        member = archive.getmember(name)
        require(member.isfile(), 'archive member is regular file')
        stream = archive.extractfile(member)
        require(stream is not None, 'archive member data')
        result = stream.read()
    require(sha(result) == pins[name], 'archive member SHA256: ' + name)
    return result


def bind_sources(data: dict[str, bytes]) -> tuple[dict, dict, int]:
    selected = json.loads(data['certificates/selected-result.json'])
    require(selected['certificate'] == ASSEMBLY, 'selected assembly path')
    require(selected['certificate_sha256'] == sha(data[ASSEMBLY]), 'selected certificate digest')
    assembly = json.loads(data[ASSEMBLY])
    require(assembly['kappa'] == selected['kappa'], 'selected kappa unchanged')
    citation = assembly['bit_supplier']
    require(citation['pr'] == 589 and citation['path'] == BIT, 'selected BIT producer')
    require(citation['commit'] == 'a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46', 'PR589 source head')
    require(citation['git_blob_sha1'] == blob(data[BIT]), 'selected BIT blob')
    bit = json.loads(data[BIT])
    require(assembly['bit_lower'] == bit['nine']['bit_lower'], 'selected BIT saving')
    source = archive_member(data, 'code/assemble.py')
    tree = ast.parse(source)
    expression(tree, 'BIT_M', '1 + 7 * BIT_L')
    expression(tree, 'BIT_K', '(BIT_L - 1) // 2')
    tuples = [n for n in tree.body if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Tuple)
                      and [x.id for x in t.elts if isinstance(x, ast.Name)] == ['BIT_L', 'BIT_T']
                      for t in n.targets)]
    require(len(tuples) == 1, 'selected stage/replica binding')
    stages, replicas = ast.literal_eval(tuples[0].value)
    require((stages, replicas) == (9, 32), 'selected nine-stage recipe')
    expression(tree, 'BIT_BLOB', repr(blob(data[BIT])))
    pricer = ast.parse(data[PRICER])
    expression(pricer, 'physical', 'W + 9')
    expression(pricer, 'row', 'DEPTH * (m * m + 1) + 9909 + 252')
    # Adaptation's only pricer edits bind ports and deficit; no source is executed.
    adapt = ast.parse(data[ADAPT])
    edits = assignment(adapt, 'EDITS')
    require(isinstance(edits, ast.Dict), 'adaptation edit map')
    pricer_edits = [v for k, v in zip(edits.keys, edits.values)
                    if isinstance(k, ast.Constant) and k.value == 'assemble9.py']
    require(len(pricer_edits) == 1, 'unique selected pricer adaptation')
    replacements = ast.literal_eval(pricer_edits[0].elts[1])
    require(len(replacements) == 2, 'selected pricer adaptation count')
    require(all('row' not in old + new and 'physical' not in old + new
                for old, new in replacements), 'reserve formula unchanged by adaptation')
    emitter = ast.parse(data[EMITTER])
    physical = [n.value for n in ast.walk(emitter) if isinstance(n, ast.keyword)
                and n.arg == 'physical']
    require(len(physical) == 1 and ast.dump(physical[0]) == ast.dump(
        ast.parse('LIVE + 9', mode='eval').body), 'selected hosted physical roles')
    return assembly, bit, 1 + 7 * stages


def ceil_q(value: Q) -> int:
    return -(-value.numerator // value.denominator)


def ceil_log2(n: int) -> int:
    require(type(n) is int and n >= 1, 'positive integer logarithm input')
    return (n - 1).bit_length()


def parameters(bit: dict, m: int) -> dict:
    nine = bit['nine']
    profile = {int(r): count for r, count in nine['profile'].items()}
    require(m == 64, 'selected ordinary dimension, not complex or historical dimension')
    require(all(type(c) is int and c > 0 and 1 <= r < m for r, c in profile.items()),
            'positive proper child inventory')
    record = nine['bit']
    live = 2 * 4 * bit['word']['v'] * 32
    require(live == record['live'] == 28416, 'selected live roles')
    physical = live + 9
    require(physical == record['physical'] == 28425, 'all nine additional roles charged')
    require(max(profile) == record['maxchild'] == 42, 'selected maximum child')
    require(sum(r * c for r, c in profile.items()) == record['rank_mass'], 'selected rank mass')
    degree = record['halving_depth']
    require(type(degree) is int and degree == 2, 'selected halving degree')
    require(2 * max(profile) ** degree < m ** degree, 'strict halving')
    coefficient = degree * (m * m + 1)
    require(record['row_coefficient'] == coefficient + 9909 + 252, 'inherited row decomposition')
    require(physical < 2 ** 80, 'all physical roles below eligible q')
    return dict(m=m, live=live, physical=physical, maxchild=max(profile),
                halving_degree=degree, halving_inequality=[m ** degree, 2 * max(profile) ** degree],
                per_level_linear=m * m, per_level_constant=1,
                parent_sigma=coefficient, inherited_outer_row=record['row_coefficient'])


def fit_guard(L: int, gap: Q, s: Q, ell: int) -> None:
    require(L >= 2 and L * gap ** 2 >= 36 and L * gap >= 2 * (4 + ell),
            'sufficient stock-fit guard')
    require(0 < gap <= 1 - s, 'stock exponent gap')


def cutoff(assembly: dict, sigma: int) -> dict:
    require(type(sigma) is int and sigma > 0, 'positive integral stock coefficient')
    s = min(Q(assembly['bit_lower']), (1 - Q(1, 10 ** 24)) * Q(assembly['complex_lower'])) - Q(1, 10 ** 27)
    a0 = Q(384599, 10 ** 10)
    a1 = (1 - s) * s + s * a0
    gap = min(s - a1, 1 - a1 - s, 1 - a1 - s * (1 - a0), 1 - s)
    require(0 < a0 < a1 < s < 1 - a1, 'selected native stage domain')
    recorded = assembly['bootstrap'][0]
    L = int(recorded['cutoff_log2'])
    require(Q(recorded['exponent']) == a1 and Q(recorded['gap']) == gap, 'selected native stage binding')
    require(L == max(ceil_q(36 / gap ** 2), ceil_q(1032 / gap)), 'recorded cutoff reconstruction')
    ell = ceil_log2(8 * sigma)
    fit_guard(L, gap, s, ell)
    return dict(stage=1, branch='native', s=str(s), exponent=str(a1), gap=str(gap),
                cutoff_log2=L, sigma=sigma, required_log2_8sigma=ell,
                guard_headroom=(L * gap // 2) - 4,
                fit='k < e/2 for every integer e >= 2^L, under the stated interfaces')


def depth_smoke(profile: dict[str, int], m: int, limit: int = 20000) -> dict:
    ranks = sorted(int(r) for r in profile)
    depths = [0] * (limit + 1)
    for n in range(m, limit + 1):
        children = [r * (n // m) for r in ranks]
        require(all(0 <= child < n for child in children), 'proper floor child')
        depths[n] = 1 + max(depths[child] for child in children)
        require(depths[n] <= 2 * ceil_log2(n), 'all-rank finite depth bound')
        x, greedy = n, 0
        while x >= m:
            x = max(ranks) * (x // m)
            greedy += 1
        require(depths[n] == greedy, 'independent greedy/all-rank depth comparison')
    return dict(atom_counts=limit + 1, minimum=0, maximum=limit,
                maximum_observed_depth=max(depths),
                one_level_halving_counterexample={'parent': 128, 'child': 84, 'half': 64})


def gl_size(q: int, m: int, w: int) -> int:
    require(q >= 2 and m >= 1 and w >= 1, 'cardinality domain')
    return math.prod(q ** m - q ** j for j in range(m)) * q ** (m * m * (w - 1))


def local_ring_smoke() -> list[dict]:
    rows = []
    for q, w in ((3, 1), (3, 2), (5, 1)):
        modulus = q ** w
        count = sum(math.gcd(a * d - b * c, modulus) == 1
                    for a in range(modulus) for b in range(modulus)
                    for c in range(modulus) for d in range(modulus))
        expected = gl_size(q, 2, w)
        require(count == expected, 'independent local-ring determinant census')
        require(2 * count < q ** (4 * w + 1), 'charged toy physical-role divisor')
        rows.append(dict(q=q, w=w, m=2, invertible=count, roles=2))
    return rows


def row_program(row: int, divisor: int, depth: int, omit_restore_at: int = -1) -> int:
    """Finite semantic fixture: two sequential children and a restored fresh role."""
    if depth == 0:
        return row
    unused, role = divmod(row, divisor)
    routed = (role + 1) % divisor
    for _ in range(2):
        unused = row_program(unused, divisor, depth - 1, omit_restore_at)
    restored = routed if depth == omit_restore_at else (routed - 1) % divisor
    return unused * divisor + restored


def require_stock(stock: int, divisor: int, depth: int, external_leaf: int = 1) -> None:
    required = divisor ** depth * external_leaf
    require(stock > 0 and stock % required == 0, 'complete divisible descendant stock')


def row_smoke() -> dict:
    divisor, depth = 3, 3
    stock = divisor ** depth
    require_stock(stock, divisor, depth)
    for row in range(stock):
        first = row_program(row, divisor, depth)
        second = row_program(first, divisor, depth)
        require(first == second == row, 'arbitrary row restoration and sequential reuse')
    return dict(divisor=divisor, depth=depth, rows=stock, complete_wrapper_calls=2,
                all_rows_restored=True, external_leaf_factor=1)


def result() -> dict:
    data = inputs()
    assembly, bit, m = bind_sources(data)
    values = parameters(bit, m)
    return dict(status='PASS_SELECTED_BIT_PARENT_RESERVE',
                claim='Conditional selected BIT parent stock; not all-size implementation or H2',
                source_sha256={path: sha(value) for path, value in sorted(data.items())},
                archive_member_sha256=sha(archive_member(data, 'code/assemble.py')),
                selected=values, first_native_cutoff=cutoff(assembly, values['parent_sigma']),
                finite_floor_depth=depth_smoke(bit['nine']['profile'], m),
                finite_local_rings=local_ring_smoke(), finite_row_reuse=row_smoke())


def compare(actual: dict, expected: dict) -> None:
    require(actual == expected, 'canonical RESULT payload mismatch')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path, help='create a new external receipt, never overwrite')
    args = parser.parse_args()
    observed = result()
    if args.write_result is not None:
        require(args.write_result.resolve() != (PACKAGE / 'RESULT.json').resolve(), 'external receipt only')
        with args.write_result.open('x') as stream:
            json.dump(observed, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        compare(observed, json.loads((PACKAGE / 'RESULT.json').read_bytes()))
    print(observed['status'], 'm=64 sigma=8194 stage=1 floor_cases=20001 local_rings=3 row_states=27')


if __name__ == '__main__':
    main()
