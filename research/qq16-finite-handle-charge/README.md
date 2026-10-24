# Conditional bounded-graph charge for QQ16 return control

This package gives an executable, explicitly charged **metadata controller**
for #4790's inventory checks and cache substitutions. It checks the actual
unchanged installed caller, including initialization and all return sites.
The cost theorem is conditional on a complete bounded source encoding; it
is not a production graph bound or a new physical QQ16 implementation.

For a contract size K, put Q=64K, w=bit_length(Q), and

```
A(Q,w) = Q(12w+3)+3w+1,
U(K)   = 1024K A(Q,w) + 4096K(16w+16).
```

Every word access pays a complete sequential Q-word scan with explicit w-bit
address comparison, selected bit copy, head movement and rewind. No Python
pointer, hash-table lookup or reflection is declared a unit-cost tape primitive.
Initialization, input-word copying and complete owned-store retirement are
charged. [PROOF.md](PROOF.md) states the model, elementary counts, source
encoding contract and remaining physical-embedding obligations.

Let C=511014Γ and S=336Γ be #4166/#4790's credited complete caller census.
The actual source has **1+2C validations**, **C+S cache exchanges** and a
conservative additional **C+1 finite binding budgets**. The first term includes
initialization; the final test-harness audit is excluded. The resulting bound is

```
B(K,Γ) = (4C+S+2) U(K).
```

The credited tape-action saving remains `C(11v+4)`. If F accounts for source
frontend/compilation/encoding and any remaining positive control charge outside
the stated kernel contract, a sufficient D* versus frozen D condition is

```
F + B(K,Γ) < C(11v+4).
```

**F is not assumed zero.** Neither a uniform production K nor a physical
embedding is supplied. This does not decide D* versus B*, execute production
O73 payloads, establish supplier admission or change κ. The bound deliberately
uses expensive scans and fresh scratch; it is not a performance recommendation.

## Why a constructor census is insufficient

The actual unchanged two-generation case executes 24 original-C calls: twelve
producer and twelve service calls in total, with the original per-generation
chronology `4 producer → 6 service → 2 later producer`. It produces 49 algorithmic
inventory validations, 147 owner traversals and 36 cache exchanges. The retained
verifier performs one additional final audit; the observer labels it separately.
All original endpoint bytes, guards, cleanup and the complete typed #4790 case
receipt remain unchanged.

The source object graph changes across phases. In the initial investigation,
the three different owners had 2,310 to 2,327 record Tape roles; this range
compares owners and does not establish tape allocation over time. Their graph
traversals had 5,017 to 5,054 edges. These are observations from reduced geometry,
not a universal maximum or a production inventory. The registered verifier
requires a same-owner vertex/edge/attribute increase over its initial graph,
furnishing a concrete
counterexample to replacing every traversal by its constructor-size census.
In the completed log, the same service owner grows from 5,033 to 5,054 edges
and 1,403 to 1,404 inspected attributes. Its 2,327 Tape roles remain constant.
Python object sharing can change vertex counts without changing semantics.

The replay instead enforces the explicit cap **K=65,536** on every complete
snapshot: the sum of three graph vertex/edge/attribute counts, all supplied
role-list lengths, plus one. Handles are persistent positive labels throughout the observed caller lifetime,
at most K; they are not reidentified independently at each check.
This gives Q=4,194,304 words and w=23 bits. Every current snapshot must satisfy
the cap; failure is a rejection, not an extrapolated successful invoice.
The enormous conservative upper bound is intentional and cannot justify a
speedup on the 512-bit reduced fixture.

## Executable boundary and independent checks

[kernel.py](kernel.py) executes encoded graph traversal with a visited-flag
array, complete engine membership checks, producer separation, ordered external
bindings, storage/acquisition exclusivity and finite cache substitution. It
performs no Tape payload read or numerical operation. Its host arrays simulate
charged sequential scans; they are not physical memory accesses of cost one.
The complete control trace includes zero filling, imports and cleanup, and
checks both the access and scalar-instruction upper bounds.

[observer.py](observer.py) independently encodes the actual three owner graphs.
It preserves the authenticated source's omission alphabet and checks exact
Tape encounter order against original `owned_tapes` at every site. The original
`ReturnProtocol.check_inventory` and exchange still execute after the kernel;
no source guard is replaced or waived. Current/auxiliary/acquisition fields
are all included. The one observer hook is inserted in #4790's **test harness**;
full AST comparison proves its removal recovers the unchanged harness. The
actual producer, service, native child and numerical sources are unchanged.

[check_bits.py](check_bits.py) is a separate bit-register/store implementation.
It expands the access path on 156 read/write cases, including address zero and
last addresses, and checks selected values, preserved other words, restored
head and exact instruction counts. It neither imports the primary charge
formula nor obtains counts by evaluating that formula. Twelve negative controls
cover every omitted snapshot field, an exceeded graph cap, insufficient handle
width, stale external order, a duplicate cache role, an out-of-range graph edge
and dropping later returns from the whole-source invoice.

The scalar-macro and residual-binding envelopes are written conservative
bounds, not independently executed physical lowerings. A producer of the encoded
source graph must prove that its own cost is included in F or in a separately
justified bounded acquisition implementation. The kernel cannot authenticate a
physical graph that its caller omitted. The read-only source observer checks
that implication only for the executed source case.

## Reproduction and provenance

```
python3.12 -B scripts/research_package.py --package research/qq16-finite-handle-charge
python3.12 -I -B research/qq16-finite-handle-charge/verify.py --log /tmp/qq16-control-log.json
```

The default replay is read-only; `--write` explicitly regenerates RESULT.json.
`--log` writes only the requested observation file, including every phase's
shape and charged counters. The receipt accepts a bounded current trace rather
than requiring incidental Python object-identity sharing to reproduce exactly.
Normal and optimized registered commands run the same explicit guards.

SOURCES.json binds 144 live inputs. The inherited loader retains its original
hash checks and exact historical selected-record projection. No selected record
or frozen source is changed. Exports need no Git or network. No full historical
suite, production replay, Lean or Docker run is required.

Base `b91956876e5b4122fd89179f1b57557ff8378f15`, priority revision 7.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19138319).
Entry overlap covered 317 open PRs, 4,064 Discussion records and all 6,636 base
local notes. Closed arbitrary diffs and unpublished work are outside that
coverage. #4949's arrangement audit and #4956's portable integration are credited
completed work; they are not repeated or superseded by this cost certificate.

## Credit

JoyboyBrian's #4790 supplies the installed-return composition and complete
source census interface; Mihir Srivastava's #4949 supplies the independent
ownership audit; #4956 supplies the portable-replay follow-up. Chris R /
Clear1nsight's #4166/#4167/#4172/#4177 supply the actual caller, return exchange,
prior tariff and complete-cost lineage. Tekalign's finite-role exchange and
Jose Manuel's physical controller/Ordinary/Compact sources retain their credit,
as do all retained QQ16/native predecessor notices. This conditional kernel,
source observer, bit checker and writing are by JoyboyBrian with substantial
OpenAI Codex assistance. Apache-2.0.

## Open next questions

- Prove a uniform production graph cap K from the actual controller, Ordinary
  inventories and lease/context lifetimes. Start at every return phase, since
  the constructor-only substitution fails. The missing invariant blocks
  production use of the reduced cap.
- Implement and price a complete physical source encoder/store interface and
  its frontend F, including control storage and compilation. The sequential
  macro price alone does not discharge this embedding.
- Combine this conditional charge with the complete unmatched D* versus B*
  native/nonchild ledger. Unknown remaining terms prevent a total sign or κ
  conclusion; the credited return saving must be used only once.
