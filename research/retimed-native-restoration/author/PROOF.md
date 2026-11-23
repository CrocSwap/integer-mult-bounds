# A uniform bound for the actual native restoration lists

## Exact target and claim

This is a narrow continuation of the decoder-owned control package. It
prices the **ordered `restores` values retained by
`StrongBinarySource.raw`**, including their complete matcher words. It does
not price all native service state. The source is #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`, authenticated by the unchanged
`inputs/decoder/SOURCE-BINDINGS.json`. The comparison base and preceding audit remain
canonical `e54523517d0f03e58352e647c403a5af3e525a57` and #8091 at
`b500f72bbcf9c03a7f7fd40b366eedd6d1dd285b`.

Retain the original successful production binary-call hypotheses, with
h>=3000, N=2^h, B=N^92, P=18906 and at most C=2N^83 inclusive live native
contexts. The complete field has W/B>=9^N. There is an exact ordered binary
encoding of every retained restoration list such that the sum of uniform
per-role historical allowances for four reusable list/image roles per bounded context slot at this fixed
production height, including a two-bit finite-alphabet encoding, is less than

\[
 \boxed{2^{28}N^{84}h < BNh < W\text{ bits}.}                 \tag{1}
\]

The final comparison uses W as its numerical byte count, so it is stronger
than requiring these bits to fit W bytes. The stated roles are the retained
list, an alternate serialization image, a reverse-read image and an inverse
word transfer image; each receives a separate maximum. These are added
control roles, not newly created data owners. The predecessor owner bound
continues to apply without treating descriptors as owners.

No native body/dispatch tariff, complete native register bound, physical
Python-memory equivalence, whole-Receiver state bound, assumption discharge
or kappa improvement follows. The existing decoder theorem remains frozen.

## 1. The actual caller retains exactly this list

The actual `BinaryWord.native` in `raw_binary_stage.py` builds one entry for
each tagged target by strict zip, checks `len(job.axes)==port.rank*columns`,
and calls `physical.raw(entries,columns)`. `binary_receiver.compiled`
constructs `StrongBinarySource(banks)` as that physical source. The wrapper
then validates all q=104904 paid tags and extents in order.

`StrongBinarySource.raw` performs one loop over those P entries. Each
iteration computes

    target = c.target(tag)
    source = job_frame(job, dimension)
    matcher = source.matcher_to(target)
    banks.route(job.owner, matcher)
    restores.append((job.owner, matcher))

before entering the paid native program. No other branch appends to
`restores`. The list is never popped during that program. At its end the
source iterates `reversed(restores)` and routes each owner with
`tuple(inverse_word(matcher))`. Thus a paid suspension retains P complete
ordered matchers, and a partially initialized context retains at most P.
Its closing continuation retains the same list until the service returns.
The owner sequence includes borrowed productive jobs; value-exact inverse
route replay preserves the original ordered return protocol. Numerical
restoration/zero obligations and the timing of child loan returns remain
the inherited custody hypotheses, rather than consequences of this codec.
The inherited inclusive C bound includes those opening and closing states.

The result does not assume the list entries are short integer masks. Their
words contain the source basis, permutation and inverse target basis.
Calling the actual native wrapper in the bounded checker binds this claim
to the source's P entries and q paid cuts; bank payload operations remain
abstracted, exactly as in the earlier metadata/source replay.

## 2. The all-size matcher bound

The frozen decoder proof established that each incoming Job is an integer
axis Job (empty basis) or has a literal lift of one of the 595 exact common
base words. Each base has at most 61 operations and at most eight coordinate
positions. An arbitrary ordered selection changes the mask, not its basis.
Because each admitted column multiplier is at most N,

\[
 |source.word|\le61N.                                      \tag{2}
\]

