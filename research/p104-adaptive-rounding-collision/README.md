# Adaptive relative accuracy still loses P104 cleanup information

The proven-relative adaptive rounded kernel can lose **256 independent input
bits** at the first physical P104 private collector. Its returned field and
working grid are identical on a family of `2^256` distinct entrance arrays.
Even retaining all seven diagnostic squared-defect totals leaves a collision
class of `binomial(256,128)` inputs, requiring at least **252 further bits**
to distinguish for exact inversion.

This is a local information and cleanup obstruction for a specified numerical
implementation. It does not contradict the exact native inverse, the relative
error theorem, or conditional absolute-grid recovery. No supplier or kappa
improvement follows. Current fixed-profile consumer obstructions remain.

## Exact object and contribution

Use ywz65's [PR2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586),
head `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`: events 2025--2039 of the
5,398-event physical dual, with rank-seven native calls at events 2031/2033.
Allocate zero C, gather D31 through D27, transport by U, add C into Q7,
transport by its exact inverse V, subtract the unchanged D fields and erase C.
Only this fifteen-event cut is executed; it is not a full rounded caller.

[PR2665](../p104-rounded-collector/README.md) already gives a same-grid
completed-child counterexample, but checks its relative contract only on that
execution. [PR2891](../p104-rounded-native-child/README.md) implements the
adaptive, universally relative-correct stage kernel for two *different*
retimed transports and deliberately retains the output grid. We reuse that
authenticated arithmetic unchanged on this collector's actual two recipes.
The delta is the adaptive collision, its history bound, and literal cleanup
failure. Neither the perturbation lemma nor rounding's general loss of
injectivity is claimed as new.

The [mixed-grid collector](../p104-mixed-grid-collector/README.md) already
achieves all-input exact cleanup with four extra fractional bits when the
native operation is exact internally and only its completed output is
quantized. That positive result stays valid. Here every binary stage is
rounded, and the precision policy is chosen for relative accuracy; this
audit quantifies its lost information rather than claiming mixed precision
cannot restore the collector.

Scientific base: canonical main `b3f3ee0392b71b118fd086a6eaf6b4cab54ef455`,
priority revision 5. [SOURCES.json](SOURCES.json) pins the actual word, native
archive, arithmetic and attribution-bearing READMEs. Frozen sources stay
unchanged. [TASK.json](TASK.json) records the changed numerical side scope,
live overlap, bounded stopping decision and remaining costs.
The final checkpoint is main `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`,
priority revision 6; its guidance was read and consumed inputs were unchanged.

## Collision and literal residual

Represent arrays by Gaussian integers times `2^-f`, with integers `b,f>=0`.
For rank seven on 512 addresses, PR2891's policy sets

```
h = floor(log2 M) - f,
F = max(f, b+7-h),
```

where M is the largest absolute integer component. Every binary C butterfly
is rounded to nearest even on grid F. The two Gaussian monomial wrappers
are exact and no final downcast is made. Let R be U's entrance monomial,
`e=R^-1 delta_0`; for this exact recipe **e = -i delta_247**. Set

```
A  = 2^(b+7),
x0 = A e 2^-f,
x1 = (A+1) e 2^-f.
```

Both inputs have the same bit-length scale and select F=f. After R, the
first C butterfly sends a real amplitude a at address zero to four real
components `(a/2,a/2,a/2,-a/2)`. Since A/2 is even, all four ties for A+1
round to the A case. Every subsequent operation therefore has the same
state. The A case is exact through all seven stages because A is divisible
by `2^7`. Thus the complete returned field and F coincide exactly.

Its maximum component is `A/16`, so the adaptive return chooses F=f+4,
retains that finer grid, and executes exactly. With D31=x1 and the other
gather fields zero, the literal collector leaves

```
C before erase = x0-x1 = -e 2^-f = +i 2^-f delta_247.
```

With D31=x0, cleanup is exactly zero and Q7 receives the same output as in
the x1 case. D fields are unchanged. Strict-zero erasure consequently rejects
the x1 execution. The outbound defect has Hilbert norm `2^-f`; the return
defect is zero. In particular
`2^-f <= 2^-b (A+1) 2^-f`, so both local relative contracts hold.

The relative contract also holds **for every Gaussian-dyadic input**, not
just these fixtures. The credited unitary perturbation argument gives at most
`7 sqrt(512/2) 2^-F = 112*2^-F` completed Hilbert defect. The policy uses the
safe guard 128 and exactly embeds the entrance. This proves the claimed
`2^-b ||input||_2` bound, including zero, for these unitary recipes. Native
unitarity and their canonical-frame interpretation remain inherited.

## A quantitative history requirement

