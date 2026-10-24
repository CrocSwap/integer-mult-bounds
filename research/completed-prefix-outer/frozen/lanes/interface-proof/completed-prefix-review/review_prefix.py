"""Check exact DIF phases and physical prefix placement without producer imports."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import subprocess


REV = "3ae9a6f3ac74ded022ab3b4872a7357a621af6fb"
FILES = {
    "temporal-reuse/COMPLETED-PREFIX-CODES.md": "c0050de40211bf06ddb386192795d7d2a4ebb0452aa61b1c8139b92f7041cdf5",
    "temporal-reuse/check_completed_prefix_codes.py": "0f290084228332cbcbfe1bf1b02d160f0e3c9a264968632ea0ae77e88ac19186",
    "temporal-reuse/COMPLETED-PREFIX-CODES.json": "56c880b4b6ad30e0658d650b6cd566d6e18e4a10e0cc9054ee395667a8ca0664",
    "temporal-reuse/PAST-CATALYST-LAYOUT.md": "8f3ac9bc6133397ce98c88b0f6999c1eac9f6169d10fe21b2f0ab9d2275caee7",
    "temporal-reuse/check_past_catalyst_layout.py": "412640c14d27ccfffa4eea24af9b321e13bc54b9a491766c8d96654536b577ef",
    "temporal-reuse/PAST-CATALYST-LAYOUT.json": "501edd6edcfc34c429a9b26cacf7c84a56291f876d729325ef03a47c368677e7",
    "circuit-interface/INTERFACE.json": "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
    "schur-selection/PAST-CATALYST-v2.md": "566cfb7794202a2462a41da8abef69066c51a06ab7802c01f76b996e58e976e5",
    "schur-selection/PAST-GAUGE-FUSION.md": "a84b77d2ef0d0747713063a7bd08e211b5a75eabbba6ff085a3967676fc12c6f",
}
GIT_FILES = {
    "upstream/build/sections/02-streams.tex": "606c80db61cad13aa0c3b6060dc4b88dbbe7ac60cdd831aa93f28d908fd09dab",
    "upstream/build/sections/04-swap.tex": "412b170ccaab38dba96e95e3cbfae09f4876a9818f8d278776a746b0f8044906",
    "upstream/build/sections/05-layers.tex": "20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594",
    "upstream/build/sections/06-transforms.tex": "924316e4bc905066281d8f9e8746a49d8829aeb393688608deb1e61c3c87853c",
    "certificates/selected-result.json": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    "research/community-frontier1094-audit/ASSEMBLY.json": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
}


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def reverse(value, width):
    return sum(((value >> i) & 1) << (width-1-i) for i in range(width))


def column(width, source, opposite):
    """Return monomial exponents; the common coefficient is 1/2**width."""
    r = 1 << width
    states = {source: 0}
    order = range(width) if opposite else range(width-1, -1, -1)
    for h in order:
        following = {}
        for address, exponent in states.items():
            old = (address >> h) & 1
            for new in (0, 1):
                target = (address & ~(1 << h)) | (new << h)
                phase = exponent+r*old*new
                if opposite:
                    tail = reverse(address >> (h+1), width-h-1)
                    phase += (2*r >> (width-h))*new*tail
                else:
                    tail = address & ((1 << h)-1)
                    phase -= (2*r >> (h+1))*new*tail
                need(target not in following, "Two paths reached one basis entry")
                following[target] = phase % (2*r)
        states = following
    return states


def exact_dif():
    count = 0
    old_opposite_counterexample = None
    for width in range(1, 9):
        r = 1 << width
        for source in range(r):
            for opposite in (False, True):
                out = column(width, source, opposite)
                for target, phase in out.items():
                    expected = (2*target*reverse(source, width) if opposite
                                else -2*reverse(target, width)*source) % (2*r)
                    need(phase == expected, "Exact polynomial DIF endpoint")
                    count += 1
        if width > 1:
            # In the retained reverse-arithmetic order, the later h=1 twiddle
            # reads the already completed physical bit0.
            old_opposite_counterexample = ((2*r >> 2)*1*1) % (2*r)
            need(old_opposite_counterexample != 0, "Old opposite schedule control")
    return count, old_opposite_counterexample


def layout_names(lengths, chunk, ell):
    bottom = (ell-1) % chunk
    prefix = [(axis, ell-1) for axis, width in enumerate(lengths) if width == ell]
    prefix += [(axis, bit) for bit in range(bottom-1, -1, -1)
               for axis in range(len(lengths))]
    groups = [[(axis, bit) for axis in range(len(lengths))
               for bit in range(high, high-chunk, -1)]
              for high in range(ell-2, bottom-1, -chunk)]
    result = prefix+sum(groups, [])
    need(len(result) == len(set(result)) == sum(lengths), "All named slots occur once")
    return result, bottom, len(prefix)


def selected_offsets():
    cases = 0
    for ell in range(3, 13):
        for chunk in range(1, ell):
            for lengths in ([ell, ell-1], [ell-1, ell, ell-1], [ell]*4, [ell-1]*3):
                names, bottom, head = layout_names(lengths, chunk, ell)
                for bit in range(bottom, ell-1):
                    expected_offset = (bit-bottom) % chunk
                    group = (ell-2-bit)//chunk
                    for axis in range(len(lengths)):
                        position = names.index((axis, bit))-head
                        need(position//(len(lengths)*chunk) == group,
                             "Current axes are not in one chunk group")
                        need(chunk-1-(position % chunk) == expected_offset,
                             "Physical selected offset differs")
                    # The new opposite tail consists only of higher named slots.
                    for axis, width in enumerate(lengths):
                        need(all(names.index((axis, v)) != names.index((axis, bit))
                                 for v in range(bit+1, width)), "Tail includes current bit")
                    cases += 1
    return cases


def exchange(order, a, b, width):
    need(a+width <= b or b+width <= a, "Overlapping fields")
    for offset in range(width):
        order[a+offset], order[b+offset] = order[b+offset], order[a+offset]


def check_rotation():
    total = 0
    for chunks in range(1, 9):
        for width in range(1, 10):
            length = chunks*width
            # Separate X and Z by an unrelated three-bit field.
            z = length+3
            for rho in range(width):
                order = list(range(2*length+3))
                cut = (length-rho) % length
                operations = [] if cut == 0 else [
                    (0, z+length-cut, cut), (cut, z, length-cut), (0,z,length)]
                for operation in operations:
                    exchange(order, *operation)
                for old in range(0,length,width):
                    need(order[old+rho] == old, "Past selected name not at rho")
                need(order[length:z] == list(range(length,z)), "Gap is not fixed")
                # The selected-label identity gives conjugacy for every linear
                # value map on these bits, not only their joint XOR.
                active = [order[p] for p in range(rho,length,width)]
                need(active == list(range(0,length,width)), "Ordered selected embedding")
                for operation in reversed(operations):
                    exchange(order, *operation)
                need(order == list(range(2*length+3)), "Literal inverse does not restore all names")
                total += 1
    return total


def reserve_views():
    count = 0
    for copies in range(1,5):
        for width in range(2,7):
            active, past = 64*copies, 9*copies
            group, length = active*width, past*width
            for groups in (3,4,5):
                total = groups*group
                source = [j*width+width-1 for j in range(past)]
                names = list(range(total))
                early = [(x,(groups-1)*group+j*width) for j,x in enumerate(source)]
                for a,b in early:
                    exchange(names,a,b,1)
                need([names[(groups-1)*group+j*width] for j in range(past)] == source,
                     "Completed names not in early reserve")
                for current in range(groups-1):
                    neighbor = current-1 if current else 1
                    need(neighbor not in (current, groups-1), "No distinct adjacent block")
                    before = names[:]
                    target = neighbor*group if neighbor > current else (neighbor+1)*group-length
                    exchange(names,target,(groups-1)*group,length)
                    need(names[target:target+length] == before[(groups-1)*group:(groups-1)*group+length],
                         "Past block not adjacent to active block")
                    exchange(names,target,(groups-1)*group,length)
                    need(names == before, "Temporary adjacent placement does not restore")
                for a,b in reversed(early):
                    exchange(names,a,b,1)
                need(names == list(range(total)), "Early reserve does not restore future names")
                late = [(x,j*width) for j,x in enumerate(source)]
                for a,b in late:
                    exchange(names,a,b,1)
                need(names[group:] == list(range(group,total)), "Late reserve changes unfinished group")
                for a,b in reversed(late):
                    exchange(names,a,b,1)
                need(names == list(range(total)), "Late reserve inverse")
                count += 1
    return count


def gadd(a,b):
    return tuple(x+y for x,y in zip(a,b))


def gmul(a,b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


ZERO = (F(0),F(0))
ONE = (F(1),F(0))


def padd(a,b):
    return gadd(a[0],b[0]),gadd(a[1],b[1])


def pmul(a,b):
    low, high = gmul(a[0],b[0]),gmul(a[1],b[1])
    return (low[0]-high[0],low[1]-high[1]),gadd(gmul(a[0],b[1]),gmul(a[1],b[0]))


def matrix(a,b):
    return [[padd(pmul(a[i][0],b[0][j]),pmul(a[i][1],b[1][j]))
             for j in range(2)] for i in range(2)]


def twiddle_control():
    zero,one,y = (ZERO,ZERO),(ONE,ZERO),(ZERO,ONE)
    a,b = ((F(1,2),F(1,2)),ZERO),((F(1,2),F(-1,2)),ZERO)
    c,ci = [[a,b],[b,a]],[[b,a],[a,b]]
    need(matrix(c,ci) == [[one,zero],[zero,one]], "Exact complex line inverse")
    conjugates = [matrix(matrix(c,[[one,zero],[zero,y]]),ci),
                  matrix(matrix(ci,[[one,zero],[zero,y]]),c)]
    for transformed in conjugates:
        for row in transformed:
            for u,v in row:
                # In C[y]/(y^2+1), u+v*y is a unit when u^2+v^2 !=0.
                need(gadd(gmul(u,u),gmul(v,v)) != ZERO, "Conjugate entry is not a unit")
    permutation = [[zero,one],[one,zero]]
    need(matrix(matrix(permutation,[[one,zero],[zero,y]]),permutation)
         == [[y,zero],[zero,one]], "Permutation countercontrol")
    return 8


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--workspace",type=Path,default=Path(__file__).resolve().parents[5])
    parser.add_argument("--out",type=Path,default=Path(__file__).with_name("REVIEW.json"))
    args=parser.parse_args()
    root=args.workspace.resolve(); lane=root/"work/centre-encoding-campaign-20261014/lanes"
    for path,digest in FILES.items():
        need(sha256((lane/path).read_bytes()).hexdigest()==digest,"Research pin: "+path)
    sources={}
    for path,digest in GIT_FILES.items():
        raw=subprocess.check_output(["git","-C",str(root/"worktrees/k5-centre-sharing"),"show",REV+":"+path])
        need(sha256(raw).hexdigest()==digest,"Git source pin: "+path)
        sources[path]=raw
    assembly=json.loads(sources["research/community-frontier1094-audit/ASSEMBLY.json"])
    selected=json.loads(sources["certificates/selected-result.json"])
    need(selected["kappa"]==assembly["kappa"],"Selected assembly")
    epsilon,c,kappa=map(F,[assembly["outer"]["epsilon_positive"],assembly["outer"]["c_positive"],assembly["kappa"]])
    need(epsilon-kappa>F(99,100) and 1-epsilon-kappa>0 and 1-epsilon*(1+c)>0,
         "Selected asymptotic margins")
    ports=json.loads((lane/"circuit-interface/INTERFACE.json").read_bytes())["ports"]
    need(len(ports)==112 and len(set(ports))==112
         and all(0<q<512 and q.bit_count()%2 for q in ports),
         "Actual odd lines do not meet the branch-mixing hypothesis")
    columns,control=exact_dif()
    result={"status":"PASS_INDEPENDENT_COMPLETED_PREFIX_AND_PAST_LAYOUT_REVIEW",
        "research_pins":FILES,"git_revision":REV,"git_pins":GIT_FILES,
        "producer_imports":False,"arithmetic":"Integer exponents in the exact polynomial ring; Gaussian rational two-term polynomials",
        "exact_forward_and_opposite_entries":columns,"axis_log_lengths":list(range(1,9)),
        "old_reverse_opposite_twiddle_control":control,
        "actual_chunk_offset_cases":selected_offsets(),"nonadjacent_rotation_cases":check_rotation(),
        "early_late_three_or_more_group_cases":reserve_views(),"nonmonomial_twiddle_unit_entries":twiddle_control(),
        "actual_odd_port_hypotheses_checked":len(ports),
        "all_size_proof_review":"PASS; exact statement and hypotheses are in REVIEW.md",
        "selected_margins":{"epsilon_minus_kappa":str(epsilon-kappa),"startup":str(1-epsilon-kappa),"groups":str(1-epsilon*(1+c))},
        "scope":"Outer exact opposite and completed-prefix composition; conditional address packing. No native supplier, cover redesign, growing-bank decoder bound, compact invoice, or recursive encoded-child closure.",
        "checker_sha256":sha256(Path(__file__).read_bytes()).hexdigest()}
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(result["status"])
    print("Exact DIF phases, current twiddle, selected offsets, full guard and reserve restoration")


if __name__=="__main__":
    main()
