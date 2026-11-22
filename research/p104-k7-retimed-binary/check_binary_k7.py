"""Check the constructive k7 binary circuit: replays, charts, sparse oracle, tariff, and #8027 control."""

from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
from random import Random
import tarfile

from installations import BINARY_C
from unpowered_price import certify

PACKAGE_DIR = Path(__file__).resolve().parent
K7_GZ_SHA256 = "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
K7_RAW_SHA256 = "f4a43e4e36ac734dea10a73dca496bf4a4f4a9804b903ea379483d0513d7abc3"
OLD_8027_GZ_SHA256 = "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326"


def check_archives_and_ledger():
    gz_bytes = (PACKAGE_DIR / "strong-bit-k7.json.gz").read_bytes()
    assert sha256(gz_bytes).hexdigest() == K7_GZ_SHA256
    raw_bytes = gzip.decompress(gz_bytes)
    assert sha256(raw_bytes).hexdigest() == K7_RAW_SHA256
    ledger = json.loads((PACKAGE_DIR / "K7-STACK-LEDGER.json").read_text(encoding="utf-8"))
    final = ledger["final_k7"]
    assert final["moves"] == 2796
    assert final["dirty_clears"] == 3426
    assert (final["frames"], final["pairs"], final["frame_gates"]) == (636, 2353, 44734)
    assert (final["n_targets"], final["n_paid"], final["linear_paid_sum"]) == (18906, 104652, 284592)
    assert final["gz_sha256"] == K7_GZ_SHA256 and final["raw_sha256"] == K7_RAW_SHA256
    return json.loads(raw_bytes)


def run_registers(program, starts, ends, ports):
    count = len(starts)
    frames = dict(enumerate(starts))
    values = {i: 1 << i for i in range(count)}
    dirty = 0
    moves = 0
    for op, dest, *args in program:
        if op == "MOVE":
            before, after = args
            assert frames[dest] == before
            frames[dest] = after
            moves += 1
        elif op == "ADD":
            read, site = args
            assert frames[dest] == frames[read] == site
            values[dest] ^= values[read]
        elif op == "SWAP":
            (read,) = args
            frames[dest], frames[read] = frames[read], frames[dest]
            values[dest], values[read] = values[read], values[dest]
        elif op == "INIT":
            assert dest >= count and dest not in frames
            frames[dest], values[dest] = args[0], 0
        elif op == "CLEAR":
            assert dest >= count and frames.pop(dest) == args[0]
            dirty += int(bool(values.pop(dest)))
        else:
            raise ValueError("Unknown graph instruction")
    assert frames == dict(enumerate(ends))
    assert len(values) == count == 630 and ports == 111
    for i in range(count):
        expected = 1 << i
        if ports <= i < 2 * ports:
            expected ^= 1 << (i - ports)
        assert values[i] == expected
    return dirty, moves


def check_outer_word(root):
    def shift(terms, mask):
        return {(role, exponent ^ mask) for role, exponent in terms}

    def stage_mask(stages):
        mask = 0
        for stage in stages:
            mask ^= 1 << stage
        return mask

    head = 1
    words = [{(i, 0)} for i in range(root["roles"])]
    for op, *args in root["events"]:
        if op == "LOCAL":
            stage, x, y = args
            body = stage_mask((stage,))
            first, second = words[x], words[y]
            words[x] = shift(first, body)
            words[y] = shift(first, body ^ head) ^ shift(second, body)
        elif op == "IDLE_ONE":
            x, stages = args
            words[x] = shift(words[x], stage_mask(stages))
        elif op == "QUERY":
            x, y = args
            words[x] ^= shift(words[y], head)
        elif op == "ADD":
            x, y = args
            words[x] ^= words[y]
        elif op == "SWAP":
            x, y = args
            words[x], words[y] = words[y], words[x]
        else:
            raise ValueError("Unknown caller instruction")
    for i, (answer, diag) in enumerate(zip(words, root["diagonal"], strict=True)):
        assert diag["q"] == 1
        assert answer == {(i, head ^ stage_mask(diag["stages"]))}


