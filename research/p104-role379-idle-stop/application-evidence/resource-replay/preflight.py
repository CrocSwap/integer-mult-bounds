#!/usr/bin/env python3
"""Run the bounded literal, grid and ordinary feasibility checks."""

import argparse
import gzip
import hashlib
import importlib.util
import json
import resource
import signal
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parents[1]
RESOURCES = OUTPUTS / 'kappa-7641-successor-20261118/resources'
VENDOR = RESOURCES / 'vendor'
SOURCE_PINS = {
    'qualify.py': '02bc6cd1a627562e69be4d2dc756e3da55048395a0b85605849b9209ec7a1902',
    'ordinary.py': 'f0325ce12226a53f52d75ba3e068f0f7d4cb80c827e302617d94ba14a10883fc',
    'tape_scalar.py': '9a22a356f3efa5605c852607b0791ecd7c6b2ef0641ae4bf0c2483c1544d31aa',
    'vendor/ODD-CALLER-EXACT-GRID.json': '87d25d9fa3778bf4784e3a9e17f32ce5ba372663c6e97392cc62b87e6719042c',
    'vendor/derive_grid.py': 'ceb7a44ef19d72a16db7b43c65c85910d965499d1715436011de32af5d39dbb0',
    'vendor/independent_bounds.py': '198521def614fe78fa728f1dde2b7fb820c0c0e0ac3ad0c9224dccbf51eac0d5',
}
ORIGINAL_COMPRESSED = 'de43ed04f58133eaef8f8d12a9dae1e6e8aa7f9721044200cc839673d86fd7c1'
ORIGINAL_RAW = '6a472688bdf2a1b293df0f4f77427a04a1f87c92fedb5b5a6921cc850c272b4f'
WORDS = {
    '7636': {
        'head': '7e68d8dd62d9a38c0f3c942262a7a85ca7125b75',
        'path': HERE.parent / 'pins/7636/data/word.json.gz',
        'gzip_sha256': '1b4e33c3e3b69d1f1b42d019a2e372ac612fa28494bd8da18a734618f9bda659',
        'raw_sha256': '98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2',
        'canonical_sha256': 'c3390064f8bff3fda737f38c1d438016125e784952c545940bbb261b10df668c',
        'lifetimes': 180,
        'reported_grid': 54675,
    },
    '7620': {
        'head': 'b1356c84a0733843ce59855f02511c49c6a44133',
        'path': OUTPUTS / 'kappa-research-20261115b/inputs/pr7620/data/word.json.gz',
        'gzip_sha256': '2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c',
        'raw_sha256': '684c1f877fe3aa9e0afaf8f494286e617bc87ed324288b589812a709d1752a5e',
        'canonical_sha256': '6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d',
        'lifetimes': 167,
        'reported_grid': 1125,
    },
    '7658': {
        'head': '0a0e71c34a5ee5a1b59a8fe7bc6abd35a4d3dd82',
        'path': HERE.parent / 'word7658.verified-source.gz',
        'gzip_sha256': 'dde0a987c2dd9e221208ca5043dfd6e2bdfbb8c4289fa20e2b93fae1696b3ea9',
        'raw_sha256': 'fa84fcdecb534700cd00dc81b74889f549a653daa2fb3658cb8142e1eeb9b9e6',
        'canonical_sha256': '9721965b3fa98cef7731ee88319fae2e62354bca3bf1a6b334bcffee14b047cf',
        'lifetimes': 234,
        'reported_grid': 225,
    },
    '7658-b': {
        'head': '0a0e71c34a5ee5a1b59a8fe7bc6abd35a4d3dd82',
        'path': HERE.parent / 'strong/run7658/WORD.json.gz',
        'gzip_sha256': '4e9cd9cc70a5423db44f870b35d8d6da9ac5746aa352f3af1420443f6dda350e',
        'raw_sha256': 'f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669',
        'canonical_sha256': 'f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669',
        'lifetimes': 234,
        'reported_grid': 225,
    },
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    with path.open('x') as stream:
        json.dump(data, stream, indent=2, default=str)
        stream.write('\n')


def run_adapted(name, substitutions, argv=None):
    source = RESOURCES / name
    raw = source.read_bytes()
    need(digest(raw) == SOURCE_PINS[name], f'source pin {name}')
    text = raw.decode()
    for before, after in substitutions:
        need(text.count(before) == 1, f'exact adapter occurrence in {name}: {before}')
        text = text.replace(before, after)
    report = {
        'source': str(source), 'source_sha256': digest(raw),
        'adapted_sha256': digest(text.encode()),
        'substitutions': substitutions,
    }
    write_json(ACTIVE_OUT / f'{source.stem}-adapter.json', report)
    original_argv = sys.argv
    try:
        if argv is not None:
            sys.argv = [str(source), *argv]
        exec(compile(text, str(source), 'exec'), {'__name__': '__main__', '__file__': str(source)})
    finally:
        sys.argv = original_argv


def smooth(value):
    if value == 0:
        return False
    for prime in (2, 3, 5):
        while value % prime == 0:
            value //= prime
    return value == 1


def problems(opcode, scalar):
    problems = []
    numerator = abs(scalar.numerator)
    if not numerator or not smooth(scalar.denominator):
        problems.append('zero_or_nonsmooth_denominator')
    if opcode == 'SCALE' and not smooth(numerator):
        problems.append('scale_not_unit')
    if abs(scalar) + 1 >= 2**16:
        problems.append('native_magnitude')
    if numerator >= 2**24:
        problems.append('fixed_tape_numerator')
    if 2 * (numerator + scalar.denominator) + 2 * (scalar.denominator // 2) >= 2**26:
        problems.append('fixed_tape_W_plus_26_rounded_work_bound')
    return problems


def literal_inventory(word):
    totals, first = Counter(), {}
    widest = largest_denominator = largest_magnitude = None
    split_count = Counter()
    for clock, event in enumerate(word['program']):
        opcode = event[0]
        if opcode not in ('ADD', 'COPY', 'SCALE'):
            continue
        scalar = Fraction(event[2] if opcode == 'SCALE' else event[3])
        witness = {'clock': clock, 'event': event, 'coefficient': str(scalar)}
        issues = problems(opcode, scalar)
        for issue in issues:
            totals[issue] += 1
            first.setdefault(issue, witness)
        if widest is None or abs(scalar.numerator) > widest[0]:
            widest = (abs(scalar.numerator), witness)
        if largest_denominator is None or scalar.denominator > largest_denominator[0]:
            largest_denominator = (scalar.denominator, witness)
        if largest_magnitude is None or abs(scalar) > largest_magnitude[0]:
            largest_magnitude = (abs(scalar), witness)
        if issues:
            integer = int(scalar)
            fraction = scalar - integer
            if opcode == 'ADD' and integer and fraction and not problems(opcode, Fraction(integer)) and not problems(opcode, fraction):
                split_count['qualifying_integer_plus_fraction_ADD'] += 1
            else:
                split_count['different_repair_required'] += 1
    control_cases = {
        'smooth_nonzero_unit_accepts': not problems('SCALE', Fraction(9, 125)),
        'nonsmooth_scale_rejects': 'scale_not_unit' in problems('SCALE', Fraction(7, 32)),
        'nonsmooth_ADD_denominator_rejects': 'zero_or_nonsmooth_denominator' in problems('ADD', Fraction(1, 7)),
        'magnitude_endpoint_rejects': 'native_magnitude' in problems('ADD', Fraction(65535)),
        'overwide_small_coefficient_rejects': problems('ADD', Fraction(2**24+1, 2**20)) == ['fixed_tape_numerator'],
    }
    need(all(control_cases.values()), 'literal guard controls')
    return {
        'failures_by_guard': totals, 'first_offending_literals': first,
        'max_numerator': widest, 'max_denominator': largest_denominator,
        'max_abs_coefficient': largest_magnitude,
        'bounded_split_screen_if_needed': split_count, 'controls': control_cases,
    }


def identity(pin):
    compressed = pin['path'].read_bytes()
    need(digest(compressed) == pin['gzip_sha256'], 'compressed word pin')
    raw = gzip.decompress(compressed)
    need(digest(raw) == pin['raw_sha256'], 'raw word pin')
    word = json.loads(raw)
    canonical = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
    need(digest(canonical) == pin['canonical_sha256'], 'canonical word pin')
    return word


def charged_total(total, sites, expected_sites, rate):
    need(sites == expected_sites and rate > 0, 'all native conversions must be charged')
    conservative_total = total + sites * rate
    return conservative_total, conservative_total < 10**9


def quick(pin, native_scale):
    path = str(pin['path'])
    word = identity(pin)
    source = {'source_pr': pin['head'], 'word_sha256': pin['raw_sha256'],
              'canonical_sha256': pin['canonical_sha256'], 'word_gzip_sha256': pin['gzip_sha256']}
    write_json(ACTIVE_OUT / 'LITERALS.json', {'scope': 'Declared literal predicates, no physical run.',
                                             **source, **literal_inventory(word)})
    del word
    caller_raw = (VENDOR / 'ODD-TYPE-AB-CALLER.json').read_bytes()
    need(digest(caller_raw) == '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc', 'pinned signed caller')
    caller = json.loads(caller_raw)
    need([e[1] for e in caller['events'] if e[0] == 'J'] == list(range(1, 18)), '17 chronological call sites')
    common = [("ROOT.parent/'word7641.json.gz'", f'Path({path!r})'),
              (ORIGINAL_COMPRESSED, pin['gzip_sha256']), (ORIGINAL_RAW, pin['raw_sha256'])]
    run_adapted('ordinary.py', [*common,
        ('    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))\n    resource.setrlimit(resource.RLIMIT_CPU, (120, 121))\n    signal.alarm(150)\n', ''),
        ("out = ROOT / 'ORDINARY-RESULT.json'", f'out = Path({str(ACTIVE_OUT / "ORDINARY.json")!r})'),
        ('lifetimes==234', f"lifetimes=={pin['lifetimes']}"),
        ('conversion_rate(10125)-conversion_rate(1125)', f'conversion_rate({native_scale})-conversion_rate(1125)'),
        ("'old':1125,'new':10125", f"'old':1125,'new':{native_scale}"),
        ("'rate_new':conversion_rate(10125)", f"'rate_new':conversion_rate({native_scale})"),
        ("'source_7641_reported_ordinary':878834276,", ''),
    ])
    run_adapted('tape_scalar.py', [*common,
        ('    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))\n    resource.setrlimit(resource.RLIMIT_CPU,(120,121));signal.alarm(150)\n', ''),
        ("out=ROOT/'TAPE-SCALAR-RESULT.json'", f'out=Path({str(ACTIVE_OUT / "TAPE-SCALAR.json")!r})'),
        ('(10125,Fraction(1,10125),odd,Fraction(1,odd))', f'({native_scale},Fraction(1,{native_scale}),odd,Fraction(1,odd))'),
        ("'scale_assumed_for_comparison':10125", f"'scale_assumed_for_comparison':{native_scale}"),
        ('Scale 10125 is the author-reported value pending independent grid outcome.', 'Scale input is separately bound by the grid receipt or marked as provisional.'),
    ])
    ordinary = json.loads((ACTIVE_OUT / 'ORDINARY.json').read_bytes())
    sites = ordinary['native_scale_comparison']['conversion_sites']
    rate = 4 * (native_scale.bit_length() + 1 + native_scale.bit_count())
    retained_total = ordinary['retained_signed_model_total']
    expected_sites = 2 * 17 * 1501
    adverse = {
        'exact_ceiling_rejected': not charged_total(10**9 - expected_sites * rate, expected_sites, expected_sites, rate)[1],
    }
    try:
        charged_total(retained_total, sites - 1, expected_sites, rate)
    except ValueError:
        adverse['omitted_conversion_rejected'] = True
    else:
        raise ValueError('omitted conversion control was accepted')
    need(all(adverse.values()), 'strict ordinary controls')
    paid_total, below_cap = charged_total(retained_total, sites, expected_sites, rate)
    write_json(ACTIVE_OUT / 'TARIFF.json', {**source,
        'scope': 'Declared 17-call model accounting. Keep the retained charge and double-charge all native conversions under the same conditional full-field tariff.',
        'native_scale': native_scale, 'native_conversion_sites': sites, 'units_per_site': rate,
        'extra_conversion_ordinary': sites * rate, 'retained_signed_model_total': retained_total,
        'conservative_total': paid_total, 'margin': 10**9 - paid_total, 'strict_ceiling_met': below_cap,
        'tape_control_arithmetic': adverse,
    })


def grid(pin, cpu, wall):
    identity(pin)
    run_adapted('qualify.py', [
        (ORIGINAL_COMPRESSED, pin['gzip_sha256']), (ORIGINAL_RAW, pin['raw_sha256']),
        ("'only pinned #7641 word is authorized'", "'only the dispatched exact word is authorized'"),
        ('(234, 50, 68)', f"({pin['lifetimes']}, 50, 68)"),
        ("'prior_7637_context': 2458,", ''),
    ], [f'--word={pin["path"]}', f'--output={ACTIVE_OUT / "GRID.json"}', f'--cpu-seconds={cpu}', f'--wall-seconds={wall}'])


def old_grid_control(pin):
    word = identity(pin)
    engine_path = VENDOR / 'independent_bounds.py'
    need(digest(engine_path.read_bytes()) == SOURCE_PINS['vendor/independent_bounds.py'], 'unchanged integer grid engine')
    spec = importlib.util.spec_from_file_location('retained_integer_grid_control', engine_path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    try:
        engine.word_run(word, scale=1125, frac=24)
    except ValueError as error:
        first_error = str(error)
    else:
        raise ValueError('insufficient inherited odd scale accepted')
    need(first_error == 'integer grid rejection at event 5650: denominator 9', 'first inherited-scale rejection')
    cut, column = 5650, 586
    coordinate = [Fraction(role == column) for role in range(word['public'] + word['owned_fields'])]
    for event in word['program'][:cut]:
        opcode, role = event[:2]
        if opcode in ('INIT', 'CLEAR'):
            coordinate[role] = Fraction(0)
        elif opcode == 'SCALE':
            coordinate[role] *= Fraction(event[2])
        elif opcode in ('ADD', 'COPY'):
            coordinate[role] += Fraction(event[3]) * coordinate[event[2]]
    event = word['program'][cut]
    need(event == ['ADD', 1300, 1298, '-10/9', 3], 'exact adverse event')
    source = coordinate[event[2]]
    coefficient = Fraction(event[3])
    product = coefficient * source
    old_tick = source * 1125 * 2**24
    need(old_tick.denominator == 1, 'original entrance coordinate integral')
    remainder = (old_tick.numerator * coefficient.numerator) % coefficient.denominator
    need(source == Fraction(2, 15) and product == Fraction(-4, 27) and remainder == 3, 'independent exact coordinate witness')
    new_tick = product * 54675 * 2**16
    need(new_tick.denominator == 1, 'fresh grid admits the adverse product')
    write_json(ACTIVE_OUT / 'OLD-GRID-CONTROL.json', {
        'status': 'PASS_SCOPED_INHERITED_GRID_REJECTION',
        'raw_word_sha256': pin['raw_sha256'], 'canonical_sha256': pin['canonical_sha256'],
        'integer_engine_sha256': SOURCE_PINS['vendor/independent_bounds.py'],
        'inherited_odd_scale': 1125, 'inherited_fractional_bits': 24, 'first_error': first_error,
        'clock': cut, 'column': column, 'event': event, 'source_coordinate_before': str(source),
        'preproduct_coordinate': str(product), 'scaled_source_integer': old_tick.numerator,
        'old_division_remainder': remainder, 'new_scaled_preproduct_integer': new_tick.numerator,
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('test', choices=('quick', 'grid', 'old-grid-control'))
    ap.add_argument('word', choices=WORDS)
    ap.add_argument('out', type=Path)
    ap.add_argument('--cpu', type=int, required=True)
    ap.add_argument('--wall', type=int, required=True)
    ap.add_argument('--scale', type=int)
    args = ap.parse_args()
    need(__debug__, 'assertions must be enabled')
    need(1 <= args.cpu <= 390 and 1 <= args.wall <= 420, 'one bounded preflight')
    need(digest((VENDOR / 'ODD-CALLER-EXACT-GRID.json').read_bytes()) == SOURCE_PINS['vendor/ODD-CALLER-EXACT-GRID.json'], 'pinned caller grid receipt')
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (args.cpu, args.cpu + 1))
    signal.alarm(args.wall)
    global ACTIVE_OUT
    ACTIVE_OUT = args.out.resolve()
    need(ACTIVE_OUT.is_relative_to(HERE), 'fresh receipt directory under app')
    ACTIVE_OUT.mkdir(parents=True, exist_ok=False)
    pin = WORDS[args.word]
    if args.test == 'quick':
        quick(pin, args.scale if args.scale is not None else pin['reported_grid'])
    elif args.test == 'grid':
        grid(pin, args.cpu, args.wall)
    else:
        need(args.word == '7636', 'old-grid witness bound to #7636')
        old_grid_control(pin)


if __name__ == '__main__':
    main()