Every actual target is covered too. `Catalogue.target` has two branches:
a root target uses `extend(joint(port),...)`; a helper target uses
`difference(start[port],final[port])`. `ActiveCatalogue.joint` and
`.difference` use the same fixed chart tables. The latter's helper pairs
are included explicitly by `fixed_binary_charts` when it extends its pair
set with `zip(starts[2*ports:],ends[2*ports:])`. The bounded checker enumerates
all P literal target tags, checks their rank and this exact table incidence,
and records the distinct target requests. The source's literal all-column
lift then proves

\[
 |target.word|\le61N                                      \tag{3}
\]

for every admitted column multiplier, not just those tested. The complete
source census has 2,120 distinct target requests across all 18,906 tags;
its largest target base has 52 operations, so 61 is a conservative common
bound. Empty/identity words and integer-axis zero exemplars are included.
Private INIT owners created later by `BinarySource.inner` are not additional
productive entries and do not append to this list. `port_stage` and other
private route words are distinct locals, not the `c.target(tag)` values
saved here; their lengths and state are explicitly outside this claim.

The retained `Frame.matcher_to` initializes `source_at`, `position` and an
alignment permutation, then executes exactly `for dst in range(n)`. Each
iteration appends either zero or one swap. Irrespective of possible sharing
in the input arrays, it returns the literal concatenation

    tuple(chain(self.word, swaps, inverse_word(target.word))).

Inversion preserves word length. Therefore every successful actual matcher
and its later inverse have at most

\[
 61N+N+61N=123N                                            \tag{4}
\]

operations. This argument requires no assumption that a composed linear
map has a small dense matrix. The source keeps the concatenated elementary
word; it does not multiply its coefficients together.

All coordinates stay in 0,...,N-1. Original base coefficients have at most
five signed numerator bits and five denominator bits. Lift and selection do
not change them; swap introduces no coefficient; inverse negates an add
coefficient or reciprocates a scale coefficient. Hence a **six-bit signed
numerator and five-bit positive denominator** represent every coefficient
in a matcher or inverse matcher. The fixed library's complete inverse
coefficient census is checked explicitly. The sixth numerator bit is needed for the actual admitted paid-basis family.
The paid tag `(move,4,830,869)`, rank 5, uses difference pair `(45,388)`;
base operation 39 is `scale` at coordinate 2 by 7/20. Its inverse contains
20/7. Positive 20 cannot fit a signed five-bit two's-complement field, whose
maximum is 15. An incoming selected Job retains this complete basis, so
return inversion must preserve that coefficient even when its active mask
is short. The checker binds this witness to the literal paid tag and chart
entry. Six bits are also a uniform consequence of a five-bit denominator
becoming a signed numerator; the conclusion is not extrapolated from the
integer-input dynamic replay.

## 3. Exact list encoding and charge

Use owner/length width w=128h and coordinate width h. Begin with the list
length in w bits. Each ordered entry stores owner and operation count, then
its operations. An operation occupies 2h+13 bits: a two-bit opcode, two
h-bit coordinates, a six-bit two's-complement numerator and a five-bit
positive denominator. Unused swap/scale fields have fixed canonical values.
The encoding rejects out-of-range owners/coordinates, zero scale, invalid
opcodes, noncanonical unused fields, malformed rational fields, a list
longer than P, a word longer than 123N, padding and trailing/truncated bits.
No dictionary of arbitrary matcher objects is assumed.

Binary uniqueness and reduced exact rationals give value-exact roundtrip.
Ordering is explicit; an owner identifier is not used to sort the list.
Inverting a decoded word yields the same literal source inverse. Reading
the records in reverse gives the same final route sequence as the actual
native body. A forward sequential implementation can scan to an index,
so reverse access does not imply free random access; no time tariff for
those scans is claimed here.

For h>=3000, 2h+13<3h, and the two scalar fields are smaller than Nh.
A complete entry therefore uses fewer than 370Nh bits. One list image has

\[
 L=w+P\{2w+123N(2h+13)\}<2^{23}Nh,                        \tag{5}
\]

