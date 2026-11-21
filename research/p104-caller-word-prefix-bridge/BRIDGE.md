# #7113 caller-word and native-contact bridge: local exact check

This is an independent finite arithmetic check and a concrete-data handoff.
It does **not** claim a kernel-checked `CallerWord.Legal` instance. No Lean
compiler was available on PATH and `Caller7113Concrete.lean` was not compiled.

The sources are #7113 at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, #7852
at `41beda1d6435760dc99e38bd7e65f36798aad212`, and #7829 at
`1fdc9ecd1b1311d8ea6e02b6f81ae0d8d24999e2`. The accompanying
`NORMALIZED.json`, `check.py`, pins, notices and receipt are the public witness
from #7864 at `4cc3d68b2e114b17d7b4096c2012dd783da221f4`, archive SHA-256
`c272074680819ef0ea05eb30c5231bd13186b9d69cabfa2999f326cf64edb1ab`.
The #7113 caller itself has SHA-256
`255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.
The #7112 native word used below has canonical JSON SHA-256
`3454c4900245ed1814ceeff79a741a45160eb3a93cf8d15f891fe2a67ba036fc`.

## What was checked

`bridge.py` implements new sparse row arithmetic without importing the
upstream caller polynomial evaluator. It evaluates in

`Q[i,q,D0,...,D16] / (i² + 1, q⁴ - 1)`.

In particular, `q` is independent of `i`; neither `q² = 1` nor `q = i` is
assumed. Every `D` has an unrestricted nonnegative exponent, represented by a
17-entry tuple, so stages are not collapsed to idempotent bits. A coefficient
is a pair of exact Python `Fraction` values. Monic reduction supplies the
unique basis `i^b q^a D^e`, with `b < 2` and `a < 4`. Thus an equality in
this quotient has a well-defined evaluation into each commutative rational
algebra for any `q` and `i` satisfying the displayed relations and arbitrary
choices of the 17 stage values. This is the mathematical bridge to the
universal quantifier in `CallerWord.Legal`; the Python implementation and its
connection to Lean still require formal verification.

Two separate dispatchers compute (1) the original source-record row equations
and (2) the `Ev`-constructor row equations specified by #7852 `evMat`. They
share the exact coefficient-ring arithmetic. At **each of 4,783 ordered
source-record boundaries**, both type-local matrices agree, and the expanded
constructor sequences agree exactly with #7864's normalized witness: 1,008 A
events and 3,911 B events. All 72 original endpoint rows agree with their
declared diagonal targets. This is not merely evaluation at numeric values.

Source stages and role namespaces are bound explicitly: source stage
`j ∈ {1,...,17}` becomes `Fin 17` index `j-1`, A global role IDs remain
unchanged, and B global role IDs are reduced by 36. For a J record
`[j,[x,y,u,v],[s,t,a,b]]`, the source equations read, from the *old* rows,

```text
A: x' = D[j-1] x;     y' = D[j-1] (y + q³ x)
   u' = D[j-1] (u + α₂ q v);  v' = D[j-1] v
B: s' = D[j-1] (s + a q t)
   t' = D[j-1] (b q³ s + (1+ab)t).
