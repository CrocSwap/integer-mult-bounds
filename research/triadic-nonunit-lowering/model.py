"""Source-bound complete ADDRESS lowering; no tape primitive implementation."""
import hashlib
import importlib.util
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for manifest, root, key in (("SOURCES.json", ROOT, "path"),
                                ("VENDOR.json", HERE, "local_path")):
        data = json.loads((HERE / manifest).read_text(encoding="utf-8"))
        for item in data["files"]:
            if manifest == "SOURCES.json" and item.get("usage") != "input":
                continue  # historical guidance is checked by the registered wrapper
            raw = (root / item[key]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source hash: " + item[key])
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            need(blob == item["git_blob"], "source blob: " + item[key])


def source():
    authenticate()
    spec = importlib.util.spec_from_file_location("frozen_triadic", HERE / "vendor/program.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def classify(k, m):
    need(type(k) is int, "integer power")
    need(type(m) is int and m >= 3 and m % 2, "odd modulus >=3")
    return 0 if k % m == 0 else 1 if gcd(k, m) == 1 else 2


def lower(k, m, original, triadic=None):
    count = classify(k, m)
    if count == 0:
        return (), ()
    if count == 1:
        return original.address_word(k), (k,)
    if triadic is None:
        u = next(u for u in range(1, m) if gcd(u, m) == gcd(k-u, m) == 1)
    else:
        j, sign = triadic
        need(type(j) is int and j >= 0 and type(sign) is int and sign in (-1, 1), "triadic indices")
        need(k == sign * 3 * (1 << j), "triadic power binding")
        u = sign * (1 << j)
    v = k-u
    need(gcd(u, m) == gcd(v, m) == 1, "unit decomposition")
    return original.address_word(u) + original.address_word(v), (u, v)


def modular(word, m):
    classify(0, m)
    def residue(x):
        return x.numerator * pow(x.denominator, -1, m) % m
    out = []
    for event in word:
        if event[0] == "child":
            need(event == ("child", 0, 5), "only designated child")
            out.append(event)
        else:
            tag, target, diagonal, controls = event
            need(tag == "affine" and 0 <= target < 6, "typed affine")
            d = residue(diagonal)
            need(gcd(d, m) == 1, "nonunit affine diagonal")
            need(all(0 <= i < target for i, _ in controls), "ordered controls")
            out.append((tag, target, d, tuple((i, residue(c)) for i, c in controls)))
    return tuple(out)


def run(z, word, m):
    a = list(z)
    need(len(a) >= 6, "six active fields")
    for event in word:
        if event[0] == "child":
            a[0], a[5] = a[5], a[0]
        else:
            _, t, d, cs = event
            value = d*a[t]
            for i, c in cs:
                value += c*a[i]
            a[t] = value % m
    return tuple(a)


def direct(z, k, m):
    d = (z[0]-z[2]-z[3]+z[5]) * k * pow(4, -1, m) % m
    return tuple((v + d*s) % m for v, s in zip(z[:6], (1,0,1,-1,0,-1))) + tuple(z[6:])


def invoice(j, sign, m, original):
    a = sign * 3 * (1 << j)
    if a % m == 0:
        return {"children": 0, "affine": 0, "xor": 0, "query_powers": []}
    powers = (-a, 2*a, -a)
    specs = ((j, -sign), (j+1, sign), (j, -sign))
    words = [lower(k, m, original, triadic=spec)[0] for k, spec in zip(powers, specs)]
    return {"children": sum(e[0] == "child" for w in words for e in w),
            "affine": sum(e[0] == "affine" for w in words for e in w),
            "xor": 2, "query_powers": list(powers)}
