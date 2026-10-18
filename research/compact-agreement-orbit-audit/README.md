# Integer-lift orbit audit of the compact agreement census

An independent integer-lift checker reproduces all **47 raw-agreement counts**
of Aaron Wang's PR1823 at head `5577d53f4bc093b5e9e960387ffc5d5bea55ee6f`:
**11,880,712 agreements out of 24,074,240 states**. It evaluates 276,224
representative states and retains the integer carry defect. Checking that
defect only modulo the observed width falsely admits **69,921
cell-representatives** across the 47 source cells. This diagnostic counts each
cell separately, so a representative reused at different rho values can
contribute more than once; the receipt records each cell's count.
This adds a proved reduction and separate evidence for the census, not a new
guard or an all-size classification of agreement states.

## Exact reduction, including arbitrary dirty target bits

Write the target as `y=2^rho Y+ell`, `0<=ell<2^rho`, and let
`q=(n+1)K-rho`, `L=(n-1)K+1`. All target increments in the source routine are
divisible by `2^rho`, so the low bits `ell` are preserved and cannot affect
the selected bits or temporary updates. Work on integer `Y` without reducing
it modulo `2^q`; temporary fields still use their exact packed modulus.
This gives the same selected bits as the literal modular routine because
`q>=L` and all observed target bits lie below `L`. This remains true for
negative intermediate integers: congruence modulo `2^q` preserves those bits.

If the initial quotient changes from `Y` to `Y+h*2^L`, every observed bit
stays fixed. Induction over the four updates therefore leaves temporary
trajectories fixed and translates every target by `h*2^L`. The ideal XOR of
bits below `L` has exactly the same translation covariance. Thus the integer
defect `D=Y_final-(Y_initial XOR mask)` and temporary restoration depend only
on `Y mod 2^L`. The argument composes for both earlier-source passes in the
later-source routine, including carries in its compact source-control field.

Consequently a representative is a raw agreement **iff** the temporaries
restore and `D=0 mod 2^q`. Each representative has `2^(q-L)` quotient lifts.
The unconstrained low target bits supply a further `2^rho` multiplicity if
counting the full target field rather than PR1823's normalized fiber. The
integer defect cannot be dropped or checked only modulo `2^L`.

A nonzero integer defect need not be a failure: it can wrap to zero modulo
`2^q`. In the late `(n,K,G)=(2,3,2)` histogram, six representatives have
`D=128`. These are valid agreements for `rho=2`, where `q=7`, but false
positives for `rho=1`, where `q=8`, if only the observed width `L=4` is checked.
The diagnostic therefore counts exactly those restored-temporary
representatives with `D=0 mod 2^L` and `D!=0 mod 2^q` for each source cell.

The proof holds for all positive `n,K,G` and `0<=rho<K` where the stated
packed routine is defined. It does not establish that a new guard admits
all agreements. Dirty back-field swap restoration and source-control
extraction retain their source contract; this checker audits target fibers.

## Evidence and reproduction

```
python -B research/compact-agreement-orbit-audit/verify.py
python -B scripts/research_package.py --package research/compact-agreement-orbit-audit
```

Python 3.12 standard library. No predecessor interpreter is imported.
The integer-lift engine computes raw-agreement counts for all 47 source cells.
A separate literal modular engine agrees on 16,384 complete small cases,
including all high and low target bits. An unload-sign mutation changes the
literal result, and omitting the carry defect falsely enlarges agreement.
A full-modulus wrap regression checks the six `D=128` representatives and a
literal two-pass witness, preventing valid wraparound from being called a
false positive.
`UPSTREAM.json` binds the unchanged PR1823 receipt and README by exact commit,
Git blob and SHA256. `SOURCES.json` binds the semantic note and guard context.
The sufficient-guard densities and minimal witnesses were not independently
recomputed here. Native execution, selected supplier admission, all-size
agreement characterization and a new kappa are not claimed.

## Open next questions

Can a finite-state transfer calculation produce the carry-defect distribution
symbolically for arbitrary n? Begin with a state carrying compact-field carry
and integer target defect, and prove its state bound before extrapolating.
This could turn the finite census into a uniform agreement characterization;
the missing state bound and wraparound proof are the blockers.

## Credit

Aaron Wang with opencode assistance supplied PR1823's census and exact domain.
The compact-control note, Hanson Sun's PR1247, Sagar Thakrar's PR1475,
PR1219 and the seed73/carry-repair audits retain their predecessor credit.
This audit was prepared by woklerx with substantial OpenAI Codex assistance.
Apache-2.0; no independent human review or full multiplication theorem.
