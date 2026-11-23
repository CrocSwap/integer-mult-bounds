# Independent review: structural prefix widths

**Decision: accept the scoped prefix-certificate and fixed-denominator
producer implication.** The logarithmic width conclusion is accepted for a
fixed admitted seed's tensor powers. It is not an established width bound
for the complete selected expression or a physical multiplier construction.

The reviewed author proof has SHA256
`b024fe8d5b8841eba2739561754c26d24a120b9fca3299bc6c41b04ff6ba12b9`;
the implementation has SHA256
`b9a49880146e5af3a37dcbc85aff60c1aba7cb7aff3ab7dfbb8ad49cf5f3300b`.
The author confirmed this freeze before review. This review changes no
author file. All five selected assumptions and conditional kappa remain
unchanged.

## 1. Inputs and independence

The source boundary is #8092 at
`6a3437d1cd94dc4e1792f4052511af6160120bf9`, over canonical
`e54523517d0f03e58352e647c403a5af3e525a57`. I read the actual
`factor_words.emit`, constructors, and `expanded_ordered_ops`, alongside the
new proof and producer. The retained transducer is the previously reviewed
two-output implementation, SHA256
`0cef837c03fcc2830fb77585dfa4a328363738f3aa453af8cb49badb14f5f6c6`.

The independent program authenticates eight frozen inputs, the retained
source SHA256s, and all three provided Git blob identities. In a separate
read-only check, the retained ALPHABET, CASES and factor_words bytes were
compared with their actual commit:path objects. Those checks are recorded
in SOURCE-COMMIT-CHECK.json. The three retained files are therefore bound
to source bytes, rather than merely to self-consistent local manifest claims.
The transducer's provenance is the prior independently accepted session
freeze; it is not represented as an additional Git source object.

No author checker was imported or run. The emitter and new evaluator are
subjects. The independent matrix oracle constructs elementary right-action
matrices, multiplies them with a general exact rational matrix product,
and measures every prefix. A separate modular oracle obtains each low row
using numerator times the modular inverse of its denominator, then obtains
the carry directly from the exact rational row. It does not call the
subject's matrix helpers, certificate helpers or elementary carry producer
to determine expected answers. Tests of the new evaluator compare its full
low/carry trace against these independent values.

## 2. Universal structural proof

I checked the following argument against the literal source chronology.
For a valid admitted recipe, its certificate bounds **every prefix in both
directions**, including the empty prefix. A literal's finite forward and
inverse prefix enumeration establishes the base case. A permutation's
emission consists only of swaps, so every prefix has denominator one and
maximum column sum one. Identity extension adds an identity block.

For products, a prefix is a completed first factor followed by a prefix
of the next. Denominator exponents add and the maximum column-sum norm is
submultiplicative. Inverse emission reverses child order and direction;
the same bound applies because the child certificates cover both directions.
For direct sums, completed, current and untouched blocks are disjoint.
Their common denominator exponent and column-sum bound are maxima, rather
than sums over the number of copies. The inverse reverses the block order
without changing this fact.

The tensor emitter first applies its left child to column fibres and then
its right child to row fibres. During either phase, a completed copy, a
partial current copy, and all untouched copies act on disjoint coordinate
sets. A simultaneous coordinate permutation makes that phase block diagonal.
Both denominator and column-sum bounds are invariant under this permutation.
The first phase costs one left-child certificate, independent of fibre
count. Its completed matrix times a partial second phase costs the sum of
the two child certificates. Reversing phases, copies and directions gives
the identical bound for inverse emission. This is an every-instruction
claim, not merely a claim about the two tensor phase endpoints.

