#!/usr/bin/env python3
"""Independent compact-control carry/repair audit; no tape or kappa claim.

SPDX-License-Identifier: Apache-2.0
John-Michael Smith, with substantial OpenAI Codex assistance.
"""
import argparse
from array import array
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import struct
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 69


def require(ok, message):
    if not ok:
        raise ValueError(message)


class Gadget:
    """Direct integer transcription of the four updates, not source op tags."""
    def __init__(self, n, K, rho, G):
        require(n >= 1 and K >= 1 and 0 <= rho < K and G >= 1, "domain")
        self.n, self.K, self.rho, self.G = n, K, rho, G
        self.B = 1 << G
        self.C = self.B ** n
        self.Y = 1 << ((n + 1) * K)
        self.positions = tuple(rho + i * K for i in range(n))

    def packed(self, y):
        return sum(((y >> j) & 1) << (i * self.G)
                   for i, j in enumerate(self.positions))

    def wide_bits(self, x):
        return sum(((x >> j) & 1) << j for j in self.positions)

    def full_ideal(self, state):
        x, y, t, u, b = state
        high = self.rho + self.n * self.K
        return x, y ^ self.wide_bits(x) ^ (((x >> high) & 1) << high), t, u, b

    def ideal(self, state):
        x, y, t, u, b = state
        return x, y ^ self.wide_bits(x), t, u, b

    def flip(self, y, t, b, c):
        # c is a radix-B vector whose digit parities are the controls.
        # Each temporary update explicitly performs its dirty-back sandwich.
        offset = sum(2 * ((c >> (i*self.G)) & 1) *
                     ((t >> (i*self.G)) & (self.B-1)) * (1 << j)
                     for i, j in enumerate(self.positions))
        y = (y + offset) % self.Y
        t, b = b, t
        b = (b + self.packed(y)) % self.C
        t, b = b, t
        offset = sum(((c >> (i*self.G)) & 1) *
                     (1-2*((t >> (i*self.G)) & (self.B-1))) * (1 << j)
                     for i, j in enumerate(self.positions))
        y = (y + offset) % self.Y
        control_mask = sum(((c >> (i*self.G)) & 1) << j
                           for i, j in enumerate(self.positions))
        t, b = b, t
        b = (b - self.packed(y ^ control_mask)) % self.C
        t, b = b, t
        return y, t, b

    def run(self, state, late):
        x, y, t, u, b = state
        if late:
            y, t, b = self.flip(y, t, b, u)
            u, b = b, u
            b = (b + self.packed(x)) % self.C
            u, b = b, u
            y, t, b = self.flip(y, t, b, u)
            u, b = b, u
            b = (b - self.packed(x)) % self.C
            u, b = b, u
        else:
            y, t, b = self.flip(y, t, b, self.packed(x))
        return x, y, t, u, b

    def inverse_flip(self, y, t, c):
        control_mask = sum(((c >> (i*self.G)) & 1) << j
                           for i, j in enumerate(self.positions))
        t = (t + self.packed(y ^ control_mask)) % self.C
        offset = sum(((c >> (i*self.G)) & 1) *
                     (1-2*((t >> (i*self.G)) & (self.B-1))) * (1 << j)
                     for i,j in enumerate(self.positions))
        y = (y-offset) % self.Y
        t = (t-self.packed(y)) % self.C
        offset = sum(2*((c >> (i*self.G)) & 1) *
                     ((t >> (i*self.G)) & (self.B-1)) * (1 << j)
                     for i,j in enumerate(self.positions))
        return (y-offset) % self.Y, t

    def inverse(self, state, late):
        x,y,t,u,b = state
        if late:
            u = (u+self.packed(x)) % self.C
            y,t = self.inverse_flip(y,t,u)
            u = (u-self.packed(x)) % self.C
            y,t = self.inverse_flip(y,t,u)
        else:
            y,t = self.inverse_flip(y,t,self.packed(x))
        return x,y,t,u,b

    def core_good(self, state):
        _, y, t, _, _ = state
        return all(((t >> (i*self.G)) & (self.B-1)) < self.B-1
                   and 2*self.B <= ((y >> (j+1)) & ((1 << (self.K-1))-1))
                   < (1 << (self.K-1))-2*self.B
                   for i, j in enumerate(self.positions))

    def good(self, state, late, expanded=False):
        if not self.core_good(state):
            return False
        if not late:
            return True
        u = state[3]
        return all(((u >> (i*self.G)) & (self.B-1)) < self.B-1
                   for i in range(self.n - int(expanded)))

    def carry_prediction(self, state):
        x, y, t, u, b = state
        carry = 0
        mask = 0
        interior = []
        for i, j in enumerate(self.positions):
            if i:
                interior.append(carry)
            ci = (x >> j) & 1
            mask |= (ci ^ carry) << j
            carry = (((u >> (i*self.G)) & (self.B-1)) + ci + carry) // self.B
        return (x, y ^ mask, t, u, b), interior, carry


