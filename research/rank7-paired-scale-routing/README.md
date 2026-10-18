# Literal tape access for one paired Gaussian SCALE

On an explicitly supplied split-component layout, PR3159's paired negation
retains a saving after every unit head move, read and write is charged. At
84 bits, one Gaussian coordinate costs **14,508 operations**, compared with
**24,568** for its two-negation control on the same three tapes. Both return
the heads, one carry bit and two temporary finite-control bits.

This constructs a local access boundary for forward native event 6872,
`SCALE(L292,1/-1)`, in both pinned rank-seven providers. Fresh native compilation
binds its next use, event 6873, `ADD(L333,L292,-1)`, in the same frame. It does
not locate L292 in an existing global allocation or execute that consumer.
The bill is per Gaussian coordinate, not per whole array-valued native event.

## Entry contract and physical operations

Supply three distinct tapes: the W little-endian real bits of one L292
coordinate, its W imaginary bits, and one zero carry cell. Each head starts
at offset zero. These are the target's own component banks, containing
arbitrary data; no additional dirty component bank is borrowed. The caller
grants exclusive mutable access for the entire macro and may observe its
output only after return. Two finite-control bits start at `00`.

The injective wire map sends `0..W-1` to real-tape offsets, `W..2W-1` to
imaginary-tape offsets, and `2W` to the carry cell. The schedule uses:

1. One selected head moving exactly one cell, charged one movement.
2. XOR-reading the scanned cell into one finite-control bit, charged one read.
3. Flipping the scanned target under saved controls, charged one read and one
   write even when the control condition is false.

For each CNOT or Toffoli, visit and XOR-read its one or two controls, visit
and flip its target, then revisit the controls in reverse order and XOR-read
them again. Distinct gate wires ensure the target update has not changed
those control cells. The rereads clear the scratch without erasure. The
target update is an atomic local involution, requiring no retained target
bit. Every final head return consists of charged unit moves.

Payload access uses only `Tape.read`, `Tape.write` and `Tape.move`. Fixture
initialization and endpoint observation are outside the macro; acquisition
is a caller obligation. Addresses and program position are compiled control
constants. This is a finite schedule, **not a uniform encoded-width tape
controller**. Its tariff counts these specified sequential access operations,
not the selected supplier's complete physical bill.

## Correctness and ownership

Each routed gate implements the logical gate and restores its control
scratch. Induction over the list reduces the endpoint to the pinned circuit:

```text
x <- x + y;  y <- y - 2*x;  x <- x + y;  y <- y - 2*x
```

These four shears over `Z/(2^W)` give `(-x,-y)`. Each ripple adder returns
the carry. Tests check both complete components, carry, heads and scratch.
Both components are ready before the next native read. Signed negation
additionally excludes the most-negative W-bit integer on each component;
the inherited precision/prefix admission remains a premise. Modular negation
works on that bit pattern, but does not give a valid signed result there.

The comparator is the predecessor's `control=True` circuit. It negates real
while restoring borrowed imaginary, then negates imaginary while restoring
now-negated real. It legally uses the same component tapes and carry. The
comparison assigns it no unnecessary third dirty component bank.

## Complete local invoice

For `4 <= W <= 256`, the emitted routes have these exact counts:

| Charge | Paired four-shear circuit | Two-negation control | Saving |
|---|---:|---:|---:|
| Unit moves, including final returns | `64W-140` | `104W-176` | `40W-36` |
| Reads, including scratch uncomputation | `88W-108` | `150W-96` | `62W+12` |
| Writes, including false-control writes | `24W-28` | `42W-24` | `18W+4` |
| Total | `176W-276` | `296W-296` | `120W-20` |

The paired circuit has `16W-16` CNOTs and `8W-12` Toffolis. A CNOT costs
three reads and one write; a Toffoli costs five reads and one write. Its
four shear routes cost `16W-28`, `16W-43`, `16W-27`, `16W-43` moves, followed
by one final imaginary-head step. The control's six unshifted full-width
adders contribute `6(16W-28)` moves; swap sweeps and intervening/final head
returns contribute `8(W-1)`. In particular, the second negation's first
adder includes two returns from the preceding swap endpoints; separating
those seeks leaves the six origin-based adder costs above.

Replay counts instructions at every admitted width, rather than fitting
formulas from samples. At W=84, paired counts are `(5236 moves, 7284 reads,
1988 writes)`; the control has `(8560, 12504, 3504)`. The saving is **10,060**.

For an integer M >= 1 already-owned consecutive coordinates on the same tapes, a conservative
serial extension resets to each coordinate's origin after its macro and
then advances W cells on both data tapes. The advances and final global
head return add `4W(M-1)` moves. Bills become `M(176W-276)+4W(M-1)` and
`M(296W-296)+4W(M-1)`. This conditional composition determines neither
L292's actual coordinate cardinality nor its producer allocation. It is a
written composition argument, not an implemented MW-cell array runner.

## Source binding, reproduction and limits

The verifier authenticates the declared source closure before imports. It
rebuilds both provider candidates, checks complete canonical word hashes,
freshly runs the pinned native transport/emitter, compares complete native
check objects, and reads the emitted events. The gate generator is inherited;
the tape interpreter and arithmetic/control tests are separate implementations.
The full predecessor coefficient-capacity and scalar-layer replays are not rerun.

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/rank7-paired-scale-routing
```

[RESULT.json](RESULT.json) records bindings, route hashes and invoices;
[SOURCES.json](SOURCES.json) pins inputs; [VERIFY.json](VERIFY.json) declares
the bounded replay. Native artifacts are temporary and removed after replay.
Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.

This in-place split-component contract differs from `physical-scalar-stream`'s
encoded-width aligned packets and protected output. No free conversion or
acquisition is assumed. Global placement, entry/exit access, whole-role
multiplicity, the ADD consumer, encoded-width control, recursive children,
frame operations, hosting, precision admission and complete producer cleanup
remain open. No selected-frontier change, supplier admission, new kappa,
formal-kernel proof or independent human review is claimed.

## Open next questions

Can a caller establish this layout and exclusive interval affordably? First
derive L292's coordinate count and physical owner mapping, then charge
conversion, seeks and acquisition; a logical role ID is not an address.

Can that layout support event 6873 and eventual producer cleanup while
retaining a saving? Bind L333's components and route its complete ADD and
restoration before expanding to the full caller. The adjacent selected
R480/T16 dispatcher investigation remains separate.

## Credit and coordination

Nick Petalas's [PR3159](https://github.com/CrocSwap/integer-mult-bounds/pull/3159),
head `f107d7331233c66c49579fdaa80c619e015cf245`, supplies the circuit, logical
invoice and physical-access handoff. Its retained PR3152 one-carry code, the
Cuccaro–Draper–Kutin–Moulton MAJ/UMA construction and native/provider lineage
remain credited through the pinned sources. `physical-scalar-stream` supplies
the contrasting packet contract; its interpreter is not used here.

The retained native lineage includes PR3080/3078/3076/3060/3056,
dcharb78/PR3042, Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979,
Cinna Davis/PR2226, DLamdata, eumemic, icekylinx, Tekalign and the geometry
and owner contributors named in the pinned notices. No predecessor bytes
are modified or re-attributed.

Prepared by thakrarsagar with substantial OpenAI Codex assistance in route
construction, source binding, accounting, tests and review. Separate Codex
executions are not independent human review. Apache-2.0.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19002854).
