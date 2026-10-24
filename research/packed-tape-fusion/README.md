# Packed tape reads and writes in 17 instructions per tape

This contribution is produced by Nick Petalas.

A selected packed tape cell can be read and overwritten in 17 successful RAM
instructions, including address computation. Read each of k tapes before any
write, retain four observations per tape, and the access bill is exactly 17k.
The separately emitted GET and SET macros in Dugongue's
[PR #4538](https://github.com/CrocSwap/integer-mult-bounds/pull/4538) cost 13k+17k=30k.
The new local schedule eliminates 13k instructions. This is a scoped construction
proof with finite executable corroboration. It is neither an optimality theorem
nor a new multiplication bound.

The contribution isolates a small part of the predecessor's complete-packed-backend
next question. Its representation and machine semantics are cited premises;
rechecking those results is not the deliverable. The XOR bit-field identity is
standard. The new repository result is the retained-read contract, explicit
instruction schedule and cost reduction at a simultaneous-read boundary.

## Contract

Fix k>=1 tapes, c=2^ell bits per field, B=2^b fields per word, H=2^h>=2k,
and a data base R above every control/cache register. For tape i with signed
head z, set u=z if z>=0, otherwise u=-z-1, and tag=2i+[z<0]. Its word address
and field offset are

```
a = R + H floor(u/B) + tag
offset = c (u mod B)
```

Assume cB<=w, u<2^w, a<2^w, and every register, literal constant and effective
address fits the w-bit machine. The packed data can contain arbitrary dirty
words, including arbitrary unused high bits and arbitrary unselected fields.
The symbol selected for writing satisfies 0<=new<2^c.

The read phase keeps a, offset, the loaded word W, and the old selected field
s=(W>>offset) AND (2^c-1) in separate registers for each tape. The intervening
finite dispatcher may read the old symbols and compute new symbols. It must
preserve these four caches, shared B metadata and all packed data words. Its
registers must be disjoint from the cache registers. Its actual instructions
are paid separately. These assumptions permit a usual finite TM dispatcher
that reads all tapes before writing any tape.

After the dispatch, commit each tape exactly once. Heads can then advance.
The result has exactly the chosen new symbol at each selected position and
preserves every other data bit. Cache/scratch registers are clobbered; this is
not a reversible dirty-workspace restoration claim.

## Four-instruction commit and proof

The emitted commit uses register operands throughout:

```
xor    delta, old, new
shiftl delta, delta, offset
xor    word, word, delta
store  address, word
```

Let M=2^c-1. Write W=L+2^offset s+2^(offset+c) U, where
0<=L<2^offset and 0<=s<=M. The three summands occupy disjoint bit ranges.
Since both s and new are c-bit values, delta=(s XOR new)<<offset is confined
to the selected field. Consequently

```
W XOR ((s XOR new)<<offset)
    = (W AND NOT(M<<offset)) OR (new<<offset).
```

This proves replacement and preservation of every other bit. It also proves
that the shifted delta fits in w bits, so modular word writes introduce no
additional truncation. All four instructions are successful, with no branch
or halt instruction in this straight-line block.

Different tapes cannot select the same packed word. If two addresses agree,
H(t-t')=tag'-tag; the right side has absolute value less than H, hence t=t'
and tag=tag'. Distinct tapes have distinct tags even when head coordinates
and sign banks coincide. Thus each commit sees the word retained by its own
read, and commits cannot invalidate another tape's cache. Applying the
single-field identity to each tape proves the simultaneous-read contract.
This argument is valid for arbitrary finite k and every word width meeting
the stated fit conditions. Finite replay does not establish that quantifier.

For a hand calculation, W=45, c=2, offset=2 has old=3. Replacing it by zero
uses delta=12 and returns 45 XOR 12=33, preserving the other four bits.

## Read schedule, cost and storage

The [emitter](fusion.py) allocates a 16-register slab per tape, starting at
r=8+16i. Shared registers 0 and 1 hold b and B-1. The slab has input index,
tag and new-symbol slots at r,r+1,r+2. The read uses nine instructions to
compute the address and offset, followed by four to load and extract the
symbol. The four caches occupy r+8,r+6,r+10,r+13. The commit uses r+14 as its
delta scratch. The dispatcher reads old symbols directly from r+13 and writes
new symbols directly into r+2, so the schedule needs no cache-copy instructions.

All reads precede all commits. The complete access count is therefore
13k+4k=17k, against the predecessor's separately emitted 13k+17k=30k.
This comparison concerns the stated macros and the same prepared-head ABI.
It is an exact instruction comparison, not a hardware timing measurement or
a globally shortest-program claim. For fixed k the new control space is
constant in input length. The provided layout chooses R to be the smallest
power of two at least max(128,8+16k), so the cache registers do not alias data.

B initialization, ABI/head preparation, dispatcher instructions, head updates,
input/output, allocation and full-machine halting remain separately paid.
For example, the executable two-tape symbol-swap dispatcher uses two additional
XOR instructions with a supplied zero register. Its complete read/dispatch/write
fragment executes 36 instructions, rather than the 62 for the separate access
macros with the same two-instruction dispatcher. This fixture includes actual
dispatch instructions, rather than an uncharged host-language swap.

The executable emitter intentionally supports 1<=k<=64, c<=16, B<=256 and
10<=w<=256 with cB<=w and checked address bounds. It does not inspect or obtain
w at machine runtime; w is a replay parameter. Extending the Python emitter's
validation limits is distinct from the unrestricted written identity.

## Evidence and reproduction

[RESULT.json](RESULT.json) is generated by the verifier and bound to SHA-256
hashes of all six proof, metadata and executable source files. It records:

- 592,308 exhaustive scalar field-replacement cases at widths one through ten.
- 6,000 emitted multi-tape fragments, executing 1,598,000 access instructions.
- Tape counts 1,2,3,8,16,64, field widths 1,2,4,8,16, word widths
  16,32,64,128,256, and all fitting power-of-two block sizes through 256.
- A literal two-tape simultaneous-swap dispatcher with a 36-instruction bill.
- Twelve invalid-input rejections and four semantic mutation controls.

The fragment oracle uses direct mask-and-replace and an independent signed
coordinate/address calculation. Every data word present in the fixture,
including an unrelated spectator word, is compared after execution. Control
registers begin dirty apart from the prepared ABI. Directed heads include zero,
minus one and both sides of a block boundary. The other cases are deterministic
random fixtures, not exhaustive claims about all such configurations.

The mutation controls omit delta preparation, use the wrong shift, clobber the
cached old symbol, and change the data word after reading. The last control
shows why the cache-preservation premise is necessary; this construction does
not permit intervening writes to another field in the cached word.

From the repository root, with the supplied interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/packed-tape-fusion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/packed-tape-fusion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/packed-tape-fusion
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/packed-tape-fusion --check-source-history
```

On another host, substitute its CPython 3.12 path. The standard library is
sufficient. The standalone verifier also runs in a Git-free package directory;
Git is required for the repository metadata and publication preflight. Explicit
`--write` regenerates the receipt. Normal verification never rewrites it, and
all correctness checks remain active with optimized Python.

## Scope, sources and code constraints

The base is canonical main `624de9dc66858af0945e5f8a0942488d62280d43`, priority
revision 7. [TASK.json](TASK.json) changes `uniform-transfer-audit` from an audit
of #4100 to this constructive access improvement. [SOURCES.json](SOURCES.json)
pins the originating card, selected context, predecessor packed contract,
macro source and actual RamStd semantics as provenance. None is a runtime input;
the new emitter/verifier is self-contained. Selected-source orientation passed
with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. The historical baseline command in
the old card was replaced by the current selected baseline as directed by the
current priorities. No predecessor numerical replay is claimed.

The overlap snapshot covered 395 open PRs and 3,895 discussion records, with
complete remote pagination. Sparse local coverage omitted 6,200 tracked note
paths. Separate all-main README searches and merged-PR searches covered the
packed representation, retained fields, read/write fusion and four-instruction
commit terms. No absent search hit establishes novelty by itself.

Code has no recursion or dynamic evaluation. The emitted blocks have fixed
length. The replay limits code to 2,048 instructions, k to 64 and words to 256
bits. Functions are under 60 lines. Explicit contracts remain active under
`-O`. Managed Python necessarily allocates during execution, a Power of Ten
rule-3 deviation: each fragment has at most 4,096 memory entries, 2,048
instructions and 256-bit words, and fragments are processed one at a time.
The scalar census has explicit finite ranges and retains only a counter.
No hard-real-time or allocation-free Python execution is claimed. A fixed-array
backend is the next step only if that execution property is needed. Higher-level
finite fixture data and receipt serialization are likewise bounded by the
literal verification ranges. No third-party linter/type checker is required;
warning-strict normal and optimized runs are registered diagnostics.

A full packed TM compiler, a physical multiplication caller, Lean refinement,
initialization and IO composition, precise whole-program constants, any RAM
exponent improvement and a complete multiplication theorem remain unclaimed.
The selected frontier is unchanged. Research stops at this first local saving.

## Open next questions

1. Install these slabs in one complete packed compiler, including its actual
   dispatcher, signed head updates, input/output and genuine halt. Start with
   one transition of Dugongue's unpacked compiler and preserve the four cached
   observations through its dispatcher. The missing full emitter is the blocker;
   a local access saving alone does not settle its complete cost.
2. Determine whether a caller needs multiple selected fields in the same word.
   Start by specifying all reads, the write order and a live-word versus retained
   word policy. Cache invalidation is the blocker. The present distinct-tape
   contract deliberately excludes that aliasing pattern.

The structured versions are in [TASK.json](TASK.json).

## Credit

This contribution is produced by Nick Petalas. Dugongue supplies PR #4538's
packed representation, original GET/SET macros, finite TM compiler and open
backend question. The retained RamStd/Problem 1.8 formalization supplies the
machine model; Szymon Torunczyk's compositional simulation and the predecessor's
credited compiler and physical/native/precision lineage remain predecessor
credit. PR #4541's Hopcroft, Paul and Valiant logarithmic-window simulation,
PR #4630's native assembly and PR #4724's portfolio comparison are separate
context, not results re-established here. All predecessor source notices are
unchanged. New work is Apache-2.0. Independent human and formal proof-kernel
review are unclaimed.