since 370P+1=6,995,221<2^23. Allocate four independent roles of maximum L
per context, even though inverse-transfer words are much shorter than a
whole list, and encode each fixed-alphabet cell by two bits. Across C=2N^83
contexts this is less than

\[
 2\cdot4\cdot C L <2^{27}N^{84}h<2^{28}N^{84}h.           \tag{6}
\]

Reserve an additional 2048Cw bits for fixed loop/framing scalars across
contexts; this fits the remaining factor-two slack because w=128h and
N>=2^3000. This is a
sum of each role's uniform historical maximum. Clearing or replacing one
list does not reduce its historical charge. Since BNh=N^93 h and
N^9>=2^27000>2^28, (1)'s first strict comparison follows for every production
height. The field comparison follows from W>=B9^N and 9^N>Nh.

### Fixed physical roles and reuse

The simultaneous-context bound alone would not bound history if every new
context identifier allocated fresh physical lists. Assign the C bounded
service slots used by the decoder to four fixed backing roles. Each backing
tape has C segments of capacity L, indexed by the bounded slot; a context
identifier or Python object address never chooses a new physical segment.
Opening acquires an unused slot before installing its list, and keeps that
slot throughout initialization, all paid suspensions, and final closing.
After its last inverse route and completed native return, clear the four
segments and release the slot. Later contexts reuse them, retaining each
segment's historical maximum. Variable-size images stay within their fixed
L capacity. A full scan can locate slot*L, whose local offset fits w; slot
lookup, clearing, and service dispatch time are expressly outside this
storage-only claim. No unpriced random access is assumed.

This gives four fixed tapes rather than a growing family of physical tapes.
The finite role description and per-slot framing scalars fit the displayed
2048Cw reserve. The proof covers arbitrarily many successive contexts and
warm uses at this fixed production height. It does not replace a whole
runtime or cross-height history proof: larger prior heights and outer
caller roles retain their separate coordinatewise maxima and require the
existing global composition argument.

The working arrays used while *constructing* a matcher, retained caller
port arrays, `active`, inner native registers, wrapper/generator frames,
other route words, banks/allocator state, service dispatch and numerical
route bodies remain outside this result. The four image roles do not stand
for all such native state.

## 4. A source-specific cache distinction

The older `Catalogue.__init__` wraps several instance methods with
`functools.cache`, and `raw_catalogue(dimension,columns)` is globally cached.
Those are not the actual initializer or supplier in this path.
`StrongBinarySource.raw` calls `active_catalogue`, which creates a fresh
`ActiveCatalogue`. Its overriding initializer assigns seven scalar/shared
source fields and does not call `Catalogue.__init__`, `super`, or install
cached methods. The actual target/difference calls therefore do not create
a per-instance cache indexed by dimension, columns or target requests.
The fixed zero-argument `fixed_binary_charts` cache remains and was already
charged as the common exact library in the decoder proof.

This distinction prevents an incorrect extra cache assumption at this
boundary. It does not say every global runtime cache is bounded: e.g.
recipe caches across different heights and unrelated services remain
separate. The checker both authenticates the literal initializer/call site
and observes unchanged instance keys through its target census.

## 5. Evidence, novelty and remaining work

The predecessor and frozen decoder results deliberately excluded native
restoration lists. Equations (2)-(6) give a new all-size storage implication
for those actual retained words, using the actual caller and matcher
constructor. The executable evidence includes complete target incidence,
exact signed rational word roundtrips, a full native-wrapper metadata run,
and the actual final reverse restoration sequence. Negative controls alter
word order, omit a restoration, truncate a list, or violate coefficient and
coordinate fields. They are checks of this narrow implication, not a proof
of the numerical route bodies.

Next, count the remaining `BinaryWord.native`/`StrongBinarySource.raw`/
`BinarySource.inner` retained arrays and frames at paid and nested callback
cuts; bind those values to an explicit service-side dispatch protocol; and
price all scan/matcher construction/route costs against the complete actual
caller. Until then native storage and time remain explicit assumptions.
