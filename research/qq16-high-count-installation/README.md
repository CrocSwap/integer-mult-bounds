# Exact scratch and installation bill for the QQ16 high count

The retained `Machine.new_context` constructs the high-field count, installs it
in a permanent `highs` Tape, retires its temporary storage, and replaces the
temporary Count by a view of that fixed Tape. This package supplies a
source-bound proof and independently computed operation bill for that boundary.
It resolves one numerical producer obligation left separate from the metadata
work in PR5034/PR5330; it is not a complete QQ16 frontend or supplier.

## Result and domain

Let `q >= 2`, `w >= 1`, `d >= 1`, and `M=q^w`. Assume the retained Ring's
canonical modulus encoding, sufficient numerical arena capacity, the fixed
source vocabulary, and an empty ScratchPool on entry. All source numerical
operations must complete successfully. Then:

1. `Context.cap=M/q` and `Context.highs` initially represents
   `H=q^((w-1)d^2)` in canonical binary, followed by one RIGHT delimiter.
2. Constructing and installing this Count acquires exactly two temporary Tape
   leases, with peak simultaneous occupancy exactly two, independently of
   `q,w,d` and the bit length of H. They are both retired on success. This is
   a bound on **temporary stream roles**, not their backing length, numerical
   registers, all Python objects, or the total constructor time.
3. Put `n=bit_length(H)+1`, including RIGHT. If the fixed destination has a
   dense old body of length `D` and both heads start at their canonical origin,
   the literal `save_count` installation costs exactly:

   | Physical operations on source and destination | Count |
   | --- | ---: |
   | Reads | `7n + 2D + 10` |
   | Writes | `2n + D` |
   | Unit head moves | `6n + 2D + 14` |
   | Total | `15n + 5D + 24` |

   These counts include destination clearing, all rewinds, copying, source
   clearing and the second idempotent lease close. They exclude producing H,
   pool selection/control, metadata assignments, and allocating the fixed
   destination/pool. Such costs are not assumed zero.
4. At exit `context.highs.tape is roles['highs']`, the Program view points to
   the fixed program Tape, and Context and Ring share the same Unsigned object.
   Program/spectator payloads and heads are preserved. Only modulus, one and
   cap remain live in the residue arena. An ended Count lease cannot erase a
   later borrower of the same physical role.

The actual `Machine.call` parks streams before `new_context`, so its highs
destination is empty (`D=0`). A fresh root also starts with an empty highs role.
The generalized D term makes the cost of overwriting nonempty storage explicit;
it does not remove the caller's parking obligation or promise to preserve the
old highs body. The full parent continuation is not replayed here.

## Source proof

All paths below are within the unmodified PR2809 archive nested as
`physical-gaussian-leaf/inputs/pr3087.tar ! inputs/pr3055.tar ! inputs/pr2899.tar
! inputs/pr2809.tar`. Complete repository input hashes are in SOURCES.json;
the verifier also prints hashes for the principal archive members.

In `inputs/pr2753/predecessor/vendor/cardinality.py`, `radix_power` repeatedly
divides M by q, hence yields exactly w times. `digit_suffix` skips its first
yield and multiplies a Count by q on each remaining yield. In `counts.py`,
`high_power` repeats this operation d^2 times and `high_count` starts at one.
This proves the displayed H; `directory.Context` computes cap by exact division.

`Count.literal(1)` first acquires an input Tape, then the `Natural` constructor
acquires the result Tape while the input remains live. It copies and normalizes
the result before clearing the input. Therefore two roles are necessary at that
instant and sufficient. The subsequent `high_power`, `digit_suffix` and
`radix_power` loops allocate numerical words but no further stream Tapes.
The constructor has just one live stream lease after `Count.literal` returns.

`macro_machine.Machine.save_count` invokes `commit(value.tape, 'highs')` then
`value.close()`. With distinct source/destination roles, `commit` clears the
destination, invokes `directory.append_tape`, rewinds the destination and clears
the source Lease. The second close sees `active=False` and performs no physical
operation. Directly counting the unchanged loops gives:

| Source operation | Reads | Writes | Moves |
| --- | ---: | ---: | ---: |
| Clear destination body D | `2D+3` | `D` | `2D+4` |
| `append_tape` for n cells, including source rewinds | `4n+3` | `n` | `3n+4` |
| Rewind destination | `n+1` | `0` | `n+2` |
| Clear temporary source body | `2n+3` | `n` | `2n+4` |
| Close ended lease | `0` | `0` | `0` |

