#!/usr/bin/env python3
"""Opt-in checks of verify.py itself (not registered; about two minutes).

Default: apply each listed mutation to a temporary copy of the stand-in header
and run verify.py against it. Every mutant must be rejected except the one
recorded as equivalent. --ubsan: run verify.py once with every binary built
with -fsanitize=undefined -fno-sanitize-recover=undefined, after a positive
control shows that the sanitizer is active.

Sagar Thakrar with substantial Anthropic Claude assistance. Apache-2.0.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
HEADER = PACKAGE/'include/boost/multiprecision/cpp_int.hpp'
VERIFY = PACKAGE/'verify.py'
# (name, original text, replacement, rejected by verify.py)
MUTANTS = [
    ('mul wraps', 'if (__builtin_mul_overflow(v_, o.v_, &v_)) refuse("*");', '(void)__builtin_mul_overflow(v_, o.v_, &v_);', True),
    ('add wraps', 'if (__builtin_add_overflow(v_, o.v_, &v_)) refuse("+");', '(void)__builtin_add_overflow(v_, o.v_, &v_);', True),
    ('sub wraps', 'if (__builtin_sub_overflow(v_, o.v_, &v_)) refuse("-");', '(void)__builtin_sub_overflow(v_, o.v_, &v_);', True),
    ('unary minus wraps', 'if (__builtin_sub_overflow(static_cast<__int128>(0), v_, &r.v_)) refuse("unary -");',
     '(void)__builtin_sub_overflow(static_cast<__int128>(0), v_, &r.v_);', True),
    ('shift range unchecked', '    if (static_cast<unsigned long long>(s) >= 127 || (v_ >> (127 - static_cast<int>(s))) != 0) refuse("<<");\n', '', True),
    ('shift wraps into the sign bit', '>= 127 || (v_ >> (127 - static_cast<int>(s)))', '>= 128 || (s > 0 && (v_ >> (128 - static_cast<int>(s))))', True),
    ('shift count narrowed', 'static_cast<unsigned long long>(s) >= 127', 'static_cast<unsigned>(s) >= 127', True),
    ('negative count accepted', '    if (s < static_cast<T>(0)) refuse("<< by a negative count");\n', '', True),
    ('zero shift falls through', '    if (v_ == 0) return *this;\n', '', True),
    # Equivalent: negative counts are refused first and the range check refuses every negative value.
    ('negative value guard removed', '    if (v_ < 0) refuse("<< of a negative value");\n', '', False),
    ('stream flags ignored', '      refuse("stream output with non-default format flags");', '      (void)0;', True),
    ('msb off by one', '  std::size_t i = 0;\n', '  std::size_t i = 1;\n', True),
    ('msb of zero accepted', '  if (x.sign() <= 0) throw', '  if (false) throw', True),
    ('str drops the sign', "    if (v_ < 0) s.insert(s.begin(), '-');\n", '', True),
    ('< implemented as <=', 'return a.v_ < b.v_; }', 'return a.v_ <= b.v_; }', True),
    ('bool truncated to 64 bits', 'explicit operator bool() const { return v_ != 0; }',
     'explicit operator bool() const { return static_cast<unsigned long long>(v_) != 0; }', True),
    ('> ignores a shared high word', 'return a.v_ > b.v_; }',
     'return (a.v_ >> 64) == (b.v_ >> 64) && (a.v_ >> 64) > 0 ? false : a.v_ > b.v_; }', True),
]


def verify(include=None, env=None):
    argv = [sys.executable, '-B', str(VERIFY)] + (['--include', str(include)] if include else [])
    p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=1200)
    return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1]


def mutants():
    source = HEADER.read_text()
    wrong = []
    with tempfile.TemporaryDirectory(prefix='standin-mutants-') as tmp:
        target = Path(tmp)/'include/boost/multiprecision/cpp_int.hpp'
        target.parent.mkdir(parents=True)
        for name, old, new, rejected in MUTANTS:
            if source.count(old) != 1:
                raise SystemExit('FAIL: mutation anchor not unique: ' + name)
            target.write_text(source.replace(old, new))
            code, last = verify(Path(tmp)/'include')
            print(('rejected ' if code else 'accepted ') + name + ' | ' + last[:100], flush=True)
            if bool(code) != rejected:
                wrong.append(name)
    if wrong:
        raise SystemExit('FAIL: unexpected mutant outcomes: ' + ', '.join(wrong))
    print('PASS_STANDIN_MUTANTS', sum(m[3] for m in MUTANTS), 'rejected,', sum(not m[3] for m in MUTANTS), 'equivalent accepted')


def ubsan():
    cxx = os.environ.get('CXX', 'c++')
    with tempfile.TemporaryDirectory(prefix='standin-ubsan-') as tmp:
        wrapper = Path(tmp)/'cxx'
        wrapper.write_text('#!/bin/sh\nexec %s -fsanitize=undefined -fno-sanitize-recover=undefined "$@"\n' % cxx)
        wrapper.chmod(0o755)
        probe = Path(tmp)/'probe.cpp'
        probe.write_text('int main(int c, char**) { __int128 x = 1; x <<= 190 + c; return (int)x; }\n')
        subprocess.run([str(wrapper), '-o', str(Path(tmp)/'probe'), str(probe)], check=True)
        p = subprocess.run([str(Path(tmp)/'probe')], capture_output=True, text=True)
        if p.returncode == 0 or 'runtime error' not in p.stderr:
            raise SystemExit('FAIL: the sanitizer positive control was not reported')
        code, last = verify(env=dict(os.environ, CXX=str(wrapper)))
        if code:
            raise SystemExit('FAIL: verify.py under UBSan: ' + last)
    print('PASS_STANDIN_UBSAN positive control reported; verify.py passed with every binary sanitized')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ubsan', action='store_true')
    ubsan() if parser.parse_args().ubsan else mutants()
