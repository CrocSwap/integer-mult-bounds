# SPDX-License-Identifier: Apache-2.0
"""Evaluate the paid rank-one quotient by direct Gaussian integer matrices."""

from hashlib import sha256
import json
import runpy

import numpy as np

from word import require

N = 512
ADDR = np.arange(N)
COL = ADDR[None, :]
ROW = ADDR[:, None]
COMPILER_SHA256 = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"


def phase(linear, upper):
    return np.array([sum(linear[j] for j in range(9) if x>>j&1)+
                     2*sum(bool(x>>i&1 and x>>j&1) for i,j in upper) for x in range(N)]) % 4


def rotate(re,im,angle):
    unit_r = np.array([1,0,-1,0])[angle%4]
    unit_i = np.array([0,1,0,-1])[angle%4]
    return re*unit_r-im*unit_i, re*unit_i+im*unit_r


def fw_axis(re, im, bit):
    alt = ADDR ^ bit
    return re-im+re[alt]+im[alt], im+re+im[alt]-re[alt]


def direct_rank_eight_adjoint(vectors):
    # Encode G's action on bit vectors by enumerating xor combinations.
    perm = [0]
    basis = []
    for v in [*vectors,*(1<<i for i in range(9))]:
        if v not in perm:
            perm += [v^w for w in perm]
            basis.append(v)
    require(len(basis)==9 and basis[:8]==vectors and len(set(perm))==N, "Invertible canonical frame extension")
    inverse = np.argsort(perm)
    preimages = [int(inverse[1<<i]) for i in range(9)]
    linear = [1 ^ (x.bit_count()&1) for x in preimages]
    upper = [(i,j) for i in range(9) for j in range(i+1,9) if (preimages[i]&preimages[j]).bit_count()&1]
    phi = phase(linear,upper)
    diff = inverse[ROW] ^ inverse[COL]
    # Exact Gaussian integer numerator for C_8^*. Integer pairs below
    # encode (1-i)^(8-h)(1+i)^h, whose real/imaginary parts are at most 16.
    powers = [rotate(np.int64(16),np.int64(0),k) for k in range(9)]
    re = np.zeros((N,N),dtype=np.int64)
    im = np.zeros_like(re)
    for h,(a,b) in enumerate(powers):
        allowed = np.array([d.bit_count()==h and d<256 for d in range(N)])
        use = allowed[diff]
        re[use], im[use] = a,b
    # (1-i)^8 = +16 and each replaced factor adds a phase of +i.
    return rotate(re,im,phi[ROW]-phi[COL])


def monomial_left(re,im,record,extra_phase=0):
    matrix = record["matrix_rows"]
    q = record["quadratic_rows"]
    terms = [(i,j) for i in range(9) for j in range(i+1,9) if q[i]>>j&1]
    angles = phase(record["linear_Z4"],terms) + record["phase"] + extra_phase
    new = np.array([record["offset"] ^ sum((((x&v).bit_count()&1)<<i)
                                          for i,v in enumerate(matrix)) for x in range(N)])
    require(len(set(new))==N,"Monomial routing is a bijection")
    a,b = rotate(re,im,angles[:,None])
    out_a,out_b = np.empty_like(a),np.empty_like(b)
    out_a[new],out_b[new] = a,b
    return out_a,out_b



def check(word, compiler_path):
    require(word["program"][76298] == ["MOVE", 133, 591, 127, False], "Literal paid role and frames")
    low, high = (word["frames"][i] for i in (591, 127))
    require(len(low) == 8 and len(high) == 9, "Rank-eight to rank-nine boundary")
    digest = sha256(compiler_path.read_bytes()).hexdigest()
    require(digest == COMPILER_SHA256, "Exact compiler bytes shared by #7113 and selected #7000")
    compiler = runpy.run_path(str(compiler_path))
    old, full = (compiler["canonical_frame"](9, tuple(v)) for v in (low, high))
    recipe, _ = compiler["lower_child"](old.adjoint().then(full))
    require(recipe["rank"] == 1, "Compiler produces exactly one rank-one child")
    expected_a, expected_b = direct_rank_eight_adjoint(low)
    for i in range(9):
        expected_a, expected_b = fw_axis(expected_a, expected_b, 1 << i)
    # The direct quotient uses denominator 2**17. The recipe uses 2.
    identity = np.eye(N, dtype=np.int64)
    zero = np.zeros_like(identity)
    a, b = monomial_left(identity, zero, recipe["right"])
    a, b = fw_axis(a, b, 1)
    recipe_a, recipe_b = monomial_left(a, b, recipe["left"])
    require(np.array_equal(expected_a, recipe_a * 2**16)
            and np.array_equal(expected_b, recipe_b * 2**16), "All 512 exact Gaussian columns")
    require(np.all(np.count_nonzero(recipe_a | recipe_b, axis=0) == 2), "Two nonzero coefficients per rank-one column")
    corrupt_a, corrupt_b = monomial_left(a, b, recipe["left"], 1)
    require(not (np.array_equal(expected_a, corrupt_a * 2**16)
                 and np.array_equal(expected_b, corrupt_b * 2**16)), "Absolute phase corruption rejected")
    return dict(role=133, pair=[591, 127], rank=1, exact_columns=N, compared_entries=N*N,
                compiler_sha256=digest,
                exact_recipe_sha256=sha256(json.dumps(recipe,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
                global_phase_mutation_rejected=True)
