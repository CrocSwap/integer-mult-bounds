"""Emit exact Walsh adapters and their involutive tensor-square lift."""

from collections import Counter
from hashlib import sha256
import argparse
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clifford_compile as c
import sources


def require(condition, message):
    if not condition:
        raise ValueError(message)


def equal(left, right, message):
    require(left.tab == right.tab, message + ' Pauli action')
    require(left.zero_state() == right.zero_state(), message + ' scalar phase')


def phase(n, value):
    return c.Op(n, c.identity(n), [('phase', value % 4)])


def shear(n, rank):
    return c.diag(n, tuple(1 << j if j < rank else 0 for j in range(n)))


def walsh_frame(n, vectors):
    rank = len(vectors)
    if not rank:
        return c.ident(n)
    if rank == n:
        return c.hadamard(n, range(n))
    chart = c.perm(n, c.transpose(c.basis_extend(vectors, n), n))
    return chart.adjoint().then(c.hadamard(n, range(rank))).then(chart)


def monomial(record):
    n = len(record['matrix_rows'])
    return c.diag(n, record['quadratic_rows'], record['linear_Z4']).then(
        c.perm(n, record['matrix_rows'])).then(c.xgate(n, record['offset'])).then(
        phase(n, record['phase']))


def recipe(record, n):
    left = monomial(record['left'])
    if not record['rank']:
        return left
    return monomial(record['right']).then(c.fourier(n, range(record['rank']))).then(left)


def adapters(loaded):
    word = loaded['CANONICAL-WORD.json.gz']
    n = 9
    common_shear = shear(n, n)
    old, new, maps, records = [], [], [], []
    for index, vectors in enumerate(word['frames']):
        before = c.canonical_frame(n, vectors)
        after = walsh_frame(n, vectors)
        exact = before.adjoint().then(common_shear.adjoint()).then(after)
        native, record = c.monomial(exact)
        equal(common_shear.then(before).then(native), after, 'frame ' + str(index))
        old.append(before)
        new.append(after)
        maps.append(native)
        records.append(record)
        if index % 250 == 0:
            print('Frame adapters:', index, '/', len(word['frames']), flush=True)
    ranks = Counter()
    for edge in loaded['CLIFFORD-RECIPES.json']['children']:
        a, b = edge['old'], edge['new']
        before = old[a].adjoint().then(old[b])
        after = new[a].adjoint().then(new[b])
        lowered = maps[a].adjoint().then(before).then(maps[b])
        require(after.tab == lowered.tab, 'The frame adapter has the wrong edge action')
        rank_old = c.rank([x for x, z, p in before.tab[n:]])
        rank_new = c.rank([x for x, z, p in after.tab[n:]])
        require(rank_old == rank_new == edge['rank'], 'The edge rank changed')
        ranks[rank_old] += 1
    endpoints = []
    full = c.fourier(n)
    full_walsh = common_shear.then(full).then(common_shear)
    for port, label in enumerate(word['ports']):
        require(label.bit_count() in (3, 7), 'The port is not an E8 label')
        sq = c.diag(n, tuple(label if label >> j & 1 else 0 for j in range(n)))
        hq = sq.then(c.cgate(n, label)).then(sq)
        hperp = hq.adjoint().then(full_walsh)
        zq = c.diag(n, (0,) * n, tuple(2 * ((label >> j) & 1) for j in range(n)))
        aq = c.xgate(n, label).then(common_shear.adjoint()).then(zq).then(phase(n, 1))
        at = zq.then(c.xgate(n, label)).then(common_shear).then(phase(n, 1))
        equal(common_shear.then(c.cgate(n, label)).then(aq), hq, 'source endpoint')
        equal(common_shear.then(c.cgate(n, label, -1)).then(full).then(at), hperp,
              'target endpoint')
        equal(hq.then(hq), phase(n, 1), 'line square')
        equal(hq.then(hperp), full_walsh, 'orthogonal endpoint product')
        equal(hperp.then(hq), full_walsh, 'orthogonal endpoint commutation')
        for role, conventional, frame_id in (
            ('source', hq, word['start'][port]),
            ('target', hperp, word['final'][112 + port]),
        ):
            op, record = c.monomial(conventional.adjoint().then(new[frame_id]))
            equal(conventional.then(op), new[frame_id], 'canonical endpoint')
            endpoints.append(dict(role=role, port=port, frame=frame_id, adapter=record))
    return dict(frame_adapters=records, endpoint_adapters=endpoints), maps, new, ranks


