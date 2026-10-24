#!/usr/bin/env python3
"""Check affine Haar tree volume in noncoordinate binary bases."""

import hashlib
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
HERE = Path.cwd()
LANES = PACKAGE / 'evidence/lanes'
PHYS = LANES / 'residual-syndrome/physical-algebra'
SOURCE = PHYS / "affine-sector-cover"


def require(value,label):
    if not value:
        raise ValueError(label)


def binary_rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length()-1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def phase(address,n,width):
    rows = [(address >> (i*width)) & ((1 << width)-1) for i in range(n)]
    phases = set()
    for q in range(1,1 << n):
        if q.bit_count()%2:
            value = 0
            for i,row in enumerate(rows):
                if (q >> i)&1:
                    value ^= row
            phases.add(value.bit_count()%4)
    return next(iter(phases)) if len(phases)==1 else None


def masks_for(m,seed):
    rows = [1 << j for j in range(m)]
    state = seed
    for _ in range(5*m):
        state = (1103515245*state+12345) & ((1 << 31)-1)
        a = state%m
        state = (1103515245*state+12345) & ((1 << 31)-1)
        b = state%m
        if a!=b:
            rows[a] ^= rows[b]
    require(binary_rank(rows)==m,"invertible noncoordinate basis")
    return rows


def build(addresses,masks,labels,accepted,depth=0):
    values = {labels[x] in accepted for x in addresses}
    origin = addresses[0]
    require(len(addresses)==1 << (len(masks)-depth),"node cardinality")
    require(binary_rank([x^origin for x in addresses])==len(masks)-depth,
            "node affine dimension")
    if len(values)==1:
        return {"size":len(addresses),"depth":depth,"accept":values.pop()}
    mask = masks[depth]
    parts = [[],[]]
    # The affine offset varies by branch; it changes no codimension.
    offset = (origin.bit_count()+depth)%2
    for x in addresses:
        parts[((x & mask).bit_count()+offset)%2].append(x)
    require(len(parts[0])==len(parts[1]),"nonconstant affine split")
    return {"size":len(addresses),"depth":depth,
            "children":[build(part,masks,labels,accepted,depth+1) for part in parts]}


def measure(node):
    if "children" not in node:
        return 0,[(node["size"],node["depth"],node["accept"])],0
    work,leaves,blocks = node["size"],[],0
    for child in node["children"]:
        child_work,child_leaves,child_blocks = measure(child)
        work += child_work
        leaves += child_leaves
        blocks += child_blocks
    require(work==sum(size*(depth-node["depth"]) for size,depth,_ in leaves),
            "unequal-codimension block identity")
    return work,leaves,blocks+1


def check_case(n,width,seed):
    m = n*width
    labels = [phase(x,n,width) for x in range(1 << m)]
    masks = masks_for(m,seed)
    entries = []
    for desired in (None,0,1,2,3):
        accepted = {0,1,2,3} if desired is None else {desired}
        tree = build(list(range(1 << m)),masks,labels,accepted)
        work,leaves,blocks = measure(tree)
        total_depth = sum(size*depth for size,depth,_ in leaves)
        require(work==total_depth,"total forward volume identity")
        count = sum(size for size,_,take in leaves if take)
        require(count==sum(x in accepted for x in labels),"all accepted labels")
        if desired is None:
            k = n*((width+1)//2)-width%2
        else:
            f = width//2
            preferred = {f%4} if width%2==0 else {f%4,(f+1)%4}
            dimension = f-int(desired not in preferred)
            k = n*(width-dimension)
        require(all(depth>=k for _,depth,take in leaves if take),"affine leaf bound")
        require(work>=k*count,"accepted-volume lower bound")
        entries.append({"residue":desired,"accepted_rank":count,
                        "forward_records":work,"lower_bound_records":k*count,
                        "all_leaves":len(leaves),"block_identities":blocks})
    return {"n":n,"tensor_width":width,"basis_seed":seed,
            "noncoordinate_masks":masks,"trees":entries}


def main():
    cases = [check_case(n,width,seed) for n,width,seed in
             ((2,2,17),(3,2,31),(3,3,7),(3,4,13))]
    sources = {
        "rigidity":PHYS/"review-gauss/maximal-affine-sectors/RIGIDITY.md",
        "density_review":PHYS/"correlated-sector-review/REVIEW.json",
        "stream_review":PHYS/"review-gauss/affine-projector-stream/REVIEW.json",
        "proof":SOURCE/"SPLIT-LIMIT.md"}
    result = {"status":"PASS_AFFINE_HAAR_TREE_VOLUME",
              "pins":{name:hashlib.sha256(path.read_bytes()).hexdigest()
                      for name,path in sources.items()},"cases":cases,
              "scope":"Exact affine-tree volume and leaf-depth checks, including grouped unequal-codimension blocks. No general circuit lower bound."}
    (HERE/"SPLIT-LIMIT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"])


if __name__=="__main__":
    main()
