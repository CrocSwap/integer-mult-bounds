# Exact forward scalar rows

## Scope and source

The consumer is the complete forward scalar checker in PR5827 `local.py`.
The main input is the PR6453 word at
`b1a3e525793eca35c56324aa7ffd0b714cf606d4`. Its 17,926 events act on
770 public and 29 owned rows. The PR6399 clean word is a second input.
The seven scalar rejection controls are the literal controls in PR6453.
`ORIGINS.json` records every retained file. Authentication precedes execution.

This is an execution change. It does not change a data word, scalar invoice,
frame, ownership rule, native operator, compiler or kappa. A complete scalar
check is only one component of a complete supplier check.

## Sparse integer invariant

A row is a pair `(a,e)`. Its coefficient at column j is `a[j]/2^e`.
The integer e is nonnegative. Missing keys have coefficient zero. The initial
row has one unit entry and exponent zero. INIT and CLEAR give an empty row.
SCALE by the reduced dyadic value p/2^d multiplies each numerator by p and
adds d to e. COPY performs the same calculation in a new dictionary.

For an ADD from row `(b,f)` with coefficient p/2^d, set

    h = max(e,f+d)
    a'[j] = 2^(h-e) a[j] + p 2^(h-f-d) b[j].

Both shifts have nonnegative integer lengths. Division by 2^h gives exactly
the source Fraction operation. Remove zero entries. The source and target
rows are distinct, as the retained guard requires. The source dictionary is
not changed. These facts prove the exact row invariant by induction through
every event, including chronological erasure. MOVE changes only the checked
frame and paid count. No fraction or probabilistic fingerprint is used for
coefficient arithmetic. Endpoint comparison converts the exact row to the
original Fraction dictionary, including every implicit zero.

The coefficient cache contains at most 128 immutable Fraction values.
The input type is part of the key. It stores no row, word or acceptance result.
The guard `abs(q)+1 < 2^16` is equivalent to `n+d < 2^16*d` for
n=abs(q.numerator), d=q.denominator>0. All other guards are unchanged.

## Packed experiment

The experimental engine uses the same denominators. A preliminary pass
propagates a nonnegative numerator l1 bound under the same ADD, SCALE, COPY,
INIT and CLEAR operations. Triangle inequality gives a bound L on every
numerator coefficient at every cut. The pass also bounds the denominator
exponent E. Choose a power-of-two radix B strictly larger than
2*(L+2^E). Encode a row numerator as sum_j a[j]*B^j.

All integer row operations commute with this evaluation. The radix map is
injective on every comparison that occurs: a difference digit has absolute
value below B/2. If a nonzero highest difference digit has index k, its
contribution has magnitude at least B^k. The lower digits have total
magnitude at most (B/2)*(B^k-1)/(B-1), which is less than B^k for B>2.
Thus no different coefficient row can produce the same integer. The same
argument proves that a zero integer represents an empty row. Balanced radix
decoding is checked against independent Fraction arithmetic on small words.

The main word has a 66-bit certified radix and denominator exponent at most
27. This is a coarse cancellation-free bound, not a precision or physical
storage lower bound. The packed engine is slower than sparse rows on the
measured forward consumer. Its preliminary bounds can reject an invalid
word before the retained checker reports its first error. One extra control
records this message difference. The seven inherited scalar controls still
reject. The sparse engine is the recommended drop-in scalar implementation.
No identical error-order contract is claimed for the packed experiment.

## Complete control and prefix checks

A static AST comparison checks the full retained scalar function against the
explicit representation changes listed in `verify.py`. It includes every
branch, guard, inventory update and returned field. It does not execute
modified source text. The unchanged retained function runs separately.

For each of the two words, the audit executes the literal Fraction updates
from the retained arithmetic and compares the changed row at every event.
All untouched rows stay unchanged, so induction covers the full matrix at
all cuts. Packed comparison uses an integer formed independently from every
Fraction coefficient. The proved radix bound includes every missing zero
column. A digest records the exact changed-row trace. No expected digest
replaces execution.

The audit also compares complete receipts, all seven original scalar
controls, extra malformed-word controls, an actual COPY variant of the
complete word, source-byte corruption, cache eviction and source isolation.
An omitted driver guard fails the AST comparison. An engine that drops ADDs
fails the complete endpoint check. Both normal and optimized Python execute
these checks; they do not depend on assertions.

## Cost and remaining obligations

Sparse ADD visits the source support and, only when required, shifts the
target support. Integer bit costs remain payable. Denominators are not
reduced after every event, so other words can have much larger integers.
No universal time or memory improvement is claimed. The packed experiment
also pays its bound pass and large-integer operations.

The benchmark includes fresh interpreter startup, source authentication,
input decoding, the complete scalar checker and output serialization.
It records five alternating triples, with no omitted samples. Function-only
times are separate. This does not measure the full native, physical-caller,
price or compiler replay, or a physical integer multiplier.
