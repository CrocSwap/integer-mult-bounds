#!/usr/bin/env python3
"""Run bit589's native step (tune/verify.sh step 4) without Boost, and check it.

The pinned verify.sh preamble, its step-3 adapt.py command and its step-4 block
run verbatim under bash with BOOST_INCLUDE set to this package's checked cpp_int
stand-in. The step-4 output must equal the committed Boost-built bit589.log and
columns_k4.json receipts. Further checks: the stand-in is the header actually
compiled, every negative control is rejected by the checkers rather than the
stand-in, an over-range control is refused, and a seeded differential test
against Python integers passes. With --boost-include, step 4 also runs against
real Boost and every receipt must match.

Sagar Thakrar with substantial Anthropic Claude assistance. Apache-2.0.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INCLUDE = PACKAGE/'include'
TUNE = ROOT/'research/e8-bit-p111-tuned/tune'
SKELETON = ROOT/'research/e8-bit-carrier-skeleton'
CHECKERS = SKELETON/'code/bit/checkers'
BOOST_K4 = ROOT/'research/community-frontier741-audit/bit/cout/columns_k4.json'
BOOST_LOG = ROOT/'research/community-frontier741-audit/bit589.log'
EXPECTED = json.loads((PACKAGE/'EXPECTED.json').read_bytes())
REFUSAL = 'checked cpp_int stand-in: 128-bit range exceeded'
OPS = ['add', 'sub', 'mul', 'imul', 'neg', 'shl', 'cmp', 'msb', 'add8', 'sub8', 'neg8',
       'shleq', 'shlbig', 'shlneg', 'hex']
PROBE = '''#include <boost/multiprecision/cpp_int.hpp>
#ifndef INTEGER_MULT_CHECKED_CPP_INT_STANDIN
#error "the checked stand-in is not the cpp_int header being compiled"
#endif
int main() { return 0; }
'''
HARNESS = '''#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <string>
using boost::multiprecision::cpp_int;
static cpp_int mk(long long h, long long l) { return cpp_int(h) * (cpp_int(1) << 62) + cpp_int(l); }
int main() {
  std::string op; long long ah, al, bh, bl;
  while (std::cin >> op >> ah >> al >> bh >> bl) {
    cpp_int a = mk(ah, al), b = mk(bh, bl);
    if (op == "add") { cpp_int c = a; c += b; std::cout << c.convert_to<std::string>() << "\\n"; }
    else if (op == "sub") std::cout << (a - b).convert_to<std::string>() << "\\n";
    else if (op == "mul") std::cout << (a * b).convert_to<std::string>() << "\\n";
    else if (op == "imul") std::cout << (bl * a).convert_to<std::string>() << "\\n";
    else if (op == "neg") std::cout << (-a).str() << "\\n";
    else if (op == "add8") { cpp_int c = a * 8; c += b * 8; std::cout << c << "\\n"; }
    else if (op == "sub8") std::cout << (a * 8 - b * 8) << "\\n";
    else if (op == "neg8") std::cout << -(a * 8) << "\\n";
    else if (op == "shl") std::cout << (a << (int)bl).convert_to<std::string>() << "\\n";
    else if (op == "shleq") { cpp_int c = a; c <<= bl; std::cout << c.str() << "\\n"; }
    else if (op == "shlbig") std::cout << (a << ((1LL << 32) + bl)).str() << "\\n";
    else if (op == "shlneg") std::cout << (a << (-1 - bl)).str() << "\\n";
    else if (op == "hex") std::cout << std::hex << a << "\\n";
    else if (op == "cmp") std::cout << (a < b) << (a > b) << (a == b) << (a <= b) << (a >= b) << (a != b) << bool(a) << "\\n";
    else if (op == "msb") std::cout << boost::multiprecision::msb(a) << "\\n";
    std::cout.flush();
  }
}
'''


def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)


def digest(data):
    return sha256(data).hexdigest()


def run(argv, **kw):
    return subprocess.run([str(a) for a in argv], capture_output=True, text=True, **kw)


def check_pins():
    rows = [r for r in json.loads((PACKAGE/'SOURCES.json').read_bytes())['files'] if r['usage'] == 'input']
    for row in rows:
        require(digest((ROOT/row['path']).read_bytes()) == row['sha256'], 'Pinned input: ' + row['path'])
    return len(rows)


def step4_script():
    """The pinned preamble, step-3 adapt.py command and step-4 block of tune/verify.sh."""
    lines = (TUNE/'verify.sh').read_text().splitlines()
    def index(predicate, what):
        found = [i for i, line in enumerate(lines) if predicate(line)]
        require(len(found) == 1, 'verify.sh marker not unique: ' + what)
        return found[0]
    start = index(lambda s: s == 'set -euo pipefail', 'set')
    helper = index(lambda s: s.startswith('step() {'), 'step()')
    adapt = index(lambda s: s.startswith('$PY $A545/adapt.py $P $WORD $WD/ad545'), 'adapt')
    four = index(lambda s: s.startswith('step "4.'), 'step 4')
    five = index(lambda s: s.startswith('step "5.'), 'step 5')
    require(start < helper < adapt < four < five, 'verify.sh step order')
    text = '\n'.join(lines[start:helper+1] + [lines[adapt]] + lines[four:five]) + '\n'
    require(digest(text.encode()) == EXPECTED['composed_step4_sha256'], 'Composed step-4 script differs from pin')
    return text


def section(text, header):
    """Lines from the `== <header>` line to the next `== ` line, timing removed."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith('== '):
            if inside:
                break
            inside = line.startswith('== ' + header)
        if inside:
            out.append(re.sub(r'  \[\d+s\]$', '', line))
    return out