For a conjugation, the actual inverse chronology remains T, A^-1, T^-1;
the boundary words are not inverted in place independently. The three-phase
bound is therefore 2 cert(T)+cert(A). For a guard, H=I tensor C appears
before the middle phase and H^-1 afterward. Middle copies act on the
disjoint fibres {i*C.n+j : i}, for the selected j. Their certificate is
cert(S), independently of rank, including rank zero and full rank. The
two boundary phases give cert(S)+2 cert(C). Nothing in this argument assumes
that the carried basis C is orthogonal. The same source boundary words and
reversed middle copies correctly implement the inverse.

Tagged constructors, splitting and placement reduce to these constructors
and explicit permutations. The permutations still generate charged swaps;
the certificate's zero exponent does not declare their execution free.

### Lowered instructions

The proof also correctly reaches the source's actual ordered-addition and
signed-scale-atom interface. For an upper addition A=P L P, the extra
intermediate matrices starting at X are X P and X P L=X A P. They are
column permutations of the pre-addition and post-addition matrices. Hence
their maximum column sums and common denominator exponents are unchanged.

For a scale split into powers of two or one half, with any sign on the first
atom, the affected column's absolute entries vary monotonically between its
two endpoint magnitudes. Its entry denominator exponents are bounded by the
larger endpoint exponent: successive halvings increase them monotonically,
and doublings decrease them. All other columns are unchanged. Thus the
existing every-prefix bound covers every added scale microstep as well.
The retained scale alphabet contains all emitted signed atoms. This review
does not equate these logical instructions with an executed tape route.

## 3. Fixed denominator and signed widths

The norm direction is essential. For a row x with 0<=x_i<q and right-action
matrix M, each output coordinate is bounded by (q-1) times the corresponding
**column** sum. Thus a certificate (d,e) gives |(xM)_j|<q*2^e. Using a maximum
row sum would not establish this result without an additional dimension
factor; the independent counterexample has row norm two and column norm three.

Put D=2^d and let y be the canonical coordinatewise residue of xM modulo
odd q. D*xM is integral. Since D is invertible modulo q, D*xM-D*y is an
integer vector divisible by q. Therefore p=D*(xM-y)/q is integral, and

    |p_j| < D*(2^e+1) <= 2^(d+e+1).

For an addition a/2^s, the reviewed low producer supplies the integer c with
2^s*l_i+a*l_k=2^s*l'_i+q*c. Substituting xM=l+q*p/D yields

    p'_i = (2^s*p_i+a*p_k+c*D)/2^s.

For a scale, omit the 2^s*p_i term and use a*p_i in its place. Untouched
coordinates keep their denominator and numerators. Swaps exchange the two
low coordinates and the two numerators. These are exactly the fixed-D
updates in the implementation.

The post-instruction prefix certificate guarantees that the **combined**
numerator is divisible by 2^s. No assumption d>=s is required. The diagnostic
word scale(2), scale(1/2) has integral prefixes in both directions and
certificate d=0. For q=3 and initial first coordinate two, the second update
has old numerator one and local carry term minus one. Their sum divides
exactly by two; separately taking signed floors gives the wrong answer.
This diagnostic word tests the general arithmetic statement and is not
advertised as a newly admitted finite source seed.

The authenticated alphabet has 94 additions and 15 scales. It is closed
under addition sign reversal, scale inversion, and the emitted scale atoms.
For additions, 2^s+|a|<=55; scales have |a|<=16; the low producer's retained
bound is |c|<=54. The combined old-register partial is below
55*2^(d+e+1), and the local carry term is at most 54*2^d. Their sum has
magnitude below 164*2^(d+e), hence below 2^(d+e+8). Each separate shifted or
small-multiplied old register also lies below the same envelope. Consequently
d+e+9 signed bits cover the arithmetic intermediates, while d+e+2 cover
stored numerators. Exact signed division and testing its low s bits need no
wider integer. This is an arithmetic representation bound, not a bound on
the host Python object's allocation or diagnostic trace memory.

## 4. Tensor family and access scope