def matrix_product(a, b):
    cols = list(zip(*b, strict=True))
    return [[sum(x * y for x, y in zip(u, v, strict=True)) for v in cols] for u in a]


def integer_matrix(a):
    den = lcm(*(v.denominator for row in a for v in row))
    assert den % 3
    return den, [[int(v * den) for v in row] for row in a]


def rational_word(frame):
    from factored_frames import inverse_word
    from ternary_frames import identity
    from vendor.cover import row_program

    word = row_program(frame, 3)
    back = tuple(inverse_word(word))
    for program, base, goal in [
        (word, identity(len(frame)), frame),
        (back, frame, identity(len(frame))),
    ]:
        rows = [list(row) for row in base]
        for op, i, *args in program:
            if op in ("scale", "add"):
                q = Fraction(args[-1])
                assert q.denominator % 3 and max(abs(q.numerator), q.denominator) <= 20
                if op == "scale":
                    assert q.numerator % 3
            for row in rows:
                if op == "scale":
                    row[i] *= q
                elif op == "add":
                    row[i] += row[args[0]] * q
                elif op == "swap":
                    j = args[0]
                    row[i], row[j] = row[j], row[i]
                else:
                    raise ValueError("Unknown frame instruction")
        assert rows == goal
    return len(word)


def check_charts(data, ports):
    from ternary_frames import frame_at_three, identity, projector, transpose

    frames, starts, ends = data["frames"], data["start"], data["final"]
    ops = data["program"]
    projectors, splits = [], []
    ident = identity(8)
    for i in range(len(frames)):
        spec = frames[str(i)]
        p = projector(transpose(spec["B"] + spec["A"]), spec["dim"])
        projectors.append(p)
        den, m = integer_matrix(p)
        assert matrix_product(m, m) == [[den * x for x in row] for row in m]
        splits.append((den, m))
    pairs = {tuple(row[2:]) for row in ops if row[0] == "MOVE"}
    pairs.update(zip(starts[2 * ports :], ends[2 * ports :], strict=True))
    pairs = {tuple(sorted(pair, key=lambda j: frames[str(j)]["dim"])) for pair in pairs}
    steps = 0
    for i, j in sorted(pairs):
        di, pi = splits[i]
        dj, pj = splits[j]
        lifted = [[dj * x for x in row] for row in pi]
        assert matrix_product(pi, pj) == matrix_product(pj, pi) == lifted
        delta = [
            [y - x for x, y in zip(a, b, strict=True)]
            for a, b in zip(projectors[i], projectors[j], strict=True)
        ]
        basis, rank = frame_at_three(delta)
        assert rank == frames[str(j)]["dim"] - frames[str(i)]["dim"]
        den, m = integer_matrix(delta)
        assert matrix_product(m, basis) == [
            [den * v if col < rank else 0 for col, v in enumerate(row)] for row in basis
        ]
        steps += rational_word(basis)
    for i in range(ports):
        head, body = projectors[starts[i]], projectors[ends[ports + i]]
        assert len(frames[str(starts[i])]["B"]) == 1
        assert projectors[ends[i]] == ident
        assert all(x == 0 for row in projectors[starts[ports + i]] for x in row)
        assert [
            [x + y for x, y in zip(a, b, strict=True)] for a, b in zip(head, body, strict=True)
        ] == ident
        basis = transpose(frames[str(starts[i])]["B"] + frames[str(ends[ports + i])]["B"])
        steps += rational_word(basis)
    return len(projectors), len(pairs), steps


def raw_moments(data, root):
    ports = root["ports"]
    dims = {int(idx): frame["dim"] for idx, frame in data["frames"].items()}
    targets = Counter()
    paid = Counter()
    local = sum(row[0] == "LOCAL" for row in root["events"])
    for row in root["diagonal"]:
        targets[1 + root["body_rank"] * len(row["stages"])] += ports
    for src, dst in zip(data["start"][2 * ports :], data["final"][2 * ports :], strict=True):
        targets[abs(dims[dst] - dims[src])] += local
    for row in data["program"]:
        if row[0] == "MOVE":
            paid[abs(dims[row[3]] - dims[row[2]])] += local
    for row in root["events"]:
        if row[0] == "QUERY":
            paid[1] += ports
        elif row[0] == "IDLE_ONE":
            paid[len(row[2]) * root["body_rank"]] += ports
    return targets, paid


