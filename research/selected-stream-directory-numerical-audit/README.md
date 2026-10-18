# Exact numerical peaks in the remaining BIT directory and ADD phases

For the unchanged source exported by PR2801, successful `directory.produce`
uses exactly **max(d², 6) additional residue Words**, hence **4,096 at selected
dimension 64**, above all entry residents. Successful `stream.add_pass` uses at
most **six additional residue Words outside its coefficient callbacks**. Neither
phase allocates an index Word. Six includes the returned coefficient.

If a coefficient callback uses at most R additional residue Words and I index
Words, returns one fresh owned residue, and restores everything else, the whole
ADD call has allowance **(max(R, 6), I)** above the same entry baseline. The
callback and stream scratch are successive phases, so their bounds compose by
maximum. This closes two explicitly excluded phases of [PR2801's handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2801).
It does not complete `Consumer.apply`, an all-size stock coefficient, physical
reserve, supplier admission or a new kappa.

There is a sharper source statement: outside callbacks the ADD peak is four
when both returned coefficients are zero or one, and six when either is at
least two. The separate [independent audit](INDEPENDENT.md) supplies the proof
and finite branch census. Equal split/merge coefficients are required for the
intended shear semantics; that equality is distinct from the storage theorem.

## Sources and exact contract

Scientific runtime: Jose Manuel/jmbarrancoml PR2697
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. The six runtime modules and complete
notice in [vendor](vendor/NOTICE.md) are byte-identical exports from Nick
Petalas PR2801 `e2564b80b86fb77610b4b78701e5446a76fbe962`.
[SNAPSHOT.json](SNAPSHOT.json) records exact paths, Git blobs and SHA256 hashes;
the checker authenticates its whole manifest and every source before executing
compiled source bytes, ignoring bytecode caches. No frozen predecessor changes.

Let B_R and B_I be the counts of **all** live residue and index Words immediately
before the entry point, including Ring, Context, operands, suspended callers and
unrelated borrowed values. They are not zero or free. Residue and index arenas
are distinct. Numerical input words are complete and have head 1 on entry.
Assume sequential successful execution, valid canonical encodings, sufficient
arena capacity and no concurrent mutations. The specification is fixed; the
default `Tape`, or any replacement payload factory, must not allocate numerical
Words. Observers must be numerical-allocation neutral. A factory allocating a
Word before the callback changes its entry baseline and invalidates this bound.

For the directory, fix positive dimension d, q >= 2, width w >= 1 and modulus
M = q^w with the source's single high-bit margin. The initialized Context has
cap q^(w-1), the finite code vocabulary, and the complete high-count metadata.
The old directory contains the positive old-count multiplicity and exactly the
encoded nonnegative field depth per prefix, with high digits below cap. Field
and count encodings have the source's required margins. Selected use has d=64
and odd prime q; the numerical proof does not require primality. Context
initialization precedes the baseline and is not priced here.

For ADD, M > 1 and positive separately canonical before/middle/suffix extents
are fixed. The complete Boolean payload has length before*M*middle*M*suffix.
Each callback is invoked with precisely the common entry numerical residents;
it may read borrowed state but must preserve its values, heads and live sets.
It returns exactly one fresh owned canonical residue in the Ring arena, and no
index result. For the intended map y <- y+c*x mod M it returns the same c in
both traversals. R includes the result, so R >= 1; I >= 0. Failure cleanup is
expressly excluded, as demonstrated below.

## Written lifetime derivation

Every numerical allocation in these entry points passes through `Arena.zero`;
`free` erases its contents before making the slot reusable. Numerical contents
can therefore be bounded at completed allocation cuts: partial initialization
or erasure cannot occupy more cells, and neither allocates a nested Word.
Counts, serialized records, payload tapes and finite controller locals are
separate categories, not secretly numerical Words.

The four-Word bound for `Unsigned.divmod` and `Ring.multiply` is already proved
in Nick Petalas [PR2759](https://github.com/CrocSwap/integer-mult-bounds/pull/2759).
This package credits that arithmetic and checks the overlap in its actual callers.
For completeness: division retains scan, quotient and remainder, then creates
shifted before freeing remainder. Its subtraction allocates only after that
free. Multiplication retains scan and result, and a modular add can retain
both its sum and reduced result. The old result is freed before the optional
second add. Both interiors therefore need at most four additional Words.

### Directory: disjoint preparation, decoded prefix and odometer

1. `high_power(expected, ...)` calls `digit_suffix`, hence `radix_power`, one at
   a time. `radix_power` retains divisor and power while division uses at most
   four more. Quotient/remainder cleanup precedes the generator yield; closing
   the generator frees its two residents. This phase peaks at six.
2. `old_prefix` decodes exactly one residue Word at a time. It serializes and
   frees that Word before the next one. The saved prefix is a Tape, not a
   numerical high matrix. It completes before constructing the new Odometer.
3. The Odometer allocates d² distinct Words. Appending digits and advancing
   their in-place carries allocate none. Its whole matrix is freed before the
   next old prefix is decoded.
4. `expected`, `emitted`, `outer` and `remaining` are Count/Counter tapes.
   The borrowed old-field Word is copied to a counter tape, not another arena
   Word. No index allocation occurs.

The total additional numerical peak is max(6,1,d²)=max(6,d²). It is exact on
every successful admissible call: d>=1 forces at least one `radix_power` with
M>1; its first division performs a digit step while two generator residents
and four division residents coexist. Positive old count forces allocation of
a full d² Odometer. This is an all-parameter written source argument, not an
extrapolation from the seven finite fixtures. All temporary numerical Words
are freed on successful return, and entry values and heads are restored.
The returned directory and count still occupy nonnumerical tapes.

### ADD: callback, multiplication and block copies

At the start of each `traverse`, `prepare_coefficient` runs before x or any
stream-owned numerical temporary exists. Its returned coefficient then stays
live throughout that traversal. `outer`, `sources`, `mid`, `blocks` and `bits`
are Counter tapes; payload copying allocates no numerical Words.

For each x the loop retains the coefficient and x. `ring.multiply` adds at
most four Words, giving six. After multiplication only offset remains, and
`subtract_exact(M, offset)` adds leading, giving four total. The complete
middle/block loops retain exactly coefficient, x, offset and leading. Offset
and leading are freed before the next x. The last x and coefficient are freed
before the merge traversal calls the callback again. The final live sets and
borrowed numerical values/heads therefore equal the entry state.

Six is attained at M=5, c=2, x=3: the multiplication's final optional add
reduces 4+2 modulo 5 while scan and doubled are retained. More generally, for
c>=2 multiplication with x=M-1 contains at least one reduction: c*(M-1)
is not below M, while multiplication's prefix recurrence would keep its
integer value unreduced if no reduction occurred. At some reduction cut the
four multiplication Words coexist. If c is zero or one, every multiply takes
a fast path and the complete block-copy interval still has four Words. The
positive extents ensure that interval is reached.

Both callback entries have the same B_R,B_I baseline. Thus the coefficient
phase and stream phase give max(R,6),I, not R+6,I. For an occupied-content
upper bound, let b_R,b_I be the two `Arena.bits` widths and include both
permanent templates:

```
(B_R + max(R,6) + 1)*(b_R+1) + (B_I + I + 1)*(b_I+1).
```

For directory production replace max(R,6) by max(d²,6) and I by zero. These
formulas exclude LEFT markers and erased backing capacity. They count encoded
symbols, not Python heap objects or a full physical allocator.

### Conditional extension across an entire adapter ADD

In [PR2801's pinned caller domain](https://github.com/CrocSwap/integer-mult-bounds/blob/e2564b80b86fb77610b4b78701e5446a76fbe962/research/selected-adapter-caller-entry/README.md),
the suspended caller contributes exactly (0,12) additional numerical Words
above all `Consumer.apply` entry residents. Its packet counters and saved
fields are tapes; that caller remains suspended throughout each adapter ADD.
Inheriting PR2781's local callback allowance (37672,22), the present theorem
therefore gives

```
(0,12) + (max(37672,6),22) = (37672,34)
```

throughout each complete adapter `stream.add_pass`, including both callbacks
and intervening arithmetic. This retains PR2801's width range 64 <= n < 128,
dimension 64, source/encoding contracts, prior-callee cleanup and observer
conditions, plus the fresh-result, equal-coefficient and numerical-neutral
payload-factory premises above. PR2781 is pinned there at
`9fdbd4b0429dbfcb4569f7768b66d318deacab6b`; its callee bound is inherited,
not recertified here. This corollary excludes preceding `Layout.extents`
construction, other caller phases and failure recovery. It asserts no sharpness
for the composed bound and no whole-caller reserve. The separate specialist
checked this lifetime composition as well as the two phase proofs.

### Explicit failure boundary

Neither entry point promises automatic exception rollback. In particular,
`old_prefix` calls `read_word` before entering its per-word cleanup block;
malformed data can leave the newly allocated Word live. Odometer allocation
also starts before the enclosing cleanup block. ADD has no encompassing
`try/finally` for a rejected callback or traversal. The independent checker
retains literal failure witnesses. Callers requiring recovery must supply and
prove rollback; success-only restoration must not be promoted to that guarantee.
A mismatched callback value can also yield an unintended permutation despite
source acceptance. That is why the repeated-value premise is explicit.

## Exact finite evidence and reproduction

```
python3.12 -I -B scripts/research_package.py --package research/selected-stream-directory-numerical-audit
python3 -I -O -B research/selected-stream-directory-numerical-audit/verify.py
python3 -I -O -B research/selected-stream-directory-numerical-audit/independent.py
```

The last two work in a Git-free export. `verify.py --emit` prints a fresh
receipt; ordinary replay is read-only and compares every typed field of
[RESULT.json](RESULT.json). No generated bytecode or predecessor receipt is an
acceptance oracle. The registered replay also runs the external corruption and
mathematical controls in `test_verify.py`.

The main checker executes the unchanged six-module source without replacing
payload loops or arithmetic. It checks 228 complete ADD calls / 25,500 payload
bits / 18,542 residue allocation events. The 152 one-hot basis cases cover
every input position for every canonical coefficient at M=3 and 5, with unit
spectators. Because the source only copies opaque bits, that establishes all
Boolean inputs for those finite shapes. The other cases cover every coefficient
at M=3,5,7,9 with three positive spectator profiles, plus callback peaks 1,6,7,19
and index peaks 0,2,3,5. These are finite fixtures, not a full selected GL64 run.

Seven complete directory fixtures use dimensions 1,2,3,64, q=3 or 5, widths 1 or 2,
depths 0,1,2 and old multiplicity 1 or 2. Independent integer/lexicographic record
construction checks every emitted symbol, multiplicity and original prefix.
The dimension 64 fixtures attain 4096 with one high lift; their 16,388 and 98,328
serialized output symbols are fully checked. They do not enumerate a large
prime or a multi-lift dimension 64 directory. Literal occupied-cell scans check
the content formula at selected allocation peaks. Every successful fixture
checks all borrowed numerical values/heads/live sets and literal slot erasure.

Underbudget controls reject five stream residues and 4095 directory residues;
callback controls detect borrowed results, leaked Words and unequal-value
semantic defects. Separate integrity controls alter source/manifest/receipt
bytes and install an effective stale bytecode sentinel. [INDEPENDENT.md](INDEPENDENT.md)
and `independent.py` are by a separate math-storage-lifetimes AI specialist,
without importing this checker. Neither review is human or formal-kernel proof.
Final run commands/environments and exact independent coverage are recorded in
[VALIDATION.md](VALIDATION.md).

## Scope, overlap and credit

The random catalogue draw was adversarial-audit / selected-stock-envelope.
The scope is explicitly changed to the concrete PR2801 numerical-phase handoff;
no selected complex m73 bootstrap coefficient is computed. The result provides
components for a later same-baseline caller proof. Do not add sharp component
constants unless their lifetimes overlap, or assume excluded resident categories
are zero. Layout construction, validation Callback, child invocation, other
primitive passes and broader caller lifetimes remain to be joined.

Base db3edc00f732806f663bfb9d4000567f18b17386, priority 5; selection and refresh
hashes are in TASK.json. Initial full overlap covered 730 open PRs including
drafts, 1,444 Discussion/comment/reply records and 1,985 local records, with complete
pagination and no warnings. The submission refresh completed at 22:41:54 UTC,
covering 734 open PRs, 1,448 Discussion/comment/reply records and 1,985 local
records, with complete pagination and no warnings. Its five focused matches
were the credited coefficient results, our own claim, the child handoff and
an unrelated arithmetic package. These are metadata searches, excluding
arbitrary diffs and unpublished work, not novelty
certificates. The canonical claim is [Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18960033).

New work: Ross Richardson with substantial OpenAI Codex assistance and a
separate math-storage-lifetimes specialist, Apache-2.0. Credit Jose
Manuel/jmbarrancoml for the original runtime; Nick Petalas for PR2759's primitive
bound, PR2770/2778/2781 numerical components and PR2801's caller boundary and
handoff; Arham Tahir for PR2796's distinct child lifecycle; David Arias for
PR2753's earlier coarser all-size logical inventory. The full runtime notice
is preserved. None of those constructions or primitive scratch bounds is
claimed as new here. No selected record or historical scientific input changes.

## Open next questions

1. Join these two phases with the adapter/child coefficient bounds and all
   remaining `Consumer.apply` phases under one entry-resident convention.
   First inventory initialization, Geometry/Layout construction, callback
   validation and every non-ADD primitive. Missing simultaneous lifetimes,
   rather than the two phase constants proved here, block that composition.
2. Bind a complete composed numerical ledger to actual physical slots,
   templates, markers, saved parent banks and movement. The current theorem
   counts occupied numerical contents only; payload/count/control/directory
   tapes and retained backing capacity remain separate obligations.
3. If failure recovery is required, wrap and verify the precise failing
   allocation/callback sites. The existing successful endpoint contracts do
   not supply exception rollback.
