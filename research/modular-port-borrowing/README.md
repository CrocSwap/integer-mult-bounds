# Exact modular echoes with 56-bit data registers

**Recursive-interface construction; no new kappa.** This supplies an explicit
modular backend for PR1057's borrowed-port echo. Integer matrix factors act
on fixed-width residues modulo `2^w`. Every dirty array is restored bit for
bit, and the final integer answer is recovered from a bound on the input
and final output. Large unreduced intermediate integers need not fit the
data registers.

The 52-factor fixture retains **1,376 complete leaf calls and three dirty
length-two arrays**, with **56-bit data**. PR1057's sufficient integer-prefix
allowance is **114 bits** when every entry value has magnitude at most seven,
or **167 bits** when the dirty entries range over all signed 56-bit values.
Those are sufficient allowances, not proven minimum integer widths. In the
retained full-dirt fixture, the actual integer lift reaches **90 signed bits**
while the modular execution and every recursive return remain exact.

| Resource, 52-factor fixture | Integer backend, entry bound 7 | Modular backend |
|---|---:|---:|
| Complete leaf calls | 1,376 | 1,376 |
| Common data width | 114 sufficient bits | 56 bits |
| Five length-two data arrays | 1,140 bits | 560 bits |
| Dense coefficient table | 23,712 bits | 11,648 residue bits |
| Four private scalar registers | 456 bits | 283 bits |
| Unrolled leaf-record storage | 17,888 bits | 17,888 bits |
| Executed scalar/access commands, including startup | 38,532 | **52,292** |
| Explicit modular reductions within those commands | 0 | **13,760** |

The modular leaf pays **38 commands instead of 28** for dimension two.
Its product register has 112 bits; all four private widths and their clearing
are charged. Coefficient/input conversion, final decoding, original input
storage, address/control routines and any physical supplier adapter remain
explicit setup or backend costs. The table is a model invoice, not measured
Python memory or a runtime speedup. [PROOF.md](PROOF.md) gives the complete
recurrence and price, including these terms.

## Reproduce

Python 3.10+ and the standard library, from any working directory:

```sh
python3 -I -B research/modular-port-borrowing/verify.py
python3 -I -B research/modular-port-borrowing/test_package.py -v
```

Expected final marker:

```text
PASS_MODULAR_PORT_BORROWING: 52 factors; 1376 calls; 56-bit data; 5280 matrix cases; 33280 scalar states; 144 dense cases; paid reductions; no new kappa
```

The first command regenerates the entire case, literal primitive program and
certificate. `--receipt NEW_FILE` retains its deterministic receipt; an
existing file is refused. It also runs under `-O` and from a relocated,
read-only package. No repository imports, native compiler, solver or network
are required.

Evidence includes **5,280 exact matrix-map cases**: all **861 ordered
binary/ternary trees through seven factors**, both signs at widths 1, 2 and
5, then the pinned parent's chosen plans for every size 8 through 64 in
both directions. Independent control-stack and matrix implementations check
**528,302 leaf prefixes and 667,416 recursive returns**, including children
temporarily borrowing ancestor ports. Each matrix case covers all ten data
columns, hence all residue inputs for those instantiated factors.

The literal scalar backend also exhausts **33,280 complete cases**: every
coefficient tuple and all five-array states for binary scalar echoes modulo
four and ternary scalar echoes modulo two, in both directions. These execute
**2,160,640 scalar/access commands**. Another **144** dense cases vary
dimension, signs, zero factors and width, with independent endpoint and
complete address invoices. Four main fixtures compare every leaf with its
unbounded integer lift and execute the literal inverse.

**19 mathematical/admission controls** cover lost restoration, insufficient
recovery width, signed-bound equality, unrepresentable input after a zero
product, rounded coefficients, missing reductions, private clearing,
aliasing, inverse order, undercharging and actual integer-prefix overflow.
**12 package tests** cover artifact/source corruption and portable encoding.
For example, a correct modulo-16 endpoint with residue 12 decodes to −4,
not the true integer 12, when the recovery guard is omitted. Saturating
arithmetic corrupts a helper; division by two fails to define a map on the
chosen quotient. These operations cannot replace the specified modular leaf.

## Sources and scope

Base **ba82555c64e1879e4b7decce28186f208fcb8262** selects conditional PR1042,
kappa `1672188119205421 / 10^18`, with PR589 still the bit supplier.
BASE-SELECTION.json freezes that context. The exact pending PR1057 source is
**78a062df1dcab2bffea5ff4d8243f3da6e465414**. Five files are vendored
unchanged; SOURCES.json gives their Git blobs and SHA-256 hashes, plus the
selected-context pin. The existing emitter and planner are reused with
credit; this pass does not claim a new borrowing identity or tree optimum.

The algebraic identity already holds for additive endomorphisms of an
abelian group, including finite residue groups. This contribution supplies
its concrete bounded-register realization, exact recovery condition, paid
reduction/access invoice and independent prefix/return evidence. The written
argument applies to every finite ordered binary/ternary tree of **integer
linear factors**. The finite tests support that proof; they are not a formal
verification of the full multiplication theorem.

The external source remains read-only at every prefix. Internal source
ports are restored on return; their values are opaque residues inside the
recursion. No internal signed decode or numerical rounding is allowed.
Rounded, irrational and general dyadic factors need another interface.
The Python interpreter checks capacities of the specified register machine;
its own host allocations are not the stated data-space bound. Physical
fixed-tape implementation, supplier placement, frame/source-access adapters,
common-label realization, hosting and outer analytic transfer remain open.
The unchanged call multiplicities retain the direct all-role obstruction.

Assignment seed **52** selects the primary size and seeded fixtures. The
domain and stopping rule are in CLAIM.json; no search or restart is used.
PR1103's rectangular batching changes restoration multiplicities, and
PR1108's compact-control return obstruction is a different interface.
PR835 uses modular reconstruction to verify a historical complex word; it
does not implement this borrowed-port backend. Their distinct evidence is
credited, with no claim of priority for modular arithmetic.

The final overlap check also found **Ali Romman's PR1135**, which studies
rounded borrowing contracts and a common-denominator rational lift. Its
Section 7 retains numerator headroom and a `q^D` coarse-lattice embedding.
The present integer-factor backend uses quotient residues throughout the
recursion; it does not remove that lift's denominator costs or solve the
rounded-leaf obstruction. Upstream advanced during publication to selected
PR1094 at `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`; the experimental base
and frozen context above are retained.

Prepared by **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance**. Credit PR1057, **shhxera PR822**, **androolloyd PR673**, **Sagar
Thakrar PR730**, **Chafik Boukhalfa PR628**, the classical Ben-Or–Cleve
constant-register principle, and retained predecessor notices. New material
is Apache-2.0. See NOTICE.md and VALIDATION.md.
