# Sharp integral-prefix scale for the positive native C tensor

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration.
No new kappa or selected-frontier change is claimed.

For `C=[[1+i,1-i],[1-i,1+i]]/2`, suppose both x and `C^(tensor f) x`
are Gaussian-integer arrays. The least common binary input scale making
every axis prefix integral is exactly

```text
2^ceil(floor(f/2)/2).
```

More precisely, at any cut with j processed axes, the sharp Gaussian
denominator exponent is `min(j,f-j)`, in units of `pi=1+i`. The sharp
binary scale at that cut is `2^ceil(min(j,f-j)/2)`. This covers every
subset of axes and therefore every fixed axis order. It allows arbitrary
Gaussian-integer inputs satisfying the final-output promise, with arbitrary
spectator fibres.

[PROOF.md](PROOF.md) proves the all-f statement. From the input, the cut
has at most j Gaussian denominator factors. From the integral output, its
inverse suffix has at most f-j. Paired-coordinate integer inputs attain
the smaller exponent at every cut.

## What changes

Jerry Chen / CubeJerry's [PR7429](https://github.com/CrocSwap/integer-mult-bounds/pull/7429)
implements this tensor as the positive rank-one central leaf of selected
MOVE24472. It requires integral, width-fitting outputs at every axis and
already gives an f=2 example with integral endpoints but a nonintegral
intermediate. That example and the implementation are credited prior work.

The new arithmetic bridge is to multiply an endpoint-promised input by the
sharp scale, run the ordinary axes with exact divisions, and divide the
completed output by the same scale. Every intermediate axis output is
integral and the original mathematical output is returned exactly.

The unrestricted-input reserve `ceil(f/2)` is established prior work,
retained in Jose Manuel / jmbarrancoml's [PR3091](https://github.com/CrocSwap/integer-mult-bounds/pull/3091)
and credited there to Alejandro Zarzuelo Urdiales. The smaller exponent
here uses an additional endpoint promise. Clear1nsight's
[PR3382](https://github.com/CrocSwap/integer-mult-bounds/pull/3382) characterizes
the different entrance where all partial products are already integral.
Neither predecessor theorem nor executable is audited or replayed here.

## Exact finite evidence

The standard-library checker imports no predecessor code. It checks:

- 164 sharp cut witnesses, covering every axis subset through f=6 and
  every prefix cut for f=7 through 10. Each also executes the complete
  scaled arithmetic program and exact final division.
- All 65,808 Gaussian arrays with real and imaginary components in `{0,1}`
  for f=1,2,3. Exactly 968 have integral final outputs; all their 3,792
  checked prefixes satisfy both denominator bounds. The other 64,840
  inputs are outside the promised endpoint domain.
- 180 signed complex prefixes checked against a separately coded rational
  butterfly, with direct tensor-entry comparisons through f=4.
- All 153 axis permutations at f=1 through 5 on the paired witnesses.
- Eight named semantic controls, including a scale one bit too small at
  f=6, a missing endpoint promise, inexact divisions, inverse-phase
  confusion and a signed complex dirty offset.

Finite checks corroborate the written proof. They do not enumerate the
unbounded input lattice. Every acceptance check remains active under `-O`.
The verifier writes nothing and prints a generated receipt containing the
results, Python version and SHA256 of every package file. No receipt is
hand-written or checked in.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/native-c-endpoint-prefix-scale/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/native-c-endpoint-prefix-scale/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/native-c-endpoint-prefix-scale
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/native-c-endpoint-prefix-scale --check-source-history
```

Substitute any installed CPython 3.12 path on another host. Expected markers
are `PASS_NATIVE_C_ENDPOINT_PREFIX_SCALE`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and, after committing, `PASS_RESEARCH_COMMIT_BYTES`. The standalone verifier
also works in a Git-free package copy. Each registered command has a
120-second cap. Normal and optimized direct runs take less than a second
locally; these are check durations, not physical performance measurements.

## Scope and source boundary

The claim is a new numerical interface theorem for a stated tensor, with
no changed supplier word. It does not establish that a production caller
supplies the endpoint promise. Signed range, scratch width, physical
scaling/unscaling, ownership, tape movement, compiler closure, stock and
the complete paid/productive invoice remain separate obligations. All five
selected framework assumptions remain. No native machine, selected cold
replay, Lean, Docker or complete multiplication theorem is run or claimed.
Independent human and formal proof-kernel review are unclaimed.

The base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`,
priority revision 8, selected #7000. [TASK.json](TASK.json) records the
explicit change from the formal-interface card to this written arithmetic
proof. [SOURCES.json](SOURCES.json) pins canonical provenance only. The
definition and proof are self-contained, with no external executable or
data inputs. TASK also records #7429's exact head, README path and the SHA256
of the source text inspected. That external document is provenance, not a
registered replay dependency or an asserted independently certified input.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19571939).
Live claims, the account's recent contributions, the main-tree READMEs and
merged PRs were checked for the formula, tensor, endpoint promise and more
general partial-product forms. The overlap snapshot reported complete
pagination of 760 open PRs and 7,346 Discussion records, without warnings.
No same-scope result was found in that coverage. Arbitrary unpublished work
and unsearched diffs remain outside it.

Power of Ten inspection found no recursion, dynamic evaluation, subprocesses
or writes in the verifier. All arithmetic domains are fixed: f is at most
10, arrays have at most 1,024 entries, and the exhaustive loop has at most
65,536 cases at one f. Every function is under 60 physical lines. All gates
use exact integers or Fractions and explicit failure checks. Receipt hashing
caps the inventory at twelve files and each file at 1 MiB. Managed Python
allocation is a deviation from fixed steady-state allocation; the fixed
domains bound live collections, but runtime allocation internals are not
measured. Warning-strict normal and optimized execution supplies the available
diagnostics; no separate static analyzer or native fixed-allocation version
is supplied.

## Open next questions

Can the sharp scale be installed around one literal positive C leaf with
a favorable complete physical bill? First supply an actual producer with
the required endpoint promise, bound every scaled intermediate magnitude,
and price both exact conversions together with movement, owners and retained
history. Those missing contracts prevent a supplier or kappa claim. This
package stops at the first sharp arithmetic result and reserves no follow-up.

## Credit

The new proof, matching all-cut witnesses and checker were produced by
Nick Petalas. Jerry Chen / CubeJerry supplies PR7429's literal leaf and its
explicit integrality boundary. Jose Manuel / jmbarrancoml supplies PR3091's
physical axis method, retaining Alejandro Zarzuelo Urdiales's C/parity and
tensor-reserve credit. Clear1nsight supplies PR3382's maximal simultaneous
exactness lattice. The selected native, Gaussian, controller and physical
lineage retains its predecessor credit. Fractional-ideal arithmetic and
tensor-product identities are classical; no literature-wide priority is
claimed for those methods.
