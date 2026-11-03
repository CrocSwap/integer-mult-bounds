# Exact bounded execution and remaining limits

CPython3.12, standard library only. Pre-execution source/code copies, plans,
hashes, first stdout/stderr, literal streams, return/resource records and final
seals are retained in the session handoff. Scientific errors raise explicit
exceptions under normal and optimized execution. No scientific run failed and
neither implementation changed after its first seal.

## Complete raw domain

All256 raw2x2 matrices A and all256 matrices B are included, Acode outer
and Bcode inner. A code's base4 digits are row-major matrix entries with
coordinate0 least significant. F4 element2 is z, not an integer modulo4.
The canonical UTF8 stream is one compact JSON array followed by LF per pair:

    [Acode,Bcode,trimmed_lowfirst_detpoly,status,pointkind,alpha,slice,inverse]

Status is `singular` or `regular`; the last four fields are null for a
singular pencil. Regular pointkind is `infinity` or `affine`; alpha is null
at infinity or a canonical F4 integer otherwise. Slice/inverse are literal
2x2 integer matrices over F4. Determinant polynomials are included even when
infinity succeeds. The point order is infinity, then0,1,2,3.

The primary ports the source polynomial/Bareiss, Frobenius/Berlekamp and
quotient-matrix routines to the credited Field tables. It constructs every
regular output and selfchecks both inverse products. The independent oracle
uses XOR/carryless base multiplication, the explicit2x2 determinant polynomial,
all five projective values and the adjugate inverse. It imports no source or
primary arithmetic implementation and reads no primary results before sealing
its own first run.

The two complete first streams are byte-identical, not merely count- or
digest-equal:65,536 rows,4,476,800 bytes, SHA256
830190a2cfee12d9c5f61506ad96fab4c093b297dc7d78a2c8bad6427ddf3301.
They contain63,360 regular and2,176 singular cases. Infinity is selected in
46,080 cases; affine selection occurs in17,280. The independent point census
resolves13,680 at0 and3,600 at1. This does not claim a returned2/3 affine
point in this domain; higher-dimensional fixtures still evaluate all four
base elements during their actual failed base-field scans.

The full streams are retained externally in the durable session archive;
the public receipts retain their exact hash/count/byte metadata, and either
program can reproduce the complete stream with `--emit --stream-file` and a
fresh external path. Default registered runs regenerate the complete hash
without writing a stream, compare the strict receipts, and independently
validate the named actual primary outputs. Named matrices are retained in
full; no compressed-header identity is used as mathematical equality.

## Ten frozen named inputs and actual returned witnesses

The named inputs cover empty dimension0, an identically singular dimension1,
a nonprime infinity slice, constant affine determinant, actual polynomial row
pivot, raw and nonprime-transformed dimension5/17 attainers, and the
dimension9 repeated-root determinant(t^4+t)^2 plus an infinity block.

Nine cases are regular and one is singular. The source-table constructor
returns relative degree2 for both dimension5 variants and the repeated-root
case, with actual h=[2,1,1]. Both dimension17 variants first succeed in
degree3 with actual h=[2,0,0,1]. The largest Frobenius polynomial degree is64;
the largest Berlekamp matrix dimension is60, with actual kernel-dimension
traces[20,5,2] for the degree3 cases. These are observed bounded traces, not
new asymptotic bounds or a new attainment theorem.

The oracle uses separate quotient arithmetic over its own carryless F4 and
literal F4/F16/F64 projective scans. A degree2/3 polynomial over F4 is
irreducible exactly when it has no F4 root; the oracle checks actual returned
moduli with that criterion. After both blind first seals, all ten actual
primary records are checked against the frozen raw matrices and independently
computed minimum: nine modulus/embedding/point/literal-slice/both-inverse
checks and one singular null record. Different valid irreducible moduli or
own witness choices need not have identical matrix hashes. No such unexamined
whole-receipt equality is claimed.

## Controls, replay and custody

The primary has14 controls:13 rejecting controls plus an observed positive
polynomial row pivot. Actual incorrect inverse, literal slice and reducible
modulus are rejected. A Z/4 multiplication table is supplied to the actual
constructor and rejected by backend admission; this is not a complete run of
the constructor with its admission guard disabled. The p-versus-q control
executes a base-linearity guard on constants, rejecting exponent2 while
exponent4 fixes all base elements. It is not a mutated complete-constructor
replay. Other controls cover source corruption, noncanonical embedding,
boolean/out-of-range/nonsquare/nonregular inputs and duplicate/nonfinite JSON.

The oracle independently rejects an actual bad inverse, F4-reducible modulus,
collapsed base embedding2 and boolean input. Its computed examples distinguish
2*2=3 in F4 from0 in Z/4, and two roots of X^2-X from four of X^4-X.
These arithmetic observations are labelled separately from actual witness
corruption tests.

Both first emissions and all final normal/optimized emissions/defaults pass
with unchanged code and receipts. The primary receipt SHA256 is
63c59d4d3cbf04f26b3e6980546b60616a3edfdfe9cb4b6f4084b486bea6730e;
the oracle's is dfd462612b5104213a3c85f16a29ea84de58d37c894da03dfa0104b32abb8233.
Six source objects are authenticated before use; only the credited Field
definitions/constructor execute, and no predecessor scientific checker runs.
PENCILS.json SHA256 is ce46d3e6f89e261e4cb9e4f5260e27c9ab498b619b4bd812f4b00b0d50ad4db8.
The included input_recipe.py regenerates those exact bytes without modifying
the retained input; a separate output file was byte-compared successfully.
Source/history/modes, official export, read-only Git-free/empty-PATH replays
and external copy-corruption controls are separate packaging checks recorded
in the final handoff. Canonical metadata is provenance-only, not an undeclared
runtime dependency.

```sh
python3.12 -I -W error -B verify.py
python3.12 -I -W error -B -O verify.py
python3.12 -I -W error -B oracle.py
python3.12 -I -W error -B -O oracle.py
```

Default modes require exact retained receipts and reject missing receipts.
Recursive type equality or canonical typed JSON comparison prevents booleans
from standing in for integers. No wall-clock speedup claim is made. Recorded
child resource measurements are not a complete process-tree peak invoice.

## Remaining obligations

This checks all2x2 pencils and the ten literal cases, not all dimensions3..17
or arbitrary nonprime base fields. The fixed-F4 code remains subject to human
and proof-kernel review; source theorem correctness and its general arithmetic
complexity are inherited claims, not recertified in full here. No field-descent
or original-field SL transport, actual native/consumer binding, physical
coefficient/access/restoration schedule, bit/tape/precision/stock/control cost,
compiler or complete recursive/outer supplier invoice is supplied. All five
selected assumptions remain. No selected full replay, Lean, Docker, new kappa
or frontier change is claimed. Open next questions are in README.md/TASK.json.