For one fixed admitted b-dimensional base with certificate (d0,e0), the
r-fold tensor has dimension N=b^r, certificate (r*d0,r*e0), and signed work
width r*(d0+e0)+9. For b>=2 this is O(log N). The emitted nonswap count obeys
m_r=b*m_(r-1)+b^(r-1)*m0, so m_r=r*b^(r-1)*m0. Copy multiplicity grows the
word length but does not multiply the per-prefix certificate.

The retained eight-dimensional actual_relative seed independently evaluates
to (2,4). The symbolic recurrence yields width 6r+9, including 129 at r=20.
The independent program checks the recurrence through r=25 without expanding
those large eight-dimensional tensor powers. Separately, it materializes
small tensor powers of a retained two-dimensional seed through dimension 16
and checks all their matrix prefixes in both directions and both lowerings.

This conclusion does not extend automatically to arbitrary recipe products
or nested conjugations. Prefix growth can be much greater than endpoint
growth, even if the final matrix is the identity. Bounding the actual selected
compact expression remains the next mathematical obligation.

The access argument retains the predecessor's two complete B-bit reads per
arithmetic gate, separate low-output channels, bounded high-register access,
and ordinary paid swaps. The fixed common denominator removes the need to
rescale all unaffected high registers after every gate. Certificate evaluation
and recipe storage remain charged. The reference validator's full numerator
scan is explicitly allowed in the conservative sequential invoice.

With W replaced by d+e+9, the stated conservative supplied-row/low-matrix
bound O_source(N^2*(ell+1)*[B+d+e+log(2N)]^2) is compatible with those paid
accesses. A materialized single row uses O(N*(B+d+e)) data bits, plus the
charged recipe/word description. This does not construct a global payload
permutation, low-type ordering, native owner return, service dispatch,
private native precision, or a full-system multiplier tariff. In particular,
logical register widths do not imply that the convenience Python adapters
have constant-size finite control or minimal physical storage.

The generic carry/cocycle and column-denominator identities remain credited
to #5841. The new implication reviewed here is the actual source grammar's
every-prefix certificate, including partial copies and lowered microsteps,
and its use to replace denominator growth based on expanded gate count.

## 5. Independent executable evidence

The normal and optimized runs are byte-identical. They cover:

- all 25 retained recipe cases, plus five additional guard ranks, three
  small fixed-seed tensor powers, and the combined-division diagnostic;
- 136 forward/inverse, native/lowered recipe variants;
- 6,984 exact matrix prefixes, comprising 1,072,308 matrix entries;
- 574 modular row executions and 244,052 independently reconstructed
  low/carry coordinates;
- 11,918 arithmetic updates, including 3,193 negative local carries,
  176 updates with d<s, and 77 updates whose individual terms do not divide;
- canonical zero, boundary and seeded mixed rows, odd composite radices,
  and two longer radix channels of 65 and 257 bits;
- exact source chronology, inverse matrix identities, lowered endpoints,
  ordered addition indices, atom closure, and the two-pass read census.

Nine negative controls reject wrong norm direction, endpoint-only bounds,
too-small fixed denominator, separate summand division, lost local carry,
omitted guard boundaries, omitted conjugation boundaries, a missing lowered
swap, and source byte corruption. The lost-carry control executes a mutation
of the subject evaluator. The missing-swap control changes the source-emitted
word. The other controls are explicit mathematical underbounds or source
integrity counterexamples, not claims to mutate every physical execution.

Commands, from the workspace root:

```text
python3 -I -B work/review-prefix-width/independent.py --package work/compiler/prefix-width --output work/review-prefix-width/EVIDENCE.json
python3 -I -O -B work/review-prefix-width/independent.py --package work/compiler/prefix-width --output work/review-prefix-width/EVIDENCE-OPTIMIZED.json
```

Finite evidence checks the bound, source interpretation and implementation;
the universal tensor/guard result follows from the structural argument above.
No additional speculative result or new kappa is claimed.

Prepared for Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