def fuse(record, before, after):
    left = monomial(record['left']).then(after)
    if record['rank']:
        right = before.adjoint().then(monomial(record['right']))
        left, left_record = c.monomial(left)
        right, right_record = c.monomial(right)
    else:
        left, left_record = c.monomial(before.adjoint().then(left))
        right_record = None
    return dict(record, left=left_record, right=right_record)


def helper_normalizers(residuals, n, doubled=False):
    result = {}
    for key, record in residuals.items():
        rank = record['rank']
        left = monomial(record['left'])
        right = monomial(record['right']) if rank else c.ident(n)
        endpoint = shear(n, rank)
        pre, pre_record = c.monomial(endpoint.then(right.adjoint()))
        post = left.adjoint().then(endpoint)
        if doubled:
            post = post.then(phase(n, -rank // 2))
        post, post_record = c.monomial(post)
        actual = pre.then(recipe(record, n)).then(post)
        expected = c.hadamard(n, range(rank))
        if doubled:
            expected = expected.then(phase(n, -rank // 2))
            require(actual.tab == expected.tab, 'The doubled helper has the wrong Pauli action')
        else:
            equal(actual, expected, 'complete helper ' + key)
        result[key] = dict(rank=rank, pre=pre_record, post=post_record)
    return result


def tensor_monomial(record):
    n = len(record['matrix_rows'])
    return {
        'matrix_rows': list(record['matrix_rows']) + [x << n for x in record['matrix_rows']],
        'quadratic_rows': list(record['quadratic_rows']) + [x << n for x in record['quadratic_rows']],
        'linear_Z4': list(record['linear_Z4']) * 2,
        'offset': record['offset'] | (record['offset'] << n),
        'phase': 2 * record['phase'] % 4,
    }


def tensor_tableau(table):
    n = len(table) // 2
    shifted = [(x << n, z << n, p) for x, z, p in table]
    return tuple(table[:n]) + tuple(shifted[:n]) + tuple(table[n:]) + tuple(shifted[n:])


def double_recipe(record, phase_difference):
    rank = record['rank']
    left = monomial(tensor_monomial(record['left']))
    if rank:
        order = list(range(rank)) + list(range(9, 9 + rank))
        order += list(range(rank, 9)) + list(range(9 + rank, 18))
        gather = c.perm(18, tuple(1 << j for j in order))
        right = monomial(tensor_monomial(record['right'])).then(gather)
        left = gather.adjoint().then(left)
        right, right_record = c.monomial(right)
    else:
        right_record = None
    left, left_record = c.monomial(left.then(phase(18, phase_difference)))
    return dict(record, rank=2 * rank, left=left_record, right=right_record)


def encoded_json(value, legacy_order=False, pretty=False):
    options = {'indent': 2} if pretty else {'separators': (',', ':')}
    return (json.dumps(value, sort_keys=not legacy_order, **options) + '\n').encode()


def save(out, name, raw):
    data = gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw
    (out / name).write_bytes(data)
    return {'payload_sha256': sha256(raw).hexdigest(),
            'file_sha256': sha256(data).hexdigest(), 'bytes': len(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=HERE.parents[1])
    parser.add_argument('--out', type=Path, default=HERE / 'evidence')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    loaded = sources.load_local(args.repo)
    word = loaded['CANONICAL-WORD.json.gz']
    adapter_payload, frame_maps, new_frames, ranks = adapters(loaded)
    adapter_raw = encoded_json(adapter_payload, legacy_order=True)
    children = []
    for index, record in enumerate(loaded['CLIFFORD-RECIPES.json']['children']):
        children.append(fuse(record, frame_maps[record['old']], frame_maps[record['new']]))
        if index % 500 == 0:
            print('Fused children:', index, '/', len(loaded['CLIFFORD-RECIPES.json']['children']), flush=True)
    residuals = {key: fuse(record, frame_maps[record['frame']], frame_maps[record.get('terminal', 1)])
                 for key, record in loaded['RESIDUAL-ADAPTERS.json']['recipes'].items()}
    endpoints = [dict(role=x['role'], port=x['port'], frame=x['frame'], rank=0,
                      left=x['adapter'], right=None) for x in adapter_payload['endpoint_adapters']]
    old_pins = {key: value for key, value in sources.LOCAL_PINS.items() if key != 'DATA-PHASES.json'}
    native = {
        'schema': 'walsh-native-retarget-v1', 'base': sources.BASE,
        'old_member_sha256': old_pins, 'adapter_sha256': sha256(adapter_raw).hexdigest(),
        'complete_helper_job': 'H_rank=S_rank F_rank S_rank',
        'recursive_child_job': 'The original coordinate F_rank, with the emitted monomial factors',
        'children': children, 'endpoint_adapters': endpoints, 'residual_adapters': residuals,
        'programs': loaded['LOCAL-PROGRAMS.json.gz'],
    }
    native_raw = encoded_json(native)
    helper = {
        'status': 'PASS_EXACT_COMPLETE_WALSH_HELPER_NORMALIZATION',
        'native_payload_sha256': sha256(native_raw).hexdigest(),
        'residual_adapter_event_semantics': {
            'pre': 'Apply the pre record: R_new^-1 S_rank, right factor first',
            'post': 'Apply the post record: S_rank L_new^-1, right factor first',
            'key': 'The frame number as a string, or frame:terminal when terminal is not one',
        },
        'complete_job': 'S_rank F_rank S_rank on the first rank axes; identity on spectators',
        'checked_residual_keys': len(residuals), 'recipes': helper_normalizers(residuals, 9),
        'scope': 'The added endpoint phase factors are literal monomial maps. The fused child inventory is unchanged. This artifact is required together with WALSH-RETARGET-NATIVE.json.gz.',
    }
    helper_raw = encoded_json(helper, pretty=True)
    dimensions = [len(vectors) for vectors in word['frames']]
    doubled_children = []
    for record in children:
        doubled = double_recipe(record, dimensions[record['old']] - dimensions[record['new']])
        expected = c.compose(tensor_tableau(new_frames[record['new']].tab),
                             c.inverse(tensor_tableau(new_frames[record['old']].tab)))
        require(recipe(doubled, 18).tab == expected, 'The doubled child has the wrong Pauli action')
        doubled_children.append(doubled)
    doubled_residuals = {
        key: double_recipe(record, dimensions[record['frame']] - dimensions[record.get('terminal', 1)])
        for key, record in residuals.items()
    }
    doubled = {
        'schema': 'involutive-native-lift-v1', 'base': sources.BASE,
        'source_native_payload_sha256': sha256(native_raw).hexdigest(),
        'source_helper_normalization_sha256': sha256(helper_raw).hexdigest(),
        'frame_dimensions': [2 * rank for rank in dimensions],
        'frame_definition': 'Gamma_V=i^(-dim V) (H_V tensor H_V), then tensor lambda',
        'complete_helper_job': 'i^(-r) H_(2r) on contiguous first 2r coordinates; identity on spectators',
        'recursive_child_job': 'The original coordinate F_(2r), with literal tensor-and-gather factors',
        'children': doubled_children,
        'endpoint_adapters': [double_recipe(record, 0) for record in endpoints],
        'residual_adapters': doubled_residuals,
        'helper_normalizers': helper_normalizers(doubled_residuals, 18, doubled=True),
        'program_rank_scale': 2,
        'program_event_semantics': 'The programs field gives the source event streams. Multiply each native rank token by two. Use the emitted doubled child, endpoint, residual, and helper records for the literal factors.',
        'programs': loaded['LOCAL-PROGRAMS.json.gz'],
    }
    outputs = {
        'WALSH-RETARGET-ADAPTERS.json': adapter_raw,
        'WALSH-RETARGET-NATIVE.json.gz': native_raw,
        'WALSH-RETARGET-HELPER-NORMALIZATION.json': helper_raw,
        'DOUBLED-WALSH-NATIVE.json.gz': encoded_json(doubled),
    }
    files = {name: save(args.out, name, raw) for name, raw in outputs.items()}
    report = {
        'status': 'PASS_GENERATED_WALSH_AND_INVOLUTIVE_NATIVE_LIFT',
        'base': sources.BASE, 'archive_sha256': sources.LOCAL_ARCHIVE_SHA256,
        'member_sha256': sources.LOCAL_PINS, 'files': files,
        'frame_adapters': len(frame_maps), 'child_recipes': len(children),
        'endpoint_adapters': len(endpoints), 'helper_normalizers': len(residuals),
        'child_rank_histogram': dict(sorted(ranks.items())),
        'doubled_child_rank_histogram': {str(2 * rank): count for rank, count in sorted(ranks.items())},
        'program_event_counts': {key: len(events) for key, events in native['programs'].items()},
        'generator_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'compiler_sha256': sha256(Path(c.__file__).read_bytes()).hexdigest(),
        'compiler_campaign_source_sha256': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
        'scope': 'Exact local recipes. Independent native review, global routing, owner admission, scalar/address pricing, and a complete supplier bound are separate obligations.',
    }
    (args.out / 'GENERATION.json').write_bytes(encoded_json(report, pretty=True))
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
