#!/usr/bin/env python3
"""Exact phase-cell, Toeplitz-convolution and boundary-Schur prototype.

The accepted output is backed by rational Gaussian intervals, exact Schur
identities and residual inverse bounds. This is a finite prototype, not a
complete fixed-tape multiplication implementation.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_gaussian import ceil_q,check_sources,require
from downstream_blocked_gaussian import dyadic_convolution,gaussian_interval,pi_interval
from downstream_banded_inverse import (apply,inverse_exact,lu_banded,matvec,
                                       nearest_data,norm_matrix,norm_vector,phi,
                                       rounding,solve_exact,upper_text)


def cells_for(s: int,t: int) -> list[list[int]]:
    rho,beta = nearest_data(s,t)
    cells = []
    previous = None
    for j in range(s):
        q = rho*j-beta[j]
        require(q.denominator == 1,"Nonintegral nearest index")
        phase = int(q)-j
        if phase != previous:
            cells.append([])
            previous = phase
        cells[-1].append(j)
    return cells


def lower_toeplitz(c: list[Q],b: list[Q],bits: int | None = None) -> list[Q]:
    if bits is None:
        return [sum((c[i-j]*b[j] for j in range(i+1)),Q(0)) for i in range(len(b))]
    values,_ = dyadic_convolution(c,b)
    return [rounding(x,bits) for x in values[:len(b)]]


def upper_toeplitz(c: list[Q],b: list[Q],bits: int | None = None) -> list[Q]:
    return list(reversed(lower_toeplitz(c,list(reversed(b)),bits)))


def gs_vector(g: list[Q],w: int) -> tuple[list[Q],dict]:
    n = len(g)
    a = [[g[abs(i-j)] for j in range(n)] for i in range(n)]
    low,high,metadata = lu_banded(a,min(w,n-1))
    x = solve_exact(low,high,[Q(int(i==0)) for i in range(n)],min(w,n-1))
    z = [Q(0)]+list(reversed(x[1:]))
    require(x[0] > Q(1,2) and sum(map(abs,x),Q(0)) < 2,
            "Gaussian Toeplitz inverse generators are not bounded")
    # Constructive independent check of every column and matrix product.
    identities = 0
    for j in range(n):
        rhs = [Q(int(i==j)) for i in range(n)]
        first = lower_toeplitz(x,upper_toeplitz(x,rhs))
        second = lower_toeplitz(z,upper_toeplitz(z,rhs))
        solution = [(a-b)/x[0] for a,b in zip(first,second)]
        require(matvec(a,solution) == rhs,"Symmetric Gohberg-Semencul identity failed")
        identities += n
    metadata.update({"dimension":n,"generator_l1_upper":upper_text(sum(map(abs,x),Q(0))),
                     "first_generator_coordinate_lower":str(rounding(x[0],128)),
                     "gs_identity_entries":identities})
    return x,metadata


def local_apply(local: dict,b: list[Q],rounded: bool) -> list[Q]:
    n,bits = len(b),local["bits"]
    weights = local["weights"]
    x = local["x"]
    if rounded:
        xr = [rounding(v,bits) for v in x]
        z = [Q(0)]+list(reversed(xr[1:]))
        reciprocal = [rounding(1/v,bits) for v in weights]
        input_values = [rounding(v*c,bits) for v,c in zip(reciprocal,b)]
        first = lower_toeplitz(xr,upper_toeplitz(xr,input_values,bits),bits)
        second = lower_toeplitz(z,upper_toeplitz(z,input_values,bits),bits)
        inv_x0 = rounding(1/x[0],bits)
        middle = [rounding((a-c)*inv_x0,bits) for a,c in zip(first,second)]
        return [rounding(v*c,bits) for v,c in zip(weights,middle)]
    z = [Q(0)]+list(reversed(x[1:]))
    input_values = [c/v for v,c in zip(weights,b)]
    first = lower_toeplitz(x,upper_toeplitz(x,input_values))
    second = lower_toeplitz(z,upper_toeplitz(z,input_values))
    return [v*(a-c)/x[0] for v,a,c in zip(weights,first,second)]


def prepare_boundary(h: list[list[Q]],w: int,bits: int) -> tuple[dict,dict]:
    """Generic cyclic row-DD solver; diagonal and wrap norm may vary."""
    n = len(h)
    # Equality is the two-cell finite case; the first/last groups remain
    # disjoint, and the Woodbury border then covers the whole matrix.
    require(n >= 2*w,"Boundary wrap groups overlap")
    a = [[h[i][j] if abs(i-j)<=w else Q(0) for j in range(n)] for i in range(n)]
    low,high,metadata = lu_banded(a,w)
    border = list(range(w))+list(range(n-w,n))
    v = [[h[i][j]-a[i][j] for j in range(n)] for i in border]
    require(norm_matrix(v) < 2,"Boundary wrap factor exceeded row norm")
    columns = [solve_exact(low,high,[Q(int(i==j)) for i in range(n)],w) for j in border]
    z = [[column[i] for column in columns] for i in range(n)]
    r = len(border)
    k = [[Q(int(i==j))+sum((v[i][l]*z[l][j] for l in range(n)),Q(0))
          for j in range(r)] for i in range(r)]
    ki = inverse_exact(k)
    gap = min(h[i][i]-sum((abs(h[i][j]) for j in range(n) if j!=i),Q(0)) for i in range(n))
    require(gap > 0 and norm_matrix(h)<2,"Boundary matrix lost row diagonal dominance")
    require(norm_matrix(ki) <= 1+norm_matrix(v)/gap,"Boundary Woodbury inverse norm failed")
    table = {"low":[[rounding(v,bits) for v in row] for row in low],
             "high":[[rounding(v,bits) for v in row] for row in high],
             "reciprocal":[rounding(1/high[i][i],bits) for i in range(n)],
             "v":v,"z":[[rounding(v,bits) for v in row] for row in z],
             "ki":[[rounding(v,bits) for v in row] for row in ki],
             "exact_low":low,"exact_high":high,"exact_z":z,"exact_ki":ki,
             "w":w,"bits":bits}
    metadata.update({"dimension":n,"half_bandwidth":w,"cyclic_gap":str(gap),
                     "wrap_norm_upper":upper_text(norm_matrix(v)),
                     "border_inverse_norm_upper":upper_text(norm_matrix(ki))})
    return table,metadata


def gaussian_phase_case(s: int,t: int,u: int,w: int,bits: int,target: int) -> dict:
    rho,beta = nearest_data(s,t)
    theta = rho-1
    cells = cells_for(s,t)
    require(all(len(c)>2*w for c in cells),"Finite phase cell has no interior")
    pi_bounds = pi_interval(bits+64)
    scale = 2**bits
    cache = {}
    def lower_weight(f: Q) -> Q:
        if f not in cache:
            lo,hi = gaussian_interval(f,pi_bounds,bits+24)
            require(hi-lo < Q(1,scale),"Phase Gaussian interval too wide")
            cache[f] = (lo,hi)
        lo,_ = cache[f]
        return Q((lo*scale).numerator//(lo*scale).denominator,scale)
    exponents = [u*(Q(1,4)-x*x)/theta for x in beta]
    weights = [lower_weight(f) for f in exponents]
    require(min(weights)>0,"Rounded proof weights vanished")
    g = [Q(1)]+[lower_weight(u*rho*delta*delta) for delta in range(1,w+1)]
    cell_of = {j:i for i,c in enumerate(cells) for j in c}
    h = [[Q(int(i==j)) for j in range(s)] for i in range(s)]
    max_row_upper = Q(0)
    identities = 0
    for j in range(s):
        row_upper = Q(0)
        for delta in range(-w,w+1):
            if not delta:
                continue
            l = (j+delta)%s
            actual_f = u*phi(rho,beta,j,delta)
            lower_weight(actual_f)
            row_upper += cache[actual_f][1]
            if cell_of[j]==cell_of[l] and abs(j-l)<=w:
                require(actual_f == u*rho*delta*delta+exponents[j]-exponents[l],
                        "Exact phase-cell Toeplitz conjugation failed")
                h[j][l] = weights[j]*g[abs(delta)]/weights[l]
                identities += 1
            else:
                h[j][l] = lower_weight(actual_f)
        max_row_upper = max(max_row_upper,row_upper)
    tail = Q(4,2**(3*u*w*(w+1)))
    gaussian_gap = 1-max_row_upper-tail
    gap_h = min(1-sum((abs(h[i][j]) for j in range(s) if j!=i),Q(0)) for i in range(s))
    require(gaussian_gap>0 and gap_h>0,"Structured rounding lost finite Gaussian contraction")
    locals,gs_metadata = [],[]
    boundary = []
    for cell in cells:
        interior = cell[w:-w]
        boundary += cell[:w]+cell[-w:]
        g_local = g+[Q(0)]*max(0,len(interior)-len(g))
        x,metadata = gs_vector(g_local[:len(interior)],w)
        locals.append({"indices":interior,"weights":[weights[i] for i in interior],
                       "x":x,"bits":bits})
        gs_metadata.append(metadata)
    all_i = [i for local in locals for i in local["indices"]]
    nb = len(boundary)
    sb = [[h[i][j] for j in boundary] for i in boundary]
    for local in locals:
        ii = local["indices"]
        for bj,j in enumerate(boundary):
            rhs = [h[i][j] for i in ii]
            if not any(rhs):
                continue
            z = local_apply(local,rhs,rounded=False)
            for bi,i in enumerate(boundary):
                sb[bi][bj] -= sum((h[i][l]*v for l,v in zip(ii,z)),Q(0))
    gap_sb = min(sb[i][i]-sum((abs(sb[i][j]) for j in range(nb) if j!=i),Q(0)) for i in range(nb))
    require(gap_sb >= gap_h,"Interior Schur gap decreased")
    require(norm_matrix(sb)<=norm_matrix(h),"Interior Schur row norm grew")
    bw = 2*w
    for i in range(nb):
        for j in range(nb):
            if min(abs(i-j),nb-abs(i-j))>bw:
                require(sb[i][j] == 0,"Boundary Schur bandwidth failed")
    sb_round = [[rounding(v,bits) for v in row] for row in sb]
    tables,border_metadata = prepare_boundary(sb_round,bw,bits)
    max_original_error = Q(0)
    max_residual = Q(0)
    local_error = Q(0)
    probes = 0
    for component in range(2):
        b = [Q(((17*j+7+5*component)%29)-14,32) for j in range(s)]
        first = [Q(0)]*s
        for local in locals:
            values = [b[i] for i in local["indices"]]
            y = local_apply(local,values,rounded=True)
            y_exact = local_apply(local,values,rounded=False)
            local_error = max(local_error,norm_vector([a-c for a,c in zip(y,y_exact)]))
            for i,v in zip(local["indices"],y):
                first[i] = v
        rhs_b = [rounding(b[i]-sum((rounding(h[i][j],bits)*first[j] for j in all_i),Q(0)),bits)
                 for i in boundary]
        xb = apply(tables,rhs_b)
        actual = [Q(0)]*s
        for i,v in zip(boundary,xb):
            actual[i] = v
        for local in locals:
            ii = local["indices"]
            rhs_i = [rounding(b[i]-sum((rounding(h[i][j],bits)*v for j,v in zip(boundary,xb)),Q(0)),bits)
                     for i in ii]
            recovered = local_apply(local,rhs_i,rounded=True)
            for i,v in zip(ii,recovered):
                actual[i] = v
        residual = norm_vector([x-y for x,y in zip(matvec(h,actual),b)])
        max_residual = max(max_residual,residual)
        require(residual/gap_h < Q(1,2**(target+8)),"Structured dyadic Schur solve error failed")
        # Independent residual enclosure for the original infinite matrix.
        original_residual = Q(0)
        for j in range(s):
            lo,hi = actual[j]-b[j],actual[j]-b[j]
            for delta in range(-w,w+1):
                if delta:
                    lower,upper = cache[u*phi(rho,beta,j,delta)]
                    products = sorted([actual[(j+delta)%s]*lower,actual[(j+delta)%s]*upper])
                    lo += products[0]
                    hi += products[1]
            original_residual = max(original_residual,abs(lo),abs(hi))
        original_residual += tail*norm_vector(actual)
        error = original_residual/gaussian_gap
        require(error < Q(1,2**(target+8)),"Full infinite Gaussian phase inverse error failed")
        max_original_error = max(max_original_error,error)
        probes += 1
    return {"status":"PASS exact phase/GS/Schur and rational-interval infinite Gaussian inverse",
            "s":s,"t":t,"u":u,"u_theta":str(u*theta),"half_bandwidth":w,
            "work_bits":bits,"target_bits":target,"phase_cell_lengths":[len(c) for c in cells],
            "phase_conjugation_identities":identities,"interior_dimensions":[len(x["indices"]) for x in locals],
            "boundary_dimension":nb,"boundary_half_bandwidth":bw,
            "gaussian_row_gap_lower":str(gaussian_gap),"structured_row_gap_lower":str(rounding(gap_h,128)),
            "Schur_row_gap_lower":str(rounding(gap_sb,128)),
            "proof_weight_inverse_norm_upper":upper_text(1/min(weights)),
            "generator_audits":gs_metadata,"boundary_audit":border_metadata,
            "gaussian_interval_evaluations":len(cache),"signed_real_imaginary_probes":probes,
            "local_inverse_error_upper":upper_text(local_error),"structured_residual_upper":upper_text(max_residual),
            "full_gaussian_inverse_error_upper":upper_text(max_original_error),
            "omitted_lattice_tail_bound":str(tail),
            "scope":"Finite precision and cells; full asymptotic transfer requires separate proof and review."}


def scalar_identity_checks() -> dict:
    checks = 0
    for n in range(1,10):
        g = [Q(1,2**(j*j+2*j)) for j in range(n)]
        matrix = [[g[abs(i-j)] for j in range(n)] for i in range(n)]
        inverse = inverse_exact(matrix)
        x = [row[0] for row in inverse]
        z = [Q(0)]+list(reversed(x[1:]))
        for i in range(n):
            for j in range(n):
                gs = sum((x[i-k]*x[j-k]-z[i-k]*z[j-k] for k in range(min(i,j)+1)),Q(0))/x[0]
                require(gs == inverse[i][j],"Independent symmetric GS formula failed")
                checks += 1
    for p in [101,128,1024,2**40]:
        require((p**64).bit_length()+64*p < 32767*p-20,
                "Phase algorithm O(p)-precision margin failed")
    return {"status":"PASS independent exact GS orientation and work-precision checks",
            "gs_matrix_entries":checks,"work_precision_per_p":32768,
            "algorithm_error_form":"p^64*2^(64p)*2^(-32768p), plus Gaussian truncation"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--small-only",action="store_true")
    args = parser.parse_args()
    start = time.monotonic()
    source = Path(__file__)
    result = {"generated_at":datetime.now(timezone.utc).isoformat(),
              "campaign":"20261007T222521Z","campaign_start":"2026-10-07T22:25:21Z",
              "campaign_deadline":"2026-10-08T08:25:21Z",
              "provenance":check_sources(args.upstream),
              "source_sha256":{source.name:hashlib.sha256(source.read_bytes()).hexdigest()},
              "scalar_identity_checks":scalar_identity_checks(),"phase_cases":[]}
    cases = [(15,16,4,2,256,16),(31,32,4,2,512,20)]
    if not args.small_only:
        cases += [(63,64,4,2,768,24),(63,66,4,2,384,24),(64,67,4,2,384,24)]
    for case in cases:
        print("Starting phase inverse",case,flush=True)
        result["phase_cases"].append(gaussian_phase_case(*case))
        print("PASS phase inverse",case[:3],flush=True)
    result["elapsed_seconds"] = time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PASS",len(result["phase_cases"]),"rigorous phase Gaussian inverse cases",flush=True)


if __name__ == "__main__":
    main()
