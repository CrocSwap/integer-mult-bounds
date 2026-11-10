"""Export the retained local_layer Beneš prefix as one complete global program.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The routing compiler and fixed words are Vlado Vojdanovski's retained source.
This module prepares encoded controls; it never evaluates a payload transform.
"""
from dataclasses import dataclass, field

END, HADAMARD, SIGNS, HALF = range(4)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def address(value, mapping):
    result = value
    for old, new in mapping.items():
        result &= ~(1 << new)
        result |= ((value >> old) & 1) << new
    return result


@dataclass(frozen=True)
class Layout:
    """Original complete long axes, numbered from the least significant end."""
    lengths: tuple
    local_bits: int

    def __post_init__(self):
        need(type(self.local_bits) is int and self.local_bits >= 1, "positive local width")
        need(bool(self.lengths) and all(type(a) is int and a >= self.local_bits for a in self.lengths),
             "complete original axes contain every local bit")

    @property
    def n(self):
        return sum(self.lengths)

    @property
    def g(self):
        return len(self.lengths)

    @property
    def starts(self):
        total = 0
        values = []
        for width in self.lengths:
            values.append(total)
            total += width
        return tuple(values)

    @property
    def local_positions(self):
        return tuple(start + bit for start in self.starts for bit in range(self.local_bits))

    @property
    def gather(self):
        source = self.local_positions
        target = tuple(range(len(source)))
        mapping = dict(zip(source, target))
        mapping.update(zip(sorted(set(target)-set(source)), sorted(set(source)-set(target))))
        need(set(mapping) == set(mapping.values()), "support-local coordinate bijection")
        return mapping

    @property
    def inverse(self):
        return {new: old for old, new in self.gather.items()}

    def coarse_label(self, packed_label):
        raw = address(packed_label << (self.g*self.local_bits), self.inverse)
        return tuple((raw >> (start+self.local_bits)) & ((1 << (width-self.local_bits))-1)
                     for start, width in zip(self.starts, self.lengths))

    @property
    def labels(self):
        return tuple(self.coarse_label(c) for c in range(1 << (self.n-self.g*self.local_bits)))


@dataclass(frozen=True)
class GlobalProgram:
    layout: Layout
    stages: tuple
    permutations: tuple
    source_stage_count: int
    compiler: object = field(repr=False, compare=False)

    def export(self):
        layout = self.layout
        return {
            "original_axis_lengths": list(layout.lengths),
            "local_bits": layout.local_bits,
            "global_binary_bits": layout.n,
            "selected_axes": layout.g,
            "complete_coarse_labels": [list(x) for x in layout.labels],
            "forward_low_bit_gather": sorted(layout.gather.items()),
            "inverse_low_bit_gather": sorted(layout.inverse.items()),
            "moved_support_at_most": 2*layout.g*layout.local_bits,
            "source_local_layer_prefix_stages": self.source_stage_count,
            "global_stages": [
                {"kind": "H", "original_selected": [layout.starts[a]+bit for a, bit in enumerate(value)],
                 "caller_selected": [a*layout.local_bits+bit for a, bit in enumerate(value)],
                 "normalization": "raw H=(2 H0) tensor g"}
                if kind == HADAMARD else
                {"kind": "D", "axis_sign_tables": value, "frame": "restored caller low-bit gather"}
                if kind == SIGNS else
                {"kind": "D", "exact_divisor": 1 << layout.g, "output_component_bits": "original"}
                for kind, value in self.stages],
            "backend": "t74-support-composition.ComposedRoot.run",
            "stock": "actual root plan stock; every nested Ordinary.run selects, pads and returns its own stock",
            "return": "inverse low-bit gather, protected distinct output; borrowed payload and program restored",
            "preparation": "complete coarse-label tables; local source prefixes regenerated in stage-major order",
        }


