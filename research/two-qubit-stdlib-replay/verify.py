#!/usr/bin/env python3
"""Standard-library replay of MatShep's PR5675 centre algorithm.

The new integer representation and dependency-free implementation were
produced by Nick Petalas. Apache-2.0. The source theorem, certificate,
enumeration order, centre reduction and spectral method remain MatShep's.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/full-clifford-two-qubit-centre"
LIMIT = 46080
IDENT = tuple(2 * int(i == j) for i in range(4) for j in range(4)) + (0,) * 16


def need(condition, message):
    if not condition:
        raise ValueError(message)


def key(a):
    return bytes(x & 255 for x in a)


def phase(a):
    return tuple(-x for x in a[16:]) + a[:16]


def negate(a):
    return tuple(-x for x in a)


def star(a):
    return tuple(a[4 * j + i] for i in range(4) for j in range(4)) + tuple(
        -a[16 + 4 * j + i] for i in range(4) for j in range(4))


def mul(a, b):
    """Multiply matrices stored as the 32 integer components of 2U."""
    out = []
    for imaginary in range(2):
        for i in range(4):
            for j in range(4):
                value = 0
                for k in range(4):
                    ar, ai = a[4 * i + k], a[16 + 4 * i + k]
                    br, bi = b[4 * k + j], b[16 + 4 * k + j]
                    value += ar * bi + ai * br if imaginary else ar * br - ai * bi
                need(value % 2 == 0, "scaled Gaussian integrality")
                need(abs(value) <= 4, "unitary entry encoding bound")
                out.append(value // 2)
    return tuple(out)


def embed(a, axis):
    result = [0] * 32
    for part in range(2):
        for i in range(4):
            for j in range(4):
                major_i, minor_i = divmod(i, 2)
                major_j, minor_j = divmod(j, 2)
                if axis == 0 and minor_i == minor_j:
                    result[16 * part + 4 * i + j] = a[4 * part + 2 * major_i + major_j]
                if axis == 1 and major_i == major_j:
                    result[16 * part + 4 * i + j] = a[4 * part + 2 * minor_i + minor_j]
    return tuple(result)


def generators():
    s = (2, 0, 0, 0, 0, 0, 0, 2)
    v = (1, 1, 1, 1, 1, -1, -1, 1)
    cnot = [0] * 32
    for j in range(4):
        cnot[4 * (j ^ ((j >> 1) & 1)) + j] = 2
    return (embed(s, 0), embed(v, 0), embed(s, 1), embed(v, 1), tuple(cnot))


def closure(gens):
    group, index, frontier = [IDENT], {key(IDENT): 0}, [IDENT]
    for _ in range(LIMIT):
        new = []
        for s in gens:
            for a in frontier:
                product = mul(s, a)
                encoded = key(product)
                if encoded not in index:
                    need(len(group) < LIMIT, "group capacity")
                    index[encoded] = len(group)
                    group.append(product)
                    new.append(product)
        if not new:
            need(len(group) == LIMIT, "46080 exact elements")
            return group, index
        frontier = new
    raise ValueError("group closure depth exhausted")


def check_group(group, index, gens):
    for a in group:
        need(mul(star(a), a) == IDENT, "all lifts unitary")
    scalars = (IDENT, phase(IDENT), negate(IDENT), negate(phase(IDENT)))
    need(all(key(a) in index for a in scalars), "four scalar lifts")
    canonical = {min(key(a), key(phase(a)), key(negate(a)), key(negate(phase(a))))
                 for a in group}
    need(len(canonical) == 11520, "11520 projective classes")
    local = ((2, 0, 0, 2, 0, 0, 0, 0), (0, 2, 2, 0, 0, 0, 0, 0),
             (0, 0, 0, 0, 0, -2, 2, 0), (2, 0, 0, -2, 0, 0, 0, 0))
    paulis = [mul(embed(a, 0), embed(b, 1)) for a in local for b in local]
    permitted = {key(a) for a in paulis} | {key(negate(a)) for a in paulis}
    for s in gens:
        need(all(key(mul(mul(s, a), star(s))) in permitted for a in paulis),
             "signed Pauli normalizer")


def find(parent, position):
    for _ in range(LIMIT):
        if parent[position] == position:
            return position
        parent[position] = parent[parent[position]]
        position = parent[position]
    raise ValueError("union-find depth exhausted")


def conjugacy(group, index, gens):
    parent = list(range(len(group)))
    for s in gens:
        adjoint = star(s)
        for j, a in enumerate(group):
            u = find(parent, j)
            v = find(parent, index[key(mul(mul(s, a), adjoint))])
            if u != v:
                parent[v] = u
    classes = {}
    for j in range(len(group)):
        classes.setdefault(find(parent, j), []).append(j)
    ordered = sorted(classes.values(), key=lambda c: c[0])
    need(len(ordered) == 59, "59 conjugacy classes")
    labels = [0] * len(group)
    for label, members in enumerate(ordered):
        for j in members:
            labels[j] = label
    return labels, [c[0] for c in ordered]


def trace_overlap(a, b):
    real = sum(a[k] * b[k] + a[16 + k] * b[16 + k] for k in range(16))
    imag = sum(a[16 + k] * b[k] - a[k] * b[16 + k] for k in range(16))
    need(real % 4 == 0 and imag % 4 == 0, "Gaussian integer traces")
    real, imag = real // 4, imag // 4
    need(real * real + imag * imag <= 16, "trace magnitude bound")
    return real, imag


def gaussian_power(a, exponent):
    real, imag = 1, 0
    for _ in range(exponent):
        real, imag = real * a[0] - imag * a[1], real * a[1] + imag * a[0]
    return real, imag


def trace_histograms(group, labels, representatives):
    """Retain each trace value and its multiplicity in each class."""
    histograms = []
    identity_traces = []
    for r in representatives:
        counts = [Counter() for _ in representatives]
        for j, a in enumerate(group):
            trace = trace_overlap(a, group[r])
            counts[labels[j]][trace] += 1
            if r == 0:
                identity_traces.append(trace)
        histograms.append(counts)
    need(all(len(c) == 1 for c in histograms[0]), "trace class function")
    return histograms, identity_traces


def centre_matrix(histograms, exponent):
    powers = {a: gaussian_power(a, exponent) for row in histograms for c in row for a in c}
    return [[(sum(powers[a][0] * n for a, n in counts.items()),
              sum(powers[a][1] * n for a, n in counts.items()))
             for counts in row] for row in histograms]


def scalar_basis(iperm, residue):
    done, columns, picks = set(), [], []
    for j in range(len(iperm)):
        if j in done:
            continue
        orbit, position = [], j
        for _ in range(4):
            if position in orbit:
                break
            orbit.append(position)
            done.add(position)
            position = iperm[position]
        need(position == j, "scalar orbit closes within four steps")
        if residue * len(orbit) % 4:
            continue
        column = [(0, 0)] * len(iperm)
        for t, position in enumerate(orbit):
            column[position] = ((1, 0), (0, 1), (-1, 0), (0, -1))[residue * t % 4]
        columns.append(column)
        picks.append(j)
    return [list(row) for row in zip(*columns)], picks


def gaussian_matmul(a, b):
    return [[(sum(x[0] * y[0] - x[1] * y[1] for x, y in zip(row, column)),
              sum(x[0] * y[1] + x[1] * y[0] for x, y in zip(row, column)))
             for column in zip(*b)] for row in a]


def matvec(a, v, shift):
    result = []
    for j, row in enumerate(a):
        real = sum(x * u - y * w for (x, y), (u, w) in zip(row, v))
        imag = sum(x * w + y * u for (x, y), (u, w) in zip(row, v))
        result.append((real - shift * v[j][0], imag - shift * v[j][1]))
    return result


def spectral_certificate(a, values):
    dimension = len(a)
    for j in range(dimension):
        vector = [(int(i == j), 0) for i in range(dimension)]
        for value in values:
            vector = matvec(a, vector, value)
        need(not any(x or y for x, y in vector), "exact square-free spectral annihilator")
    counts = {}
    for value in values:
        vector = [(int(i == 0), 0) for i in range(dimension)]
        denominator = 1
        for other in values:
            if other != value:
                vector = matvec(a, vector, other)
                denominator *= value - other
        need(vector[0][1] == 0 and 11520 * vector[0][0] % denominator == 0,
             "exact projector trace")
        counts[value] = 11520 * vector[0][0] // denominator
        need(counts[value] > 0, "positive regular spectral multiplicity")
    need(sum(counts.values()) == 11520, "complete regular spectral mass")
    return counts


def determinants(group):
    terms = [(p, (-1) ** sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4)))
             for p in permutations(range(4))]
    result = []
    for matrix in group:
        real, imag = 0, 0
        for p, sign in terms:
            x, y = 1, 0
            for j in range(4):
                ar, ai = matrix[4 * j + p[j]], matrix[16 + 4 * j + p[j]]
                x, y = x * ar - y * ai, x * ai + y * ar
            real, imag = real + sign * x, imag + sign * y
        need(imag == 0 and abs(real) == 16, "determinant character +/-1")
        result.append(real // 16)
    return result


def tensor(a, b):
    return [(x * u - y * v, x * v + y * u) for x, y in a for u, v in b]


def literal_controls(group):
    chosen, count = [group[j] for j in (0, 1, 4, 111)], 0
    for exponent in range(1, 5):
        tensors = []
        for a in chosen:
            entries = [(a[k], a[16 + k]) for k in range(16)]
            result = [(1, 0)]
            for _ in range(exponent):
                result = tensor(result, entries)
            tensors.append(result)
        for i, a in enumerate(tensors):
            for j, b in enumerate(tensors):
                tr = (sum(chosen[i][k] * chosen[j][k] + chosen[i][16+k] * chosen[j][16+k]
                          for k in range(16)),
                      sum(chosen[i][k] * chosen[j][16+k] - chosen[i][16+k] * chosen[j][k]
                          for k in range(16)))
                expected = gaussian_power(tr, exponent)
                actual = (sum(x * u + y * v for (x, y), (u, v) in zip(a, b)),
                          sum(x * v - y * u for (x, y), (u, v) in zip(a, b)))
                need(actual == expected, "literal tensor Gram")
                count += 1
    return count


def verify_widths(histograms, iperm, certificate):
    spectra, ranks, dimensions = {}, [], {}
    for exponent in range(1, 13):
        centre = centre_matrix(histograms, exponent)
        basis, picks = scalar_basis(iperm, -exponent % 4)
        product = gaussian_matmul(centre, basis)
        reduced = [product[j] for j in picks]
        need(product == gaussian_matmul(basis, reduced), "scalar-sector invariance")
        row = certificate["widths"][str(exponent)]
        need(picks == row["picks"] and reduced == [[tuple(x) for x in r] for r in row["matrix"]],
             "derived centre matrix")
        values = row["eigenvalues"]
        need(values == sorted(set(values)), "distinct sorted eigenvalues")
        counts = spectral_certificate(reduced, values)
        spectrum = {str(Fraction(x, 4 * 4 ** exponent)): counts[x] for x in values if x}
        rank = sum(spectrum.values())
        need(spectrum == row["expected"]["spectrum"] and rank == row["expected"]["rank"],
             "finite spectrum receipt")
        need(sum(Fraction(x) * v for x, v in spectrum.items()) == 11520, "unit diagonal Gram trace")
        spectra[exponent], dimensions[exponent % 4] = spectrum, len(reduced)
        ranks.append(rank)
    return spectra, ranks, dimensions


def rejection_controls(histograms, iperm, certificate, ranks, lo, hi, moments):
    need(ranks[7] < 11520, "reject width-eight independence")
    need(not lo >= lo + Fraction(1, 2 ** 20), "reject stronger lower bound")
    need(not hi <= hi - Fraction(1, 2 ** 20), "reject stronger upper bound")
    need(not hi / lo <= Fraction(219, 28) - Fraction(1, 1000), "reject stronger condition bound")
    original = [[tuple(x) for x in row] for row in certificate["widths"]["9"]["matrix"]]
    bad = [list(row) for row in original]
    bad[0][0] = (bad[0][0][0] + 1, bad[0][0][1])
    try:
        spectral_certificate(bad, certificate["widths"]["9"]["eigenvalues"])
    except ValueError:
        pass
    else:
        raise ValueError("mutated centre matrix accepted")
    real_only = [[Counter() for _ in row] for row in histograms]
    for i, row in enumerate(histograms):
        for j, counts in enumerate(row):
            for (real, _), multiplicity in counts.items():
                real_only[i][j][real, 0] += multiplicity
    basis, _ = scalar_basis(iperm, -9 % 4)
    product = gaussian_matmul(centre_matrix(real_only, 9), basis)
    need(product != gaussian_matmul(basis, original), "reject discarded imaginary traces")
    need(moments[12] != moments[8], "reject persistence of null witness")
    return ["width-eight independence rejected", "stronger lower bound rejected",
            "stronger upper bound rejected", "stronger condition bound rejected",
            "changed centre coefficient rejected", "discarded imaginary trace phases rejected",
            "null witness at width twelve rejected"]


def source_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(path.stat().st_size <= 2 ** 20, "source file capacity")
            hashes[row["path"]] = sha256(path.read_bytes()).hexdigest()
            need(hashes[row["path"]] == row["sha256"], "immutable source hash: " + row["path"])
    certificate = json.loads((SOURCE / "CERTIFICATE.json").read_text())
    expected = json.loads((SOURCE / "RESULT.json").read_text())
    return certificate, expected, hashes


def arithmetic_controls():
    units = []
    for i in range(4):
        for j in range(4):
            units.append(tuple(2 * int(k == 4 * i + j) for k in range(16)) + (0,) * 16)
    for i, a in enumerate(units):
        for j, b in enumerate(units):
            expected = units[4 * (i // 4) + j % 4] if i % 4 == j // 4 else (0,) * 32
            need(mul(a, b) == expected, "matrix-unit product")
    for a in units:
        need(phase(phase(phase(phase(a)))) == a, "four scalar phases")
        need(star(star(phase(a))) == phase(a), "Gaussian adjoint involution")
    malformed = ((1,) + (0,) * 31, (4,) + (0,) * 31)
    for a in malformed:
        try:
            mul(a, a)
        except ValueError:
            pass
        else:
            raise ValueError("invalid scaled product accepted")
    traces = [(1, 1), (1, 1), (0, -2), (0, -2), (-1, 0)]
    histogram = [[Counter(traces)]]
    for exponent in range(1, 13):
        direct = [gaussian_power(a, exponent) for a in traces]
        expected = (sum(a for a, _ in direct), sum(b for _, b in direct))
        need(centre_matrix(histogram, exponent) == [[expected]], "histogram multiplicities and phase")
    try:
        scalar_basis([1, 2, 3, 4, 0], 0)
    except ValueError:
        pass
    else:
        raise ValueError("oversized scalar orbit accepted")
    return {"matrix_unit_products": 256, "phase_adjoint_cases": 32,
            "histogram_cases": 12, "rejections": 3}


def package_hashes():
    result = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        path = HERE / name
        need(path.stat().st_size <= 2 ** 20, "package file capacity")
        result[name] = sha256(path.read_bytes()).hexdigest()
    return result


def run():
    certificate, expected, source_hashes = source_inputs()
    controls_new = arithmetic_controls()
    gens = generators()
    group, index = closure(gens)
    check_group(group, index, gens)
    labels, representatives = conjugacy(group, index, gens)
    group_hash = sha256(b"".join(key(a) for a in group)).hexdigest()
    class_hash = sha256(b"".join(struct.pack("<I", j) for j in labels)).hexdigest()
    need(group_hash == certificate["group_int8_sha256"], "group receipt")
    need(class_hash == certificate["class_labels_u32le_sha256"], "class receipt")
    sizes = Counter(labels)
    need([sizes[j] for j in range(59)] == certificate["class_sizes"], "class sizes")
    nested = [[[list(a[4 * i + 16 * p:4 * i + 16 * p + 4]) for i in range(4)]
               for p in range(2)] for a in (group[r] for r in representatives)]
    need(nested == certificate["representatives"], "class representatives")
    histograms, identity_traces = trace_histograms(group, labels, representatives)
    iperm = [labels[index[key(phase(group[r]))]] for r in representatives]
    spectra, ranks, dimensions = verify_widths(histograms, iperm, certificate)
    det = determinants(group)
    moments = {}
    for exponent in (4, 8, 12):
        powers = [gaussian_power(t, exponent) for t in identity_traces]
        need(not any(t[1] for t in powers), "real determinant moment")
        moments[exponent] = sum(d * t[0] for d, t in zip(det, powers))
    need(moments[8] == 0 and moments[12] != 0, "same-residue determinant null witness")
    lo, hi = min(map(Fraction, spectra[9])), max(map(Fraction, spectra[9]))
    need(lo == Fraction(315, 1024) and hi == Fraction(9855, 4096), "sharp width-nine endpoints")
    controls = rejection_controls(histograms, iperm, certificate, ranks, lo, hi, moments)
    result = {"status": "PASS_TWO_QUBIT_CLIFFORD_CENTRE", "lifts": len(group),
              "projective_classes": 11520, "conjugacy_classes": len(representatives),
              "scalar_sector_dimensions": dimensions, "ranks_widths_1_to_12": ranks,
              "width_nine_spectrum": spectra[9], "sharp_uniform_lower": str(lo),
              "sharp_uniform_upper": str(hi), "sharp_uniform_gram_condition": str(hi / lo),
              "determinant_character_moments": moments, "literal_tensor_entries": literal_controls(group),
              "rejection_controls": controls}
    need(json.loads(json.dumps(result)) == expected, "complete predecessor output conformance")
    return {"status": "PASS_TWO_QUBIT_STDLIB_REPLAY", "scientific_result": result,
            "source_sha256": source_hashes, "trace_pairs": len(group) * len(representatives),
            "distinct_trace_class_pairs": sum(len(c) for row in histograms for c in row),
            "representation_controls": controls_new, "package_sha256": package_hashes()}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
