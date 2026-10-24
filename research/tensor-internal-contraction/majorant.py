"""Checker-only exact signed staged expansion; no physical owner is replaced."""
from fractions import Fraction as F


def need(condition, message):
    if not condition:
        raise ValueError(message)


def trunc(value, bits):
    need(type(bits) is int and bits >= 0, "nonnegative inward shift")
    return (abs(value) >> bits) * (-1 if value < 0 else 1)


class Cursor:
    def __init__(self, raw):
        self.raw, self.pos = raw, 0

    def take(self, n):
        need(n >= 0 and self.pos+n <= len(self.raw), "bounded exact page extent")
        out = self.raw[self.pos:self.pos+n]
        self.pos += n
        return out

    def count(self):
        bits = []
        while True:
            bit = self.take(1)[0]
            if bit == 3:
                break
            need(bit in (0, 1), "count binary alphabet")
            bits.append(bit)
        need(bits and (len(bits) == 1 or bits[-1] == 1), "canonical count")
        return sum(bit << i for i, bit in enumerate(bits))

    def integer(self):
        sign = self.take(1)[0]
        n = self.count()
        need(sign in (0, 1) and (not sign or n), "canonical signed origin")
        return -n if sign else n

    def word(self, width):
        bits = self.take(width)
        need(width > 0 and all(x in (0, 1) for x in bits), "signed binary record")
        n = sum(bit << i for i, bit in enumerate(bits))
        return n-(1 << width) if bits[-1] else n

    def frame(self):
        return Cursor(self.take(self.count()))

    def header(self, names):
        return {name: self.count() for name in names.split()}

    def end(self):
        need(self.pos == len(self.raw), "complete exact page consumption")


def block_page(raw):
    cursor = Cursor(raw)
    out = cursor.header("version p P width sigma s t alpha radius n m nc")
    out["source_start"] = cursor.integer()
    out["target_offset"] = cursor.pos
    out["target_start"] = cursor.integer()
    out["factor_offset"] = cursor.pos
    for name, n in (("A", out["n"]), ("K", out["nc"]), ("B", out["m"])):
        out[name] = [cursor.word(out["width"]) for _ in range(n)]
    out["c"] = cursor.word(out["width"])
    cursor.end()
    Q = 1 << out["P"]
    need(all(0 <= x <= Q for name in ("A", "K", "B") for x in out[name])
         and 0 < out["c"] <= Q//4, "positive normalized factor domain")
    need(out["nc"] == out["n"]+out["m"]-1 and out["P"] >= out["p"]+2*out["sigma"],
         "complete cropped convolution and final extraction")
    return out


def tile_page(raw):
    cursor = Cursor(raw)
    out = cursor.header("version p P sigma s t alpha radius source_count input_capacity target_length blocks")
    out["source_start"], out["target_start"] = cursor.integer(), cursor.integer()
    blocks = []
    for _ in range(out["blocks"]):
        child = cursor.frame()
        blocks.append(block_page(child.raw))
    cursor.end()
    return out, blocks


def pairs(raw, width):
    cursor, result = Cursor(raw), []
    need(len(raw) % (2*width) == 0, "complete complex records")
    while cursor.pos < len(raw):
        result.append((cursor.word(width), cursor.word(width)))
    return result


def count_raw(raw):
    cursor = Cursor(raw)
    n = cursor.count()
    cursor.end()
    return n


def signed_raw(raw, negative):
    n = count_raw(raw)
    return -n if negative and n else n


def block(values, page):
    """Every truncation and rational majorant in p-grid integer units."""
    p, P, n, m = (page[k] for k in ("p", "P", "n", "m"))
    Q, promote, extract = 1 << P, P-p, P-p-2*page["sigma"]
    need(len(values) == n, "exact block input count")
    need(page["width"] == P+n.bit_length()+3, "actual source work-width formula")
    need(all(a*a+b*b <= (1 << (2*p)) for a, b in values), "unit-disk block input")
    trace, outputs = [], [[], []]
    remainders = dict(weighted=0, convolution=0, post=0, fine=0, extract=0)
    def inward(value, bits, module, stage):
        result = trunc(value, bits)
        trace.append((module, value, bits, result))
        remainders[stage] += bool(abs(value) % (1 << bits))
        need(abs(result) <= F(abs(value), 1 << bits), "inward stage majorant")
        return result
    for component in (0, 1):
        weighted = [inward(page["A"][i]*(values[i][component] << promote), P,
                            "block", "weighted") for i in range(n)]
        need(all(abs(x) <= Q for x in weighted), "weighted amplitude fits work width")
        convolution = [inward(sum(weighted[i]*page["K"][k-i]
                              for i in range(n) if 0 <= k-i < page["nc"]), P,
                              "convolution", "convolution") for k in range(page["nc"])]
        need(all(abs(x) <= n*Q < (1 << (page["width"]-3)) for x in convolution),
             "signed convolution intermediate headroom")
        for z in range(m):
            post = inward(page["B"][z]*convolution[n-1+z], P, "block", "post")
            need(abs(post) <= n*Q, "post-factor intermediate headroom")
            fine = inward(page["c"]*post, P, "block", "fine")
            need(abs(fine) <= F(n*Q, 4), "normalization intermediate headroom")
            outputs[component].append(inward(fine, extract, "block", "extract"))
    outputs = list(zip(*outputs))
    row_masses = []
    maximum_norm2 = max(a*a+b*b for a, b in values)
    for z, pair in enumerate(outputs):
        weights = [F((1 << (2*page["sigma"]))*page["c"]*page["B"][z]
                     *page["K"][n-1+z-i]*page["A"][i], Q**4) for i in range(n)]
        mass = sum(weights, F(0))
        for component in (0, 1):
            need(abs(pair[component]) <= sum(w*abs(v[component]) for w, v in zip(weights, values)),
                 "complete signed component majorant")
        need(sum(x*x for x in pair) <= mass*mass*maximum_norm2,
             "complex weighted-Cauchy majorant")
        row_masses.append(mass)
    return outputs, trace, remainders, row_masses


def expand(line, profile):
    result = [None]*profile["t"]
    for tile, blocks in profile["expansion_pages"]:
        for page in blocks:
            data = [line[(page["source_start"]+i) % len(line)] for i in range(page["n"])]
            output, _, _, _ = block(data, page)
            for z, pair in enumerate(output):
                position = page["target_start"]+z
                need(0 <= position < len(result) and result[position] is None,
                     "unique original-axis output ownership")
                result[position] = pair
    need(all(x is not None for x in result), "complete original-axis coverage")
    return result


def axis(data, shape, position, profile):
    rows, columns = shape
    if position == 0:
        lines = [[data[i*columns+j] for i in range(rows)] for j in range(columns)]
        output = [expand(line, profile) for line in lines]
        return [output[j][i] for i in range(profile["t"]) for j in range(columns)], (profile["t"], columns)
    need(position == 1, "bounded two-axis fixture")
    output = [expand(data[i*columns:(i+1)*columns], profile) for i in range(rows)]
    return [pair for line in output for pair in line], (rows, profile["t"])


def fraction(value):
    return [value.numerator, value.denominator]
