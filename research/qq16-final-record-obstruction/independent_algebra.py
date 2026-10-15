"""Independent exact factored-map evidence for the QQ16 final-record theorem.

Five rational models exercise noncommuting selected charts. These are algebra
fixtures, not actual-cover rank evidence. No research module is imported.
Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import gzip
import json
import tarfile

ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
MEMBER = "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz"
MEMBER_SHA = "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def zero(n): return [Q(0)] * n

def add(a, b): return [x + y for x, y in zip(a, b)]

def scale(c, a): return [c * x for x in a]

def sub(a, b): return add(a, scale(-1, b))

def mv(matrix, vector): return [sum(a*b for a, b in zip(row, vector)) for row in matrix]

def mm(a, b): return [[sum(x*y for x, y in zip(row, column)) for column in zip(*b)] for row in a]


def inverse(a):
    x, y = a[0]; z, w = a[1]; determinant = x*w-y*z
    need(determinant != 0, "invertible selected chart")
    return [[w/determinant, -y/determinant], [-z/determinant, x/determinant]]


def frame(k):
    return [[Q(1+k*(k+1)), Q(k)], [Q(k+1), Q(1)]]


def schedule(root):
    data = (Path(root)/ARCHIVE).read_bytes()
    need(sha256(data).hexdigest() == ARCHIVE_SHA, "independent archive pin")
    with tarfile.open(fileobj=BytesIO(data), mode="r:gz") as archive:
        members = [item for item in archive.getmembers() if item.name == MEMBER]
        need(len(members) == 1 and members[0].isfile(), "one independent recipe member")
        raw = archive.extractfile(members[0]).read()
    need(sha256(raw).hexdigest() == MEMBER_SHA, "independent recipe pin")
    recipe = json.loads(gzip.decompress(raw))["recipe"]
    local = [event for event in recipe if event["kind"] == "local"]
    need(len(recipe) == 19 and [event["stage"] for event in local] == list(range(9)), "complete schedule")
    need([event["pair"] for event in local] == [0,0,0,1,1,2,2,3,3], "actual local pairs")
    need(all(event["reverse"] == bool(event["stage"] % 2) for event in local), "actual orientations")
    return recipe


def check_case(recipe, seed, mutation=None):
    la = [frame(seed+s+1) for s in range(9)]
    lt = [frame(seed+2*s+2) for s in range(9)]
    pa, pt = [inverse(a) for a in la], [inverse(a) for a in lt]
    need(mm(la[0], la[1]) != mm(la[1], la[0]), "noncommuting selected charts")
    unit = [[Q(1), Q(0)], [Q(0), Q(1)]]
    need(all(mm(a, b) == mm(b, a) == unit for a, b in zip(la+lt, pa+pt)), "two-sided selected units")
    z0, z1, v = [Q(1),Q(0),Q(0),Q(0)], [Q(0),Q(1),Q(0),Q(0)], [Q(1),Q(2)]
    d = scale(-1, mv(pa[1], v)); linked = mv(la[2], d)
    readers, centres = [], []
    for s in range(9):
        columns = [[Q(s+1),Q(s+2)], [Q(s+3),Q(-s-1)], [Q(1),Q(0)], [Q(0),Q(1)]]
        if s == 0: columns[0] = zero(2)
        if s == 1: columns[0] = v
        if s == 2:
            columns[0] = zero(2)
            columns[1] = scale(-1 if mutation == "wrong_link_sign" else 1, linked)
        if s in (3,4): columns[1] = zero(2)
        readers.append([list(row) for row in zip(*columns)])
        centres.append([[Q(0),Q(0)], [Q(0),Q(0)], [Q(12),Q(0)], [Q(0),Q(12)]])
    need(all(mm(b, k) == [[Q(12),Q(0)], [Q(0),Q(12)]] for b, k in zip(readers, centres)), "centre response 12I")
    need(mv(readers[1], z0) == scale(-1, mv(la[1], d)), "first selected cancellation")
    if mutation != "wrong_link_sign":
        need(mv(readers[2], z1) == mv(la[2], d), "ordered cross-bank compatibility")
    def query(s, fields):
        return add(add(mv(readers[s], fields[0]), mv(la[s], fields[1])), mv(lt[s], fields[2]))
    banks = [[[zero(4),zero(2),zero(2)] for _ in range(2)] for _ in range(4)]
    xt = scale(-1, mv(pt[0], mv(la[0], d)))
    banks[0] = [[z0,d,xt], [zero(4),scale(-1,d),scale(-1,xt)]]
    banks[1][0][0] = z1
    records = [mv(readers[s], banks[k][0][0]) for k in range(4)
               for s in ([0,2] if k == 0 else [2*k+1,2*k+2])]
    need(len(records) == 8 and not any(any(record) for record in records), "all eight initial records")
    histories = []
    events = deepcopy(recipe)
    if mutation == "wrong_bridge_sign":
        next(event for event in events if event["kind"] == "bridge")["coefficient"] *= -1
    for event in events:
        if event["kind"] == "bridge":
            i,j,c = event["src"],event["dst"],event["coefficient"]
            banks[j][0][0] = add(banks[j][0][0], scale(c, banks[i][0][0]))
            banks[i][1][0] = sub(banks[i][1][0], scale(c, banks[j][1][0]))
        elif event["kind"] == "terminal":
            for pair in banks:
                pair[0],pair[1] = pair[1], [scale(-1,field) for field in pair[0]]
        else:
            s,k = event["stage"],event["pair"]; x,y = banks[k]
            if not event["reverse"]:
                # Three source assignments, rather than the final-row formula.
                z,a,c = x[0],mv(la[s],x[1]),mv(lt[s],x[2])
                c = add(c,add(mv(readers[s],z),a)); histories.append(c)
                z = sub(z,mv(centres[s],c))
                a = sub(scale(-1,a),add(mv(readers[s],z),scale(11,c)))
                nx = [z,mv(pa[s],a),mv(pt[s],c)]
                ny = [add(y[0],z),sub(add(x[1],y[1]),nx[1]),sub(add(x[2],y[2]),nx[2])]
            else:
                # Separate E, full-query exchange, then H=I+(K_U-12P)R.
                t = s+1
                u = [y[0],add(y[1],mv(pa[t],add(mv(readers[t],y[0]),mv(lt[t],y[2])))),y[2]]
                a,b = mv(lt[s],x[2]),query(s,u)
                intermediate = [u[0],u[1],add(u[2],mv(pt[s],sub(a,b)))]
                current = query(s,intermediate)
                ny = [add(intermediate[0],mv(centres[s],current)),intermediate[1],sub(intermediate[2],mv(pt[s],scale(12,current)))]
                nx = [sub(x[0],y[0]),sub(add(x[1],y[1]),ny[1]),sub(add(x[2],y[2]),ny[2])]
            banks[k] = [nx,ny]
    need(len(histories) == 5 and not any(any(f) for f in histories), "forward histories vanish")
    need(all(not any(field) for pair in banks for field in pair[0][1:]+pair[1]), "final selected and completed-X vanish")
    need([pair[0][0] for pair in banks] == [z0,z1,zero(4),zero(4)], "former-Y residuals")
    need(any(d), "nonzero original selected A")
    return {"seed":seed, "initial_A":list(map(str,d)), "initial_records":len(records), "zero_histories":len(histories)}


def verify(root):
    recipe = schedule(root)
    cases = [check_case(recipe, seed) for seed in range(5)]
    rejected = []
    for mutation in ("wrong_link_sign", "wrong_bridge_sign"):
        try:
            check_case(recipe, 0, mutation)
        except ValueError as error:
            need(str(error) == "forward histories vanish", "independent control failed for unrelated reason")
            rejected.append(mutation)
        else:
            raise ValueError("independent mutation accepted: " + mutation)
    return {"status":"PASS_INDEPENDENT_FACTORIZED_QQ16_TRAJECTORY", "model_count":len(cases),
            "query_dimension":2, "ordinary_dimension":4, "recipe_events":len(recipe),
            "cases":cases, "rejected_controls":rejected,
            "scope":"exact noncommuting algebra fixtures; actual-cover existence is proved separately"}


if __name__ == "__main__":
    print(json.dumps(verify(Path(__file__).resolve().parents[2]), indent=2))
