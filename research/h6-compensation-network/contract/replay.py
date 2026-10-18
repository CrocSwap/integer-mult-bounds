"""Exact all-column test of the edge composer around an abstract K interface."""
from fractions import Fraction as F
from pathlib import Path
import json


def require(value, message):
    if not value:
        raise ValueError(message)


H, N = 3, 3
PORTS = [1, 2, 4]
A = [[F(0), F(1,16), F(-5,16)],
     [F(5,16), F(0), F(-1,16)],
     [F(-1,16), F(5,16), F(0)]]
K = [[F(t == s)-A[t][s] for s in range(N)] for t in range(N)]
EDGES = [(t,s) for t in range(N) for s in range(N) if A[t][s]]
SIZE = 2*N + len(EDGES) + 2  # Two independent K auxiliary dirt columns.
FULL = set(range(1 << H))
CAP = lambda p: {u for u in FULL if (u&p).bit_count()%2 == 0}
LINE = lambda p: {0,p}


def add(state, destination, source, coefficient):
    state[destination] = [a+coefficient*b for a,b in zip(state[destination],state[source])]


def replay(dual=False, omit=None, wrong_edge=False):
    state = [[F(i == j) for j in range(SIZE)] for i in range(SIZE)]
    frame = [LINE(p) for p in PORTS] + [{0} for _ in range(SIZE-N)]
    events = 0
    climbs = []

    def gate(destination, source, coefficient, phase):
        nonlocal events
        require(frame[destination] == frame[source], "Common frame")
        if phase != omit:
            if dual:
                add(state,source,destination,-coefficient)
            else:
                add(state,destination,source,coefficient)
            events += 1

    def climb(register, newframe):
        old = frame[register]
        require(old < newframe, "Strict nested frame climb")
        rank = (len(newframe).bit_length()-1)-(len(old).bit_length()-1)
        climbs.append(rank)
        frame[register] = newframe

    # All precompensation occurs before the first helper leaves zero.
    for e,(t,s) in enumerate(EDGES):
        gate(N+t,2*N+e,-A[t][s],"precompensation")
    for e,(t,s) in enumerate(EDGES):
        helper = 2*N+e
        climb(helper,LINE(PORTS[s]))
        gate(helper,s,F(1),"gather")

    # Abstract certified K block: the arbitrary-input endpoint map is its
    # contract, not a claim that these aggregate operations are frame gates.
    old = [row[:] for row in state]
    if dual:
        for s in range(N):
            for t in range(N):
                state[s] = [a-K[t][s]*b for a,b in zip(state[s],old[N+t])]
    else:
        for t in range(N):
            for s in range(N):
                state[N+t] = [a+K[t][s]*b for a,b in zip(state[N+t],old[s])]
    frame[:N] = [FULL for _ in PORTS]
    frame[N:2*N] = [CAP(p) for p in PORTS]

    for e,(t,s) in enumerate(EDGES):
        helper = 2*N+e
        cap = CAP(PORTS[s]) if wrong_edge and e == 0 else CAP(PORTS[t])
        climb(helper,cap)
        gate(N+t,helper,A[t][s],"scatter")
    for e,(t,s) in enumerate(EDGES):
        helper = 2*N+e
        climb(helper,FULL)
        gate(helper,s,F(-1),"cleanup")

    expected = [[F(i == j) for j in range(SIZE)] for i in range(SIZE)]
    for t in range(N):
        if dual:
            expected[t][N+t] = -1
        else:
            expected[N+t][t] = 1
    require(state == expected, "Exact transparent shear on every input column")
    require(climbs.count(1) == 3*len(EDGES), "H3 fixture path [1,1,1] on every helper")
    return dict(input_columns=SIZE, edge_helpers=len(EDGES), scalar_additions=events,
                helper_climb_rank_mass=sum(climbs), frame_dimension=H,
                k_internal_stream="abstract certified arbitrary-input interface")


checks = {"forward": replay(), "same_order_inverse_transpose": replay(dual=True)}
controls = []
for dual in (False,True):
    for omit in ("precompensation","gather","scatter","cleanup"):
        try:
            replay(dual=dual,omit=omit)
        except ValueError as error:
            controls.append(dict(orientation="dual" if dual else "forward",mutation=omit,rejected=str(error)))
        else:
            raise ValueError("Omission control did not fail")
try:
    replay(wrong_edge=True)
except ValueError as error:
    controls.append(dict(mutation="nonorthogonal_helper_incidence",rejected=str(error)))
else:
    raise ValueError("Nonorthogonal incidence control did not fail")

R, R3 = 480337920, 3363840
result = dict(status="PASS_EDGE_HELPER_COMPOSITION_FIXTURE",checks=checks,negative_controls=controls,
              h6_conditional_extension=dict(edge_helpers=R,path=[1,15,1],
                  scalar_additions=4*R,helper_local_climb_rank_mass=17*R,
                  inherited_scalar_primitive_bound=24*R+6*R3),
              scope="Exact small all-column composition around an abstract certified K block, with frame checks on the extension. Does not replay K internals, full H6 geometry, full-size edge word, pure bank compiler, precision/tape or outer inequalities.")
destination = Path(__file__).with_name("REPLAY.json")
destination.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(result["status"])
print(json.dumps(result["h6_conditional_extension"],sort_keys=True))