def check_weighted_sparse(data, root):
    from check_raw_delta import Sparse, right_columns
    from strong_binary import StrongBinarySource
    from direct_body import direct_actions, direct_factors
    from factored_frames import Frame, inverse_word
    from periodic import Job
    from raw_binary import Axis, job_frame
    from tagged_sources import binary_ports
    from ternary_frames import residue

    source = binary_ports(data, root)
    seeds = {0, 111, 114, len(source.targets) - 1}
    for grade in (4, 8):
        seeds.add(
            next(
                i
                for i, port in enumerate(source.targets)
                if port.tag[0] == "helper" and port.rank == grade
            )
        )
    for modulus, columns in ((3, 1), (9, 2)):
        n = source.ambient * columns
        ident = tuple(bytes(int(x == y) for x in range(n)) for y in range(n))
        rng = Random(7914)
        units = [x for x in range(modulus) if x % 3]
        A = [rng.choice(units) for _ in range(n)]
        Ai = [pow(a, -1, modulus) for a in A]

        @cache
        def scaled_word(word):
            out = []
            for op, tail, i, j, coeff in direct_actions(word, 1):
                a = residue(coeff, modulus)
                if not tail and op == "swap":
                    a = A[i] * Ai[j] % modulus
                elif not tail and op == "add":
                    a = a * A[j] * Ai[i] % modulus
                out.append((op, tail, i, j, a))
            return tuple(out)

        @cache
        def factors(word, axis):
            u, v = direct_factors(Frame(n, word, (axis,)), modulus)
            return bytes(u), bytes(v)

        class DirectSparse(Sparse):
            dimension = n

            def route(self, owner, word):
                if not self.values[owner]:
                    return
                self.active_routes += 1
                out = set()
                for label, h, t in self.values[owner]:
                    pair = list(h), list(t)
                    for op, tail, i, j, a in scaled_word(word):
                        bank = pair[tail]
                        if op == "swap":
                            bank[i], bank[j] = (
                                a * bank[j] % modulus,
                                pow(a, -1, modulus) * bank[i] % modulus,
                            )
                        elif op == "scale":
                            bank[i] = a * bank[i] % modulus
                        else:
                            bank[j] = (bank[j] + a * bank[i]) % modulus
                    out.add((label, bytes(pair[0]), bytes(pair[1])))
                self.values[owner] = out

            def pay(self, job):
                if not self.values[job.owner]:
                    return
                self.active_paid += 1
                frame = job_frame(job, n)
                out = set()
                for label, h, t in self.values[job.owner]:
                    d = [(y - ai * x) % modulus for x, ai, y in zip(h, Ai, t, strict=True)]
                    change = [0] * n
                    for axis in frame.mask:
                        u, v = factors(frame.word, axis)
                        coeff = sum(x * y for x, y in zip(v, d, strict=True)) % modulus
                        if coeff:
                            change = [
                                (x + coeff * y) % modulus for x, y in zip(change, u, strict=True)
                            ]
                    self.moved += any(change)
                    out.add(
                        (
                            label,
                            bytes(
                                (x + a * v) % modulus for x, a, v in zip(h, A, change, strict=True)
                            ),
                            bytes((y - v) % modulus for y, v in zip(t, change, strict=True)),
                        )
                    )
                self.values[job.owner] = out

        banks = DirectSparse(None, modulus)
        entries, expected = [], {}
        for i, port in enumerate(source.targets):
            owner = banks.zero()
            if i in seeds:
                g = (
                    ("add", 7, 113, Fraction(4, 5)),
                    ("swap", 0, 126),
                    ("scale", 4, Fraction(-2)),
                    ("add", 0, 32, 2),
                    ("add", 7, 0, i % 4 + 1),
                )
                axes = tuple(Axis(g, j) for j in range(port.rank * columns))
                h, t = (bytes(rng.randrange(modulus) for _ in range(n)) for _ in range(2))
                banks.values[i].add((i, h, t))
                data_mat = right_columns(ident, g, modulus)
                inv = right_columns(ident, tuple(inverse_word(g)), modulus)
                diff = [(y - ai * x) % modulus for x, ai, y in zip(h, Ai, t, strict=True)]
                local = [
                    sum(col[j] * x for col, x in zip(inv, diff, strict=True)) % modulus
                    for j in range(port.rank * columns)
                ]
                change = [
                    sum(data_mat[j][k] * entry for j, entry in enumerate(local)) % modulus
                    for k in range(n)
                ]
                expected[i] = {
                    (
                        i,
                        bytes((x + a * v) % modulus for x, a, v in zip(h, A, change, strict=True)),
                        bytes((y - v) % modulus for y, v in zip(t, change, strict=True)),
                    )
                }
            else:
                axes = tuple(range(port.rank * columns))
            entries.append((port.tag, Job(owner, axes)))
        count = 0
        for (tag, job), paid in zip(
            StrongBinarySource(banks).raw(entries, columns), source.paid, strict=True
        ):
            assert tag == paid.tag and len(job.axes) == paid.rank * columns
            banks.pay(job)
            count += 1
        assert count == 104652 and len(banks.values) == len(entries) == 18906
        wrong = [k for k, v in banks.values.items() if v != expected.get(k, set())]
        assert not wrong, wrong[:3]