def source_prefix(compiler, local_bits, permutation, identity_word):
    n = 1 << local_bits
    inverse = [0]*n
    for old, new in enumerate(permutation):
        inverse[new] = old
    pairs = [(inverse[2*j], inverse[2*j+1]) for j in range(n//2)]
    emitted = compiler.local_layer(n, pairs, [identity_word]*(n//2))
    depth = 2*local_bits-1
    need(len(emitted) == 8*depth+13, "actual source matching-layer shape")
    return emitted[:4*depth]


def compile_route(compiler, layout, permutations):
    """Consume actual local_layer outputs, with one network per axis and label.

    permutations[label][axis][i] is the desired image of local wire i. Label
    order is the physical packed coarse-prefix order, not a silently sorted
    original-label order. No selected support is accepted as an extra input.
    """
    n = 1 << layout.local_bits
    need(len(permutations) == len(layout.labels), "all complete coarse-label tables")
    depth = 2*layout.local_bits-1
    prefixes = []
    normalized = []
    identity_word = compiler.gateword("diag", (1, 1))
    for group in permutations:
        need(len(group) == layout.g, "one source circuit per actual axis")
        row, saved = [], []
        for permutation in group:
            need(len(permutation) == n and all(type(i) is int for i in permutation)
                 and sorted(permutation) == list(range(n)), "complete original local permutation")
            row.append(source_prefix(compiler, layout.local_bits, permutation, identity_word))
            saved.append(tuple(permutation))
        prefixes.append(row)
        normalized.append(tuple(saved))
    stages = []
    for step in range(4*depth):
        nodes = [[prefixes[c][a][step] for a in range(layout.g)] for c in range(len(prefixes))]
        kinds = {op[0] for row in nodes for op in row}
        need(len(kinds) == 1, "one global source stage on all coarse labels")
        if kinds == {"H"}:
            bits = tuple(nodes[0][a][1] for a in range(layout.g))
            need(all(tuple(op[1] for op in row) == bits for row in nodes),
                 "label-independent Hadamard schedule")
            need(all(type(bit) is int and 0 <= bit < layout.local_bits for bit in bits),
                 "source Hadamard bits lie in original local coordinates")
            stages.append((HADAMARD, bits))
        else:
            need(kinds == {"D"} and all(len(op[1]) == n for row in nodes for op in row),
                 "complete source diagonal tables")
            values = [entry for row in nodes for op in row for entry in op[1]]
            if all(entry in (-1, 1) for entry in values):
                signs = tuple(tuple(tuple(0 if entry == 1 else 1 for entry in op[1]) for op in row)
                              for row in nodes)
                stages.append((SIGNS, signs))
            else:
                need(all(entry == compiler.s.Rational(1, 2) for entry in values),
                     "retained switch normalization only")
                stages.append((HALF, None))
    need([kind for kind, _ in stages] == [HADAMARD, SIGNS, HADAMARD, HALF]*depth,
         "complete emitted switch boundaries")
    return GlobalProgram(layout, tuple(stages), tuple(normalized), 4*depth, compiler)


def encode_controls(program, tape_factory):
    """Prepare control tapes by sequential passes through the local inputs.

    Regenerating one local prefix at a time avoids a constant-time global
    table lookup in the preparation cost. The enclosing passes and this
    deliberately conservative extra source work are paid in PROOF.md.
    """
    layout = program.layout
    width = max(1, (layout.n-1).bit_length())
    forward, inverse, code = (tape_factory() for _ in range(3))

    def fixed(target, value):
        need(0 <= value < 1 << width, "coordinate fits encoded position width")
        for bit in range(width):
            target.append((value >> bit) & 1)

    for target, mapping in ((forward, layout.gather), (inverse, layout.inverse)):
        for old, new in sorted(mapping.items()):
            fixed(target, old)
            fixed(target, new)
        target.rewind()
    identity_word = program.compiler.gateword("diag", (1, 1))
    for step, (kind, value) in enumerate(program.stages):
        code.append(kind & 1)
        code.append(kind >> 1)
        for label, group in enumerate(program.permutations):
            for axis, permutation in enumerate(group):
                node = source_prefix(program.compiler, layout.local_bits, permutation, identity_word)[step]
                if kind == HADAMARD:
                    need(node[0] == "H" and node[1] == value[axis], "same emitted global H schedule")
                    if label == 0:
                        fixed(code, axis*layout.local_bits+node[1])
                elif kind == SIGNS:
                    need(node[0] == "D" and all(entry in (-1, 1) for entry in node[1]),
                         "source-produced complete sign diagonal")
                    for entry in node[1]:
                        code.append(0 if entry == 1 else 1)
                else:
                    need(node[0] == "D" and all(entry == program.compiler.s.Rational(1, 2)
                                               for entry in node[1]),
                         "source-produced exact normalization")
    code.append(0)
    code.append(0)
    code.rewind()
    return forward, inverse, code


class PreparedCall:
    """Caller-owned source export, with all geometric Counts derived here.

    Only the numerical input format and its complete replication extents are
    supplied by the caller. Selected supports, coordinate maps and the stage
    order are taken from the retained compiler's GlobalProgram.
    """
    def __init__(self, program, p, width, coefficients, rows, tape_factory, count_type):
        need(isinstance(program, GlobalProgram), "source-derived global program")
        need(all(type(x) is int for x in (p, width, coefficients, rows)) and
             0 <= p <= width and width >= 2 and coefficients >= 1 and rows >= 1,
             "complete signed-grid input format")
        self.program = program
        self.controls = encode_controls(program, tape_factory)
        layout = program.layout
        numbers = (layout.n, p, width, layout.g, layout.local_bits,
                   max(1, (layout.n-1).bit_length()), len(layout.gather), coefficients, rows)
        self.parameters = tuple(count_type.literal(value) for value in numbers)
        self.closed = False

    def run(self, boundary, payload):
        need(not self.closed, "live caller-owned compiler export")
        return boundary.run(payload, *self.controls, *self.parameters)

    def close(self):
        if not self.closed:
            for tape in self.controls:
                tape.clear()
            for count in self.parameters:
                count.close()
            self.closed = True
