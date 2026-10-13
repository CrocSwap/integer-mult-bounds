"""Concrete source-bound X4 primitive lowering, following Philipp's PR883.

Prepared for nightangelflowerwin-ops with substantial OpenAI Codex assistance.
Apache-2.0. Original sources and attribution are retained in vendor/pr883.
"""
import gzip
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sources():
    pins = read(HERE / 'SOURCES.json')
    for name, digest in pins['repo_inputs'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'Repository source drift: ' + name)
    for name, digest in pins['vendor_inputs'].items():
        require(sha256((HERE / 'vendor/pr883' / name).read_bytes()).hexdigest() == digest, 'PR883 source drift: ' + name)
    for name, digest in pins['coverage_inputs'].items():
        require(sha256((HERE / 'vendor/pr865' / name).read_bytes()).hexdigest() == digest, 'PR865 source drift: ' + name)
    return pins


def predecessor():
    spec = importlib.util.spec_from_file_location('p883_lowering', HERE / 'vendor/pr883/verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_prefix(stream, pairs, backward):
    """Independent two-row matrix check of every emitted physical block."""
    require(stream[0] == ['phase', 'zero_frame_precondition'], 'Primitive entrance phase')
    for index, (x, y) in enumerate(pairs):
        registers = {('L', x): 0, ('L', y): 1}
        rows = [[Q(1), Q(0)], [Q(0), Q(1)]]
        for event in stream[1 + 4*index:1 + 4*(index+1)]:
            require(len(event) == 3 and event[0] == 'primitive' and type(event[2]) is int and event[2] == 0,
                    'Primitive zero-frame block')
            op = event[1]
            require(tuple(op[1]) in registers, 'Primitive target escapes pair')
            target = registers[tuple(op[1])]
            if op[0] == 'add':
                require(len(op) == 4 and tuple(op[2]) in registers and tuple(op[1]) != tuple(op[2]) and
                        type(op[3]) is int and op[3] in (-1, 1), 'Primitive signed source')
                source = registers[tuple(op[2])]
                rows[target] = [a + op[3]*b for a, b in zip(rows[target], rows[source])]
            else:
                require(len(op) == 2 and op[0] in ('neg', 'half', 'double'), 'Primitive two-register alphabet')
                factor = {'neg': Q(-1), 'half': Q(1, 2), 'double': Q(2)}[op[0]]
                rows[target] = [factor*a for a in rows[target]]
        expected = [[Q(-1), Q(1)], [Q(1), Q(1)]] if backward else [[Q(-1,2),Q(1,2)],[Q(1,2),Q(1,2)]]
        require(rows == expected, 'Primitive pair matrix differs')


def emit(directory, out):
    """Expand the actual fresh provider; retain every non-scalar event literally."""
    sources()
    module = predecessor()
    expected_word, expected_programs, expected_checks = module.load_inputs(ROOT)
    word = read(directory / 'CANONICAL-WORD.json.gz')
    programs = read(directory / 'LOCAL-PROGRAMS.json.gz')
    checks = read(directory / 'LOCAL-CHECKS.json')
    require(canonical(word) == canonical(expected_word), 'Fresh X4 word differs from source')
    require(canonical(programs) == canonical(expected_programs), 'Fresh logical program differs from source')
    require(canonical(checks) == canonical(expected_checks), 'Fresh logical invoice differs from source')
    pairs = module.pairs(word)
    receipt, streams = {}, {}
    for orientation in ('forward', 'backward'):
        backward = orientation == 'backward'
        audit = module.run_orientation(word, programs[orientation], checks[orientation], pairs, backward)
        events = programs[orientation]
        stream = [events[0]]
        # A fused block still has three logical macros for conservative compiler
        # reserves; this concrete expansion implements their joint endpoint.
        for x, y in pairs:
            stream.extend([['primitive', list(op), 0] for op in module.replacement(x, y, backward)])
        cursor = 1 + 3 * len(pairs)
        for event in events[cursor:]:
            if event[0] == 'scalar':
                stream.extend([['primitive', list(op), event[2]] for op in module.lower(event[1])])
            else:
                stream.append(event)
        # Replay the emitted instructions themselves, not just the builder's
        # audited recipe. Physical non-scalar operators remain hash-bound to
        # the freshly checked source word, phase and wrapper receipts.
        replay = module.Replay(2 * word['v'] + word['R'])
        check_prefix(stream, pairs, backward)
        for event in stream:
            if event[0] == 'primitive':
                op = event[1]
                op = tuple(tuple(x) if isinstance(x, list) else x for x in op)
                replay.apply(op)
        replay.endpoint(2 * word['v'] + word['R'], word['v'], backward)
        require(replay.count * 2 == audit['replacement']['real_component_primitives'], 'Emitted primitive bill')
        require(replay.receipt() == audit['replacement'], 'Emitted full prefix/clearing audit')
        require([e for e in stream if e[0] != 'primitive'] ==
                [e for e in events if e[0] != 'scalar'], 'Physical event stream changed')
        streams[orientation] = stream
        receipt[orientation] = dict(audit=audit, emitted= replay.receipt(),
                                    stream_sha256=sha256(canonical(stream)).hexdigest(),
                                    logical_macros_retained=checks[orientation]['scalar_macros'],
                                    coefficient_work_operations_removed=504)
    out.mkdir()
    data = canonical(streams)
    (out / 'PRIMITIVE-PROGRAMS.json.gz').write_bytes(gzip.compress(data, mtime=0))
    result = dict(status='PASS_SOURCE_BOUND_X4_PRIMITIVE_LOWERING', orientations=receipt,
                  source_artifacts={name: sha256((directory / name).read_bytes()).hexdigest()
                                    for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json',
                                                 'INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-RECIPES.json',
                                                 'CLIFFORD-REVIEW.json', 'RESIDUAL-ADAPTERS.json', 'WRAPPER-CHECKS.json')},
                  primitive_program_content_sha256=sha256(data).hexdigest(),
                  pair_count=len(pairs), pair_instruction_controls=module.controls(pairs),
                  scope='Explicit primitive compiler refinement; physical word/phase/wrapper stream unchanged. No new recursive profile or kappa.')
    (out / 'LOWERING.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    return result
