#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independently reconstruct the owner-411 tree and its physical paired input."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from heapq import heapify, heappop, heappush
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from finite import PACKAGE_PINS, PAIRED, candidate_receipt, load, need, pinned

SOURCE_WORD = "c38f1881fa87f9b9e4a27e6ba8f4ce1a608a6d6ab014648bbe758d3c48a353d9"
SOURCE_LITERAL = "ec04317b7d098facdf02eda6aa14c6d26fce82672843269b06b92bbdf8bc123e"
TREE_WORD = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
TREE_GZIP = "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9"
FINITE_SHA = "0cebc543d64ca53ac6c7141dfab40c658bf451fe89bb7744befb76c116ea45e6"
PHYSICAL_SHA = "fc59fbff30fc2ca1fb28a90b2cc8f9eb5f6c03b6ca4bcf677cb757d8e2aec612"
JOURNAL_SHA = "7fa07209cee23b15d9bbd178bab4bed7bb01b7ce2da743744e6ddbd9d3f5920c"
WITHDRAWALS_SHA = "82d0ad19182d248f075022860b5ef441c24cd85b71bd514b01c36b64ba3a3f02"


def labels(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length()-1
        mask ^= low


def packet_word(word):
    n = word["public"]
    state = [1<<j for j in range(n)] + [0]*word["owned_fields"]
    routes, transfer, clocks = {}, {}, {}
    for ii,(opcode,owner,*tail) in enumerate(word["program"]):
        if opcode == "MOVE":
            packet = n+len(routes)
            routes[packet], transfer[packet], clocks[packet] = tuple(tail),state[owner],ii
            state[owner] = 1<<packet
        elif opcode == "SWAP":
            peer, = tail
            state[owner],state[peer] = state[peer],state[owner]
        elif opcode == "ADD":
            state[owner] ^= state[tail[0]]
        else:
            need(opcode in ("INIT","CLEAR"),"literal packet extraction opcode")
            state[owner] = 0
    transfer.update({~j: state[j] for j in range(n)})
    return routes,transfer,clocks


def dual(n, routes, transfer):
    dual_rows = dict.fromkeys(transfer,0)
    for row, form in transfer.items():
        output = row if row>=0 else ~row
        for j in labels(form):
            dual_rows[~j if j<n else j] ^= 1<<output
    return {k:(b,a) for k,(a,b) in routes.items()},dual_rows


def evaluate(start, final, routes, rows, adjoint):
    arrivals = dict(enumerate(start)) | {k:b for k,(a,b) in routes.items()}
    waits, next_packets = {},defaultdict(list)
    for k,row in rows.items():
        want = routes[k][0] if k>=0 else final[~k]
        parents = list(labels(row))
        need(all(arrivals[p]==want for p in parents),"all chronological packet XOR charts")
        if k>=0:
            pending = [p for p in parents if p in routes]
            waits[k] = len(pending)
            for p in pending:
                next_packets[p].append(k)
    ready = [k for k in waits if not waits[k]]
    heapify(ready)
    order,values = [],{j:1<<j for j in range(len(start))}

    def receive(row):
        result = 0
        for j in labels(row):
            result ^= values[j]
        return result

    while ready:
        head = heappop(ready)
        order.append(head)
        values[head] = receive(rows[head])
        for k in next_packets[head]:
            waits[k] -= 1
            if not waits[k]:
                heappush(ready,k)
    need(len(order)==len(routes),"acyclic restored packet word")
    for j in range(len(start)):
        desired = 1<<j
        if adjoint and j<111:
            desired ^= 1<<(j+111)
        if not adjoint and 111<=j<222:
            desired ^= 1<<(j-111)
        need(receive(rows[~j])==desired,"every exact protected public packet return")
    return order,values


def restore_tree(before, after):
    n = before["public"]
    start, final = before["start"],before["final"]
    need((n,start,final,before["frames"]) == (680,after["start"],after["final"],after["frames"])
         and after["public"]==n,"680 independent owner endpoints and frames unchanged")
    old,rows,clocks = packet_word(before)
    old,rows = dual(n,old,rows)
    _,values = evaluate(final,start,old,rows,True)
    owner,donor,alias,vanish = 411,2329,3298,2946
    need(values[vanish] == values[alias]^values[donor] == 1<<owner, "exact owner-411 alias and isolated pulse")
    need((old[alias],old[vanish],old[donor]) == ((0,509),(1,517),(390,509)),
         "literal retired packet and donor charts")
    live = {k:v for k,v in old.items() if k not in (vanish,alias)}
    killed = (1<<owner)|(1<<alias)|(1<<vanish)
    revised = {k:(r&~killed)^((1<<donor) if r>>alias&1 else 0)
               for k,r in rows.items() if k not in (vanish,alias,~owner)}
    bridge = max(old)+1
    live[bridge] = final[owner],start[owner]
    revised[bridge] = 1<<owner
    revised[~owner] = 1<<bridge
    feeder = rows[alias] & ~((1<<owner)|(1<<vanish))
    need(not set(labels(feeder)).intersection({donor,2590,2944}) and feeder,
         "independent exterior source breaks cycle")
    live.update({donor:(0,509),2590:(509,390),2944:(390,517)})
    revised.update({donor:feeder,2590:1<<donor,2944:1<<2590})
    _,new_values = evaluate(final,start,live,revised,True)
    need(all(new_values[r] == values[r]&~(1<<owner) for r in live if r!=bridge)
         and new_values[bridge]==1<<owner,"every retained old adjoint payload and fresh owned bridge")
    forward,frows = dual(n,live,revised)
    order,_ = evaluate(start,final,forward,frows,False)
    literal_routes,literal_rows,_ = packet_word(after)
    relabel = {r:r for r in range(n)} | {r:n+i for i,r in enumerate(order)}
    need(all(literal_routes[relabel[r]]==forward[r] for r in order)
         and len(literal_routes)==len(forward),"every reconstructed forward paid packet agrees with literal word")
    need(all(literal_rows[relabel.get(r,r)]==sum(1<<relabel[k] for k in labels(form))
             for r,form in frows.items()),"every reconstructed literal forward sender and protected return row")
    return dict(owner=owner,old_alias=alias,old_pure=vanish,old_packet_clocks=[clocks[alias],clocks[vanish]],
                tree=[[donor,0,509],[2590,509,390],[2944,390,517]],
                bridge=[bridge,*live[bridge]],external_root_operands=list(labels(feeder)),
                retained_packet_values=len(live)-1,all_reconstructed_packet_and_terminal_rows=len(frows))


def identity(n):
    return tuple(tuple(Q(i==j) for j in range(n)) for i in range(n))


def product(a,b):
    return tuple(tuple(sum(x*y for x,y in zip(row,col,strict=True) if x and y)
                       for col in zip(*b,strict=True)) for row in a)


def inverse(a):
    n = len(a)
    work = [list(r+s) for r,s in zip(a,identity(n),strict=True)]
    for j in range(n):
        i = next(i for i in range(j,n) if work[i][j])
        work[j],work[i] = work[i],work[j]
        pivot = work[j][j]
        work[j] = [x/pivot for x in work[j]]
        for i,r in enumerate(work):
            if i!=j and r[j]:
                a = r[j]
                work[i] = [x-a*y for x,y in zip(r,work[j],strict=True)]
    return tuple(tuple(r[n:]) for r in work)


def subtract(a,b):
    return tuple(tuple(x-y for x,y in zip(r,s,strict=True)) for r,s in zip(a,b,strict=True))


def projector_geometry(word, routes, caller):
    projectors,bases,ranks = {},{},{}
    prime, I = {2}, identity(8)
    for label,info in word["frames"].items():
        r = int(label)
        b,a = (tuple(tuple(map(Q,line)) for line in info[k]) for k in ("B","A"))
        dim = info["dim"]
        need(len(b)==dim and len(a)==8-dim and all(len(x)==8 for x in b+a),"complete eight-axis frame")
        G = tuple(zip(*(b+a),strict=True))
        W = inverse(G)
        active = tuple(tuple(x if j<dim else Q(0) for j,x in enumerate(row)) for row in G)
        P = product(active,W)
        need(product(G,W)==I and P==tuple(zip(*P,strict=True)) and product(P,P)==P and
             sum(P[i][i] for i in range(8))==dim,"rational orthogonal projector on the stated frame")
        prime.update(x.denominator for m in (G,W,P) for row in m for x in row)
        projectors[r],bases[r],ranks[r] = P,b+a,dim
    protected = {(a,b) for a,b in zip(word["start"][222:],word["final"][222:],strict=True)}
    paid = set(routes.values())
    projected, digest = {},sha256()
    for a,b in sorted(paid|protected):
        lo,hi = sorted((a,b),key=ranks.__getitem__)
        U,V = projectors[lo],projectors[hi]
        D = subtract(V,U)
        need(product(U,V)==U and product(V,U)==U and product(D,D)==D
             and sum(D[i][i] for i in range(8))==ranks[hi]-ranks[lo]>0,
             "complete translated MOVE and helper quotient on nested chart axes")
        prime.update(x.denominator for row in D for x in row)
        projected[a,b] = ranks[hi]-ranks[lo]
        for row in D:
            digest.update((" ".join(map(str,row))+"\n").encode())
    ports = caller["ports"]
    stages = tuple(tuple(range(8+7*s,15+7*s)) for s in range(caller["stages"]))
    need(ports==111 and len(stages)==18 and all(len(set(s))==7 for s in stages) and
         len(set().union(*map(set,stages)))==126 and stages[-1][-1]==133,"134-axis complete head/body space")
    for j in range(ports):
        x,y = j,j+ports
        start_x,start_y = word["start"][x],word["start"][y]
        end_x,end_y = word["final"][x],word["final"][y]
        H,B = projectors[start_x],projectors[end_y]
        head_body = tuple(zip(*(bases[start_x][:1]+bases[end_y][:7]),strict=True))
        inv = inverse(head_body)
        need(ranks[start_x]==1 and ranks[end_y]==7 and ranks[start_y]==0 and ranks[end_x]==8
             and subtract(I,H)==B and product(head_body,inv)==I,
             "physical main quartet and rational inverse stage basis")
        prime.update(x.denominator for m in (head_body,inv) for row in m for x in row)
    calls = [r for r in caller["events"] if r[0]=="LOCAL"]
    for stage in range(1,19):
        pairs = [r[2:] for r in calls if r[1]==stage]
        need(len(pairs)==2 and len(set().union(*map(set,pairs)))==4,
             "two genuinely disjoint actual native calls per stage")
    return dict(rational_frames=len(projectors),distinct_paid_pairs=len(paid),distinct_helper_pairs=len(protected),
                quotient_digest=digest.hexdigest(),main_port_quartets=ports,physical_main_contacts=len(calls)*ports,
                native_calls=len(calls),working_ambient=134,head_grade=1,stage_body_grade=7,
                new_block_axes=[list(g) for g in stages], raw_fixed_prime_denominators=sorted(prime))


def check_physical(cache, before_path, literal_script):
    literal = load(literal_script,"literal")
    before_content = gzip.decompress(before_path.read_bytes())
    need(sha256(before_content).hexdigest()==SOURCE_LITERAL,"decompressed enrolled literal bytes")
    before = json.loads(before_content)
    tree_path = HERE/"WORD.json.gz"
    tree = json.loads(gzip.decompress(pinned(tree_path,TREE_GZIP)))
    need((literal.canonical(before),literal.canonical(tree))==(SOURCE_WORD,TREE_WORD),"both literal word pins")
    caller = literal.pinned(cache/"source"/PAIRED/"EFREE-CALLER.json.gz", literal.CALLER_SHA)
    finite = json.loads(pinned(HERE/"FINITE.json",FINITE_SHA))
    journal = restore_tree(before,tree)
    b_native = candidate_receipt(literal,before_path,SOURCE_WORD,before,caller)
    native = candidate_receipt(literal,tree_path,TREE_WORD,before,caller)
    for k in ("targets","paid"):
        need(native[k]==literal.histogram(finite[k]),"complete paired finite rank inventory")
    need(native["ordinary"]==finite["ordinary"],"whole raw ordinary and ownership funding")
    signed_delta = native["paid"].copy()
    signed_delta.subtract(b_native["paid"])
    need({k:v for k,v in signed_delta.items() if v}=={1:-36,3:-36,4:36}
         and native["targets"]==b_native["targets"],"correct whole tariff for the restored tree")
    geometry = projector_geometry(tree,packet_word(tree)[0],caller)
    receipt = dict(status="PASS_INDEPENDENT_OWNER_411_RESTORED_TREE_AND_PAIRED_PHYSICAL_INPUT",
                   source_word_sha256=SOURCE_WORD,word_sha256=TREE_WORD, ordinary_admitted=finite["ordinary_admitted"],
                   caller_sha256=literal.CALLER_SHA,tree=journal,geometry=geometry,
                   signed_paid_delta={k:v for k,v in signed_delta.items() if v},
                   native=native,
                   positive_caller_operand_rule="Apply T(P) to both complete chunks as the partial swap on Im(P). Rational body-stage conjugation swaps seven body basis vectors with fresh axes, fixing the head and every other spectator. Complete native scalar endpoint is D_s(x,y+Qx).",
                   caller_query_paid_jobs=4*111, caller_idle_paid_jobs=32*111,
                   root_binary_product="F2[q,D_1,...,D_18]/(q^2-1)")
    return receipt


def rebuild_before(cache, scratch, literal_script):
    journal, withdrawals = HERE/"BIRTHS.json", HERE/"WITHDRAWALS.json"
    pinned(journal,JOURNAL_SHA)
    pinned(withdrawals,WITHDRAWALS_SHA)
    contact = scratch/"contact"
    enrolled = scratch/"enrolled.json.gz"
    source = cache/"source"

    def run(script, *arguments):
        subprocess.run([sys.executable,"-I","-B",str(HERE/script),*map(str,arguments)],check=True)

    run("replay.py","--source-root",source,"--parent-word",cache/"parent/binary/WORD.json.gz",
        "--journal",journal,"--out",contact)
    run("replay_quotients.py","--contact",contact/"WORD.json.gz","--withdrawals",withdrawals,
        "--edge",source/"research/p104-dual-supplier-lift/bit_native.py",
        "--literal",literal_script,"--out",enrolled)
    return enrolled


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache",type=Path,required=True,help="Prepared source cache")
    parser.add_argument("--before",type=Path,help="Optional already reconstructed enrolled c38f word")
    parser.add_argument("--out",type=Path,required=True)
    args = parser.parse_args()
    need(__debug__,"run physical replay with assertions")
    literal = args.cache/"parent/binary/independent/literal.py"
    pinned(literal,PACKAGE_PINS["binary/independent/literal.py"])
    with TemporaryDirectory(prefix="p104-physical-") as work:
        before = args.before or rebuild_before(args.cache,Path(work),literal)
        receipt = check_physical(args.cache,before,literal)
    encoded = (json.dumps(receipt,indent=2,sort_keys=True)+"\n").encode()
    need(encoded==pinned(HERE/"PHYSICAL.json",PHYSICAL_SHA),"frozen physical caller receipt")
    args.out.write_bytes(encoded)
    print(receipt["status"], receipt["word_sha256"], receipt["ordinary_admitted"])


if __name__ == "__main__":
    main()
