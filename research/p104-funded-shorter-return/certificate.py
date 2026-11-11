# SPDX-License-Identifier: Apache-2.0
"""Independent exact scalar proof of the correction and retimed terminal basis."""
from copy import deepcopy
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def accumulate(a, b, k):
    out = a.copy()
    for i,v in b.items():
        value = out.get(i,0)+k*v
        if value:
            out[i] = value
        else:
            out.pop(i,None)
    return out


def replay(program, values):
    """Normalized chart coordinates; the native stage separately proves the maps."""
    state = values.copy()
    for e in program:
        op,r,*args = e
        if op=="MOVE":
            continue
        if op in ("INIT","CLEAR"):
            state.pop(r,None)
        elif op=="SCALE":
            state[r] = {i:Q(args[0])*v for i,v in state.get(r,{}).items() if Q(args[0])*v}
        elif op=="ADD":
            state[r] = accumulate(state.get(r,{}),state.get(args[0],{}),Q(args[1]))
        else:
            raise ValueError("Unexpected non-ADD operation in changed suffix")
    return {r:a for r,a in state.items() if a}


def check_affine(old, new):
    p,q = old["program"],new["program"]
    first, after, end = 45667,45677,76416
    shift = 3
    n = old["public"]+old["owned_fields"]
    independent = {r:{r:Q(1)} for r in range(n)}
    need(p[:first]==q[:first], "Original prefix, all earlier guards and phases preserved")
    a,b = replay(p[first:after],independent),replay(q[first:after+shift],independent)
    actual = {r:v for r in a.keys()|b.keys() if (v:=accumulate(b.get(r,{}),a.get(r,{}),-1))}
    want = {r:{1499:Q(-8)} for r in (988,991)}
    need(actual==want, "Exact early shifts after all external consumers")
    mid=p[after:end]
    need(mid==q[after+shift:end+shift], "All events of the original middle word preserved")
    result = replay(mid,actual)
    need(result=={r:{1499:Q(-8)} for r in (991,1500)}, "Second retirement preserves both equal corrections")
    tail = independent | {r:accumulate(independent[r],v,1) for r,v in result.items()}
    need(replay(p[end:],independent)==replay(q[end+shift:],tail), "Same arbitrary-input normalized terminal map")
    return {"status":"PASS_SHORTER_RETURN_AFFINE_DELTA", "compared_coefficient_domain":"all independent cut coordinates",
            "early_changed_roles":[988,991], "tail_changed_roles_before_basis":[991,1500],
            "donor_shift":"-8 times role 1499", "guard_prefix_preserved":True, "events":len(p)}


def check(old, new):
    receipt = check_affine(old,new)
    controls = {}
    program = new["program"]
    correction = program.index(["ADD",988,1499,"-8",245])
    consumer = program.index(["ADD",779,988,"-1/2",245],45667)
    rotate = program.index(["SCALE",1500,"2",245],76416)

    def reject(name, bad, reason):
        try:
            check_affine(old,new|{"program":bad})
        except ValueError as exc:
            need(str(exc)==reason, "Expected exact rejection for "+name)
            controls[name]=True
        else:
            raise ValueError("Control accepted: "+name)

    bad = deepcopy(program)
    bad[correction][-2]="0"
    reject("omitted_988_correction",bad,"Exact early shifts after all external consumers")
    bad = program.copy()
    bad[correction],bad[consumer] = bad[consumer],bad[correction]
    reject("premature_correction_changes_779",bad,"Exact early shifts after all external consumers")
    bad = deepcopy(program)
    bad[rotate][-2]="1"
    reject("wrong_terminal_basis",bad,"Same arbitrary-input normalized terminal map")
    return receipt,controls
