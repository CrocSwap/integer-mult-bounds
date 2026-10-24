"""Independent exact arithmetic audit of the source's five rounding sites.

Inputs to audit_block are integer p-grid complex pairs and decoded page dicts.
Linear helpers instead use pairs of Fractions in physical value units. This
module supplies no page producer, tail estimate or production admission.
Prepared by Hiroki KUMAZAKI with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json

STAGES = ("weighted", "convolution", "post", "fine", "extract")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fraction(value):
    value = F(value)
    return [value.numerator, value.denominator]


def pair(value):
    return [fraction(x) for x in value]


def digest(values):
    def encode(value):
        if isinstance(value, F):
            return fraction(value)
        if isinstance(value, (list, tuple)):
            return [encode(x) for x in value]
        if isinstance(value, dict):
            return {k: encode(v) for k, v in value.items()}
        return value
    return sha256(json.dumps(encode(values), sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def norm2(values):
    return max((a*a+b*b for a, b in values), default=F(0))


def inward(integer, shift):
    require(type(integer) is int and type(shift) is int and shift >= 0,
            "integer inward-rounding operands")
    quotient = abs(integer) // (1 << shift)
    return -quotient if integer < 0 else quotient


def parameters(page):
    for key in ("p", "P", "sigma", "n", "m", "nc", "width", "c"):
        require(type(page[key]) is int, "integer arithmetic page field: " + key)
    p, P, sigma, n, m = (page[k] for k in ("p", "P", "sigma", "n", "m"))
    require(p >= 1 and sigma >= 0 and P >= p+2*sigma and n >= 1 and m >= 1,
            "arithmetic scale and dimensions")
    require(page["nc"] == n+m-1 and page["width"] == P+n.bit_length()+3,
            "source convolution extent and work width")
    Q = 1 << P
    for name, length in (("A", n), ("K", page["nc"]), ("B", m)):
        require(len(page[name]) == length and
                all(type(x) is int and 0 <= x <= Q for x in page[name]),
                "normalized stored factor: " + name)
    require(0 < page["c"] <= Q//4, "positive stored reciprocal at most one quarter")
    return p, P, sigma, n, m, Q


def row_data(page):
    """Return each exact stored linear row and its component error bound."""
    p, P, sigma, n, m, Q = parameters(page)
    R, c, eta, h = 1 << (2*sigma), F(page["c"], Q), F(1, Q), F(1, 1 << p)
    rows = []
    for z in range(m):
        b = F(page["B"][z], Q)
        kernel = [F(page["K"][n-1+z-j], Q) for j in range(n)]
        weights = [R*c*b*k*F(a, Q) for k, a in zip(kernel, page["A"])]
        bound = h + R*eta*(c*b*(sum(kernel, F(0))+1)+c+1)
        rows.append((weights, bound, kernel))
    return rows


def linear_block(values, page):
    """Exact stored-page linear action on arbitrary physical Fraction pairs."""
    require(len(values) == page["n"], "complete linear source window")
    return [tuple(sum((w*v[j] for w, v in zip(weights, values)), F(0))
                  for j in (0, 1)) for weights, _, _ in row_data(page)]


def audit_block(data, page):
    """Return (integer output pairs, source-compatible trace, JSON summary).

    The summary retains exact propagated residuals in physical value units;
    component_bound bounds each component, so 2*component_bound**2 bounds
    the squared complex defect. Geometry/tails are separate source premises.
    """
    p, P, sigma, n, m, Q = parameters(page)
    require(len(data) == n and all(len(v) == 2 and all(type(x) is int for x in v)
                                  for v in data), "integer p-grid source pairs")
    require(norm2(data) <= 1 << (2*p), "source unit disk")
    scale, R = 1 << p, 1 << (2*sigma)
    trace, nonzero = [], dict.fromkeys(STAGES, 0)
    outputs = [[0, 0] for _ in range(m)]
    terms = [{stage: [F(0), F(0)] for stage in STAGES} for _ in range(m)]

    def rounded(integer, shift, module, stage):
        # Integer division with a separately restored sign; no float or floor
        # on negative operands is used.
        result = inward(integer, shift)
        trace.append((module, integer, shift, result))
        nonzero[stage] += integer != result*(1 << shift)
        return result

    for component in (0, 1):
        weighted, e_a = [], []
        for j in range(n):
            operand = page["A"][j]*data[j][component]*(1 << (P-p))
            value = rounded(operand, P, "block", "weighted")
            weighted.append(value)
            e_a.append(F(value, Q)-F(page["A"][j]*data[j][component], Q*scale))
        convolution, e_k = [], []
        for k in range(page["nc"]):
            operand = sum(weighted[j]*page["K"][k-j]
                          for j in range(n) if 0 <= k-j < page["nc"])
            value = rounded(operand, P, "convolution", "convolution")
            convolution.append(value)
            e_k.append(F(value, Q)-F(operand, Q*Q))
        for z in range(m):
            index = n-1+z
            post = rounded(page["B"][z]*convolution[index], P, "block", "post")
            e_b = F(post, Q)-F(page["B"][z]*convolution[index], Q*Q)
            fine = rounded(page["c"]*post, P, "block", "fine")
            e_c = F(fine, Q)-F(page["c"]*post, Q*Q)
            output = rounded(fine, P-p-2*sigma, "block", "extract")
            e_e = F(output, scale)-F(R*fine, Q)
            outputs[z][component] = output
            b, c = F(page["B"][z], Q), F(page["c"], Q)
            terms[z]["weighted"][component] = R*c*b*sum(
                (F(page["K"][index-j], Q)*e_a[j] for j in range(n)), F(0))
            terms[z]["convolution"][component] = R*c*b*e_k[index]
            terms[z]["post"][component] = R*c*e_b
            terms[z]["fine"][component] = R*e_c
            terms[z]["extract"][component] = e_e
            require(all(abs(e) < F(1, Q) for e in (*e_a, *e_k, e_b, e_c)) and
                    abs(e_e) < F(1, scale), "individual inward residual sizes")
    outputs = [tuple(v) for v in outputs]
    physical = [tuple(F(x, scale) for x in v) for v in data]
    linear = linear_block(physical, page)
    rows = []
    for z, (weights, bound, kernel) in enumerate(row_data(page)):
        defect = tuple(F(outputs[z][j], scale)-linear[z][j] for j in (0, 1))
        reconstructed = tuple(sum((terms[z][stage][j] for stage in STAGES), F(0))
                              for j in (0, 1))
        require(defect == reconstructed, "exact five-term stored-row defect identity")
        require(all(abs(x) < bound for x in defect) and norm2([defect]) < 2*bound*bound,
                "complete stored-row quantization bound")
        rows.append(dict(stored_linear=pair(linear[z]), defect=pair(defect),
                         terms={stage: pair(terms[z][stage]) for stage in STAGES},
                         component_bound=fraction(bound), complex_bound2=fraction(2*bound*bound),
                         defect_norm2=fraction(norm2([defect])), row_mass=fraction(sum(weights, F(0))),
                         kernel_mass=fraction(sum(kernel, F(0))),
                         nonzero_propagated={stage: any(terms[z][stage]) for stage in STAGES}))
    return outputs, trace, dict(nonzero=nonzero, rows=rows,
                                output_sha256=digest(outputs), trace_sha256=digest(trace))


def profile_rows(profile):
    """Bind every natural target to exactly one stored page row."""
    result = [None]*profile["t"]
    precisions = set()
    for _, pages in profile["expansion_pages"]:
        for page in pages:
            precisions.add(page["p"])
            for z, (weights, bound, _) in enumerate(row_data(page)):
                target = page["target_start"]+z
                require(0 <= target < len(result) and result[target] is None,
                        "unique complete natural target")
                result[target] = ([( (page["source_start"]+j) % profile["s"], w)
                                   for j, w in enumerate(weights)], bound)
    require(len(precisions) == 1 and all(row is not None for row in result),
            "common p grid and complete axis rows")
    return precisions.pop(), result


def linear_axis(values, shape, position, profile):
    """Exact Fraction action on one complete natural tensor axis."""
    shape = tuple(shape)
    require(0 <= position < len(shape) and shape[position] == profile["s"],
            "original axis extent")
    require(len(values) == _size(shape), "complete tensor input")
    _, rows = profile_rows(profile)
    following = shape[:position]+(profile["t"],)+shape[position+1:]
    result = []
    for coordinate in product(*(range(n) for n in following)):
        row, _ = rows[coordinate[position]]
        total = [F(0), F(0)]
        for source, weight in row:
            at = list(coordinate)
            at[position] = source
            value = values[_index(at, shape)]
            total[0] += weight*value[0]
            total[1] += weight*value[1]
        result.append(tuple(total))
    return result, following


def _size(shape):
    size = 1
    for extent in shape:
        require(type(extent) is int and extent >= 1, "positive tensor extent")
        size *= extent
    return size


def _index(coordinate, shape):
    index = 0
    for value, extent in zip(coordinate, shape):
        index = index*extent+value
    return index


class AxisAudit:
    """Observe successive actual computed axes; never treat rounding as linear."""
    def __init__(self):
        self.exact = self.last = self.shape = self.p = None
        self.component_bound = F(0)
        self.records = []

    def observe(self, data, shape, position, profile, output, output_shape):
        p, rows = profile_rows(profile)
        shape, output_shape = tuple(shape), tuple(output_shape)
        data, output = [tuple(v) for v in data], [tuple(v) for v in output]
        if self.exact is None:
            self.p, self.shape, self.last = p, shape, data
            self.exact = [tuple(F(v, 1 << p) for v in row) for row in data]
        require(p == self.p and shape == self.shape and data == self.last,
                "telescope uses the preceding computed input")
        computed = [tuple(F(v, 1 << p) for v in row) for row in data]
        actual = [tuple(F(v, 1 << p) for v in row) for row in output]
        require(norm2(computed) <= 1, "computed-input unit-disk admission")
        on_computed, following = linear_axis(computed, shape, position, profile)
        exact, exact_shape = linear_axis(self.exact, shape, position, profile)
        require(following == exact_shape == output_shape and len(actual) == len(exact),
                "complete natural output shape")
        previous = [tuple(x-y for x, y in zip(c, e)) for c, e in zip(computed, self.exact)]
        propagated, _ = linear_axis(previous, shape, position, profile)
        local = [tuple(x-y for x, y in zip(a, c)) for a, c in zip(actual, on_computed)]
        total = [tuple(x-y for x, y in zip(a, e)) for a, e in zip(actual, exact)]
        require(all(t == tuple(l+p for l, p in zip(d, old))
                    for t, d, old in zip(total, local, propagated)),
                "exact computed-input linear error propagation")
        local_bound = max(bound for _, bound in rows)
        beta = max(sum((weight for _, weight in row), F(0)) for row, _ in rows)
        for coordinate, defect in zip(product(*(range(n) for n in following)), local):
            bound = rows[coordinate[position]][1]
            require(all(abs(v) < bound for v in defect), "row-specific actual local defect")
        bound = local_bound+beta*self.component_bound
        require(all(abs(v) < bound for error in total for v in error),
                "complete component telescope bound")
        record = dict(axis=position, input_shape=shape, output_shape=following,
                      local_component_bound=fraction(local_bound), row_norm_bound=fraction(beta),
                      cumulative_component_bound=fraction(bound),
                      local_defect_norm2=fraction(norm2(local)),
                      total_defect_norm2=fraction(norm2(total)), complex_bound2=fraction(2*bound*bound),
                      exact_identity_sha256=digest((local, propagated, total)),
                      omitted_prior_error_distinguished=any(any(v) for v in propagated))
        self.exact, self.last, self.shape, self.component_bound = exact, output, following, bound
        self.records.append(record)
        return record


def controls():
    """Exact arithmetic-only discriminators; no Gaussian/production fixture."""
    page = dict(p=3, P=8, sigma=1, n=1, m=1, nc=1, width=12,
                A=[255], K=[255], B=[255], c=63)
    data = [(7, -3)]
    output, trace, summary = audit_block(data, page)
    row = summary["rows"][0]
    unpack = lambda x: F(*x)
    actual = tuple(unpack(x) for x in row["defect"])
    terms = {stage: tuple(unpack(x) for x in row["terms"][stage]) for stage in STAGES}
    omitted = {}
    for missing in STAGES:
        wrong = tuple(sum((terms[stage][j] for stage in STAGES if stage != missing), F(0))
                      for j in (0, 1))
        require(wrong != actual, "omitted propagated residual is observable: " + missing)
        omitted[missing] = pair(tuple(a-b for a, b in zip(actual, wrong)))
    wrong_scale = tuple(sum((terms[stage][j]/4 for stage in STAGES if stage != "extract"), F(0))
                        + terms["extract"][j] for j in (0, 1))
    require(wrong_scale != actual, "omitting restoration from internal errors is observable")
    # This is the exact scalar truncation used internally, not a continuity
    # assumption inferred from norm contraction at zero.
    left, right = F(3, 4), F(4, 4)
    rounded_left, rounded_right = inward(3, 2), inward(4, 2)
    require(abs(rounded_right-rounded_left) > abs(right-left),
            "inward truncation is not nonexpansive")
    return dict(scope="arithmetic-only normalized page; not a source-produced Gaussian page",
                page=page, data=data, output=output, nonzero=summary["nonzero"],
                omitted_term_discrepancies=omitted,
                missing_restoration_discrepancy=pair(tuple(a-b for a, b in zip(actual, wrong_scale))),
                nonlinear_lipschitz=dict(inputs=[fraction(left), fraction(right)],
                                         outputs=[rounded_left, rounded_right]),
                trace_sha256=digest(trace))
