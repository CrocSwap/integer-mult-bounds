# One compatibility factor suffices for the current recursive NODE guards

The current PR2753/PR2809 BIT caller's fresh-row guards admit

```
S_0 = 1,
S_D = 9475 * (28416 * N * H)^D       for D >= 1,
N = |GL_64(F_q)|,
H = q^(4096(w-1)).
```

The published sufficient reserve is `(269241600*N*H)^D`. The new divisor is
smaller by exactly `9475^(D-1)` at positive depth. Every existing local 9475
guard is retained. This is a source-bound stock-divisibility implication, not
an installed backend change, a new supplier, an exponent improvement or a
complete physical-caller verification. The selected result is unchanged.

Ross Richardson's PR2420 already separates live-row stock from the older
physical-slot format. This result answers a narrower successor question about
the actual later runtime: its local compatibility check can be kept without
repeating that factor independently at every depth. PR2420's minimum for
**both full depth-D formats** remains valid. The new smallest stock fails that
stronger promise at every D greater than one.

## Source boundary

Base canonical main is `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority
revision 6. All live inputs and their exact Git blobs/SHA256s are in
[SOURCES.json](SOURCES.json). Frozen predecessors are unchanged.

| Source | Relevant behavior |
| --- | --- |
| David Arias, PR2753, `selected-bit-recursive-caller/node.py` | `fresh_rows.quotient` divides R by `28416*N*H`; the returned U must be divisible by 9475. `child_stock=U` remains separate from spectators `U*B`. |
| PR2753, `driver.py` and `recursive_call.py` | Pass the complete U to a child, preserve the atom modulus and expose parent fields as frozen ancestors. |
| Jose Manuel, PR2809, `selected-bit-physical-caller/macro_machine.py` | NODE performs the same quotient and local guard; the child capsule receives the `unused` tape. |
| PR2809, `macro_binding.py`, `SelectedBinding` | `stock_multiple=9475`; its residual `check_stock` adds no global depth-format test. |
| PR2753 `PROOF.md`, sections 1, 4 and 7 | States the stronger sufficient `K^D` reserve, decreasing widths and pointwise fresh-row/spectator contract. |
| Ross Richardson, PR2420, `selected-live-row-divisor/README.md` | Proves the separate exact dual-format acceptance gate and retains all private work. |

The physical archive's `fresh_rows.py` and `cardinal_counts.py` are byte-equal
to the logical versions executed by this checker. The source mapping and
written induction identify the contract; substring checks alone do not prove
that every physical macro refines its logical counterpart. PR3223's independent
NODE/peel/owned-return audit is complementary, not repeated or promoted here.

## Exact guard theorem

Fix positive integers b and Q. At each internal node, divide its positive fresh
row count R by b exactly, require the quotient U to be positive and divisible
by Q, and pass the entire U to each child. A leaf accepts every positive row
count. Fix a maximum active depth D. No coprimality assumption is needed.

For a chain of exactly D internal nodes, all these guards hold if and only if

```
Q*b^D divides R                 when D >= 1.
```

Indeed, the successive quotients are `R/b, ..., R/b^D`. The last guard implies
`R=t*Q*b^D` for a positive integer t. Conversely that form makes every earlier
quotient positive and divisible by Q. At D=0 the least positive reserve is one.
Thus `Q*b^D` is the least positive cardinality for this guard contract. It is
not a lower bound for arbitrary reversible implementations or for a particular
source tree that never reaches depth D.

For a tree of depth at most D, suppose also that every completed child restores
its fresh row and exposed spectators pointwise before the next child uses them.
Take `R=t*S_D`. At an internal node with D positive,

```
U = R/b = t*Q*b^(D-1).
```

For any child of positive depth d at most D-1, this is
`(t*b^(D-1-d))*S_d`; a depth-zero child accepts it directly. Induction therefore
supplies every child's local guards. Completed siblings reuse U, rather than
multiplying reserves. This is the same endpoint/freshness/restoration premise
as the predecessors, not a consequence of an aggregate final-row check.

For the actual BIT width bound,

```
D(n) = 0                           if n < 64,
D(n) = 1 + D(42*floor(n/64))        otherwise.
```

The child-width map is monotone and contracts strictly. Every good child
`r*floor(n/64)` with `1<=r<=42`, and every fallback child of width at most
`floor(n/64)`, has depth at most `D(n)-1`. This applies the theorem with
`b=28416*N*H` and `Q=9475` at fixed q,w throughout a recursive call. Peeled
remainders occur before the fresh split and retain their completed-leaf
contract; they are not incorrectly bounded by `42*floor(n/64)`.

This establishes the recursive **stock implication** under the named completed
caller premises. It does not independently establish their endpoint, native
coefficients, arbitrary dirty-state restoration, physical refinement or time
charges. No private COPY buffer, owner slot, routing call or cleanup is removed.

### Uniform logarithmic envelope

For the selected prime domain `q>2^80` and integer `w>=1`,

```
log_q b < 4096*w + 3/16,
log_q Q < 7/40,
log_q S_D < D*(4096*w + 3/16) + 7/40       for D >= 1.
```

The group-order bound `N<q^4096`, together with `28416<2^15` and `9475<2^14`,
proves these inequalities. The exact integer certificate
`2^17*42^28 < 64^28` gives `D(e) <= (28/17)*log2(e)` for every integer e at
least one, by induction on the floor-child recurrence. Consequently

```
log_q S_D(e) < (28/17)*(4096*w + 3/16)*log2(e) + 7/40.
```

This also holds when D is zero because the left side is zero. The 28/17 depth
certificate is the predecessor PR2120 argument, not new mathematics here.
This envelope does not identify or admit fourteen implemented bootstrap stages,
bound the separate complex m=73 stock, or settle the inherited uniform-time
premises. No additional cutoff/headroom calculation is needed for this result.

### Exact boundary with the old physical format

Let `P=28425`, `W=28416`, so `P/gcd(P,W)=9475=Q`. At positive depth,
PR2420's physical-format criterion for `t*Q*(WNH)^D` becomes

```
(PNH)^D divides t*Q*(WNH)^D
    if and only if Q^D divides t*Q
    if and only if Q^(D-1) divides t.
