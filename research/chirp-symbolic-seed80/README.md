# Independent symbolic check of PR479's chirp transition

**Independent verification; no new kappa.** The pinned `ChirpStream.advance`
preserves its quadratic state invariant in the checked symbolic branch patterns.
This package executes the actual PR479 transition on an independent sparse
integer-polynomial implementation. It adds source-linked coefficient identities
to Chafik Boukhalfa's existing numerical exact replay; it does not repeat or
replace that package's full verification.

```sh
python3 -B -I -O research/chirp-symbolic-seed80/verify.py
python3 -B -I -O research/chirp-symbolic-seed80/test_verify.py
```

Python 3.10+ and its standard library suffice. The first command recomputes and
compares the entire deterministic [EXPECTED.json](EXPECTED.json), printing:

```text
PASS_CHIRP_SYMBOLIC_INVARIANTS symbolic=27 identities=587 transitions=8605 controls=16
```

The second runs eight test groups. Reproduction needs no Git objects, network,
prebuilt artifact, numerical exponential, optimizer, or symbolic algebra library.
`--write /absolute/new/receipt.json` writes a fresh receipt without overwriting.

## What is independently checked

For each axis the promised state is

```text
value ≡ A*j², difference ≡ A*(2*j+1)  (mod Q), Q=2r,
phase ≡ sum(value) (mod Q).
```

The sparse-polynomial engine uses integer coefficients and monomials. The
production transition executes unchanged, with symbolic coefficients, radices
and indices supplied as its state. No predecessor `direct_phase`, test, or
algebra engine is called. Every difference between the resulting and expected
state polynomials must have **all coefficients exactly zero**.

There are 27 source executions: dimensions 1 through 6, each with every possible
length of the wrapped trailing suffix. They check 587 state equalities, including
untouched fields, plus branch guards, continuation, axis visits, wraps and
rewinds. These are not 587 independent theorems. Each polynomial identity is
universal in its integer variables under its stated guard; the **set of compound
control-flow patterns is finite**. [PROOF.md](PROOF.md) gives the elementary
arbitrary-dimension composition argument separately. Neither is a Lean proof.

The symbolic model intentionally checks congruence: reduction modulo the same
positive Q is erased in the polynomial lift. It cannot by itself certify
canonical residue representatives or constructor initialization. Exact integer
checks therefore compare every register and the continuation flag on **8,605
states in 129 boxes**, with **129 complete rollover transitions** and **21 wide
transitions**. Initial states and next addresses come from a direct quadratic
formula and mixed-radix rank/unrank, not the incremental algorithm. Distant
states are initialized directly; their enormous prefixes are not executed.

All **16 source mutations** have concrete state, accounting, or continuation
witnesses. Ten are also rejected symbolically. The other six deliberately show
the boundary: wrong initial sign, modulus, or difference; and omitted reductions
of phase, value, or difference. A wrong stored difference may leave the current
emitted phase correct, so the receipt calls these **state-invariant witnesses**,
not necessarily immediate output errors. Two algebraically equivalent source
rewrites pass both engines, including a closed-form replacement for the next
quadratic value.

One readable control replaces the phase increment Δ with A. At r=t=4,
s=1 and j=1, the next phase becomes 6 modulo 8 instead of the required 4.
The full pre-state and post-state are retained in the receipt.

## Fixed domain and stopping rule

- Assignment seed 80 was drawn from operating-system randomness. Candidate
  selection and overlap checks are recorded in [CLAIM.md](CLAIM.md).
- Small domain: r in {2,4,8}; dimensions 1..3; every radix tuple from
  {r/2,r} with radix at least 2. For r<=4, every admissible source tuple is
  checked. For r=8, the all-one tuple, maximal tuple, and one `Random(80)` tuple
  are checked after deduplication. Every coordinate in each resulting box is
  checked. The implementation's zero-axis edge is checked separately and is
  included in the reported 129 boxes; it is not an application dimension claim.
- Wide domain: r=2^80; dimensions 1,2,5,9; alternating full/half radices;
  source `s_i=(80+17i) mod (t_i-1)+1`; every wrapped-suffix length. These are
  21 single-step checks, not complete large streams.
- Stop after the fixed symbolic, small and wide domains, all 16 rejecting
  controls and both positive controls. No improvement search is performed.
- The period visit total is 10,752 for the small domain. It includes the final
  rollover and agrees with the independent prefix-product formula. This is
  instrumentation accounting, not a physical-tape benchmark.

## Pins, attribution and limits

Base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
PR479 head: `40dd01058439cdffae3e3b41c4fe52edaccf5f91`.
[SOURCES.json](SOURCES.json) binds five byte-identical predecessor files by
commit, repository path, Git blob and SHA-256. The original proof, source
manifest, license and notice are preserved in `vendor/`. That inherited manifest
lists further manuscript/outer-cost dependencies; those are **not replayed here**.

The fetched selected record is PR890's conditional
`kappa=1661957774647029/10^18`. This package changes no supplier, selected
certificate, production checker, `upstream/` file, or global generator. PR479
remains a pending research contribution, listed as unreviewed at this head in
the base ledger. This result corroborates only its local exact state transition.

The high-precision exponential, chirp/Fourier convolution identity, physical
fixed-tape implementation and total bit cost, outer assembly, all-size compiler,
realization, recursive hosting, precision/recovery and analytic transfer remain
outside this check. Constructor rejection of invalid inputs under optimized
Python is also outside scope; all supplied target inputs satisfy its domain.
No new exponent, full theorem formalization, or independent human review is
claimed. See [VALIDATION.md](VALIDATION.md) for actual executed checks.

Prepared by Ross Richardson (`RossRichardson`) with substantial OpenAI Codex
assistance in task selection, mathematical analysis, code, verification and
writing. Chafik Boukhalfa (`chafreaky`) authored PR479's stream, proof and prior
controls. The manuscript and retained analytic interfaces are credited to
Douglas Colkitt and the manuscript's contributors, including the cited Harvey
and van der Hoeven algorithms. The inherited outer accounting credits eumemic,
icekylinx and Zhihao Chen. The preserved predecessor notice remains authoritative
for its own files. This new package is Apache-2.0 under the repository license.
