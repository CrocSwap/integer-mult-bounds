"""Exact displacement and optimistic volume price for one fixed caller pair."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
from itertools import product
from pathlib import Path
import gzip
import json
import runpy

PACKAGE = Path(__file__).resolve().parent
CALLER = "inputs/CALLER.json.gz"
INVOICE = "inputs/INVOICE-7277.json.gz"
PHYSICAL = "inputs/check_odd_physical_binding.py.gz"
APPLICATION = "inputs/upstream_application.py.gz"


def authenticate(raw, pin, name):
    blob = f"blob {len(raw)}\0".encode() + raw
    if sha256(raw).hexdigest() != pin["sha256"] or sha1(blob).hexdigest() != pin["git_blob"]:
        raise ValueError(f"Changed source: {name}")


def load(word_path):
    manifest = json.loads((PACKAGE / "PROVENANCE.json").read_bytes())
    pins = manifest["bundled"]
    assert set(pins) == {CALLER, INVOICE, PHYSICAL, APPLICATION}
    raw = {}
    for name, pin in pins.items():
        source = gzip.decompress((PACKAGE / name).read_bytes())
        authenticate(source, pin, name)
        raw[name] = source
    projection = manifest["port_projection"]
    assert projection["path"] == "inputs/TYPE-B-PORTS.json"
    port_bytes = (PACKAGE / projection["path"]).read_bytes()
    assert sha256(port_bytes).hexdigest() == projection["sha256"]
    ports = json.loads(port_bytes)
    if word_path is not None:
        native = word_path.read_bytes()
        authenticate(native, manifest["word_reference"], "complete #7277 word")
        original = json.loads(gzip.decompress(native))["ports"]
        assert {p: original[int(p)] for p in ports} == ports
    source_hashes = {name: pin["sha256"] for name, pin in pins.items()}
    source_hashes[projection["path"]] = projection["sha256"]
    return raw, ports, source_hashes


UPPER = Q('0.00364566992869893192829683504045604')
TRIAL = Q('0.0036475')
HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'


def counts(signs):
    c = [1, 0, 0, 0]
    for a in signs:
        assert a in (-1, 1)
        c = [c[k] + c[(k - a) % 4] for k in range(4)]
    return c


def imbalance(r):
    assert r > 0
    return Q(1, 1 << ((r + 2) // 2 if r % 2 == 0 else (r + 3) // 2))


def audit_counts(signs, got):
    r = len(signs)
    neg = signs.count(-1)
    # Independent product of Gaussian factors and roots-of-unity filter.
    re, im = 1, 0
    for j in range(r):
        a = -1 if j < neg else 1
        re, im = re-a*im, im+a*re
    assert got == [(2**r + 2*v)//4 for v in (re, im, -re, -im)]
    assert got[0]+got[2] == got[1]+got[3] == 1 << (r-1)
    assert max(abs(Q(v, 2**r) - Q(1, 4)) for v in got) == imbalance(r)
    if r % 2:
        assert all(got[j] != got[j+2] for j in (0, 1))
    else:
        assert sum(got[j] == got[j+2] for j in (0, 1)) == 1


def orthonormal(axes):
    return all((a & b).bit_count() % 2 == (i == j)
               for i, a in enumerate(axes) for j, b in enumerate(axes))


def controls():
    # Full truth tables for every plus/minus pattern up to rank 6 and a
    # spectator translation. The added spectator toggles phase by 2.
    cases = 0
    for r in range(1, 7):
        for signs in product((-1, 1), repeat=r):
            brute = Counter(sum(a*b for a,b in zip(signs,bits,strict=True)) % 4
                            for bits in product((0, 1), repeat=r))
            got = counts(signs)
            assert got == [brute[k] for k in range(4)]
            audit_counts(signs, got)
            assert [got[k]+got[(k+2)%4] for k in range(4)] == [2**(r-1)]*4
            cases += 1
    # Ranks alone do not certify signs. A positive central axis permutes
    # the two odd multiplicities for the actual rank-9 child.
    assert counts((1,)*9) != counts((-1,)+(1,)*8)
    assert not orthonormal([1, 2, 2])
    return {'exhaustive_small_signed_patterns':cases, 'wrong_sign_detected':True,
            'duplicate_axis_rejected':True, 'spectator_translation_checked':True}


def run(word_path=None):
    raw, central_ports, source_hashes = load(word_path)
    caller = json.loads(raw[CALLER])
    receipt = json.loads(raw[INVOICE])
    patch = raw[PHYSICAL].decode()
    binding = raw[APPLICATION].decode()
    assert receipt["caller_sha256"] == source_hashes[CALLER]
    assert receipt["checks"]["ODD-PHYSICAL-BINDING.json"]["source_reviewer_sha256"] == source_hashes[APPLICATION]
    assert all(s in patch for s in ("len(selected)==1 and a[1:]==[-1]", "signed=sub(pos,terms([(q,2)]))",
                                  "translation(sub(pos,signed))==q"))
    assert all(s in binding for s in ("parity(sum x_i)", "v == 2", "rank = 8*len(selected)"))
    assert caller['ambient_rank']==145 and receipt['checks']['ODD-FIXED-TAPE-COUNTS.json']['compiler_ambient_cap']==153
    assert caller['events'][1339]==['B','IDLE_ODD',68,[8],-1]
    assert caller['events'][2324]==['B','IDLE_ONE',36,[16,15,14,13,12,11,10,9]]
    contact = runpy.run_path(str(PACKAGE / 'contact.py'))
    timed = {r['clock']:r for r in contact['backward'](caller)}
    assert len(timed) == 94
    assert (timed[1339]['role'],timed[2324]['role'])==(68,36)
    assert (timed[1339]['window'],timed[2324]['window'])==([0,4783],[2324,2325])
    assert caller['types']['B']['ports']==[15,17,27,34,35,42,47,55]
    assert set(central_ports) == set(map(str,caller['types']['B']['ports']))
    axes = {stage:[1 << (9+8*(stage-1)+j) for j in range(8)] for stage in range(8,17)}
    layouts = []
    for port in caller['types']['B']['ports']:
        first = [central_ports[str(port)],*axes[8]]
        second = sum((axes[stage] for stage in range(16,8,-1)),[])
        assert (len(first),len(second))==(9,64)
        assert orthonormal(first+second) and max(first+second).bit_length()<=145
        layouts.append({'port':port,'central':first[0], 'rank':[9,64,73]})
    signs = {9:(-1,)+(1,)*8,64:(1,)*64,73:(-1,)+(1,)*72}
    residue = {r:counts(s) for r,s in signs.items()}
    for r,s in signs.items():
        for f in (1,2,3,4,8):
            audit_counts(s*f, counts(s*f))
            assert imbalance(r*f)<=imbalance(r)
    assert residue[9]==[136,120,120,136]
    assert residue[64]==[2**62+2**31,2**62,2**62-2**31,2**62]
    assert residue[73]==[2**71+2**35,2**71-2**35,2**71-2**35,2**71+2**35]
    identity_defect = sum(1-Q(residue[r][0],2**r) for r in (9,64))
    translation_defect = Q(3,2)-imbalance(9)-imbalance(64)
    parity_bypass_defect = 1-2*imbalance(9)-imbalance(64)
    child_capacity = Q(3,4)+imbalance(73)
    v_min = translation_defect/child_capacity
    v_min_parity = parity_bypass_defect/child_capacity
    assert identity_defect==translation_defect>1
    assert 1 < v_min_parity < v_min
    # Under clean reversible embeddings a twofold wider canonical
    # carrier still lacks enough -i eigenvectors for identity bypass.
    target_minus_i = Q(residue[9][3],2**9)+Q(residue[64][3],2**64)
    max_twofold_root = 2*(Q(1,4)+imbalance(73))
    assert target_minus_i > max_twofold_root
    invoice = receipt['price']['after']
    P,T = (Counter({int(r):n for r,n in invoice[k].items()}) for k in ('P','T'))
    assert sum(P.values())==110536 and sum(T.values())==22461
    assert sum(r*(T[r]-P[r]) for r in P.keys()|T.keys())==invoice['S']==1424
    assert P[9]>=8 and P[64]>=8
    assert Q(receipt['price']['price']['independent_raw_bracket'][1])==UPPER
    maths = runpy.run_path(str(PACKAGE/'pricing.py'))
    quotes = {}
    for label,k in (('old_crossing_upper',UPPER), ('trial',TRIAL), ('moonshot',maths['TARGET'])):
        cost = {r:maths['power'](r,k) for r in (9,64,73)}
        mlo,mhi = maths['moment'](P,T,k)
        optimistic = (cost[9][1]+cost[64][1]+mhi/8)/cost[73][0]
        one = (mlo+8*(cost[9][0]+cost[64][0]-cost[73][1]),
               mhi+8*(cost[9][1]+cost[64][1]-cost[73][0]))
        assert optimistic < v_min_parity
        assert mhi+8*(cost[9][1]+cost[64][1]-v_min_parity*cost[73][0]) < 0
        assert one[1] < 1
        if label=='old_crossing_upper':
            assert mhi<0<one[0] and 1<optimistic<Q(1002,1000)
        quotes[label] = {'k':str(k), 'old_margin':[str(mlo),str(mhi)],
                         'optimistic_unit_volume_margin':list(map(str,one)),
                         'affordable_volume_upper':str(optimistic),
                         'required_volume_margin_upper':str(mhi+8*(cost[9][1]+cost[64][1]-v_min_parity*cost[73][0]))}
    return {
        'status':'PASS_SCOPED_ONE_CHILD_DISPLACEMENT_AND_VOLUME_EXCLUSION',
        'source_head':HEAD,'source_pins':source_hashes,'site':[1339,2324],
        'old_roles':[68,36],'port_layouts':layouts,'fixed_pairs_checked':1,'physical_site_tests':0,
        'phase_multiplicities':residue,'even_translation_defect_lower':str(translation_defect),
        'two_parity_scalar_defect_lower':str(parity_bypass_defect),
        'maximum_rank73_displacement_fraction':str(child_capacity),
        'minimum_volume_translation':str(v_min),
        'minimum_volume_two_parity_scalars':str(v_min_parity),
        'identity_bypass_minus_i_requirement':str(target_minus_i),
        'twofold_carrier_max_one_root_capacity':str(max_twofold_root),
        'volume_price_linear':True, 'quotes':quotes, 'controls':controls(),
    }


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path,
                        help="Authenticate the eight port masks against the exact public #7277 word")
    result = json.dumps(run(parser.parse_args().word), indent=2, sort_keys=True) + "\n"
    assert result == (PACKAGE / "AUDIT.json").read_text()
    print(result, end="")
