# A literal Word lifecycle for the current CRT source

The current CRT arithmetic package [#7596](https://github.com/CrocSwap/integer-mult-bounds/pull/7596)
leaves Word allocation, copying, retirement and its finite owner binder as
supplied services. This package implements that local lifecycle on fixed tapes.
It also matches the two reservation contracts used by the existing arithmetic
graph. **No new kappa; all five foundational assumptions remain.**

One fixed graph stores the ordered free stack physically, preserves the eight
protected owners, allocates the exact top slot, copies complete Words, and
erases a Word before returning its owner to the stack. It uses no host free
stack to choose a result. Heads return, selectors retire, and physical history
is retained after erasure. Higher source control and initial physical grants
remain supplied.

The graph has 130,936 fixed R/W/M/J/H locations. Its local inventory is the 64
Word roles, the retained template, one 338-cell stack, and two eight-cell
selectors. It shares the latter with two existing arithmetic selectors, giving
a compatible 70-role union. The complete arithmetic graph is not replayed in
that union here: actual-source tests use retained raw arithmetic with the new
lifecycle, and the arithmetic reservation join has a separate modular proof.

For `P >= 4` and `m` free slots, exact successful counts are:

| Service | Instructions, excluding a source setter |
|---|---:|
| Reserve one blank owner | `36m + 155` |
| Allocate zero | `165P + 36m + 417` |
| Copy a live Word | `287P + 97m + 676` |
| Erase and release a Word | `160P + 61m + 409` |

A source setter costs 31 instructions. INIT costs 2,744 and complete metadata
retirement costs 1,395. [PROOF.md](PROOF.md) derives these counts and the
universal trace invariant, gives the paid liveness/reservation bills, and
keeps all previous physical extents in the storage charge.

## Reproduce

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/literal-crt-word-lifecycle
```

The registered source-history check needs the exact predecessor commit in
the local Git object store. If it is absent from a fresh checkout, fetch
only that pinned history before running the registered command:

```sh
git fetch --depth=1 --filter=blob:none https://github.com/CubeJerry/integer-mult-bounds.git ee6005fe241ab947e511fe9f6d86f5f4fa58478b
```

The standalone commands below use the vendored, hash-authenticated inputs
and do not need a network connection or predecessor checkout.

The direct standalone commands are:

```sh
python3 -I -B research/literal-crt-word-lifecycle/source_check.py
python3 -I -B research/literal-crt-word-lifecycle/verify.py
python3 -I -O -B research/literal-crt-word-lifecycle/verify.py
```

The primary verifier authenticates eight retained inputs, checks 4,544 primitive
packets, a seeded 360-operation trace with long retained histories, three complete
pinned current numerical producer calls, and ten controls. Original
Arena.zero/copy/free and Word.erase providers are unavailable during the
positive producer/consumer runs. A returning wrong-owner mutation is detected
even though its heads and selectors are restored. The complete typed receipt
must match [RESULT.json](RESULT.json).

The proof covers all admitted precisions and legal stack histories. Finite
execution is corroboration. No human or formal-kernel acceptance is claimed.

## Open next questions

- Execute the existing #7596 arithmetic graph and this lifecycle together on
  the same owners. Begin with aliased ADD, two-output division, release and
  reuse; preserve each physical selector identity and update the common invoice.
- Attach and retire one lifecycle stack through the actual changing-Entry
  iterator. Begin at a completed result boundary; initial framing, grants and
  the whole iterator's control remain prerequisites.
- Lower the higher numerical controller and its finite return state. The new
  Word services remove one dependency, but do not compile its loops or records.

Detailed scope, source pins and next-step blockers are in [TASK.json](TASK.json)
and [SOURCES.json](SOURCES.json). The scientific base is
`e54523517d0f03e58352e647c403a5af3e525a57`; the immediate source head is
`ee6005fe241ab947e511fe9f6d86f5f4fa58478b`.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
JoyboyBrian's original CRT/Word/entry work and the literal arithmetic
predecessors retain their credit; see [NOTICE.md](NOTICE.md).