def check_predecessor_8027_fails_binary_c(root):
    tar_path = PACKAGE_DIR / "predecessor" / "predecessor-8030.tar.gz"
    with tarfile.open(tar_path, "r:gz") as archive:
        member = archive.getmember("strong-bit.json.gz")
        with archive.extractfile(member) as f:
            old_gz = f.read()
    assert sha256(old_gz).hexdigest() == OLD_8027_GZ_SHA256
    old_data = json.loads(gzip.decompress(old_gz))
    old_targets, old_paid = raw_moments(old_data, root)
    assert (old_targets.total(), old_paid.total()) == (18906, 104904)
    try:
        margin, cells = certify(BINARY_C, (old_targets, old_paid))
    except (AssertionError, ValueError):
        return
    assert cells is None or margin <= 0, "PR #8027 binary source unexpectedly certified at k7 BINARY_C"


def check():
    from strong_binary import caller, graph

    k7_from_pkg = check_archives_and_ledger()
    data, root = graph(), caller()
    assert data == k7_from_pkg
    assert sum(r[0] == "LOCAL" for r in root["events"]) == 36
    dirty, moves = run_registers(data["program"], data["start"], data["final"], root["ports"])
    assert (dirty, moves) == (3426, 2796)
    check_outer_word(root)
    frames, pairs, steps = check_charts(data, root["ports"])
    assert (frames, pairs, steps) == (636, 2353, 44734)

    targets, paid = raw_moments(data, root)
    assert (targets.total(), paid.total()) == (18906, 104652)
    linear_t = sum(r * c for r, c in targets.items())
    linear_p = sum(r * c for r, c in paid.items())
    assert (linear_t, linear_p) == (286098, 284592)
    signed = {r: targets[r] - paid[r] for r in targets.keys() | paid.keys() if targets[r] != paid[r]}
    expected_signed = dict(enumerate((-48720, -45144, -1980, -396, -1296, -2664, -480), 1))
    expected_signed.update({8: 14268, 64: 444, 127: 222})
    for low in range(14, 57, 7):
        expected_signed[low] = -444
        expected_signed[low + 1] = 444
    assert signed == expected_signed

    margin, cells = certify(BINARY_C, (targets, paid))
    assert cells is not None and len(cells) == 24 and margin > 0

    check_weighted_sparse(data, root)
    check_predecessor_8027_fails_binary_c(root)
    print(
        "PASS_K7_BINARY_CIRCUIT",
        f"moves={moves}",
        f"dirty={dirty}",
        f"targets={targets.total()}",
        f"paid={paid.total()}",
        f"linear_paid={linear_p}",
        f"frames={frames}",
        f"pairs={pairs}",
        f"frame_gates={steps}",
        f"cells={len(cells)}",
        "control_8027=rejected",
    )


if __name__ == "__main__":
    check()
