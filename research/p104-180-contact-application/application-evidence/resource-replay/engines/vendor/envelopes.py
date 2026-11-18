"""Exact positive forward envelopes with independent backward cut checks.

These are scalar triangle bounds under the stated complete-fibre unitary
contracts. They neither simulate rounding nor establish native provider admission.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from source_binding import need, sources, strict_power, fraction_string, oddpart


def frame_span(basis):
    s = {0}
    for v in basis:
        need(isinstance(v, int) and 0 < v < 512 and v not in s, "independent frame basis")
        s |= {u ^ v for u in tuple(s)}
    return frozenset(s)


def validate_word(word):
    n, owned_count = word["public"], word["owned_fields"]
    need(n == len(word["initial"]) == len(word["final"]), "public frame lists")
    spans = list(map(frame_span, word["frames"]))
    cur = list(word["initial"]) + [None] * owned_count
    owned, zero = set(), set(range(n, n + owned_count))
    life = peak = 0
    counts = Counter()
    scalar = Counter()
    max_num = max_den = 0
    for i, e in enumerate(word["program"]):
        op, r = e[:2]
        need(0 <= r < len(cur), "word role at " + str(i))
        counts[op] += 1
        if op == "INIT":
            need(len(e) == 3 and r >= n and r not in owned and cur[r] is None,
                 "fresh owned INIT at " + str(i))
            need(0 <= e[2] < len(spans), "INIT frame")
            owned.add(r); zero.add(r); cur[r] = e[2]
            life += 1; peak = max(peak, len(owned))
        elif op == "CLEAR":
            need(len(e) == 3 and r in owned and cur[r] == e[2], "owned CLEAR")
            owned.remove(r); zero.add(r); cur[r] = None
        elif op == "MOVE":
            _, _, a, b, private = e
            need(cur[r] == a and bool(private) == (r in owned), "MOVE source/owner")
            need(0 <= b < len(spans), "MOVE destination")
            need((spans[a] < spans[b] or spans[b] < spans[a]) if private
                 else spans[a] < spans[b], "strict source frame nesting")
            cur[r] = b
            # A rounded child need not preserve exact zero.
            zero.discard(r)
        else:
            need(op in ("ADD", "COPY", "SCALE"), "known native operation")
            q = F(e[2] if op == "SCALE" else e[3])
            need(q and abs(q) + 1 < 2 ** 16, "nonzero bounded source coefficient")
            need(cur[r] == e[-1] and cur[r] is not None, "scalar live frame")
            if op != "SCALE":
                s = e[2]
                need(0 <= s < len(cur) and s != r and cur[s] == cur[r], "same-frame source")
                if op == "COPY":
                    need(r in owned and r in zero, "COPY into freshly exact zero")
                zero.discard(r)
            max_num = max(max_num, abs(q.numerator))
            max_den = max(max_den, q.denominator)
            scalar["noninteger" if q.denominator > 1 else "integer"] += 1
            scalar["odd" if oddpart(q.denominator) > 1 else "dyadic"] += 1
    need(not owned and cur[:n] == word["final"], "all owned returned; declared final frames")
    need((life, peak, owned_count) == (54, 43, 51), "source lifecycle census")
    return dict(events=len(word["program"]), public=n, owned_labels=owned_count,
                lifetimes=life, peak_owned=peak, opcodes=dict(counts), scalars=dict(scalar),
                max_numerator=max_num, numerator_bits=max_num.bit_length(),
                max_denominator=max_den, denominator_bits=max_den.bit_length())


def summarize(values):
    return {k: {"exact": fraction_string(v[0]), "strict_power_of_two": strict_power(v[0]),
                "witness": v[1]} for k, v in values.items()}


def native_envelope(word):
    census = validate_word(word)
    n, size = word["public"], word["public"] + word["owned_fields"]
    mass = [F(i < n) for i in range(size)]
    error = [F(0) for _ in range(size)]
    peaks = {"M": (F(1), {"cut": 0, "register": 0, "factor": "1"}),
             "Sigma": (F(0), {"cut": 0, "register": 0, "factor": "1"})}

    def note(name, value, cut, register, factor=F(1), kind="stored"):
        if value > peaks[name][0]:
            peaks[name] = (value, dict(cut=cut, register=register,
                                       factor=str(factor), kind=kind))

    for i, e in enumerate(word["program"]):
        op, r = e[:2]
        if op == "MOVE":
            error[r] += 1
        elif op in ("INIT", "CLEAR"):
            mass[r] = error[r] = F(0)
        else:
            q = abs(F(e[2] if op == "SCALE" else e[3]))
            if op == "SCALE":
                mass[r] *= q; error[r] *= q
            else:
                s = e[2]
                note("M", q * mass[s], i, s, q, "pre-add-product")
                note("Sigma", q * error[s], i, s, q, "pre-add-product")
                mass[r] += q * mass[s]; error[r] += q * error[s]
            if q.denominator > 1:
                error[r] += 1
        note("M", mass[r], i + 1, r)
        note("Sigma", error[r], i + 1, r)
    r = max(range(n), key=error.__getitem__)
    peaks["Gamma"] = (error[r], dict(cut=len(word["program"]), register=r, factor="1", kind="public-return"))
    checks = {}
    for name, (value, witness) in peaks.items():
        m, d, active = native_adjoint(word, witness)
        need((m if name == "M" else d) == value, "backward native witness: " + name)
        checks[name] = dict(entrance_mass=str(m), residual_mass=str(d), active_residual_sites=active)
    return peaks, dict(census=census, bounds=summarize(peaks), independent_adjoint=checks)


def native_adjoint(word, witness):
    """Transpose recurrence from one cut, not a second forward-state run."""
    size = word["public"] + word["owned_fields"]
    lam = [F(0) for _ in range(size)]
    lam[witness["register"]] = F(witness["factor"])
    residual, active = F(0), 0
    for e in reversed(word["program"][:witness["cut"]]):
        op, r = e[:2]
        if op in ("INIT", "CLEAR"):
            lam[r] = F(0)
        elif op == "MOVE":
            residual += lam[r]; active += bool(lam[r])
        else:
            q = abs(F(e[2] if op == "SCALE" else e[3]))
            if q.denominator > 1:
                residual += lam[r]; active += bool(lam[r])
            if op == "SCALE":
                lam[r] *= q
            else:
                lam[e[2]] += q * lam[r]
    return sum(lam[:word["public"]]), residual, active


def caller_envelope(caller, word_peaks, word):
    """Contract J only at its proved exact endpoint; include each native interior."""
    mw, sw, gw = (word_peaks[k][0] for k in ("M", "Sigma", "Gamma"))
    size = caller["roles"]
    mass, error = [F(1)] * size, [F(0)] * size
    peaks = {"M_caller": (F(1), {}), "Sigma_caller": (F(0), {}),
             "M_joint_entrance": (F(1), {}), "E_joint_entrance": (F(0), {}),
             "M_context": (F(1), {}), "Sigma_context": (F(0), {})}
    sites = Counter()
    j_order = []
    log = []

    def note(name, value, i, r=None, *, cut=None, factor=F(1), kind="stored"):
        if value > peaks[name][0]:
            peaks[name] = (value, dict(event=i, register=r, cut=i + 1 if cut is None else cut,
                                      factor=str(factor), kind=kind))

    for i, e in enumerate(caller["events"]):
        ty = e[0]
        if ty == "J":
            _, j, ar, br = e
            need(len(ar) == 4 and len(br) == 4 and br[2:] == ["-1", "1/2"], "exact J source signature")
            u, v, x, y = ar; s, t = br[:2]
            regs = (u, v, x, y, s, t)
            need(len(set(regs)) == 6 and all(0 <= r < size for r in regs), "six distinct J roles")
            need(all(0 <= r < 38 for r in ar) and all(38 <= r < 76 for r in br[:2]),
                 "current type-local J main binding")
            mi, ei = max([F(1)] + [mass[r] for r in regs]), max(error[r] for r in regs)
            mr, er = max(regs, key=mass.__getitem__), max(regs, key=error.__getitem__)
            note("M_joint_entrance", mi, i, mr, cut=i)
            note("E_joint_entrance", ei, i, er, cut=i)
            note("M_context", mw * mi, i)
            note("Sigma_context", mw * ei + sw, i)
            # Each stage's 1,061 arbitrary public helper inputs are distinct raw
            # inputs, not zero; their initial bound is 1 and prior defect is 0.
            out_m = (mass[u], mass[v] + mass[u], mass[x] + mass[y], mass[y],
                     mass[s] + mass[t], (mass[s] + mass[t]) / 2)
            out_e = (error[u], error[v] + error[u], error[x] + error[y], error[y],
                     error[s] + error[t], (error[s] + error[t]) / 2)
            for r, a, b in zip(regs, out_m, out_e):
                mass[r], error[r] = a, b + gw
            j_order.append(j); sites["J"] += 1
            log.append(dict(event=i, stage=j, entrance_mass=str(mi), entrance_defect=str(ei)))
        else:
            need(ty in ("A", "B"), "known caller type")
            op, r = e[1:3]
            off = caller["types"][ty]["offset"]
            count = caller["types"][ty]["roles"]
            need(off <= r < off + count, "type-local target")
            sites[op] += 1
            if op == "SWAP":
                s = e[3]
                need(off <= s < off + count and s != r, "type-local SWAP")
                mass[r], mass[s] = mass[s], mass[r]
                error[r], error[s] = error[s], error[r]
            elif op in ("LAMBDA", "IDLE_ONE"):
                if op == "LAMBDA":
                    need(e[3] in (-1, 1), "unit Lambda sign")
                else:
                    need(len(e[3]) == len(set(e[3])) and all(1 <= k <= 18 for k in e[3]), "idle mask")
                error[r] += 1
            elif op == "QUERY":
                s = e[3]
                need(off <= s < off + count and s != r and e[4] == -1, "retained negative query")
                mass[r] += mass[s]; error[r] += error[s] + 1
            elif op == "ADD":
                s, q = e[3], abs(F(e[4]))
                need(off <= s < off + count and r != s and q, "type-local ADD")
                note("M_caller", q * mass[s], i, s, cut=i, factor=q, kind="pre-add-product")
                note("Sigma_caller", q * error[s], i, s, cut=i, factor=q, kind="pre-add-product")
                mass[r] += q * mass[s]; error[r] += q * error[s] + (q.denominator > 1)
                sites["noninteger_scalar"] += q.denominator > 1
            elif op == "SCALE":
                q = abs(F(e[3])); need(q, "nonzero caller SCALE")
                mass[r] *= q; error[r] = q * error[r] + (q.denominator > 1)
                sites["noninteger_scalar"] += q.denominator > 1
            else:
                raise ValueError("non-retained caller opcode: " + str(op))
        for r in range(size):
            note("M_caller", mass[r], i, r)
            note("Sigma_caller", error[r], i, r)
    need(j_order == list(range(1, 19)), "exact eighteen native calls")
    # Completed helper outputs have ideal norm <=1 and defect <=gw; maximum
    # over independent helper fields does not multiply by 1,061 or by 18.
    peaks["M_context"] = max(peaks["M_context"], peaks["M_caller"], key=lambda a: a[0])
    peaks["Sigma_context"] = max(peaks["Sigma_context"], peaks["Sigma_caller"], key=lambda a: a[0])
    ri = max(range(size), key=error.__getitem__)
    need(error[ri] >= gw, "main output dominates helper-return defect in this source")
    peaks["Gamma_context"] = (error[ri], dict(register=ri, cut=len(caller["events"]), factor="1", kind="public-return"))
    need(len(caller["types"]["A"]["ports"]) == 96 and len(caller["types"]["B"]["ports"]) == 8,
         "current physical type multiplicities")
    mains = set(word["live"]) | {r + 112 for r in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    need(len(mains) == 400 and word["public"] - len(mains) == 1061, "fresh per-stage helper census")
    adjoints = {}
    for name in ("M_caller", "Sigma_caller", "M_joint_entrance", "E_joint_entrance", "Gamma_context"):
        value, witness = peaks[name]
        m, d, j_part, primitive_part = caller_adjoint(caller, witness, gw)
        need((m if name.startswith("M_") else d) == value, "backward caller witness: " + name)
        adjoints[name] = dict(entrance_mass=str(m), residual_mass=str(d),
                              joint_coefficient=str(j_part), primitive_coefficient=str(primitive_part))
    return peaks, dict(bounds=summarize(peaks), sites=dict(sites), joint_entries=log,
                      independent_adjoint=adjoints,
                      physical_main_inputs=3952, fresh_arbitrary_helpers=18 * 1061,
                      helper_allocation_premise="distinct (stage, helper) public inputs as in frozen caller proof")


def caller_adjoint(caller, witness, gamma_word):
    lam = [F(0)] * caller["roles"]
    lam[witness["register"]] = F(witness["factor"])
    joint, primitive = F(0), F(0)
    for e in reversed(caller["events"][:witness["cut"]]):
        if e[0] == "J":
            u, v, x, y = e[2]; s, t = e[3][:2]
            joint += sum(lam[r] for r in (u, v, x, y, s, t))
            a, b = lam[s], lam[t]
            lam[u] += lam[v]
            lam[y] += lam[x]
            lam[s] = lam[t] = a + b / 2
            continue
        op, r = e[1:3]
        if op == "SWAP":
            s = e[3]; lam[r], lam[s] = lam[s], lam[r]
        elif op in ("LAMBDA", "IDLE_ONE"):
            primitive += lam[r]
        elif op == "QUERY":
            primitive += lam[r]; lam[e[3]] += lam[r]
        else:
            q = abs(F(e[3] if op == "SCALE" else e[4]))
            if q.denominator > 1:
                primitive += lam[r]
            if op == "SCALE":
                lam[r] *= q
            else:
                lam[e[3]] += q * lam[r]
    return sum(lam), joint * gamma_word + primitive, joint, primitive


def run():
    caller, word = sources()
    wp, wr = native_envelope(word)
    cp, cr = caller_envelope(caller, wp, word)
    expected_w = {"M": 237, "Sigma": 235, "Gamma": 235}
    expected_c = {"M_caller": 121, "Sigma_caller": 342, "M_joint_entrance": 119,
                  "E_joint_entrance": 340, "M_context": 355, "Sigma_context": 576,
                  "Gamma_context": 337}
    for k, p in expected_w.items():
        need(strict_power(wp[k][0]) == p, "frozen native bound " + k)
    for k, p in expected_c.items():
        need(strict_power(cp[k][0]) == p, "frozen caller bound " + k)
    return dict(native=wr, caller=cr)
