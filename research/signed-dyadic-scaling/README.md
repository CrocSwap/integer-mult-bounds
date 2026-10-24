# Complete signed-dyadic scaling on literal fixed tapes

This supplies the entire `unit_scale` coefficient class in the actual
helper462/frame506 route of PR4989:2,1/2,-1,-2,-1/2 modulo every runtime
odd Q. It covers all80 literal source sites at f=1 and the source's
80f² sites in S8 tensor I_f, with N=8f. No new kappa is claimed.

Ten fixed finite tables provide both a source-preserving separately owned
output and a true ORIGINAL-OWNER in-place interface. They use fourteen
tapes, seven symbols, scanned-symbol branches, one-cell writes, unit head
moves and fixed jumps only. They take canonical binary P,Q,S descriptors
and transform an arbitrary complete [P]x[Q]x[S] Boolean stream. Every
descriptor/spectator and head is preserved; all eight private tapes return
blank at their original independently translated origins.

The in-place version first gathers the whole source into two owned
buckets, then rewinds and overwrites the same original physical owner
while consuming the buckets. It pays for storage, all copying, the owner
rewind and full erasure. It assumes no free bank swap, productive clean
owner, source retirement, runtime scalar inverse or address oracle.
Doubling/half use inverse split/interleave procedures; negation reverses
records while keeping every record's S bits in order. Negative doubling
and half link completed stages with returned private work.

[PROOF.md](PROOF.md) proves the all-size endpoint and full conservative
bound: **2048V transitions and64V visited cells**, V=PQS, including setup,
cyclic direction, runtime counters, all record motion, both signed stages,
owner installation, rewinds and cleanup. Cleared work stays in the space
bill. Invalid inputs need not be cleaned; initially blank owned tapes are
a contract premise, not certified by checking one origin.

## Evidence and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/signed-dyadic-scaling
python3.12 -I -W error -B research/signed-dyadic-scaling/verify.py --mode independent
python3.12 -I -O -W error -B research/signed-dyadic-scaling/verify.py --mode primary
```

Both retained disjoint PR2776 interpreters execute exactly the same emitted
tables; the new coordinate-scatter oracle imports neither kernel. The
bounded suite has560 interface/coefficient executions and16040 payload
bits, including all basis columns at Q5 with3bit records, nontrivial
prefixes, odd composite moduli, Q1 and independently translated tape
origins. All80 actual source coefficients are separately executed at
the source's actual Q=5³=125 with compressed spectator extents;30 complete
in-place inverse roundtrips preserve every physical owner, descriptor,+spectator, private cell and head. The actual source assignment and complete
coefficient inventory are byte/AST-bound. Huge actual P/S extents are not
materialized in these finite tests.

Controls reject invalid/noncanonical/even moduli, wrong coefficient or
missing signed stage, nonlocal movement, corrupted output, retained work,
source drift and endpoint-preserving uncharged extra transitions. The
typed scientific receipt and complete tables are compared exactly.
Seven actual relocated CLI tests also execute both engines normally/optimized
with Git absent and verify unchanged bytes. They reject source, table and
Boolean receipt drift. Three semantic code mutants regenerate their tables
and still fail the actual owner/cleanup contract: missing Q-counter tail seek,
missing in-place owner rewind, and missing negative-prefix cursor positioning.
Normal verification writes nothing. `--write` regenerates only TABLE.json.gz
and RESULT.json. Both sources and decompressed table/receipt content are
proof-relevant; a recompressed gzip stream is not a mathematical invariant.

## Complete source-family ledger and stop

For site volumes V_j the new scaling contribution is bounded by
2048 sum_j V_j transitions and reusable64 max_j V_j visited capacity.
At common volumeV, all80f² scaling sites cost at most163840f²V. These
are sufficient physical charges, not optimized invoice terms.

The whole source still has224f² ordered shifts (160f² later-target,
64f² earlier-target),80f² ordinary high swaps,2N² low-controlled carries,
two finite low-type commits and one canonical native invocation. A borrowed
swap still needs two raw-body calls, three body additives, an older-high
interchange and complete borrow/pad/return/unpad. Full header/descriptor
and low-cache producers, packet-layout installation, general ROW allocation,
earlier-target routing, native/raw/older suppliers, whole#4814 matcher
coverage, P3 reserve/recurrence/stock/precision thresholds and supplier/outer
admission remain unknown. They are never priced as zero.

Family decision: **NARROW** to this completed full operation class. The
original physical owner return is established at the declared complete
stream interface; installing that representation in the full recursive
owner bank remains the caller's job. A new small coefficient fixture is
not another research result. Stop here until a different exact remaining
contract and complete allowance are selected. No selected frontier changes.

## Source and credit

Scientific base f259dabc7d70e0db8d6d36bfda888f008bbfecc1, priority7.
PR4989's PROGRAM/generator/interpreter and proof, plus the retained
PR2776 machine/counter/copy/dense-interpreter sources, are live authenticated
inputs. The pending PR5019 at39f3cf9fb4f2e495a716c7b501ea3bceb6b2a748
is contextual predecessor work: it implements the complementary later-target
affine shear and leaves unit_scale open. No code or Git object from that
pending PR is a dependency here. Frozen inputs are unchanged.

Credit David Arias/PR2776 for the finite machine, conversion, local copy and
erasure macros and both retained execution engines; Charles Bethin's unit
carry successor; Jose Manuel and the retained ordered-affine stream lineage;
ai-nanachi #4760/#4814/#4326, Chris R/Clear1nsight #4957, #4989 and #5019,
and all retained native/ROW/ordinary/stock/routing/precision/tape authors.
JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
No independent human or formal proof-kernel review is claimed.

Entry overlap at06:50:51/06:51:43UTC October23 covers320 open PRs,
4130 Discussion records and all6710 main notes. The eleven scaling leads
have no same physical-inventory claim; live#5019/#5007 and current board
claims were checked. Cached arbitrary-diff and unpublished-work limits
remain; no novelty guarantee follows. Publication refresh is recorded in
the PR. No Lean, Docker, full selected cold replay or unrelated historical
suite was run; passing finite tables is not full supplier admission.

## Open next questions

Bind the complete marked-stream representation and all P/Q/S descriptor
production to one actual recursive owner invocation, retaining packet
layout, ROW/cache costs and primitive dispatch. The in-place kernel removes
an owner-retirement oracle at its own boundary, but not the caller's missing
producer. Separately select one of earlier-target routing, low-type carry
production or finite low-type commit only after naming its full allowance.
Structured questions and blockers are in TASK.json.
