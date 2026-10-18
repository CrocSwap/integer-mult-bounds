# Exact two-helper dyadic scaling of the k8 scalar provider

Scaling L251 and L427 saves 576 scalar primitives per complex invocation in each orientation. This is optimal among dyadic gauges on at most two of the 237 eligible helpers, with ADD topology and existing SCALEs fixed. Each pair's cost is affine between vertical, horizontal and diagonal break lines. Boundary charges make it coercive; unit discounts lower boundary values. A minimum therefore occurs at an integral intersection. Independent integer-grid enumeration confirms every pair minimum. Exact replay checks all 712 input columns. Native hosting remains unchecked; no new kappa is claimed. Hanson Sun, with substantial OpenAI Codex assistance, credits @woklerx's PR1161, Sagar Thakrar's lowerer and the retained supplier lineage.

| Orientation | Gauges on L251, L427 | Baseline | Candidate | Scalar saving |
|---|---|---:|---:|---:|
| Forward | 1/4, 1/4 | 149002 | 148426 | 576 |
| Backward | 4, 4 | 149018 | 148442 | 576 |

| Scope / evidence | Value |
|---|---|
| Status | Finite scalar construction; scoped optimization proof |
| Base | `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` |
| Predecessor | [PR1161](https://github.com/CrocSwap/integer-mult-bounds/pull/1161), `d210969d3158a1e6c505e41f67dd84e555c88564` |
| Scalar compiler | Sagar Thakrar, [PR696 lowering](../complex-dyadic-lowering/lower.py) |
| Pair domain | 237 non-center, no-COPY/clear, unwrapped helpers; entry frame 0, exit FULL |
| Exponents | All of `Z²`, including zero |
| Topology | Original ADD operands/order; original SCALE/COPY/clear operations fixed |
| Pair count / orientation | 27966 = 2414 interacting + 25552 separable |
| Vertex evaluations / orientation | 735975 |
| Independent integer-grid evaluations | 19162332, plus separable single-coordinate enumeration |
| Original Horner saving | 416 scalar primitives / complex invocation / orientation |
| Added boundary charges | 8 real shifts = 16 scalar primitives / complex invocation |
| New helpers / frame moves / recursive children | 0 / 0 / 0 |
| Paid profile | Exact equality in both orientations |
| Positive prefix bounds | 52 / 68 bits; retained local charge 192 bits |
| Independent literal inputs | 6 exact dirty-state cases, including coefficient workspace |
| Rejection controls | 16 |
| Excluded | Other helper interfaces; 3+ simultaneous gauges; negative signs; changing existing SCALEs; coefficient-work persistence; native/global invoice admission |
| Inherited | All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, analytic transfer, bit H1–H5 |
| Concurrent comparator | [PR1170](https://github.com/CrocSwap/integer-mult-bounds/pull/1170): stage SCALE consolidation; composition untested |
| License | Apache-2.0 |

```sh
python3 -I -B research/k8-pair-dyadic-seed25/verify.py
python3 -I -B research/k8-pair-dyadic-seed25/independent.py
python3 -I -O -B research/k8-pair-dyadic-seed25/test_package.py
```

```text
PASS_K8_PAIR_DYADIC_CENSUS
PASS_INDEPENDENT_PAIR_GRID_AND_PRIMITIVES
PASS_PAIR_REJECTION_CONTROLS
```

## Exact algebra and finite reduction

```text
h,j in eligible_helpers; (k,l) in Z²
k_h = k, k_j = l, all other k_r = 0
D = diag(2^k_r)
ADD(t,s,q) -> ADD(t,s,q * 2^(k_t-k_s))
D^-1 (D A_m D^-1) ... (D A_1 D^-1) D = A_m ... A_1

|q_g| = p_g * 2^e_g, p_g positive odd
c(p,e) = 2 + floor(log2(p)) + popcount(p) + |e| - [p=1 and e=0]
f_g(x) = |x| - [p_g=1 and x=0]
Delta(k,l) = 2|k| + 2|l|
             + sum_g (f_g(e_g + sigma_g*k + tau_g*l) - f_g(e_g))
(sigma_g,tau_g) in {(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)}
Delta(k,l) >= 2|k| + 2|l| - sum_g f_g(e_g) - number_of_ADDs

V = {0} union {-sigma_g*e_g : tau_g=0, sigma_g!=0}
H = {0} union {-tau_g*e_g : sigma_g=0, tau_g!=0}
D_break = {-sigma_g*e_g : sigma_g=-tau_g!=0}
Vertices = {(v,h): v in V, h in H}
           union {(v,v-d): v in V, d in D_break}
           union {(h+d,h): h in H, d in D_break}

Delta: lower semicontinuous, coercive, affine on each relative face interior
face boundary discounts <= adjacent affine limits
all nonparallel line-pair determinants = +/-1
min_(Z²) Delta = min_(R²) Delta = min_Vertices Delta

M = max_g |e_g| = 15
Vertices subset [-2M,2M]²
Independent interacting-pair grid = {-31,...,31}²
Separable pairs: min Delta = min Delta_h + min Delta_j
```

[Certificate](CERTIFICATE.json) · [Full pair census](PAIR-CENSUS.json.gz) ·
[Candidate programs](PROGRAMS.json.gz) · [Task card](CLAIM.json) ·
[Sources](SOURCES.json) · [Validation](VALIDATION.json) ·
[Retained predecessor proof](vendor/pr1161/PROOF.md) ·
[Retained attribution](vendor/pr1161/PROVENANCE.md)
