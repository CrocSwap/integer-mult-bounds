# Guarded packed differences preserve Newton membership

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algorithm-preservation proof. Ali Romman's PR5374 supplies
bounded residues and Clear1nsight's PR3382 supplies the Gaussian Newton lattice.
Those mathematical predicates are premises, not new results here.

## Contract

Let `N=2^r`, `0<=r<=9`, and let `values` be a list of N Gaussian-integer
pairs with absolute component bit lengths at most 8192. Set `b=ceil(r/2)`
and `M=2^b`. The reference computes the Boolean difference coefficients,
modulo M in each component, and returns the first mask failing its existing
power-of-1+i divisibility test. The new implementation returns exactly the
same tuple `(mask, real_residue, imaginary_residue, b)`, or None. It preserves
the input. This includes negative components, r=0 and every value in the
stated domain. It rejects malformed inputs and inputs outside that domain.
It does not claim the reference's unbounded-rank API outside this domain.

## Lane arithmetic

Store real and imaginary residues as separate base-256 digits, in that
order at each mask. Each digit is in `[0,M-1]`, and `M<=32`. At a stage
for address bit k, select the upper masks, whose k-th bit is one. Let U
be the packed word restricted to their low b bits. Let L be the low b
bits of the corresponding lower masks, shifted by `16*2^k` bits into
the upper positions. Let G have digit 128 in each selected component lane
and digit zero elsewhere. Then one integer subtraction

    D = (U | G) - L

has the intended independent digit values `128+u-l` at selected lanes and
zero elsewhere. Every selected digit is between 97 and 159, so no digit
borrows from another or carries into another. Unselected digits subtract
zero from zero. This is an equality in base 256, proved by independent
nonnegative digit differences. Masking D to the low b bits in selected lanes
therefore yields `(u-l) mod M`. The discarded guard has zero residue modulo
M. The lower lanes are copied unchanged from the previous word.

`lower = upper >> shift` in the public plan selects precisely the lower
partner lanes. The implementation masks the word before shifting, which
keeps even intermediate positive integers within 16N bits. The shift never
moves a real digit into an imaginary digit or a different Boolean pair.

This guard is necessary for the simple packed-subtraction scheme.
Without it, two destination bytes 0 minus two source bytes 1 give low-five-bit
residues `0x1e1f`, rather than the desired `0x1f1f`. With guards the masked
result is `((0x8080-0x0101)&0x1f1f)=0x1f1f`.

## Stage induction and certificate

The invariant after each processed address bit is equality, in every real
and imaginary component, with the reference partial Boolean difference
transform modulo M. Packing establishes it before the first stage. The lane
lemma proves one simultaneous stage, so induction proves every final
coefficient. It holds for all inputs in the domain, rather than only for the
finite fixtures.

The unpacking uses the same increasing mask order and the same existing
divisibility predicate as PR5374. Equal complete coefficient arrays therefore
produce the same first failing mask, both identical residues and the same b.
For r=0 there are no stages, residues are zero modulo 1 and every valid
Gaussian input is accepted. All work uses newly allocated local objects;
none writes into the input list or its tuples.

## Exact work and bounds

The reference uses rN modular component subtractions. The packed transform
uses r packed integer subtractions, plus its masks, shifts, packing,
unpacking, validation and existing divisibility tests. At rank nine these
counts are 4608 and 9. These are different operation alphabets; their ratio
is not a bit-complexity or runtime speedup. The packed word has at most
16N bits, hence 8192 bits at rank nine, including unused and guard bits.
The private residue byte array has 2N bytes, hence 1024 bytes at rank nine.
The plan is immutable and depends only on rank and mask positions. No
coefficient, verdict, receipt or scientific result is cached.

Packing and unpacking each scan N pairs; each transform stage operates on
O(N) machine bits. Input type checks and the 8192-bit limit run on every
call. Precomputed public plans for ranks zero through nine are built once
at module import. This cost is outside steady API timing and inside the
fresh-process end-to-end timing. Python object overhead, integer allocation
and physical tape costs are additional. No fixed-allocation or paid physical
scan bound follows from the bit counts.

## Verification and limits

The executable checker exhausts guarded subtraction on all residue digit
pairs for b=1 through 5, checks every small binary Gaussian array through
rank two and all rank-three real arrays over residues 0 through 3, compares
complete first-failure tuples and preserves inputs. A separate subset-sum
definition checks complete transformed arrays, including signed rank-nine
fixtures. Boundary and source-drift controls reject.

An opt-in adapter runs the complete original PR5374 scientific replay with
only its member/obstruction globals replaced by this implementation. Its
independent source decoder, subset oracle, literal collector, source hashes,
rejection controls and recorded output comparison remain executed. The old
receipt's `rank9_modular_subtractions=4608` describes the original reference
algorithm, not instrumentation of the substituted transform. New operation
counts are reported separately. This is a preservation check for the new
implementation, not a scientific re-review of the predecessor result.

No lattice theorem, sharp residue modulus, decoder, producer admission,
physical caller, native frame operation, owned erasure, precision/tape,
compiler or multiplication theorem is proved here. Selected kappa and all
five framework assumptions retain their status. No proof assistant or
independent human review is claimed.