def verify_pins():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for rel, digest in pins["files"].items():
        actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        require(actual == digest, f"source drift: {rel}")
    return pins


def load_source():
    # Imports use only the pinned repository Python files listed in SOURCES.
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "pinned_compact_controls", ROOT / "scripts/audit_compact_controls.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_state(s, late):
    x, y, t, u, b = s
    d = dict(x=x, y=y, t=t, b=b)
    if late:
        d["u"] = u
    return d


def source_agreement(source):
    rng = random.Random(SEED)
    cases = 0
    counts = {"early": 0, "late": 0}
    # Distinct widths and offsets, full spectator bits, arbitrary back dirt.
    for n, K, rho, G in ((1,5,4,1), (2,5,4,1), (2,6,5,2),
                          (3,7,6,2), (4,9,0,3), (7,10,9,3)):
        g = Gadget(n,K,rho,G)
        for late in (False,True):
            for _ in range(256):
                s = (rng.randrange(g.Y),rng.randrange(g.Y),rng.randrange(g.C),
                     rng.randrange(g.C),rng.randrange(g.C))
                expected = source_state(g.run(s,late),late)
                original = source_state(s,late)
                actual = source.execute(original,n,K,rho,G,late=late)
                require(actual == expected, "independent/source forward mismatch")
                require(g.inverse(g.run(s,late),late) == s, "independent inverse")
                require(source.execute(actual,n,K,rho,G,late=late,inverse=True)
                        == original, "source inverse mismatch")
                require(source.exceptional(original,n,K,rho,G,late)
                        == (not g.good(s,late)), "source good predicate mismatch")
                if late and g.core_good(s):
                    require(g.run(s,late) == g.carry_prediction(s)[0], "carry law")
                cases += 1
                counts["late" if late else "early"] += 1
    return dict(cases=cases, counts=counts, seed=SEED,
                scope="Finite comparison with pinned source; not exhaustive outside main domain")


def repair_records(payloads, holes, ideal_xor, *, wrong_keys=False, duplicate_key=False):
    extracted = [((q if wrong_keys else payloads[q]) ^ ideal_xor, payloads[q])
                 for q in holes]
    if duplicate_key:
        extracted[1] = (extracted[0][0], extracted[1][1])
    extracted.sort(key=lambda pair: pair[0])
    require([key for key,_ in extracted] == holes,
            "destination keys do not fill exactly the marked holes")
    repaired = payloads[:]
    for hole, (_,record) in zip(holes,extracted):
        repaired[hole] = record
    return repaired