```

For all 17 source J records the A owners are pairwise distinct and the B pair
is distinct. With that condition, #7852's `jA` two HOSTs followed by four
idles, and `jB` one simultaneous HOST followed by two idles, implement these
equations. Ordinary ADD, SCALE, SWAP, QUERY, LAMBDA, IDLE_ONE and IDLE_ODD
are checked as individual constructors. Every target zero flag is zero.

`CONTACTS.json` gives the exact physical input assignment for all 17 × 104 =
1,768 stage/port tuples. Each row records the source-event position, stage,
native port and native direction, native X/Y field IDs and their **global**
caller roles; A also records the native X2/Y2 field IDs and roles. It is built
from the native's `live`, `ports`, `Dports`, `X2` and `Y2` fields and the
caller J operands. The check compares both initial and final frames of the two
A planes, verifies the exact 96/8 A/B partition, native hosted constants and
the caller's `α₂`, and verifies owner distinctness. The 1,768 rows include
1,632 A and 136 B port/stage tuples. At the first stage and port 0, for
example, native `(x,y,x2,y2) = (0,112,772,882)` maps to caller global roles
`(1,0,18,19)`; the source J is event 43 (zero-based).
The native direction is an integer-encoded binary vector; it is distinct from
the formal phase indeterminate called `q` in the coefficient ring.

The script separately reverse-propagates exact rational linear forms through
all 72,143 native instructions and compares the resulting transpose to the
full intended map on all 1,484 public fields: no rows differ. This calculation
treats a MOVE as the identity in chart-conjugated scalar coordinates; it is
not a proof of frame validity, phase geometry, or the complete fixed-tape
application. The predecessor receipt reports an independent physical checker
for the same #7112 native and its own premises; that check was not rerun by
`bridge.py`. This native is **not** the separate t7669 native used by #7829's
invoice.

## Distinct wrong-role control

Change only the first J's A owners `[1,0,18,19]` to `[2,0,18,19]`. All four
remain distinct, so the no-alias/WF test alone accepts the roles. #7829's
`callerfacts.encode` and `callerfacts.invoice` give exactly the same values
for original and mutant. This equality concerns the price projection: the
source hashes differ and the unchanged pinned source manifest would reject
the mutated bytes.

The changed role alters exactly 96 contact tuples, one for each A port at the
first stage. At port 0, native X field 0 now maps to role 2 instead of role 1.
The changed source and the original have different exact prefix matrices at
event 43. A concrete coefficient is output role A0, input role A0, monomial
`q D0`: original `(1-i)/2`, mutant `0`. At the endpoint, A rows 0, 1 and 2
fail their target, while B has no bad rows. For another explicit witness, the
coefficient at A output 0/input 0 of `D1 D2 ... D16` is `0` in the original
and `(-1+i)/2` in the mutant. The tuple is nonzero in the independent quotient
ring. Thus this control catches a role error that is invisible to pricing and
is not an aliased HOST pair. It does not claim that the generic physical
checker would reject every distinct wrong owner on its own.

## Concrete data and remaining proof work

`Caller7113Concrete.lean` contains generated definitions of the two explicit
`CallerWord.CWord 36 17` values, the 17 literal J records, and 104 native-port
rows. The role operands, rational coefficients, phase exponents and stage sets
are all retained. It is intended as Lean source data, not as a compiled or
trusted certificate. The separate format-specific `check_lean_data.py` reads
the emitted constructor literals back and compares all 4,919 primitives and
72 masks with the normalized witness; it also reconstructs all 1,768 contacts
from the Lean J and native-port data. It is not a general Lean parser or a
Lean compilation. `CONTACTS.json` expands the stage/port assignment for
independent inspection. `BRIDGE-RESULT.json` gives exact control witnesses,
source pins, per-stage term counts, and data digests.

To close the formal gap, a Lean build must first compile the data against the
pinned #7852 `CallerWord` definitions. It must prove WF and either prove the
formal quotient-ring endpoint calculation by a kernel-checked reflection
procedure or supply another kernel-checked calculation. It must also prove
the evaluation homomorphism from that quotient into every algebra in `Legal`,
and connect the generated event/target/contact data to the intended source
records. A JSON/SHA-256 check in Python does not supply those theorems. The
native phase geometry and application obligations remain separate. No change in
κ or t7669 crossing is asserted.

## Reproduction

Use Python 3 with assertions enabled. This packet includes hash-pinned partial
source exports, and `python3 -B verify_packet.py` checks and replays them in a
temporary copy. See the packet `README.md` for that offline recipe and its
file-hash-only provenance limit. To use three full source checkouts at the
heads above instead, run in the directory containing this file:

```sh
sha256sum -c SHA256SUMS
ulimit -v 4194304
timeout 180s nice -n 19 python3 -B bridge.py \
  --pr7113 /path/to/7113 --pr7829 /path/to/7829 --pr7852 /path/to/7852
python3 -B check_lean_data.py
```

The script checks checkout heads and all predecessor source-file hashes before
reading the witness. For pinned source exports without `.git`, pass
`--allow-exports`; the result then explicitly records file-hash-only
verification. It writes `CONTACTS.json`, `Caller7113Concrete.lean`, and
`BRIDGE-RESULT.json` in this directory. The recorded run used one Python
process, a 4 GiB virtual-memory cap, and 180-second timeout; it completed in
43.81 s with 94,256 KiB peak RSS. Runtime is machine-dependent. Check the
compiler and mathlib version pinned by #7852 before any attempted Lean build.

The source authors and predecessor credits are retained in `NOTICE.md` and
their upstream packages. This local check uses those artifacts under the
accompanying Apache-2.0 license.