For each of the 256 first-stage pairs, independently choose `z_j in {0,1}`,
put real numerator `A+z_j` at child address 2j and zero at 2j+1, then pull
the entire vector back through R. All choices have the same scale and F=f.
The preceding four-component calculation applies independently to every
pair. After the first stage the complete state is independent of all z_j,
so the final returned field and grid agree for all `2^256` inputs.

An exact deterministic inverse receiving only that field, grid and fixed
precision/recipe parameters cannot recover every entrance. If it also
receives a fixed B-bit history, injectivity requires `2^B>=2^256`, hence
B>=256. This is a worst-case information bound for the stated interface,
not a count of physical registers or proof that every reversible algorithm
must allocate 256 additional bits simultaneously.

PR2891's executable additionally returns diagnostic defect totals, which its
README excludes from the execution kernel's priced operations. We do not
silently discard their possible information: the first total is
`4*sum z_j`, and all later totals are zero. Restricting to weight 128 leaves
the same field, grid **and all diagnostics** for `binomial(256,128)` inputs.
Exact integer comparison gives

```
2^251 < binomial(256,128) <= 2^252.
```

Thus at least 252 further binary history bits are necessary even given those
seven diagnostics. This conditions on a fixed retained transcript; other
input-derived metadata is additional history and must be counted too.
Supplying retained source fields to a new corrective operation changes the
interface. The original unchanged-source subtractions alone do not repair it.

Increasing the requested precision by seven bits restores the fixed sparse
fixture exactly. Rechoosing A for the increased b produces another collision.
This does not exclude choosing precision from an *absolute* magnitude and
grid bound, the [PR2878 recovery premise](../p104-retimed-error-recovery/README.md),
source-assisted cleanup, reversible rounding/history, or a priced reset.

## Evidence and reproduction

Python 3.12 or later, standard library, from the repository root:

```sh
python3 -I -O -B research/p104-adaptive-rounding-collision/verify.py
python3 -I -O -B research/p104-adaptive-rounding-collision/test_verify.py
python3 scripts/research_package.py --package research/p104-adaptive-rounding-collision
```

The read-only verifier authenticates all inputs before compiling the one
arithmetic module directly from checked bytes. It checks all 512 exact
outbound and inverse basis columns, with a separate closed tensor-convolution
oracle for outbound columns and completed defects. Fifteen sparse fixtures
use b=0,1,8,64,256 and f=0,19,300. Four dense fixtures check collisions even
with retained diagnostics, relative defects and literal cleanup. The argument
above, rather than enumeration of exponentially many inputs, proves the
all-b/f and collision-class statements. [RESULT.json](RESULT.json) is compared
in full with type-sensitive equality.

Controls include a separate Fraction first-butterfly calculation, strict
erase rejection, finer-policy exact cleanup, wrong native phase and cleanup,
misbound occurrence, invalid relative defect, executable/source/typed receipt
drift, duplicate keys, occupied output and read-only optimized Git-free export.
`--write-result NEW_PATH` creates a separate receipt exclusively.

Local validation passed on Windows AMD64 with CPython 3.12.14: registered
replay, source pins and all nine behavioral groups. The sandbox's default
temporary-cache directory denied cleanup; rerunning with a writable workspace
TMPDIR passed without changing checks. Warning-as-error source compilation
passes; Ruff is unavailable. Hosted CI is separate.

This is author-checked evidence from separate algorithms by the same assistant,
not independent human or formal-kernel review. Full native ancestry, a complete
rounded word, recursive implementation costs, physical owners, recovery scans,
precision/tape admission, all-size lowering and selected cold replay are unrun.
The written pigeonhole argument is not a formal memory-complexity theorem for
arbitrary implementations with different access or reversible interfaces.

## Open next questions

Can a reversible rounded collector retain and uncompute sufficient rounding
history within a viable complete cost? Start with these two literal calls and
retain their first-stage rounding residues, then specify how those bits and
the private field are restored or disposed of. That would change the proved
failure boundary. A priced state lifecycle and viable consumer are blockers;
the existing fixed-profile cost exclusions prevent inferring construction
expansion from a local cleanup improvement. This audit stops here.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance in research, mathematics,
implementation, checking and writing. New work is Apache-2.0.

Credit ywz65/PR2586 for the word and physical recipes; Arham Tahir/PR2665 for
the earlier deterministic collector example and PR2891 for the unchanged
adaptive kernel; Nick Petalas/PR2771 for the block-scale/perturbation lemma;
PR2878 for conditional recovery. Retain commdata2338/PR2662, Vasek/flyingviper,
Ross Richardson, Nick Petalas, Rohan Arun/PR1972, Chafik Boukhalfa/PR1991,
Adam Gall/PR1940, Josie Elliston/PR1071, Ali Romman/PR1125/1862, icekylinx and
the full geometry/native/compiler lineage in the pinned predecessor READMEs.
