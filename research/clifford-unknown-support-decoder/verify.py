"""Exercise the complete decoder, its physical-index convention and its rejection tests."""

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from decode import decode, guaranteed_size
from example import observation


def require(ok, message):
    if not ok:
        raise ValueError(message)


def expected_terms():
    # Apply phase and CZ gates to |x>, then four separate Hadamard gates.
    cycle = ((0, 1), (1, 2), (2, 3), (0, 3))
    diagonals = ((0, 2), (1, 3))
    expected = {}
    for pairs, target, imaginary in ((cycle, 11, False), (diagonals, 2, True)):
        for mask in range(1 << len(pairs)):
            entries = []
            for x in range(16):
                power = x % 2
                for j, (a, b) in enumerate(pairs):
                    if mask & (1 << j) and x & (1 << a) and x & (1 << b):
                        power += 2
                for y in range(16):
                    entries.append("+i-j"[(power + 2*(x & y).bit_count()) % 4])
            label = "".join(entries)
            sign = "-" if (target & mask).bit_count() % 2 else ""
            weight = expected.setdefault(label, ["0", "0"])
            weight[int(imaginary)] = sign + ("1/4" if imaginary else "1/16")
    return expected


def product_train(n, factors):
    return dict(format="clifford-tt/1", qubits=n,
                cores=[dict(left=1, right=1,
                            entries=[[q, 0, 0, re, im] for q, re, im in factor])
                       for factor in factors],
                sites=list(range(len(factors))))


def cli(*args):
    flags = ["-O"] if sys.flags.optimize else []
    return subprocess.run([sys.executable, *flags, "-B", str(Path(__file__).with_name("decode.py")),
                           *map(str, args)], capture_output=True, text=True)


def check_example(temp):
    path = temp / "observation.json"
    result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("example.py")),
                             str(path)], capture_output=True, text=True)
    require(result.returncode == 0, result.stderr)
    generated = json.loads(path.read_text())
    require(sum(len(c["entries"]) for c in generated["cores"]) == 6144, "example input size")
    result = cli(path)
    require(result.returncode == 0, result.stderr)
    parsed = json.loads(result.stdout)
    require(parsed["status"] == "member" and parsed["support_limit"] == 19, "example classification")
    require(len(parsed["terms"]) == 19 and all(t["h"] == 4 for t in parsed["terms"]), "dense heights")
    got = {t["signature"]: t["coefficient"] for t in parsed["terms"]}
    require(got == expected_terms(), "signed gate columns or normalization")
    require(decode(generated, 18)["status"] == "outside_model", "support cap")
    for width in (25, 27):
        answer = decode(observation(width))
        require(answer["full_span_decision"] and answer["status"] == "member", "full-span domain")
        require({t["signature"]: t["coefficient"] for t in answer["terms"]} == got, "changing width")
        if width == 25:
            require(answer["cut_certificate"]["bound"] == 20 and
                    answer["complete_fibre_limit"] == 226718, "compact-input certificate")
    print("PASS_PARITY_PROVIDER 6144 sparse records, 19 exact terms at widths 13, 25, 27")


def check_controls(temp):
    eye = [(17*x, 1, 0) for x in range(16)]
    ccz = [(17*x, -1 if (x & 7) == 7 else 1, 0) for x in range(16)]
    off = product_train(4, [eye]*12 + [ccz] + [eye]*12)
    result = decode(off)
    require(result["status"] == "outside_model" and result["full_span_decision"], "full-span exclusion")
    require(result["cut_certificate"]["bound"] == 1, "rank-one exclusion certificate")
    require(not decode(product_train(4, [eye]*25), 0)["full_span_decision"], "explicit zero cap")
    z = [(0, 1, 0), (1, 1, 0)]
    one_eye = [(0, 1, 0), (3, 1, 0)]
    require(decode(product_train(1, [z, one_eye, z]))["status"] == "outside_model", "global residual")
    require(decode(product_train(4, [eye, [], eye]))["terms"] == [], "zero tensor")

    # A huge numerical index is harmless if only one coordinate carries data.
    big = 1 << 2000
    padded = dict(format="clifford-tt/1", qubits=4, sites=[0, 1, 2], cores=[
        dict(left=1, right=big+1, entries=[[q, 0, big, 1, 0] for q, _, _ in eye]),
        dict(left=big+1, right=big+1, entries=[[q, big, big, 1, 0] for q, _, _ in eye]),
        dict(left=big+1, right=1, entries=[[q, big, 0, 1, 0] for q, _, _ in eye])])
    require(decode(padded) == decode(product_train(4, [eye]*3)), "sparse padding")

    # The two X paths cancel. The packed cut has dimension three and rank one.
    records = [[], [], []]
    for channel, (shift, sign) in enumerate(((0, 1), (1, 1), (1, -1))):
        for x in range(16):
            q = 16*x + (x ^ shift)
            records[0].append([q, 0, channel, sign, 0])
            records[1].append([q, channel, channel, 1, 0])
            records[2].append([q, channel, 0, 1, 0])
    cancellation = dict(format="clifford-tt/1", qubits=4, sites=[0]+[1]*12+[2],
                        cores=[dict(left=a, right=b, entries=es) for a, b, es in
                               zip((1, 3, 3), (3, 3, 1), records, strict=True)])
    reduced = decode(cancellation)
    require(reduced["full_span_decision"] and reduced["cut_certificate"]["kind"] == "flattening_rank"
            and reduced["cut_certificate"]["bound"] == 1 and
            reduced["terms"][0]["coefficient"] == [str(4**14), "0"], "rank through cancellation")

    large = product_train(4, [[(q, "1"+"0"*400, 0) for q, _, _ in eye]])
    large["sites"] = [0]*13
    path = temp / "large.json"
    path.write_text(json.dumps(large))
    result = cli(path)
    require(result.returncode == 0, result.stderr)
    require(json.loads(result.stdout)["terms"][0]["coefficient"] == [str(4**13)+"0"*5200, "0"],
            "decimal conversion of large coefficients")
    invalid = product_train(1, [[(0, "1e500000", 0)]])
    path.write_text(json.dumps(invalid))
    require(cli(path).returncode == 2, "scientific notation outside input grammar")
    require([guaranteed_size(4, k) for k in range(14)] ==
            [1, 2, 3, 4, 6, 10, 19, 32, 64, 119, 234, 447742, 58040063, 12128668876800],
            "width contracts")
    print("PASS_DECODER_CONTROLS full residual, unrestricted exclusion, dimensions, precision and caps")


if __name__ == "__main__":
    with TemporaryDirectory() as temp:
        check_example(Path(temp))
        check_controls(Path(temp))
