"""External integer schedule oracle; never used by the physical consumer.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This checks bit semantics. Original-source inverse validation is separate.
"""


def truncate(value, bits):
    return (-1 if value < 0 else 1) * (abs(value) >> bits)


def action(words, bundle, run_oracle, folded_pages, *, omit_k=False,
           floor_down=False, transpose_banks=False):
    p = bundle.plan
    f, boundary, permutation = p.f, bundle.boundary_indices, bundle.folded_plan['permutation']

    def down(value, bits):
        return value >> bits if floor_down else truncate(value, bits)

    def block(values):
        result = []
        for run in bundle.runs:
            q = run.native.plan.f
            native = tuple(down(x, f-q) for x in values[run.start:run.start+run.n])
            result.extend(x << (f-q) for x in run_oracle.action(native, run.native))
        return result

    def matrix(bank, values):
        m, b = len(values), p.band
        vector = [values[i] for i in permutation]
        rows = [[bank[i*(2*b+1)+j-i+b] if abs(j-i) <= b else 0
                 for j in range(m)] for i in range(m)]
        if transpose_banks:
            rows = list(zip(*rows))
        result = [0] * m
        for i, original in enumerate(permutation):
            result[original] = truncate(sum(a*x for a,x in zip(rows[i],vector)), f)
        return result

    components = []
    for c in (0,1):
        rhs = [words[q][c] for q in bundle.selected]
        y = block(rhs)
        t = matrix(bundle.sb_coefficients, [y[i] for i in boundary])
        q = bundle.folded_plan['precision']
        z = [x << (f-q) for x in folded_pages.rounded_oracle(
            bundle.folded_plan, [down(x, f-q) for x in t])]
        kz = [0]*len(boundary) if omit_k else matrix(bundle.k_coefficients, z)
        corrected = list(rhs)
        for i, value in zip(boundary,kz):
            corrected[i] -= value
        answer = block(corrected)
        output = [v[c] for v in words]
        for i, value in zip(bundle.selected,answer):
            output[i] = value
        components.append(output)
    return tuple(zip(*components))
