#!/usr/bin/env python3
"""Source-bound stopping audit; see PROOF.md for scope and universal bounds."""
from __future__ import annotations
import argparse
import ast
import sys
import hashlib
import json
from pathlib import Path
D = 10**21
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def require(condition, message):
    if not condition:
        raise ArithmeticError(message)

class Tape:
    """Bounded bit strip, charging every read, write, and unit head move."""
    def __init__(self, width, value=0):
        require(0 <= value < (1 << width), 'register overflow')
        self.bits = [(value >> i) & 1 for i in range(width)]
        self.head = 0
        self.ticks = width + 2
    def seek(self, index):
        require(0 <= index < len(self.bits), 'head outside strip')
        self.ticks += abs(self.head - index)
        self.head = index
    def read(self):
        self.ticks += 1
        return self.bits[self.head]
    def write(self, value):
        require(value in (0, 1), 'non-bit write')
        self.ticks += 1
        self.bits[self.head] = value
    def wipe(self):
        for i in range(len(self.bits)):
            self.seek(i)
            self.write(0)
        self.seek(0)
    def integer(self):
        return sum(bit << i for i, bit in enumerate(self.bits))

def copy_low(src, dst):
    require(len(src.bits) >= len(dst.bits), 'short copy source')
    for i in range(len(dst.bits)):
        src.seek(i)
        dst.seek(i)
        dst.write(src.read())
    src.seek(0)
    dst.seek(0)

def compare(a, b):
    relation = 0
    for i in range(max(len(a.bits), len(b.bits))):
        av = bv = 0
        if i < len(a.bits):
            a.seek(i)
            av = a.read()
        if i < len(b.bits):
            b.seek(i)
            bv = b.read()
        if av != bv:
            relation = 1 if av else -1
    a.seek(0)
    b.seek(0)
    return relation

def product(a, b):
    """Horner multiplication with serial shifts and finite-carry additions."""
    width = len(a.bits)
    require(len(b.bits) == width, 'unequal widths')
    before = a.ticks + b.ticks
    out = Tape(2 * width + 1)
    for i in reversed(range(width)):
        b.seek(i)
        take = b.read()
        carry = 0
        for j in range(len(out.bits)):
            out.seek(j)
            old = out.read()
            out.write(carry)
            carry = old
        require(carry == 0, 'shift overflow')
        out.seek(0)
        if take:
            carry = 0
            for j in range(len(out.bits)):
                av = 0
                if j < width:
                    a.seek(j)
                    av = a.read()
                out.seek(j)
                total = out.read() + av + carry
                out.write(total & 1)
                carry = total >> 1
            require(carry == 0, 'addition overflow')
            a.seek(0)
            out.seek(0)
    a.seek(0)
    b.seek(0)
    cost = a.ticks + b.ticks + out.ticks - before
    require(cost <= 64 * (width + 2)**2, 'serial product budget')
    return out

def lowered_le(base, power, ceiling):
    require(1 <= base <= ceiling and power > 0, 'caller domain')
    width = (ceiling + 2).bit_length()
    limit = Tape(width, ceiling)
    cap = Tape(width, ceiling + 1)
    current = Tape(width, base)
    value = Tape(width, 1)
    cap.ticks += 8 * (width + 2)
    all_tapes = [limit, cap, current, value]
    products = 0
    accepted = True
    while power:
        if power & 1:
            result = product(value, current)
            all_tapes.append(result)
            products += 1
            if compare(result, limit) > 0:
                result.wipe()
                accepted = False
                break
            copy_low(result, value)
            result.wipe()
        power //= 2
        if power:
            result = product(current, current)
            all_tapes.append(result)
            products += 1
            copy_low(cap if compare(result, limit) > 0 else result, current)
            result.wipe()
    for tape in (cap, current, value):
        tape.wipe()
    require(all(t.head == 0 for t in all_tapes), 'unrestored head')
    require(all(not any(t.bits) for t in all_tapes[1:]), 'uncleared work strip')
    ticks = sum(t.ticks for t in all_tapes)
    require(ticks <= 2**20 * (width + 2)**2, 'complete data-head budget')
    return accepted, ticks, products

def source_function(path):
    source = path.read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)
                and n.name == 'power_le')
    space = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), space)
    return space['power_le'], source