def permutation_audit(late):
    """Exhaust representatives; sort correction keys and fill marked holes.

    Only fixed x,b fibers are split. t may change on bad addresses. All three
    selected x bits and y's top selected bit are represented, including spill.
    """
    g = Gadget(2,5,4,1)
    active_y = 1 << 11
    u_count = g.C if late else 1
    size = active_y*g.C*u_count
    total = old_good = new_good = core = carry_errors = mismatches = 0
    corrected = [0,0]
    digests = [hashlib.sha256() for _ in range(5)]
    first_error = None
    for x_code in range(8):
        x = sum(((x_code >> i)&1) << (4+5*i) for i in range(3))
        ideal_xor = (x_code & 1) | (((x_code >> 1)&1) << 5)
        high_xor = ((x_code >> 2)&1) << 10
        for b in range(g.C):
            # payloads[q] is the unique input record now at address q.
            payloads = array("i", [-1])*size
            masks = [bytearray(size), bytearray(size)]
            for idx in range(size):
                qy = idx % active_y
                t = (idx // active_y) % g.C
                u = idx // (active_y*g.C)
                s = (x,qy << 4,t,u,b)
                out = g.run(s,late)
                require(out[0] == x and out[4] == b and out[1] % 16 == 0,
                        "fiber/spectator not preserved")
                dest = (out[1] >> 4) + active_y*(out[2]+g.C*out[3])
                require(0 <= dest < size and payloads[dest] == -1,
                        "actual map is not a permutation")
                payloads[dest] = idx
                for mode in (0,1):
                    is_good = g.good(s,late,expanded=bool(mode))
                    masks[mode][idx] = not is_good
                    require(g.good(out,late,expanded=bool(mode)) == is_good,
                            "bad-set invariance")
                    if is_good:
                        require(dest == (idx ^ ideal_xor), "good-set identity")
                old_good += not masks[0][idx]
                new_good += not masks[1][idx]
                if late and g.core_good(s):
                    prediction, carries, _ = g.carry_prediction(s)
                    require(out == prediction, "exhaustive carry law")
                    require((out == g.ideal(s)) == (not any(carries)),
                            "interior carry iff failure")
                    core += 1
                    carry_errors += any(carries)
                if dest != (idx ^ ideal_xor):
                    mismatches += 1
                    if first_error is None:
                        first_error = dict(input=list(s), actual=list(out),
                                           ideal=list(g.ideal(s)))
                total += 1
            require(all(v >= 0 for v in payloads), "unfilled output address")
            digests[0].update(struct.pack(f"<{size}I", *payloads))
            for mode in (0,1):
                holes = [q for q in range(size) if masks[mode][q]]
                # Invert by the independently built full permutation table.
                # It does not call the original inverse interpreter.
                repaired = repair_records(payloads,holes,ideal_xor)
                # The elementary highest-bit XOR acts on addresses afterwards.
                full = repaired[:]
                for q, record in enumerate(repaired):
                    full[q ^ high_xor] = record
                for q, record in enumerate(full):
                    original = (x,(record % active_y) << 4,
                                (record // active_y) % g.C,
                                record // (active_y*g.C),b)
                    expected = g.full_ideal(original)
                    expected_index = (expected[1] >> 4) + active_y*(expected[2]+g.C*expected[3])
                    require(q == expected_index,
                            "full selected XOR / record preservation")
                digests[mode+1].update(struct.pack(f"<{size}I", *repaired))
                digests[mode+3].update(struct.pack(f"<{size}I", *full))
                corrected[mode] += len(holes)
    require(total == (1048576 if late else 262144), "coverage total")
    require(old_good == 16384, "original good count")
    require(new_good == (32768 if late else 16384), "expanded good count")
    require(digests[1].digest() == digests[2].digest(), "repair policies differ")
    require(digests[3].digest() == digests[4].digest(), "full maps differ")
    return dict(order="late" if late else "early", parameters=dict(n=2,K=5,rho=4,G=1),
                representatives=total, complete_rectangle_addresses=2**36,
                spectator_multiplicity=2**(16 if late else 18),
                original_good=old_good, expanded_good=new_good,
                uncorrected_mismatches=mismatches, first_uncorrected_mismatch=first_error,
                carry_law_cases=core, carry_law_failures_predicted=carry_errors,
                sorted_hole_records_original=corrected[0],
                sorted_hole_records_expanded=corrected[1],
                actual_permutation_sha256=digests[0].hexdigest(),
                repaired_low_permutation_sha256=digests[1].hexdigest(),
                repaired_full_permutation_sha256=digests[3].hexdigest())


def density_checks():
    # Exact product count, contrasted with the original union bound; no sampling.
    rows = []
    for n,K,G in ((1,5,1),(2,5,1),(2,3,2),(2,12,4),(3,16,8),(7,20,8)):
        B,H = 1<<G, 1<<(K-1)
        wide = Fraction(max(0,H-4*B),H)**n
        t_good = Fraction(B-1,B)**n
        old = wide*t_good*t_good
        new = wide*t_good*Fraction(B-1,B)**(n-1)
        bound = min(Fraction(1), n*(Fraction(2,B)+Fraction(8*B,1<<K)))
        new_bound = min(Fraction(1), Fraction(2*n-1,B)+Fraction(8*n*B,1<<K))
        require(1-old <= bound and 1-new <= new_bound, "density bound")
        require(new*Fraction(B-1,B) == old, "expanded density ratio")
        rows.append(dict(n=n,K=K,G=G,original_good_fraction=str(old),
                         expanded_good_fraction=str(new),old_bad_bound=str(bound),
                         expanded_bad_bound=str(new_bound)))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a receipt instead of comparing RESULT.json")
    args = parser.parse_args()
    pins = verify_pins()
    source = load_source()
    result = dict(status="PASS_COMPACT_CARRY_REPAIR_AUDIT", seed=SEED,
                  base_commit=pins["base_commit"], source_agreement=source_agreement(source))
    result["exhaustive"] = [permutation_audit(False),permutation_audit(True)]
    result["densities"] = density_checks()
    result["negative_controls"] = negative_controls(source)
    if args.write:
        args.write.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        require(result == expected, "receipt mismatch")
    print("PASS_COMPACT_CARRY_REPAIR_AUDIT: 1310720 representatives; "
          "3072 source comparisons; " + str(len(result["negative_controls"])) + " negative controls")


# Negative controls are below the main routines so their witnesses remain easy
# to review independently of the exhaustive interpreter.
def negative_controls(source):
    controls = []
    # Named tuple order is (x,y,t,u,b). These are omitted-hypothesis examples,
    # never counterexamples to the original sufficient good-set statement.
    witnesses = [
        ("omit_lower_u_guard",(2,5,4,1),(16,4224,0,1,2),"u"),
        ("omit_t_guard",(2,6,5,2),(2080,33312,3,0,7),"t"),
        ("omit_wide_guard",(2,6,5,2),(2080,34784,2,0,7),"wide"),
    ]
    for name,p,s,violated in witnesses:
        g = Gadget(*p)
        out,wanted = g.run(s,True),g.ideal(s)
        t_ok = all(((s[2] >> (i*g.G)) & (g.B-1)) < g.B-1 for i in range(g.n))
        u_ok = all(((s[3] >> (i*g.G)) & (g.B-1)) < g.B-1 for i in range(g.n))
        wide_ok = all(2*g.B <= ((s[1] >> (j+1)) & ((1 << (g.K-1))-1))
                      < (1 << (g.K-1))-2*g.B for j in g.positions)
        conditions = dict(t=t_ok,u=u_ok,wide=wide_ok)
        require([k for k,v in conditions.items() if not v] == [violated],
                "guard control is not isolated")
        require(out != wanted and not g.good(s,True), "undetected omitted guard")
        require(source.execute(source_state(s,True),*p,late=True)
                == source_state(out,True), "source control mismatch")
        require(g.ideal(g.inverse(out,True)) == wanted, "valid repair failed")
        controls.append(dict(name=name,parameters=list(p),input=list(s),
                             actual=list(out),expected=list(wanted),premises=conditions))
    g = Gadget(2,6,5,2)
    s = (2080,33312,3,0,7)
    q = g.run(s,True)
    wrong = g.inverse(g.ideal(q),True)
    require(wrong != g.ideal(s), "wrong composition not detected")
    controls.append(dict(name="wrong_repair_order_S_inverse_T",input=list(s),
                         post_S=list(q),wrong=list(wrong),expected=list(g.ideal(s))))
    # Use real incorrect T(q) keys in a complete later-source x=16,b=0 fiber.
    # Every hole still receives one key, but payload provenance is incorrect.
    h = Gadget(2,5,4,1)
    size,active_y = 32768,2048
    payloads = array("i", [-1])*size
    holes = []
    for idx in range(size):
        s0 = (16,(idx % active_y)<<4,(idx//active_y)%4,idx//8192,0)
        out = h.run(s0,True)
        dest = (out[1]>>4)+active_y*(out[2]+4*out[3])
        require(payloads[dest] == -1,"control map collision")
        payloads[dest] = idx
        if not h.good(s0,True):
            holes.append(idx)
    correct = repair_records(payloads,holes,1)
    require(all(q == (r ^ 1) for q,r in enumerate(correct)),"control repair")
    wrong = repair_records(payloads,holes,1,wrong_keys=True)
    misplaced = sum(q != (r ^ 1) for q,r in enumerate(wrong))
    require(misplaced > 0,"T(q) mutation not detected")
    controls.append(dict(name="repair_with_T_of_current_address",parameters=[2,5,4,1],
                         fixed_x=16,fixed_b=0,fiber_records=size,holes=len(holes),
                         holes_only_check_passes=True,misplaced_records=misplaced))
    try:
        repair_records(payloads,holes,1,duplicate_key=True)
    except ValueError as error:
        require(str(error) == "destination keys do not fill exactly the marked holes",
                "unexpected duplicate rejection")
    else:
        raise ValueError("duplicate repair key was accepted")
    controls.append(dict(name="duplicate_repair_key",fiber_records=size,
                         rejection="destination keys do not fill exactly the marked holes"))
    s = (1 << 17,33280,1,0,7)
    low = g.ideal(g.inverse(g.run(s,True),True))
    require(g.good(s,True) and low != g.full_ideal(s), "omitted highest bit undetected")
    controls.append(dict(name="omit_highest_selected_XOR",input=list(s),
                         wrong=list(low),expected=list(g.full_ideal(s)),
                         scope="The source's low-n contract is correct; this tests misuse as full f=n+1."))
    return controls


if __name__ == "__main__":
    main()
