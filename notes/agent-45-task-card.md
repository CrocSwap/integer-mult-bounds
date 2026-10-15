# Local task card — agent-45 (written before substantial computation)

Task ID / proposed scope key: `uniform-transfer-audit` (chooser scope key `603f341b99f590f17a76`),
refined to the hosted-template post-emit field-contract read-set audit.
Track: adversarial-audit. Chooser nonce: `2bb90ec128a184bdec47e263785b9c5d` (OS-random draw,
priority revision 4, catalogue SHA-256 `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`).

Base commit; exact predecessor and dependency heads:
- Base main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Predecessor: Josie Elliston's PR1959 `research/t16-audit-mutant-coverage` (on main at base),
  whose README records the exact claim audited here and labels it "a text search, not a proof".
- Adjacent concurrent work: PR2158 `research/invoice-mutant-coverage` (invoice `run()` mutation
  testing; different object and method — dynamic mutation of invoice predicates vs static
  read-set/whole-object channel audit across all pinned post-emit consumers).

Concrete object and question:
The frozen PR1087 `code/audit_allcold.py` acceptance audit does not read 15 hosted-template
fields (`cover`, `m`, `version`, `port_restriction`, `provider_dispatch`, `replica_lift`,
`route_semantics`, `supplier_substitution`, `expanded_scalar_interface`,
`hosting.{rule, scope, idle_remainder_semantics, owner_map_sha256}`,
`async_schedule.{scope, source_plan_sha256}`). PR1959 asserts by text search that no stage
after `emit_allcold.py` reads any of them. Question: is that claim machine-checkable over the
pinned consumer universe (frozen PR1087 archive `code/` + maintainer frontier1094 scripts),
and through which whole-object channels (hash binding, serialization, iteration, equality)
could a change to those 15 fields still reach a post-emit acceptance decision?

Scope status: refined; reason: the card asks for one exact hosting/transfer implication with
explicit quantified hypotheses; the refined object is one named claim ("no post-emit reader of
the 15 audit-unread fields") whose downstream consequence is the template acceptance boundary.

Existing restriction being changed (or exact claim being audited):
Exact claim audited: research/t16-audit-mutant-coverage/README.md, "Accepted: 19 path mutations"
bullet ("A text search of the PR1087 archive and the maintainer frontier1094 scripts finds no
reader of the 15 unread fields in the hosted template after `emit`. This is a text search, not
a proof."). No restriction is changed; the audit upgrades the evidence class.

Method; explicit parameter ranges/candidate alphabet:
stdlib-only AST read-set analysis (Python `ast`): every constant string equal to one of the 15
names in every pinned file is classified by syntactic context (subscript key, attribute, call
argument of `get`/`pop`/`setdefault`, plain string, other); every dynamic-access site
(`x[name]`, `getattr(x, name)`, `**` unpacking, whole-object iteration/serialization/hash/
comparison) is enumerated per file. Universe: all `.py` members of
`research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz` (SHA-256 pinned) plus
`scripts/verify_frontier1094*.py` and `research/community-batch1099-audit/check_frontier1094.py`
and the selected stage wrapper `research/complex-t16-rare-pattern-exchanges/verify.py`.
Falsification first: any name-directed post-emit read or unresolvable dynamic access falsifies
the claim at the smallest instance (the exact file/line).

Nearest overlapping PRs and why this adds something:
- PR1959 (merged): raised the gap and left it as a text search; open question 2 is a different
  (driver-binding) item blocked on a maintainer decision. This adds the missing machine check.
- PR2158 (open): dynamic mutation of `invoice_allcold.py` predicates; mine is a static,
  universe-complete channel map over all post-emit consumers, and states exactly which channels
  mutation testing can and cannot reach.

Optimistic full cost budget; required observable improvement:
No kappa/supplier claim. Deliverable is a checked statement + channel map with pinned hashes;
cost is bounded by universe size (a few dozen source files); runtime target well under 60 s.

Success evidence; falsification test; time/compute cap:
Success: `verify.py` prints PASS with EXPECTED.json equality over the pinned universe; a
corruption control (a name-directed read injected into a scratch copy) flips the result.
Falsification: a single name-directed post-emit read of any of the 15 names, or a dynamic access
that cannot be resolved from constants. Compute cap: seconds per run; one bounded pivot maximum.

Predecessor authors; intended artifact and reproduction command:
Josie Elliston (PR1959); Jeremy Kothe (PR1087/PR870 frozen code); Rohan Arun (PR1094 selected
run); agent-43/Aaron Wang (PR2158, adjacent). Intended artifact: `research/hosted-template-postemit-fields/`
(README, TASK.json, SOURCES.json, VERIFY.json, verify.py, EXPECTED.json). Reproduce:
`python3 -B research/hosted-template-postemit-fields/verify.py`.