def receipt(path):
    value = json.loads(Path(path).read_bytes())
    for name in EXPECTED['nondeterministic_fields']:
        value.pop(name)
    return value


def compile_probe(cxx, includes, work):
    source = work/'probe.cpp'
    source.write_text(PROBE)
    flags = [f for d in includes for f in ('-I', d)]
    return run([cxx, '-std=c++17', *flags, '-fsyntax-only', source])


def run_step4(script, wd, cxx, boost):
    env = {k: v for k, v in os.environ.items() if k not in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONSAFEPATH')}
    env.update(BOOST_INCLUDE=str(boost), PYTHON=sys.executable, CXX=cxx)
    p = run(['bash', '-c', script, TUNE/'verify.sh', wd], env=env, timeout=600)
    require(p.returncode == 0, 'Step 4 failed:\n' + p.stdout[-2000:] + p.stderr[-2000:])
    return p.stdout


def controls_from_checkers(wd):
    """Rerun both mutation suites with full output; rejections must not come from the stand-in."""
    word, bins = TUNE/'bitE8mut-p111-tuned.json.gz', wd/'bin'
    v, r = (json.loads(__import__('gzip').decompress(word.read_bytes()))[k] for k in ('v', 'R'))
    py = [sys.executable, '-I', '-B']
    suites = [
        [*py, wd/'ad545/mutate_records.py', wd/'records', wd/'cin', wd/'cout', bins/'legality',
         bins/'columns_k5', bins/'legality_ncopy_h'],
        [*py, ROOT/'research/e8-bit-p111-tuned/code/mutrec_b.py', word, wd/'records', wd/'cin', wd/'cout',
         bins/'legality', bins/f'columns_h_{v}_{r}', bins/'columns_k4', bins/'columns_k5'],
    ]
    lasts = []
    for argv in suites:
        p = run(argv, timeout=600)
        require(p.returncode == 0, 'Mutation suite failed: ' + p.stderr[-1000:])
        require(REFUSAL not in p.stdout + p.stderr, 'A negative control was rejected by the stand-in, not the checker')
        lasts.append(p.stdout.strip().splitlines()[-1])
    return v, r, lasts


def overflow_control(wd, v, r):
    """Every ADD coefficient set to +-2^30: the stand-in must refuse, never wrap."""
    raw = (wd/'cout/COHORT249-RECORDS.bin').read_bytes()
    width = struct.calcsize('=6i')
    require(len(raw) % width == 0, 'record stream alignment')
    out, adds = bytearray(), 0
    for i in range(0, len(raw), width):
        rec = list(struct.unpack('=6i', raw[i:i+width]))
        if rec[0] == 1:
            rec[3] = (1 << 30) if adds % 2 == 0 else -(1 << 30)
            adds += 1
        out += struct.pack('=6i', *rec)
    require(adds > 0, 'no ADD records found')
    mutated = wd/'overflow-RECORDS.bin'
    mutated.write_bytes(bytes(out))
    p = run([wd/'bin'/f'columns_h_{v}_{r}', mutated, wd/'overflow.json'], timeout=120)
    require(p.returncode != 0 and REFUSAL in p.stderr and not (wd/'overflow.json').exists(),
            'Over-range control was not refused by the stand-in')
    return adds


def differential(cxx, work, include):
    source = work/'harness.cpp'
    source.write_text(HARNESS)
    binary = work/'harness'
    p = run([cxx, '-O2', '-std=c++17', '-I', include, '-o', binary, source], timeout=300)
    require(p.returncode == 0, 'Harness build failed: ' + p.stderr[-1000:])
    spec = EXPECTED['differential']
    rng, limit = random.Random(spec['seed']), 1 << 127
    def operand():
        bits = rng.choice([1, 8, 30, 62, 64, 100, 124])  # high word stays within long long
        return divmod(rng.randrange(-(1 << bits), 1 << bits), 1 << 62)
    def expect(op, a, b, bl):
        """(expected output, or None for a required refusal; whether a refusal is within 2x of the bound)."""
        if op == 'cmp':
            return ''.join(str(int(x)) for x in (a < b, a > b, a == b, a <= b, a >= b, a != b, a != 0)), False
        if op == 'msb':
            return (str(a.bit_length() - 1) if a > 0 else None), False
        if op in ('hex', 'shlneg'):
            return None, False
        if op == 'shlbig':
            return ('0' if a == 0 else None), False
        if op == 'shleq':
            op = 'shl'
        if op == 'shl' and a < 0:
            return None, False
        if op.endswith('8'):
            a, b, op = 8*a, 8*b, op[:-1]
            if not (-limit <= a < limit and (op == 'neg' or -limit <= b < limit)):
                return None, max(abs(a), abs(b) if op != 'neg' else 0) < 2*limit
        value = dict(add=a+b, sub=a-b, mul=a*b, imul=bl*a, neg=-a, shl=a << bl if op == 'shl' else 0)[op]
        return (str(value), False) if -limit <= value < limit else (None, abs(value) < 2*limit)
    inside, outside, near = [], {op: [] for op in OPS}, []
    def add(op, ah, al, bh, bl):
        out, close = expect(op, ah*(1 << 62)+al, bh*(1 << 62)+bl, bl)
        row = (op, ah, al, bh, bl, out)
        if out is not None:
            inside.append(row)
        else:
            outside[op].append(row)
            if close:
                near.append(row)
    for _ in range(spec['operations']):
        op = rng.choice(OPS)
        (ah, al), (bh, bl) = operand(), operand()
        if op in ('shl', 'shleq'):
            bh, bl = 0, rng.randrange(0, 130)
        if op == 'shlbig':
            bh, bl = 0, rng.randrange(0, 64)
        if op in ('imul', 'shlneg'):
            bh, bl = 0, rng.randrange(0, 1 << 62)
        add(op, ah, al, bh, bl)
    # Fixed rows: values at -2^127 and 2^127 - 1, shifts that end exactly at or below 2^127,
    # zero shifted far, multiples of 2^64 (zero low word) and pairs sharing a high word.
    low, high = divmod(-(1 << 124), 1 << 62), divmod((1 << 124) - 1, 1 << 62)
    w = (4, 0)  # 2^64
    for op, (ah, al), (bh, bl) in [
            ('neg8', low, (0, 0)), ('add8', low, (0, 0)), ('add8', high, high), ('sub8', low, (0, 1)),
            ('sub8', high, low), ('add8', low, low), ('sub8', (0, 0), low), ('msb', high, (0, 0)),
            ('shl', (0, 0), (0, 129)), ('shleq', (0, 0), (0, 200)), ('shlbig', (0, 0), (0, 5)),
            ('shlneg', (0, 0), (0, 0)), ('shl', (0, 1), (0, 126)), ('shleq', (0, 1), (0, 126)),
            ('shl', (0, 1), (0, 127)), ('shleq', (0, 1), (0, 127)), ('shl', high, (0, 3)), ('shl', high, (0, 4)),
            ('shleq', high, (0, 4)), ('shl', (1, 0), (0, 64)), ('shl', (1, 0), (0, 65)),
            ('cmp', w, (0, 0)), ('cmp', (-4, 0), w), ('cmp', (4, 5), (4, 3)), ('cmp', (4, 3), (4, 5)),
            ('cmp', (-4, 5), (-4, 3)), ('cmp', (1 << 42, 7), (1 << 42, 9)), ('cmp', (1 << 42, 9), (1 << 42, 7)),
            ('add', w, (-4, 0)), ('sub', w, (8, 0)), ('add', (-8, 0), w), ('neg', w, (0, 0)),
            ('msb', w, (0, 0)), ('mul', w, (1, 0)), ('mul', w, (2, 0)), ('mul', (-4, 0), (2, 0)),
            ('imul', w, (0, 1 << 61))]:
        add(op, ah, al, bh, bl)
    feed = ''.join('%s %d %d %d %d\n' % row[:5] for row in inside)
    p = run([binary], input=feed, timeout=300)
    got = p.stdout.split('\n')[:len(inside)]
    require(p.returncode == 0 and got == [row[5] for row in inside], 'Stand-in differs from Python integers')
    # Every near-bound refusal runs, plus a per-operation sample so that every refusal path is exercised.
    sample = list(dict.fromkeys(near + [row for op in OPS for row in outside[op][:spec['refusals_per_operation']]]))
    require({row[0] for row in sample} == set(EXPECTED['refusing_operations']), 'Refusal coverage by operation')
    counts = [len(inside), len(near), len(sample)]
    require(counts == spec['counts'], 'Differential coverage changed: ' + str(counts))
    for row in sample:
        q = run([binary], input='%s %d %d %d %d\n' % row[:5], timeout=30)
        require(q.returncode != 0 and q.stdout == '', 'Out-of-range operation was not refused: ' + str(row[:5]))
    return len(inside), len(near), len(sample)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--boost-include', type=Path, help='also compare against real Boost headers')
    parser.add_argument('--include', type=Path, default=INCLUDE, help=argparse.SUPPRESS)  # mutants.py only
    args = parser.parse_args()
    include = args.include.resolve()
    require(sys.version_info >= (3, 11) and not sys.flags.optimize, 'Python 3.11+ with assertions')
    require(' ' not in str(ROOT), 'The pinned verify.sh expands paths unquoted; use a checkout path without spaces')
    pins = check_pins()
    cxx = os.environ.get('CXX', 'c++')
    require(shutil.which(cxx) and shutil.which('bash'), 'Needs bash and a C++17 compiler (CXX, default c++)')
    version = run([cxx, '--version']).stdout.splitlines()[0]
    script = step4_script()
    expected_lines = section(BOOST_LOG.read_text(), '4.')
    require(len(expected_lines) == EXPECTED['step4_log_lines'], 'Committed Boost log section')
    with tempfile.TemporaryDirectory(prefix='bit589-standin-') as tmp:
        work = Path(tmp)
        require(' ' not in str(work), 'Temporary directory path contains spaces; set TMPDIR')
        includes = [SKELETON/'portable-include', CHECKERS, include]
        p = compile_probe(cxx, includes, work)
        require(p.returncode == 0, 'Include order does not select the stand-in: ' + p.stderr[-500:])
        wd = work/'standin'
        output = run_step4(script, wd, cxx, include)
        require(section(output, '4.') == expected_lines, 'Step-4 output differs from the committed Boost log')
        require(receipt(wd/'cout/columns_k4.json') == receipt(BOOST_K4),
                'columns_k4.json differs from the committed Boost receipt')
        v, r, lasts = controls_from_checkers(wd)
        require(lasts == EXPECTED['mutation_suite_last_lines'], 'Mutation suite summaries')
        adds = overflow_control(wd, v, r)
        checked, near, refused = differential(cxx, work, include)
        compared = 'committed Boost receipts'
        if args.boost_include:
            p = compile_probe(cxx, [SKELETON/'portable-include', CHECKERS, args.boost_include], work)
            require(p.returncode != 0, '--boost-include resolves to the stand-in, not real Boost')
            boost = run_step4(script, work/'boost', cxx, args.boost_include.resolve())
            require(section(boost, '4.') == section(output, '4.'), 'Step-4 output differs from real Boost')
            for name in sorted(p.name for p in (wd/'cout').glob('*.json')):
                require(receipt(work/'boost/cout'/name) == receipt(wd/'cout'/name)
                        if name.startswith('columns') else
                        json.loads((work/'boost/cout'/name).read_bytes()) == json.loads((wd/'cout'/name).read_bytes()),
                        'Receipt differs from real Boost: ' + name)
            compared += ' and a real-Boost rerun'
    print('compiler:', version)
    print('pinned inputs:', pins, '| step-4 log lines equal:', len(expected_lines), '| columns_k4.json equal')
    print('mutation suites:', ' / '.join(lasts))
    print('over-range control refused with', adds, 'ADD coefficients at +-2^30')
    print('differential: %d in-range operations equal to Python integers, %d refusals (%d within 2x of the bound)'
          % (checked, refused, near))
    print('PASS_BIT589_STEP4_CHECKED_CPP_INT_STANDIN', 'matches', compared)


if __name__ == '__main__':
    main()
