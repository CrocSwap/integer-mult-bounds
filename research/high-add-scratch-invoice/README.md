# Ordered high-field ADD: exact scratch and a complete linear tape bill

For the unchanged PR2915 `kernels.added`, with odd high modulus Q>=3,
canonical positive extents B,M,S and coefficient in {-4,-2,-1,1,2,4}:

- Exactly **10+[S>1] free scratch roles** suffice and are necessary.
- **Six additional numerical words**, above all entry residents, suffice;
  one complete fixture attains six.
- With V=BQMQS, complete local physical reads/writes/unit moves are at most
  **4096V**, including encoded coefficient arithmetic and pool acquisition.
  Clearing the returned output gives the convenient bound **4102V**.

[PROOF.md](PROOF.md) derives the all-parameter result and an exact
non-arithmetic invoice. It also gives an occupied-content bound, separating
borrowed state, markers and retained backing. An empty split still costs a
countdown, priced by the zero case of PR2877's countdown identity (four
operations beyond the positive formula). The output is separately owned;
borrowed source, counts and entry roles are preserved, and all other new
roles close.

This answers the **ordered high ADD component** of Nick Petalas's
[PR2982 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18977416).
The claim is in [discussion #2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19001907). The contribution is a scoped proof and
independent source-bound audit, not a whole-stage stock coefficient or a new
kappa. Fixed-control machine steps, initial markers/templates, enclosing
high-bank setup, reversed-field B1 swaps and complete caller storage remain
separate charges. No source construction or selected record changes.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -I -B scripts/research_package.py --package research/high-add-scratch-invoice
```

Expected primary output:

```text
PASS_HIGH_ADD_SCRATCH_INVOICE cases=109 payload_bits=37241 scratch=10,11 numerical_extra<=6 io<=4096V
```

The registered commands also run ten optimized behavioral control groups.
`--check-only` validates package metadata and source pins. Direct verification
is `python3 -I -B research/high-add-scratch-invoice/verify.py`; `--emit` prints
a fresh receipt without replacing the committed [RESULT.json](RESULT.json).

The 109 complete packets include four occupied-pool cases and all nine
Boolean basis columns of one complete Q=3 packet. Their exact endpoints use
an independent modular address oracle. All source traffic is observed on raw
physical tapes and checked against unique physical-object meters; Word/Lease
alias meters are not added again. Fifty-one countdown fixtures include zero
and padded inputs. Thirty-six separate arithmetic checks reach 82-bit words
without materializing the corresponding huge packet.

Meaningful controls cover insufficient stream/numerical capacity, wrong
coefficient, endpoint-preserving cost mutation, noncanonical input padding,
the zero-count correction, source corruption and typed receipt corruption.
These are local source checks and a written proof, not independent human,
formal-kernel, full selected GL64 payload, selected cold-replay or hosted-CI
verification. General failure cleanup is not established.

## Sources and scope

Scientific base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
PR2915 author head: `fecc5a87574df441ddc3dad44f99fca9bd7fdd92`.
The loader authenticates the complete retained PR2899/PR2809/PR2753 source
archives before executing the original modules. Live transitive inputs are
declared in [SOURCES.json](SOURCES.json) and [VERIFY.json](VERIFY.json).
The selected-record compatibility adaptation on main is inherited and is
not described as byte-identical to the original author source. No retained
file or archive is rewritten.

The `selected-stock-envelope` card is explicitly **changed** to this named
local reserve/time implication. Cutoff comparisons, the earlier conditional
8194/6748 coefficients, the lcm-wrapper fit and PR3113's m=73 source gap are
not repeated. [TASK.json](TASK.json) records the task, exact dependencies,
overlap, expansion decision and remaining obligations.

## Open next questions

1. Bind the **remaining single-cube setup and operations** to this invoice.
   Start with `high_route.extents/execute`, preserving initialized-bank costs,
   owned intermediate outputs and the two swaps on reversed ADDs. This closes
   the next part of PR2982's tariff handoff; native B1 contracts and the other
   kernels' complete bills remain dependencies.
2. Join the source-level role/content bounds to **physical backing and a caller
   stock ledger**. Start at the same chronological cuts, retaining all entry
   roles, marker/template provisioning and native inventories. Local occupied
   content and exact I/O do not establish full caller capacity or a uniform
   selected-stage reserve. No construction-family expansion is proposed here.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
OpenAI Codex (GPT-6 Astra) performed the derivation, implementation, checking
and writing; no independent human review is claimed. New work is Apache-2.0.

Jose Manuel/jmbarrancoml supplied PR2915's actual kernels, PR2899's physical
arena, PR2809's scratch specialization and PR2157's factor words, with the
retained PR2753 logical caller by David Arias. Nick Petalas supplied PR2982's
prefix-wrapper tariff and released handoff, and PR2968's separate scaling/pool
invoice. Arham Tahir's PR2877 supplies the all-width countdown identity,
including its zero case; ywz65's PR2473 derived the same Counter bill, and
the unpooled ADD's exact payload bill, earlier. The invoice here adds pool
acquisitions, the one-bit-suffix path and the marginal lifecycles. Ross
Richardson's PR2810 proves the six-Word `stream.add_pass` bound outside
callbacks for the same `stream.py`; the six-slot statement here composes it
with the actual coefficient callback. Nick Petalas's PR2905 and PR2923 bound
the Counter and joint backing of the same ADD; the occupied-content corollary
is separate from them. The new content is the exact pooled scratch inventory,
the complete ordered-ADD invoice and the explicit 4096V bound.
The numerical arithmetic, ywz65's parking work, this account's PR2399
substitution algebra and DreamingOfClouds' selected PR589 on eumemic's
PR555/source527 lineage keep their original attribution and notices.