```

In particular t=1 fails for D greater than one. Requiring both complete formats
therefore restores the old least reserve `(lcm(W,P)*N*H)^D` exactly. This result
does not remove a necessary divisor from a consumer that actually requires it.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
python3.12 -Werror -I -B research/selected-runtime-guard-stock/verify.py
python3.12 -Werror -I -B research/selected-runtime-guard-stock/independent_check.py
python3.12 -Werror -I -O -B research/selected-runtime-guard-stock/test_verify.py
python3.12 -B scripts/research_package.py --package research/selected-runtime-guard-stock
```

The primary checker authenticates 23 live input files before importing its fixed
12-module predecessor closure. It executes the unchanged tape-based
`fresh_rows.quotient` and `Count.divide_small` on three depth-two cases:

- Dimension 64, all 28,416 live families, actual `|GL64(F3)|`, w=1, Q=9475.
- Two dimension-2 GL2(F3) controls with w=1 and w=2, including nontrivial high
  matrix fibers.

Each rejects omission of Q, one missing packet level and an incomplete row
count. **These are quotient/guard probes, not full NODE or payload execution.**
The q=3 case is outside the selected large-prime supplier domain; the all-domain
stock theorem is the algebraic proof above. The checker also verifies 16,730
small exact divisor decisions, 349,504 child-depth checks and 32 inverse-depth
boundaries. It compares the required stored [RESULT.json](RESULT.json), never
repairs it, and writes only with explicit `--emit-to NEW_PATH`, refusing overwrite.

The separate checker imports neither the primary nor its receipt. It checks
315 LCM-derived contracts, all 8,640 rows of a three-level Cartesian codec with
pointwise inverse, and the old-format boundary through depth eight. These finite
checks corroborate the proof; they do not extrapolate it. Eleven behavioral
tests exercise normal contracts and the optimized public CLI, including
executable-source, manifest, receipt and emission failures.

[VALIDATION.md](VALIDATION.md) records the observed commands and environment.
No full selected cold replay, selected GL64 payload, complete physical compiler,
formal-kernel proof, independent human review or hosted CI pass is claimed.

## Open next questions

1. Can the ordinary backend select this smaller stock while retaining its
   complete input contract? Trace its actual selector and one complete return
   with `R=9475*b^D`. This could reduce borrowing capacity, but the pending
   PR2753/2809 refinement obligations and every physical-format consumer must
   still be checked. This package does not patch that selector.
2. Which outer consumer genuinely requires both full depth-D formats? Locate a
   concrete P-based divisibility check rather than assuming the local NODE
   guard implies it. A consumer requiring the old promise needs its original
   reserve or a separately justified adapter.

These questions are structured in [TASK.json](TASK.json). The family expansion
decision is **narrow**: retain this stock lemma, do not start another supplier
construction or optimization campaign from it without a complete boundary and
cost ledger.

## Credit and implementation constraints

David Arias supplied PR2753's all-size logical caller. Jose Manuel supplied
PR2195/2234's compatible stock and PR2809's fixed-role implementation. Ross
Richardson supplied PR2420's live-only stock and exact dual-format gate. Nick
Petalas supplied PR2120's earlier depth certificate; Adam Gall supplied PR2084's
conditional parent reserve. PR3223 supplies the adjacent NODE audit. Retain
DreamingOfClouds/PR589, eumemic/PR555/source527, Rohan Arun/PR1094, Jeremy Kothe's
assembly work and the full predecessor lineage in the pinned PR2234 notice.
The new contribution is the later runtime's one-factor compatibility induction
and its literal guard checks, not those predecessor results. Nick Petalas.
New work follows Apache-2.0. No predecessor notice or source is changed.

The verifier is bounded research software, not a fixed-memory tape algorithm.
Power-of-Ten rule 3 has a managed-runtime deviation: Python integers and test
objects allocate dynamically. Explicit domains bound widths to 256 bits,
model depth to 64, the literal probes to depth two and q=3, source files to
1 MB each and source inventory to 32 files. The unmodified predecessor's loops
are outside this patch; probe inputs bound their tape lengths to 13,026 bits
and modulus width to five bits. Rule 9 has a fixed-import substitution-boundary
deviation: only 12 source-authenticated predecessor modules are imported and
their actual paths are checked. A fresh private bytecode namespace prevents
cached code from replacing authenticated source. Reassess these limits before
expanding the fixtures; no framework, recursion or unbounded search is added.
