# Local validation and handoff

Base: `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, canonical main,
fetched over HTTPS in this session. Assignment seed 17 came from OS randomness.
Selected source bindings pass `scripts/research_baseline.py` and identify
conditional kappa `0.001672660197076918`, with complex binding.

Python 3.12.14 on Linux: the registered package replay and all seven controls
pass. Python 3.13.5: optimized mathematical replay and all seven controls pass
with the same mathematical receipt. Tests include a read-only, Git-free source
export at a path with spaces, both coefficient engines, changed live sources,
an altered receipt and a wrong independent coefficient digest.

```sh
python3.12 -B scripts/research_package.py --package research/bit-extension-one-relation-seed17
python3.13 -I -O -B research/bit-extension-one-relation-seed17/verify.py
python3.13 -I -B research/bit-extension-one-relation-seed17/test_package.py -v
git diff --check
```

Expected: `PASS_BIT_EXTENSION_ONE_RELATION`, seven passing tests and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.
The fresh finite receipt has 144 endpoints, 576 rejected omissions and
432 rejected interior placements. Both engines agree on every coefficient of
all 720 outside placements; all 20 F4 projectors agree after binary embedding.
The assignment seed also picks one explicitly retained interior obstruction
within that complete domain; it is not a sampling-based exclusion.

No selected cold replay, native supplier, CI or proof-assistant run is claimed.
The mathematical theorem is the written proof, open to independent review.
The finite checks corroborate its new case. The binary cost consequence uses
the componentwise field-call simulation, not arbitrary joint binary resynthesis.
All changes are confined to this package; upstream and the selected frontier
are unchanged. Substantial OpenAI Codex assistance is disclosed throughout.

Before handoff canonical main was rechecked and remained at the exact base.
Relevant predecessor/open-PR head metadata is retained in TASK.json. No matching
scalar-extension one-relation contribution appeared in the targeted refresh.
Coverage is partial and does not certify novelty. No pinned coordination issue
was found. Discussion participation was unavailable through the invalid CLI
authentication, so the local claim has been updated once with its result.

The donor receives a committed branch, a draft PR body, an offline patch and a
publish script. No push, public PR, merge or modification of others' work was
performed. Future work first needs a changed relation count, role count or
pricing contract, and its own complete optimistic bill.