def linear_reference(base, power, ceiling):
    value = 1
    for _ in range(power):
        value *= base
        if value > ceiling:
            return False
    return True

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--runtime', type=Path, required=True)
    args = cli.parse_args()
    runtime = args.runtime.resolve()
    sys.path.insert(0, str(runtime))
    from upstream import install
    install()
    import positive
    predicate_path = Path(positive.__file__)
    caller_path = runtime / 'retimed_supplier.py'
    require(hashlib.sha256(predicate_path.read_bytes()).hexdigest() ==
            'a1b5d1725c6230667646d3e50551d566e2faac39bc39a02c703c3da065f4db5c',
            'resolved stopping predicate differs from pinned source')
    require(hashlib.sha256(caller_path.read_bytes()).hexdigest() ==
            '4bd969e3f1cfdcdf26c36e5fa7ab64c8e72904f516a51af6b2a29524e1cf8eb2',
            'stopping caller differs from pinned source')
    source_le, source_text = source_function(predicate_path)
    caller = ast.unparse(ast.parse(caller_path.read_text()))
    require('power_le(selected, self.denominator, root_width)' in caller,
            'lost actual stopping call')
    require('bundle, extra = divmod(selected, n)' in caller, 'changed child width')
    require('bundle, columns, root_width)' in caller, 'changed recursive root limit')
    require(D.bit_length() == 70 and D.bit_count() == 29, 'changed exponent')
    max_products = D.bit_length() - 1 + D.bit_count()
    require(max_products == 98, 'wrong product count')
    arithmetic_cases = 0
    for width in range(1, 7):
        for a in range(1 << width):
            for b in range(1 << width):
                at, bt = Tape(width, a), Tape(width, b)
                result = product(at, bt)
                require(result.integer() == a * b, 'bit-product mismatch')
                require(at.integer() == a and bt.integer() == b, 'input mutation')
                arithmetic_cases += 1
    source_cases = 0
    for ceiling in range(1, 97):
        for base in range(1, ceiling + 1):
            for power in range(1, 17):
                require(source_le(base, power, ceiling) ==
                        linear_reference(base, power, ceiling), 'source mismatch')
                source_cases += 1
    lowered_cases = 0
    peak_ticks = 0
    for ceiling in (1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128, 255):
        for base in sorted({1, min(2, ceiling), max(1, ceiling // 2), ceiling}):
            for power in (1, 2, 3, 7, 16, 31, D):
                answer, ticks, count = lowered_le(base, power, ceiling)
                require(answer == source_le(base, power, ceiling), 'lowering mismatch')
                require(count <= power.bit_length() - 1 + power.bit_count(),
                        'too many products')
                peak_ticks = max(peak_ticks, ticks)
                lowered_cases += 1
    require(lowered_le(1, D, 1)[2] == max_products, '98-product path untested')
    require(2**32 * (3 * D + 2)**3 < 2**256, 'coefficient overflow')
    require(2**256 * 1024**3 <= 2**1024, 'volume induction base')
    for e in range(4, 10004):
        require((e + 1)**3 <= 2 * e**3, 'cube-step corroboration')
    child_cases = 0
    for d in range(2, 10):
        for carrier in range(2, 9):
            for parent in range(carrier * (carrier + 1), carrier * (carrier + 9)):
                e = parent // carrier
                h = parent**d - 1
                require(carrier <= e and parent < carrier * (e + 1), 'child relation')
                require((h + 2).bit_length() + 2 <= (3 * d + 2) * e,
                        'parent-relative width bound')
                child_cases += 1
    mutated = source_text.replace('min(ceiling + 1, base * base)',
                                  'min(ceiling, base * base)')
    node = next(n for n in ast.parse(mutated).body if isinstance(n, ast.FunctionDef)
                and n.name == 'power_le')
    env = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'cap-mutant', 'exec'), env)
    require(env['power_le'](2, 2, 3) and not source_le(2, 2, 3), 'cap mutant escaped')
    require(source_le(2, 3, 8) and not (2**3 < 8), 'equality mutant escaped')
    require(((1 << 4096) + 2).bit_length() + 2 > (3 * 3 + 2) * 5,
            'missing-parent-premise control escaped')
    print(json.dumps({
        'status': 'PASS_STOPPING_CONTROL_AUDIT',
        'source_sha256': hashlib.sha256(predicate_path.read_bytes()).hexdigest(),
        'caller_sha256': hashlib.sha256(caller_path.read_bytes()).hexdigest(),
        'D': str(D), 'exponent_bits': 70, 'max_products': max_products,
        'serial_product_cases': arithmetic_cases,
        'source_against_linear_cases': source_cases,
        'lowered_cases': lowered_cases, 'maximum_model_data_ticks': peak_ticks,
        'child_relation_cases': child_cases,
        'negative_controls': ['cap_h_instead_of_h_plus_1', 'strict_equality',
                              'missing_parent_failed_test'],
        'scope': 'stopping control; no new kappa; no global storage proof'
    }, indent=2))

if __name__ == '__main__':
    main()
