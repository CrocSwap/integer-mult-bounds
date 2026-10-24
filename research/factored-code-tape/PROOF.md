# A complete local tariff for the factored mode code

This is a conditional arithmetic construction on a fixed classical multitape
machine. It does not establish common-coordinate access in a Gaussian caller.
The source matrix, rounding rule and original tape contract are the inputs in
SOURCES.json. The scalar factorization was first recorded in
[Discussion #5314](https://github.com/CrocSwap/integer-mult-bounds/discussions/5314).
This package adds a fixed-word instruction table, temporary allocation and a
complete local tariff.

## Domain and schedule

Use the same integer grid, input bound H>=0 and word width
W=bit_length(56H+2)+1 as the source kernel. Each of 112 owner tapes contains N
signed W-bit words, with one delimiter per word and a final end marker.
Real and imaginary components are separate records. The source mode matrix
is fixed in the finite control. The emitter checks its fourteen sign cubes;
it is a certificate generator, not a variable-matrix machine oracle.

There are eight mode tapes, eight temporary tapes, one division tape and one
readonly bound tape: 130 tapes in total. The 17 owned words start with arbitrary
bits. Initialize them once. On each coordinate validate all 112 owner values,
run the 308-instruction gather, run the eight source ROUND52 transducers,
run the 280-instruction scatter, clear the 16 mode/temporary words and advance
all owner heads. The division word is already zero after each source range or
division operation. Rewind all owner tapes at the end. For N=0, initialization
and final framing still run.

All gathers finish before the first owner update. The emitted gather and
scatter programs use separate temporary identifiers. The allocator computes
last uses, then reuses a last-used input slot for an output when possible.
It rejects a read before definition, an allocation above eight words and
any live temporary at the end. It emits literal tape indices 0,...,127 for
signed sums. Division uses tape 128 and the readonly bound is tape 129.
No arbitrary native helper tape appears.

The actual matrix has fourteen four-mode supports, each with the eight
projective sign patterns. For one group, signed source views identify the
rows with (1,+/-1,+/-1,+/-1). Four pair sums and four pair differences cost 8.
The sum of differences costs 3. Three selected transforms of the four sums
cost 7. Four updates to global modes cost 4. Thus gather costs14*22=308.
For scatter, form a+b,a-b,c+d,c-d in 4 sums, form each of the eight corrections
in one sum, and perform eight owner updates:14*20=280. Source signs are part
of each signed binary instruction. Copies or sign maps are not extra hidden
instructions: the next section gives a direct two-input signed primitive.

## Finite signed primitive and range

An instruction is z=a*x+b*y, with a,b in {-1,1}. Read the two source bits
before writing the destination bit. Start carry at [a=-1]+[b=-1]. At bit j,
add (x_j xor [a=-1]), (y_j xor [b=-1]) and the carry; write the low bit and
retain the remaining carry. Carry is in {0,1,2}. This is the usual two's
complement identity for the sum of two signed words. The destination may
be a last-used source word: the current bits are read first, and later bits
are not changed. A forward scan and a return sweep cost at most 2W+4
transitions. All addressed heads move together; unaddressed heads stay put.
The destination is written in full, so its prior contents do not matter.

Each temporary gather sum has magnitude at most8H; each partial mode has
magnitude at most56H. The source division returns q with
|q|<=14H/13+1/2. A scatter temporary is a signed sum of at most four such
values. Its magnitude is at most56H/13+2. An updated owner has magnitude at
most69H/13+2. All are at most56H+2. Hence every mathematical signed result
fits W bits and the modular carry loop equals that result. Division and
range validation are the authenticated source bit loops. Rounding occurs
at exactly the same eight mode values as before. The final owner words
therefore agree for every valid input, including signed ties.

The allocator attains eight temporary words. One can also see this directly:
form the four sums and differences; reduce the differences first; form each
sum-pair's sum before its difference releases the old pair; then form the
three required coefficients and consume all four outputs. Scatter needs
only four pair values and one current correction. The runtime representation
is a reference interpreter of these fixed words. It is not a measured
physical TM or a benchmark of the full Gaussian caller.

## Complete tariff

Reuse the source primitive bounds: validation 8W+16, ROUND52 at most 24W+64,
and CLEAR/INIT at most 2W+4. Signed binary sums have the bound proved above.
All primitives return their participating heads to the current word start.
Owner advance costs W+1 with all 112 heads moving together. Final rewind
costs N(W+1)+2. Include 62 further framing transitions.

```text
T <= 17(2W+4)
   + N[112(8W+16) + 588(2W+4) + 8(24W+64)
        + 16(2W+4) + (W+1)]
   + N(W+1) + 64
  = N(2298W+4722) + 34W+132.
```

At most 130T individual head moves, symbol reads and symbol writes suffice.
The storage bound is 112[N(W+1)+1] owner cells, 17(W+1) owned scratch cells,
and W+1 readonly bound cells, plus fixed framing. There are 144N+17 complete
zero-writing scans: 112 range clears, 16 internal division clears and 16 final
mode/temporary clears per coordinate, plus 17 initial clears. This cleanup
is paid classical writing, not reversible uncomputation.

The old bound is N(2898W+5922)+18W+100. Old minus new equals
N(600W+1200)-16W-32, which is positive for every N>=1 and W>=3. This compares
constructive upper bounds in two stated fixed-tape models. The new machine
has130 tapes rather than122 and uses eight more temporary words. It is not
an optimality or measured speed claim. The rounded map, two-grid-unit local
error and noninjectivity are unchanged.

## Evidence and remaining obligations

The verifier checks all 112 gather and eight scatter basis columns with the
emitted finite-word instructions. It compares 48 mixed/extreme coordinate
vectors in 36 batches, including N=0,1,3 and H=0,1,6,26,51,250, against the
actual source kernel. It starts every owned scratch bit dirty and requires
all 17 words clean. An independent primitive invoice sums to the displayed
formula. A changed numerical sign and owner alias are rejected. Hash pins
bind every external input; source modules load from their authenticated
source bytes, without a bytecode-cache import.

The written range, carry, schedule and sweep arguments give the quantified
local result. Finite replay does not establish the full physical caller,
common-coordinate field access, native Gaussian accuracy, compiler reserve,
reversible ownership, a new supplier or a new kappa. Extra wrappers and
field movement remain charged caller obligations.

Credit JoyboyBrian's PR #5035 for the source divider, validation, rounding and
classical sweep contract; Dillon's PR #4933 for the physical mode factorization;
Dugongue and retained native/precision/compiler authors for their source work.
The Walsh transform is standard. New emitted schedule, allocation, tariff,
proof and checks: Ali Romman with OpenAI Codex assistance. Apache-2.0.
