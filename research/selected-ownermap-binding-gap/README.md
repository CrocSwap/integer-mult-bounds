# Accepted-but-unbound: the selected chain's cross-stage owner-map binding

**A scoped adversarial audit of one named acceptance boundary of the selected
chain. κ, the certificate, the suppliers and the frontier are unchanged. This
is not a bug claim against the selected fixture and not a cold replay.**

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no independent human review). Apache-2.0.

## Question and result

The frozen PR1087 selected chain certifies the frozen `data/OWNERS.json.gz`
role map twice: `lift16` checks every role inside its owner's actual window and
`independent-t16` rechecks the map against invocation times. `emit` copies that
map verbatim into the hosted template's `hosting.pooled_slots` (eleven fields
per role, `time` included), and `audit_allcold.py` binds ten of the eleven
fields back to the base-derived call owners (line 172, "the frozen pooled
metadata must bind the actual serialized owner maps"). The whole chain also
binds the template's **bytes** tightly by hash (`audit` line 185, `invoice`
line 175, `assemble` line 240 and `verify_t16.py`'s
`asm.template_sha256 == owner.template_sha256 == inv.template_sha256`).

Two fields are bound to nothing: the pooled slot's `time` (which invocation
hosts the role) and `hosting.owner_map_sha256` (the field that names the owner
map). Josie Elliston's
[PR #1959](https://github.com/CrocSwap/integer-mult-bounds/pull/1959) recorded
this in source text ("line 172 compares a pooled slot's roles fields but not
its `time`"; the owner-map link "was previously implied by that determinism,
not checked") and added the boundary check to its own verifier. This package
**executes** the gap: the smallest invalid fixtures that a defective-but-coherent
`emit` could write are accepted by the complete frozen post-emit stage sequence
and by `verify_t16.py`'s final binding, while failing the owner-map binding.

Fixtures (each is a canonical re-emit of the archived selected hosted template,
so every template-hash binding stays tight and only the audited field differs
from the frozen owner map):

| Fixture | Mutation | audit | invoice | assembly | both control stages | independent-t16 | final binding | link check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 | none (re-emit fidelity control) | pass | pass | pass | pass | pass | 20/20 | passes |
| F1 | two equal-width pooled slots exchange `time` | pass | pass | pass | pass | pass | 20/20 | fails on 2 role times |
| F2 | `hosting.owner_map_sha256` set to a wrong digest | pass | pass | pass | pass | pass | 20/20 | fails on the naming field |
| F3 | one pooled slot's `port` (checked roles field) changed | rejected, line 172 | not run | not run | not run | not run | not run | fails on `port` |
| F4 | F1's swap with a stale `HOSTED.json` hash | rejected, line 185 | not run | not run | not run | not run | not run | fails on 2 role times |

**The accepted counterexample (F1).** Pooled slots 0 and 480 — `(stage 0,
replica 0, helper 0)` and `(stage 0, replica 8, helper 0)`, both `width 9` —
exchange their invocation times (`time` 0 and 1). Every per-time width count is
preserved, so no count, profile, `rank_mass`, `deficit`, prefix or row
coefficient moves: the complete frozen chain from `audit` through
`independent-t16` accepts the template, and all 20 of `verify_t16.py`'s final
binding assertions pass. The only differences from the archived receipts are
the expected `template_sha256` hash cascades. The owner-map binding
(`pooled_slots` equals the frozen OWNERS list, times included) fails on exactly
those two roles: the template now says each helper runs at the other's
invocation.

**What would change downstream.** The certified owner-window admissibility
(lift16's actual-window check and independent-t16's invocation-time check)
applies to the frozen OWNERS times, not to the template's. A hosted-schedule
consumer that reads `hosting.pooled_slots` from the accepted template would
host those two helpers at invocations that no check validated. Inside the
frozen chain the `time` column is inert (F1's receipt diffs are hash cascades
only), so this is a contract gap at the accepted artifact boundary, not a
change to the selected arithmetic.

**What the chain does catch.** The rejection controls delimit the gap: a
checked roles field is rejected at `audit` line 172 (F3), and a template whose
bytes disagree with `HOSTED.json`'s recorded hash is rejected at `audit` line
185 (F4). Artifact integrity is enforced; semantic equality of the pooled role
map with the frozen owner map is not, beyond the ten fields line 172 compares.

## Reproduce

```sh
python3 -B research/selected-ownermap-binding-gap/verify.py
```

Expected status `PASS_SELECTED_OWNERMAP_BINDING_GAP` (about 3–5 minutes on the
author's host; it runs the frozen stages out-of-process per fixture). The
deterministic output must equal [EXPECTED.json](EXPECTED.json).
`--write` regenerates `EXPECTED.json`; normal verification writes no files.
Stdlib only. Checked on CPython 3.12 (Windows); the generic replay declares
Python 3.12.

The harness pins its inputs ([SOURCES.json](SOURCES.json)), reproduces PR #1959's
in-process/complete-caller discipline, runs the frozen stages exactly as
`verify_t16.py` invokes them (through the pinned `run_portable.py` wrapper), and
reimplements `verify_t16.py`'s final binding 1:1 (20 assertions, driver pinned
by archive-member SHA-256 `050e2dfb…`). The audited guard
(`link_check`) is PR #1959's `template_to_frozen_owners_binding`.

**Serialisation notes** (CONTRIBUTING.md "Regenerated artifacts and hashes"):
two machine-dependent serialisations are normalized before comparing receipts
with the archived selected ones — `independent-t16` keys its `input_sha256` by
absolute input paths, and the frozen invoice's `artifact_semantic_sha256` map
is serialized in directory-enumeration order, so the byte hash `assemble`
records as `input_sha256.fresh_invoice` varies by filesystem. On this host the
fresh invoice receipt differs from the archived copy only in nested key order;
parsed proof-relevant content is identical. Everything else reproduces the
archived receipts exactly.

## Scope and not checked

- The pre-emit stages (`restore-parent`, `bind8`, `lift16`, `bind`, `emit`) are
  not re-run: the fixture mutation stands in for a defect of `emit` in the
  unchecked fields (or post-emit tampering), and `emit` itself pins the OWNERS
  input by hash against the SPEC. Provider content binding against
  baseline1042's `slots/local` is not re-checked (upstream of the mutation
  point; in a fixture run the bound copy is its own input).
- `audit`'s module-level provider checks (its lines 20–80), the nine other
  archived `audit_allcold.py` versions (PR #1959 open question 1) and every
  stage of the cold baseline are untouched.
- No cold rebuild, no Linux/macOS run, no formal kernel, no human review, no
  supplier, certificate or κ change. The archived selected fixture satisfies
  the binding; the counterexample is synthetic and scoped to this interface.
- This is one missing implication at one interface, executed end to end. It is
  not a general statement about emitter correctness or about other templates.

## Repair status and credit

The minimal repair is the two-line guard this package's `link_check` implements
(pooled slots equal the frozen OWNERS content; `owner_map_sha256` equals the
SHA-256 of the frozen gzip), added to a successor replay driver with the frozen
code unchanged. That repair remains **blocked on a maintainer decision** on
wrapping the frozen `verify_t16.py` (PR #1959 open question 2), so it is not
attempted here.

Credit and predecessors: Josie Elliston's
[PR #1959](https://github.com/CrocSwap/integer-mult-bounds/pull/1959)
(`research/t16-audit-mutant-coverage/`) identified the gap, supplied the
boundary-check precedent and open question 2, and is the direct predecessor of
this package. The frozen chain is Jeremy Kothe's PR1087/#870 `gauge44-barch-t16`
code with Hao Yan's (@FanPUYen) PR #858 T16 controller, `lift16` and `indep16`;
Rohan Arun's [PR #1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094)
supplies the selected exchanges and archived run; the maintainer's frontier1094
audit archived the fixture. Concurrent and complementary:
[PR #2273](https://github.com/CrocSwap/integer-mult-bounds/pull/2273)
machine-checks that the 15 audit-unread fields (owner_map_sha256 among them)
have no post-emit reader; this package supplies the executed end-to-end
acceptance of the wrong value and of the retimed role map.

## Open next questions

1. **Add the two-equality owner-map guard to a successor replay driver.** Why it
   matters: it closes the demonstrated gap without touching frozen code.
   First step: wrap `verify_t16.py` with this package's `link_check` (or PR
   #1959's `template_to_frozen_owners_binding`) between `emit` and `audit`.
   Blocked by: the maintainer decision on wrapping the frozen driver (PR #1959
   open question 2).
2. **Does any accepted consumer of the hosted template outside the frozen chain
   read pooled-slot `time`?** Why it matters: it decides whether F1 is inert
   contract metadata or a live hosting-schedule hazard. First step: extend PR
   #2273's consumer-universe machine check from field names to time-directed
   reads of `pooled_slots`. Blocked by: nothing but session time.
3. **The nine other archived `audit_allcold.py` versions** (PR #1959 open
   question 1): does each bind its pooled roles the same way? First step:
   parametrize a receipt over archive member and script hash, using the #1042
   audit archive as fixture. Blocked by: locating each version's hosted
   template in the retained receipts.
