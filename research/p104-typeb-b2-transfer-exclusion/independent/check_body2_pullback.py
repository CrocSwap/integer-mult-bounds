"""Independently check the fixed B2 relocation by reverse rational covectors."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
}
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
START, STOP, CAP, OFFSET, COUNT = 1855, 2338, 30, 36, 36
EARLY, LATE = (1855, 1869), (2324, 2337)
ROLES = range(OFFSET, OFFSET + COUNT)


def emit(**result):
    print(dumps(result, default=str, sort_keys=True), flush=True)


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON key"
    return result


def conjugate_walsh_eigenvalue(axes, address):
    # C=((1+i)I+(1-i)X)/2 fixes X=+1 and has eigenvalue i on X=-1.
    count = (axes & address).bit_count()
    return ((1,0),(0,1),(-1,0),(0,-1))[count % 4]


def geometry(caller):
    assert caller["ambient_rank"] == 145
    # Stages are disjoint width-one eight-axis coordinate groups starting at 9.
    axis_groups = [tuple(range(9 + 8*j, 17 + 8*j)) for j in range(17)]
    axes = axis_groups[1]
    assert axes == tuple(range(17,25))
    address = (1 << axes[0]) | (1 << axes[1])
    signs = [conjugate_walsh_eigenvalue(sum(1 << a for a in group), address) for group in axis_groups]
    assert signs[1] == (-1,0) and all(value == (1,0) for i,value in enumerate(signs) if i != 1)
    assert address & ((1 << 9) - 1) == 0  # Includes the native q-axis bit plane.
    return [value[0] for value in signs], {"width":1,"minus_X_axes":list(axes[:2]),"q_eigenvalue":1,
            "body2_axes":list(axes),"body2_eigenvalue":-1,"other_bodies_eigenvalue":1}


def edited_masks(tape):
    early = list(range(2,9))
    late = list(range(16,8,-1))
    assert [tape[i] for i in EARLY] == [["B","IDLE_ONE",36,early],["B","IDLE_ONE",38,early]]
    assert [tape[i] for i in LATE] == [["B","IDLE_ONE",36,late],["B","IDLE_ONE",37,late]]
    assert tape[1887] == ["B","IDLE_ONE",36,list(range(3,9))]
    result = {i: [*tape[i][:3], [s for s in tape[i][3] if s != 2]] for i in EARLY}
    result.update({i: [*tape[i][:3], [*tape[i][3],2]] for i in LATE})
    return result


def signed_body(mask, signs):
    assert mask and len(set(mask)) == len(mask) and all(1 <= stage <= 17 for stage in mask)
    value = 1
    for stage in mask:
        value *= signs[stage-1]
    return value


def pulled_row(block, role, signs):
    weights = [Q(r == role) for r in ROLES]
    for branch, op, dest, *args in reversed(block):
        assert branch == "B" and dest in ROLES
        i = dest - OFFSET
        if op == "ADD":
            source, q = args
            assert source in ROLES and source != dest
            weights[source - OFFSET] += Q(q) * weights[i]
        elif op == "SWAP":
            source, = args
            assert source in ROLES and source != dest
            j = source - OFFSET
            weights[j], weights[i] = weights[i], weights[j]
        elif op == "SCALE":
            coefficient = Q(args[0])
            assert coefficient
            weights[i] *= coefficient
        else:
            assert op == "IDLE_ONE" and len(args) == 1
            weights[i] *= signed_body(args[0], signs)
    return weights


def inverse_ordinary(block):
    inverse = []
    for branch, op, r, *args in reversed(block):
        if op == "IDLE_ONE":
            continue
        if op == "ADD":
            inverse.append([branch,op,r,args[0],-Q(args[1])])
        elif op == "SCALE":
            inverse.append([branch,op,r,1/Q(args[0])])
        else:
            assert op == "SWAP"
            inverse.append([branch,op,r,*args])
    return inverse


def normalized_traces(old, new, signs):
    undo = inverse_ordinary(old)
    ones = [1] * 17
    assert all(pulled_row(old + undo, role, ones) == [Q(r == role) for r in ROLES] for role in ROLES)
    result = {}
    for label, block in (("old",old),("edited",new)):
        trace = sum(pulled_row(block + undo,role,signs)[role-OFFSET] for role in ROLES)
        result[label] = trace
    return result


def first_difference(base, changed):
    for column, source in enumerate(ROLES):
        for row, destination in enumerate(ROLES):
            old, edited = base[row][column], changed[row][column]
            if old != edited:
                return {"input":source,"first_output":destination,"old_entry":old,"edited_entry":edited,
                        "old":[v[column] for v in base],"edited":[v[column] for v in changed]}
    return None


def check_global_invertible(caller):
    # At this specialization all body monomials are signs and q=1; hence every
    # surrounding Type B operation is an invertible elementary map.
    for event in caller["events"]:
        if event[0] == "A":
            continue
        if event[0] == "J":
            _, _, _, (r,s,a,b) = event
            a,b = Q(a),Q(b)
            assert r in ROLES and s in ROLES and r != s
            assert (1+a*b)-a*b == 1
        else:
            tag, op, r, *args = event
            assert tag == "B" and r in ROLES
            if op in ("ADD","SWAP"):
                assert args[0] in ROLES and args[0] != r
            elif op == "SCALE":
                assert Q(args[0])
            elif op == "LAMBDA":
                assert args[0] in (-1,1)
            else:
                assert op in ("IDLE_ONE","IDLE_ODD")
    return True


def main():
    assert __debug__ and version_info[:2] == (3,12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", nargs="?", type=Path)
    parser.add_argument("lead_sha256", nargs="?")
    args = parser.parse_args()
    started = perf_counter()
    done = []

    def capped(_signal, _frame):
        emit(status="INDEPENDENT_CAP", completed_rows=done, unvisited_rows=[r for r in ROLES if r not in done],
             cap_seconds=CAP, seconds=perf_counter()-started)
        raise SystemExit(124)

    signal(SIGALRM, capped)
    alarm(CAP)
    raw = {p:(args.root / p).read_bytes() for p in PINS}
    assert {p:sha256(data).hexdigest() for p,data in raw.items()} == PINS
    caller = loads(raw["inputs/7113-CALLER.json"], object_pairs_hook=unique)
    app = loads(raw["inputs/7481-APPLICATION.json"], object_pairs_hook=unique)
    assert app["caller_head"] == CALLER and app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    tape = caller["events"]
    assert len(tape) == 4783 and caller["stages"] == 17
    assert caller["types"]["B"]["offset"] == caller["types"]["B"]["roles"] == 36
    assert caller["types"]["B"]["ports"] == [15,17,27,34,35,42,47,55]
    changed = edited_masks(tape)
    old = tape[START:STOP]
    new = [changed.get(i,tape[i]) for i in range(START,STOP)]
    assert Counter(e[1] for e in old) == {"ADD":405,"SWAP":38,"SCALE":26,"IDLE_ONE":14}
    assert [i for i,e in enumerate(old,START) if e[1] == "IDLE_ONE" and 2 in e[3]] == list(EARLY)
    assert [i for i,e in enumerate(new,START) if e[1] == "IDLE_ONE" and 2 in e[3]] == list(LATE)
    signs, physical = geometry(caller)
    simple = [["B","ADD",36,37,"-3/2"]]
    assert pulled_row(simple,36,signs)[:2] == [Q(1),Q(-3,2)]
    assert pulled_row(simple,37,signs)[:2] == [Q(0),Q(1)]
    # Equality at unit bodies is checked on complete rows, not inferred from
    # the count of sign-trigger clocks.
    unit = [1] * 17
    omitted = list(old)
    omitted[0] = changed[START]
    old_rows, new_rows, mutant = [], [], None
    for role in ROLES:
        a,b = pulled_row(old,role,signs), pulled_row(new,role,signs)
        assert pulled_row(old,role,unit) == pulled_row(new,role,unit)
        if mutant is None:
            candidate = pulled_row(omitted,role,signs)
            if candidate != a:
                idx = next(i for i,(x,y) in enumerate(zip(a,candidate,strict=True)) if x != y)
                mutant = [role,OFFSET+idx,a[idx],candidate[idx]]
        old_rows.append(a)
        new_rows.append(b)
        done.append(role)
    assert mutant is not None
    mismatch = first_difference(old_rows,new_rows)
    traces = normalized_traces(old,new,signs)
    assert (args.lead_receipt is None) == (args.lead_sha256 is None)
    if args.lead_receipt is not None:
        lead_raw = args.lead_receipt.read_bytes()
        assert sha256(lead_raw).hexdigest() == args.lead_sha256
        start, lead = [loads(row, object_pairs_hook=unique) for row in lead_raw.splitlines()]
        assert (start["window"], start["old_clocks"],start["new_clocks"]) == ([START,STOP],list(EARLY),list(LATE))
        assert start["q"] == 1 and start["b2"] == -1 and start["tested_port"] == 15
        assert lead["tested_columns"] == list(ROLES)
        if mismatch:
            assert lead["status"] == "EXCLUDED_FIXED_B2_RELOCATION"
            compare = {k:v for k,v in mismatch.items() if k not in ("old_entry","edited_entry")}
            assert loads(dumps(compare,default=str)) == lead["excluded_witnesses"][0]
        else:
            assert lead["status"] == "B2_SIGN_SURVIVOR"
    emit(status="PASS_INDEPENDENT_B2_RELOCATION_EXCLUSION" if mismatch else "INDEPENDENT_B2_SIGN_SURVIVOR",
         completed_rows=done, specialization=physical, window=[START,STOP], first_mismatch=mismatch,
         unit_body_full_matrix_equal=True, omitted_1855_mutant_first_mismatch=mutant,
         invertible_unchanged_type_b_prefix_and_suffix=check_global_invertible(caller),
         caller_head=CALLER,input_pins=PINS,lead_sha256=args.lead_sha256,cap_seconds=CAP,
         ordinary_inverse_normalized_traces=traces,
         seconds=perf_counter()-started)
    alarm(0)


if __name__ == "__main__":
    main()
