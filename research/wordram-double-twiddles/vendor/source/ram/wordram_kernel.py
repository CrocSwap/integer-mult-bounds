"""Literal tcslib WordRAM.Basic ISA programs; Python is only the assembler/interpreter.
Original implementation, 2026. See PROOFS.txt for contracts and source attribution.
"""
from collections import Counter
from dataclasses import dataclass

W = 64
MODULUS = 65537
MASK = (1 << W) - 1
ZERO, ONE, VALUE, TEMP = 10, 11, 8, 9
CONSTANTS = tuple(range(20, 36))
SCRATCH = frozenset((ZERO, ONE, VALUE, TEMP, *CONSTANTS))

@dataclass
class Execution:
    accepted: bool
    memory: dict
    steps: int
    counts: dict
    writes: frozenset

def signed(x):
    x &= MASK
    return x if x < (1 << (W - 1)) else x - (1 << W)

def run(program, memory, budget=None):
    """Match WordRAM.exec at W=64, including signed indirect addresses and halt step.
    Memory is a finite support dict; unspecified cells contain zero. No native %
    reduction/division/shift is an interpreted instruction.
    """
    m = {a: v & MASK for a, v in memory.items()}
    pc = steps = 0
    counts, writes = Counter(), set()
    budget = len(program) + 1 if budget is None else budget
    def read(a):
        return m.get(a, 0)
    while steps < budget:
        ins = program[pc] if 0 <= pc < len(program) else ('reject',)
        op, *args = ins
        steps += 1
        counts[op] += 1
        if op in ('accept', 'reject'):
            return Execution(op == 'accept', m, steps, dict(counts), frozenset(writes))
        next_pc = pc + 1
        if op == 'bltz':
            a, label = args
            if signed(read(a)) < 0:
                next_pc = label
        else:
            i = args[0]
            if op == 'one':
                value = 1
            elif op == 'add':
                value = read(args[1]) + read(args[2])
            elif op == 'sub':
                value = read(args[1]) - read(args[2])
            elif op == 'mul':
                value = read(args[1]) * read(args[2])
            elif op == 'load':
                value = read(signed(read(args[1])))
            elif op == 'store':
                i = signed(read(args[0]))
                value = read(args[1])
            else:
                raise ValueError('Unknown tcslib instruction: ' + str(op))
            m[i] = value & MASK
            writes.add(i)
        pc = next_pc
    return None

class Builder:
    """Forward-only literal assembler. Branch targets are absolute program indices.
    All cells except reserved SCRATCH may be chosen by the caller; fresh/disjoint
    input/output cells are required for butterfly. `setup` is exactly 35 instructions.
    Constants remain valid until cleanup. `literal` charges every construction op.
    """
    def __init__(self):
        self.code = []
        self.ready = False
    def emit(self, *ins):
        self.code.append(tuple(ins))
    def setup(self):
        if self.ready:
            raise ValueError('Setup already live')
        self.emit('one', ONE)
        self.emit('sub', ZERO, ONE, ONE)
        self.emit('one', CONSTANTS[0])
        for _ in range(16):
            self.emit('add', CONSTANTS[0], CONSTANTS[0], CONSTANTS[0])
        self.emit('add', CONSTANTS[0], CONSTANTS[0], ONE)
        for src, dst in zip(CONSTANTS, CONSTANTS[1:]):
            self.emit('add', dst, src, src)
        self.ready = True
    def literal(self, dst, value):
        if not self.ready or dst in SCRATCH or not 0 <= value < (1 << 63):
            raise ValueError('Bad literal contract')
        if value == 0:
            self.emit('sub', dst, ZERO, ZERO)
        else:
            self.emit('one', dst)
            for bit in bin(value)[3:]:
                self.emit('add', dst, dst, dst)
                if bit == '1':
                    self.emit('add', dst, dst, ONE)
    def copy(self, dst, src):
        if not self.ready or dst in SCRATCH:
            raise ValueError('Bad copy contract')
        self.emit('add', dst, src, ZERO)
    def _reduce_once(self, value, constant):
        self.emit('sub', TEMP, value, constant)
        self.emit('bltz', TEMP, len(self.code) + 2)
        self.emit('add', value, TEMP, ZERO)
    def _mul(self, a, b, out):
        self.emit('mul', out, a, b)
        for constant in reversed(CONSTANTS):
            self._reduce_once(out, constant)
    def mul(self, a, b, out):
        if not self.ready or {a, b, out} & SCRATCH:
            raise ValueError('Bad multiplication ABI')
        self._mul(a, b, out)
    def butterfly(self, u, b, twiddle, plus, minus, fused=True):
        cells = {u, b, twiddle, plus, minus}
        if not self.ready or cells & SCRATCH or plus == minus or {plus, minus} & {u, b, twiddle}:
            raise ValueError('Butterfly requires fresh output cells')
        self._mul(b, twiddle, VALUE)
        self.emit('add', plus, u, VALUE)
        self._reduce_once(plus, CONSTANTS[0])
        if not fused:
            self._mul(b, twiddle, VALUE)
        self.emit('add', minus, u, CONSTANTS[0])
        self.emit('sub', minus, minus, VALUE)
        self._reduce_once(minus, CONSTANTS[0])
    def cleanup(self):
        if not self.ready:
            raise ValueError('Setup not live')
        # ZERO was set to zero and never subsequently changed.
        for cell in sorted(SCRATCH - {ZERO}):
            self.emit('sub', cell, cell, cell)
        self.ready = False
    def accept(self):
        self.emit('accept')
    def program(self):
        return list(self.code)

def multiply_program():
    b = Builder(); b.setup(); b.mul(0, 1, 3); b.cleanup(); b.accept()
    return b.program()

def butterfly_program(fused=True):
    b = Builder(); b.setup(); b.butterfly(0, 1, 2, 3, 4, fused=fused); b.cleanup(); b.accept()
    return b.program()

if __name__ == '__main__':
    p = butterfly_program()
    result = run(p, {0: 65536, 1: 65536, 2: 65536})
    print({'static_instructions': len(p), 'dynamic_instructions': result.steps,
           'outputs': [result.memory[3], result.memory[4]]})
