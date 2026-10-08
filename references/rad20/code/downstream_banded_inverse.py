#!/usr/bin/env python3
"""Exact finite audit for a reusable circular-banded Gaussian inverse.

The theorem-level precomputation is polynomial in the line length and may
use long exact rational records.  The online factors are rounded to O(p)
bits and applied on fixed tapes.  This finite Python prototype verifies
the algebra and rigorously bounds errors; it is not a tape simulator.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_gaussian import ceil_q, check_sources, require
from downstream_blocked_gaussian import gaussian_interval, pi_interval


def norm_vector(v: list[Q]) -> Q:
    return max(map(abs,v),default=Q(0))


def norm_matrix(a: list[list[Q]]) -> Q:
    return max((sum(map(abs,row),Q(0)) for row in a),default=Q(0))


def matvec(a: list[list[Q]],v: list[Q]) -> list[Q]:
    return [sum((x*y for x,y in zip(row,v)),Q(0)) for row in a]


def rounding(x: Q,bits: int) -> Q:
    scale = 2**bits
    z = x*scale
    integer = abs(z.numerator)//z.denominator
    return Q(integer if z >= 0 else -integer,scale)


def upper_text(x: Q,bits: int = 128) -> str:
    """Compact exact outward bound, avoiding huge determinant numerators."""
    return str(Q(ceil_q(x*2**bits),2**bits))


def nearest_data(s: int,t: int) -> tuple[Q,list[Q]]:
    rho = Q(t,s)
    beta = [rho*j-((rho*j+Q(1,2)).numerator//(rho*j+Q(1,2)).denominator)
            for j in range(s)]
    require(all(-Q(1,2) <= x < Q(1,2) for x in beta),"Rounding convention failed")
    return rho,beta


def phi(rho: Q,beta: list[Q],j: int,delta: int) -> Q:
    return (rho*delta+beta[j])**2-beta[(j+delta)%len(beta)]**2


def check_nearest_bounds() -> dict:
    comparisons = 0
    cases = [(s,t) for s in range(2,33) for t in range(s+1,2*s)]
    cases += [(63,64),(64,65),(127,128),(128,129),(511,512),(1009,1024)]
    for s,t in cases:
        rho,beta = nearest_data(s,t)
        theta = rho-1
        for j in range(s):
            for delta in [-2*s-1,-s,-4,-2,-1,1,2,4,s,2*s+1]:
                value = phi(rho,beta,j,delta)
                coarse = rho*rho*delta*delta-rho*abs(delta)
                require(value >= coarse,"General Gaussian exponent bound failed")
                if delta in (-1,1):
                    sharper = 1+2*theta+2*delta*beta[j]
                    require(value >= sharper,"Nearest-neighbour sharpening failed")
                require(value > 0,"Off-diagonal exponent is not positive")
                comparisons += 1
    # Exact integer sufficient conditions for the analytic contraction.
    for p in [101,128,1024,2**40]:
        u = max(4,(8*p-1).bit_length())
        require(2**u >= 8*p,"Logarithmic width prerequisite failed")
        extra = Q(5,2**(6*u))
        require(extra < Q(1,4*p),"Gaussian extra-tail allowance failed")
    return {"status":"PASS exact nearest, distant, tie and periodic-alias bounds",
            "cases":len(cases),"exponent_comparisons":comparisons,
            "row_bound":"exp(-2*pi*u*theta)+5*exp(-2*pi*u)",
            "contraction_gap":"min(u*theta,1)/4 when u>=ceil(log2(8p)), theta>1/(4p)"}


def lu_banded(a: list[list[Q]],w: int) -> tuple[list[list[Q]],list[list[Q]],dict]:
    """Exact no-pivot factorization, checking every Schur row invariant."""
    n = len(a)
    b = [row.copy() for row in a]
    low = [[Q(int(i==j)) for j in range(n)] for i in range(n)]
    high = [[Q(0) for _ in range(n)] for _ in range(n)]
    gap = min(a[i][i]-sum((abs(a[i][j]) for j in range(n) if j!=i),Q(0))
              for i in range(n))
    row_bound = norm_matrix(a)
    require(gap > 0,"Input is not strictly row diagonally dominant")
    minimum_pivot = Q(2**256)
    maximum_schur_row = Q(0)
    for k in range(n):
        # Rows outside this band do not change at this elimination step.
        for i in range(k,min(n,k+w+1)):
            indices = range(max(k,i-w),min(n,i+w+1))
            current_row = [b[i][j] for j in indices]
            current_gap = b[i][i]-sum((abs(b[i][j]) for j in indices if j!=i),Q(0))
            require(current_gap >= gap,"Schur diagonal-dominance gap decreased")
            require(sum(map(abs,current_row),Q(0)) <= row_bound,
                    "Schur row norm grew")
            maximum_schur_row = max(maximum_schur_row,sum(map(abs,current_row),Q(0)))
        pivot = b[k][k]
        require(pivot >= gap,"Unstable or zero LU pivot")
        minimum_pivot = min(minimum_pivot,pivot)
        for j in range(k,min(n,k+w+1)):
            high[k][j] = b[k][j]
        for i in range(k+1,min(n,k+w+1)):
            low[i][k] = b[i][k]/pivot
            for j in range(k+1,min(n,k+w+1)):
                b[i][j] -= low[i][k]*b[k][j]
            b[i][k] = Q(0)
    # Exact scalar factor identity on all possibly nonzero product entries.
    identities = 0
    for i in range(n):
        for j in range(max(0,i-w),min(n,i+w+1)):
            product = sum((low[i][k]*high[k][j] for k in range(max(0,i-w),min(i,j)+1)),Q(0))
            require(product == a[i][j],"L U does not reconstruct the band matrix")
            identities += 1
    require(norm_matrix(high) <= row_bound,"Upper factor norm exceeds Schur bound")
    require(norm_matrix(low) <= 1+w*row_bound/gap,"Lower factor norm bound failed")
    return low,high,{"row_gap":str(gap),"minimum_pivot_lower":str(rounding(minimum_pivot,128)),
                     "maximum_schur_row_norm_upper":upper_text(maximum_schur_row),
                     "lower_factor_norm_upper":upper_text(norm_matrix(low)),
                     "upper_factor_norm_upper":upper_text(norm_matrix(high)),
                     "factor_identity_checks":identities}


def solve_exact(low: list[list[Q]],high: list[list[Q]],b: list[Q],w: int) -> list[Q]:
    n = len(b)
    y = [Q(0)]*n
    for i in range(n):
        y[i] = b[i]-sum((low[i][j]*y[j] for j in range(max(0,i-w),i)),Q(0))
    x = [Q(0)]*n
    for i in reversed(range(n)):
        x[i] = (y[i]-sum((high[i][j]*x[j] for j in range(i+1,min(n,i+w+1))),Q(0)))/high[i][i]
    return x


def inverse_exact(a: list[list[Q]]) -> list[list[Q]]:
    """Independent dense Gauss-Jordan inversion for the small border matrix."""
    n = len(a)
    b = [a[i].copy()+[Q(int(i==j)) for j in range(n)] for i in range(n)]
    for k in range(n):
        pivot = next((i for i in range(k,n) if b[i][k]),None)
        require(pivot is not None,"Singular border matrix")
        b[k],b[pivot] = b[pivot],b[k]
        value = b[k][k]
        b[k] = [x/value for x in b[k]]
        for i in range(n):
            if i!=k and b[i][k]:
                value = b[i][k]
                b[i] = [x-value*y for x,y in zip(b[i],b[k])]
    result = [row[n:] for row in b]
    for i in range(n):
        for j in range(n):
            value = sum((a[i][k]*result[k][j] for k in range(n)),Q(0))
            require(value == int(i==j),"Independent border inverse identity failed")
    return result


def prepare(h: list[list[Q]],w: int,bits: int) -> tuple[dict,dict]:
    n = len(h)
    require(n > 2*w,"Wrap correction requires distinct boundary indices")
    a = [row.copy() for row in h]
    for i in range(n):
        for j in range(n):
            if abs(i-j)>w:
                a[i][j] = Q(0)
    low,high,metadata = lu_banded(a,w)
    border = list(range(w))+list(range(n-w,n))
    r = len(border)
    v = [[h[i][j]-a[i][j] for j in range(n)] for i in border]
    require(norm_matrix(v) < 1,"Wrap factor norm too large")
    columns = []
    for j in border:
        rhs = [Q(int(i==j)) for i in range(n)]
        columns.append(solve_exact(low,high,rhs,w))
    z = [[columns[j][i] for j in range(r)] for i in range(n)]
    k = [[Q(int(i==j))+sum((v[i][l]*z[l][j] for l in range(n)),Q(0))
          for j in range(r)] for i in range(r)]
    ki = inverse_exact(k)
    gap_h = min(h[i][i]-sum((abs(h[i][j]) for j in range(n) if j!=i),Q(0))
                for i in range(n))
    require(gap_h > 0,"Cyclic matrix lost diagonal dominance")
    require(norm_matrix(z) <= 1/Q(metadata["row_gap"]),"A^-1 U border norm bound failed")
    require(norm_matrix(ki) <= 1+norm_matrix(v)/gap_h,
            "Woodbury small inverse norm bound failed")
    tables = {"low":[[rounding(x,bits) for x in row] for row in low],
              "high":[[rounding(x,bits) for x in row] for row in high],
              "reciprocal":[rounding(1/high[i][i],bits) for i in range(n)],
              "v":v,"z":[[rounding(x,bits) for x in row] for row in z],
              "ki":[[rounding(x,bits) for x in row] for row in ki],
              "exact_low":low,"exact_high":high,"exact_z":z,"exact_ki":ki,
              "w":w,"bits":bits}
    metadata.update({"cyclic_gap":str(gap_h),"border_rank":r,
                     "wrap_factor_norm":str(norm_matrix(v)),
                     "border_solution_norm_upper":upper_text(norm_matrix(z)),
                     "border_inverse_norm_upper":upper_text(norm_matrix(ki)),
                     "factor_rounding_bits":bits})
    return tables,metadata


def apply(tables: dict,b: list[Q],rounded: bool = True) -> list[Q]:
    n,w,bits = len(b),tables["w"],tables["bits"]
    if rounded:
        low,high = tables["low"],tables["high"]
        y = [Q(0)]*n
        for i in range(n):
            y[i] = rounding(b[i]-sum((low[i][j]*y[j] for j in range(max(0,i-w),i)),Q(0)),bits)
        x0 = [Q(0)]*n
        for i in reversed(range(n)):
            value = y[i]-sum((high[i][j]*x0[j] for j in range(i+1,min(n,i+w+1))),Q(0))
            x0[i] = rounding(tables["reciprocal"][i]*value,bits)
        vb = [rounding(x,bits) for x in matvec(tables["v"],x0)]
        zb = [rounding(x,bits) for x in matvec(tables["ki"],vb)]
        correction = [rounding(x,bits) for x in matvec(tables["z"],zb)]
        return [rounding(x-y,bits) for x,y in zip(x0,correction)]
    x0 = solve_exact(tables["exact_low"],tables["exact_high"],b,w)
    zb = matvec(tables["exact_ki"],matvec(tables["v"],x0))
    return [x-y for x,y in zip(x0,matvec(tables["exact_z"],zb))]


def gaussian_case(s: int,t: int,u: int,w: int,bits: int,target: int) -> dict:
    rho,beta = nearest_data(s,t)
    pi_bounds = pi_interval(bits+64)
    scale = 2**bits
    h = [[Q(int(i==j)) for j in range(s)] for i in range(s)]
    intervals = {}
    max_row_upper = Q(0)
    for j in range(s):
        row_upper = Q(0)
        for delta in range(-w,w+1):
            if not delta:
                continue
            f = u*phi(rho,beta,j,delta)
            if f not in intervals:
                intervals[f] = gaussian_interval(f,pi_bounds,bits+24)
            lo,hi = intervals[f]
            require(hi-lo < Q(1,scale),"Gaussian coefficient interval too wide")
            h[j][(j+delta)%s] = Q((lo*scale).numerator//(lo*scale).denominator,scale)
            row_upper += hi
        max_row_upper = max(max_row_upper,row_upper)
    tail_bound = Q(4,2**(3*u*w*(w+1)))
    gap_analytic = 1-max_row_upper-tail_bound
    require(gap_analytic > 0,"Finite full Gaussian contraction not certified")
    tables,metadata = prepare(h,w,bits)
    max_residual,max_exact_error,max_gaussian_error = Q(0),Q(0),Q(0)
    outputs = []
    for component in range(2):
        b = [Q(((17*j+7+5*component)%29)-14,32) for j in range(s)]
        exact = apply(tables,b,rounded=False)
        require(matvec(h,exact) == b,"Exact cyclic Woodbury solution failed residual")
        actual = apply(tables,b)
        residual = norm_vector([x-y for x,y in zip(matvec(h,actual),b)])
        exact_error = norm_vector([x-y for x,y in zip(actual,exact)])
        require(exact_error <= residual/Q(metadata["cyclic_gap"]),
                "Exact inverse residual bound failed")
        # Independently enclose the original infinite Gaussian residual.
        original_residual = Q(0)
        for j in range(s):
            lo,hi = actual[j]-b[j],actual[j]-b[j]
            for delta in range(-w,w+1):
                if delta:
                    lower,upper = intervals[u*phi(rho,beta,j,delta)]
                    endpoints = sorted((actual[(j+delta)%s]*lower,actual[(j+delta)%s]*upper))
                    lo += endpoints[0]
                    hi += endpoints[1]
            original_residual = max(original_residual,abs(lo),abs(hi))
        original_residual += tail_bound*norm_vector(actual)
        error_bound = original_residual/gap_analytic
        require(error_bound < Q(1,2**(target+8)),"Certified full Gaussian inverse error failed")
        max_residual,max_exact_error,max_gaussian_error = max(max_residual,residual),max(max_exact_error,exact_error),max(max_gaussian_error,error_bound)
        outputs += actual
    metadata.update({"status":"PASS rigorous circular-banded Gaussian inverse",
                     "s":s,"t":t,"u":u,"u_theta":str(u*(rho-1)),"half_bandwidth":w,
                     "target_bits":target,"gaussian_row_gap_lower":str(gap_analytic),
                     "omitted_lattice_tail_bound":str(tail_bound),
                     "max_dyadic_residual_upper":upper_text(max_residual),
                     "max_error_to_exact_dyadic_inverse_upper":upper_text(max_exact_error),
                     "max_full_gaussian_inverse_error_upper":upper_text(max_gaussian_error),
                     "real_and_imaginary_cases":2,"coefficient_interval_evaluations":len(intervals),
                     "rounded_outputs_sha256":hashlib.sha256("\n".join(map(str,outputs)).encode()).hexdigest(),
                     "scope":"Finite work precision; not a full asymptotic P=256p tape implementation."})
    return metadata


def adversarial_case() -> dict:
    n,w,bits = 19,3,72
    gap = Q(1,2**20)
    h = [[Q(int(i==j)) for j in range(n)] for i in range(n)]
    for i in range(n):
        for delta in range(-w,w+1):
            if delta:
                sign = -1 if (i+delta)%3 else 1
                h[i][(i+delta)%n] = sign*(1-gap)/(2*w)
    tables,metadata = prepare(h,w,bits)
    b = [Q((i*13)%17-8,16) for i in range(n)]
    exact = apply(tables,b,rounded=False)
    require(matvec(h,exact) == b,"Adversarial exact cyclic solve failed")
    actual = apply(tables,b)
    error = norm_vector([x-y for x,y in zip(actual,exact)])
    require(error < Q(1,2**32),"Adversarial rounded factor solve failed")
    metadata.update({"status":"PASS signed near-singular row-DD cyclic matrix",
                     "dimension":n,"half_bandwidth":w,"max_error_upper":upper_text(error)})
    return metadata


def precision_bounds() -> dict:
    cases = []
    for p in [101,128,256,1024,2**40]:
        eta = Q(1,2**(256*p)) if p <= 1024 else None
        # Integer bit length avoids allocating 2^(256*2^40).
        require((2**40*p**14).bit_length() < 255*p-20,
                "Rounded solver error cannot fit O(p) work precision")
        require((16*p*p).bit_length() < 45*p-20,"Gaussian truncation error bound failed")
        cases.append({"p":p,"rounded_solver_error_coefficient":str(2**40*p**14),
                      "work_bits":256*p,"tail_exponent_bits":46*p})
    return {"status":"PASS exact universal O(p) work-precision inequalities",
            "mu_lower":"1/(4p)","solver_error_upper":"2^40*p^14*2^(-256p)",
            "matrix_tail_upper":"2^(-46p)","cases":cases}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--skip-large",action="store_true")
    args = parser.parse_args()
    start = time.monotonic()
    source = Path(__file__)
    result = {"generated_at":datetime.now(timezone.utc).isoformat(),
              "campaign":"20261007T222521Z","campaign_start":"2026-10-07T22:25:21Z",
              "campaign_deadline":"2026-10-08T08:25:21Z",
              "provenance":check_sources(args.upstream),
              "source_sha256":{source.name:hashlib.sha256(source.read_bytes()).hexdigest()},
              "nearest_bounds":check_nearest_bounds(),"precision_bounds":precision_bounds(),
              "gaussian_cases":[],"adversarial_signed_case":adversarial_case()}
    cases = [(17,18,4,3,56,16),(32,33,9,3,64,20),(63,64,16,3,64,20)]
    if not args.skip_large:
        cases += [(127,128,16,3,72,24),(128,129,16,3,72,24),(511,512,16,3,72,24)]
    for case in cases:
        print("Starting Gaussian inverse",case,flush=True)
        result["gaussian_cases"].append(gaussian_case(*case))
        print("PASS Gaussian inverse",case[:3],flush=True)
    result["elapsed_seconds"] = time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PASS",result["nearest_bounds"]["exponent_comparisons"],"Gaussian exponent bounds",flush=True)
    print("PASS",len(result["gaussian_cases"]),"rigorous Gaussian inverse cases",flush=True)


if __name__ == "__main__":
    main()