For example, canonical rewind from head 1 takes two moves and one read;
rewind from the first blank after n cells takes n+2 moves and n+1 reads.
Summing the table proves the exact bill for arbitrary n and D, rather than
extrapolating from the finite fixture. `scratch_pool.Lease.clear` marks the
lease inactive and removes it from `pool.live`; a later invocation on that
ended lease returns before touching its physical Tape. This proves the reuse
property. Finally `new_context` installs `self.count('highs')` and a Program
view, neither of which allocates a Tape. These assignments prove the exit aliases.

## Executable evidence and limits

The checker executes unchanged source definitions and complete numerical
constructors. It loads the actual words, records, stream, cardinality, counts,
cardinal_counts and directory modules in separate namespaces. It extracts the
literal five Machine methods, `view`, `Lease` and `ScratchPool` definitions.
Only their module setup is supplied explicitly; it does not run the historical
selected-record loader, the full Machine constructor or a complete Ordinary.

For the reached allocation sites it performs the same Tape-global specialization
as `ScratchPool.install`, using the actual `acquire`/Lease operations and
forbidding additional physical Tape construction. It does **not** claim coverage
of the full installation hook, callback/default-argument adaptations or every
caller module. Fixture input loading, the observation wrapper and independent
decoding happen outside the charged algorithm. The wrapper records meters
without changing the source method bodies or Tape actions.

There are 81 cases across q in {2,3,5}, w in {1,2,3}, d in {1,2,4}, D in
{0,1,7}, plus q=3,w=3,d=8,D=31. The largest Count has 203 value bits.
The q=2 cases are reduced-source controls, not selected-geometry admission.
The q=3,w=2,d=2,D=0 witness constructs H=81, n=8 and incurs exactly
**66 reads, 16 writes and 62 moves** during installation.

Each case checks source value/encoding, cap, aliases, canonical heads, no
temporary numerical words, scratch cleanup, dirty spectators, the exact bill,
subsequent reuse of the same scratch role and final owned cleanup. Three
executed rejection controls cover one insufficient scratch role, closing the
Count before copying, and installing the wrong fixed Tape view. Three arithmetic
discriminators distinguish d^2 from d, a one-read undercharge, and dirty versus
empty destination costs. Normal and optimized Python use explicit checks.

This result does not give a numerical-word running-time bound for producing H,
a storage/backing bound, a lowering of `new_context` metadata, complete schema
initialization, exceptional-path cleanup, native/precision/outer admission,
complete F(K), a D* versus B* comparison, or a new kappa. Uniform statements
above are written source arguments with finite corroboration, not formal proof
kernel or independent human acceptance.

## Reproduce

From the repository root with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/qq16-high-count-installation --check-only
python3.12 -B scripts/research_package.py --package research/qq16-high-count-installation
```

The registered replay runs both normal and optimized modes. A direct replay is
`python3.12 -B research/qq16-high-count-installation/verify.py`; it takes about
one second locally. An official export includes all explicit source inputs and
can run that direct command without Git or network access.

## Overlap and attribution

Base: canonical main `7c472563474e60185e6ca101a17622133d047e56`, priority 7.
The selected source-bound orientation passed; it is not a cold native replay.
The initial complete search covered 305 open PRs, 4,634 Discussion records and
all 7,267 tracked top-level README/TASK notes. It found the concurrent
[restore_context claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19152880).
This package changed scope to the complementary numerical producer, as recorded
in the [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19152915).
No result is claimed for the abandoned restoration draft. Searches exclude
unpublished work and arbitrary historical diffs.

PR5034 supplies the return-cut graph bound; PR5330 supplies finite adoption and
the open constructor question. Neither is re-proved here. R437 descendant ingress
also reaches `new_context`; this package adds the exact scratch and installation
invoice, not a new ingress implementation. The count formula and source algorithms
are inherited. New work is the scoped obligation proof, exact meter decomposition,
source-bound test and failure coverage.

Credit Jose Manuel/jmbarrancoml's PR2753/PR2769/PR2809 physical caller, cardinality,
pool and parking sources; JoyboyBrian's PR5034/PR5330 and explicit handoff;
Chris R/Clear1nsight, Tekalign, ywz65, Mihir Srivastava and the retained QQ16/control
lineage. Prepared by Mihir Srivastava with substantial OpenAI Codex assistance
for source inspection, proof, checker and writing. Apache-2.0; all predecessor
archives and notices remain unchanged.

## Open next questions

1. Price the numerical-word work of the actual `Context` constructor. This is
   needed to turn the exact stream-installation charge into a complete producer
   bill. Start from the reached `radix_power`/`divmod` loops and retain their
   word-width and register-capacity hypotheses; their complete uniform tariff
   is the missing obligation.
2. Compose this producer with the concurrent finite-handle restoration frontend
   and real parent parking. Start at `Machine.call`'s stream park and saved slot
   header, then verify the complete constructor-to-return lifetime. Metadata
   lowering of numerical creation and the full caller/parking price remain open.
