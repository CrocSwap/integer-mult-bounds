# Task card (autoresearch.md section 3)

Task ID / proposed scope key: supplier-boundary-audit / dcdb0fa8e49b08a958d0,
refined object: "mutation coverage of the selected finite invoice"
(package research/invoice-mutant-coverage).

Base commit; exact predecessor and dependency heads:
base 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2 (origin/main at draw).
Frozen predecessor: PR1087 archive research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz
(SHA-256 d4acf04daef85d4514f80ec5fcd2492d0c60e5d6c49fa71b3e6523f8db2dea86),
fixture research/community-frontier1094-audit/selected-replay.tar.gz.
Selected record SHA-256 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32.

Concrete object and question:
The frozen PR1087 code/invoice_allcold.py run() is the selected #1094 chain's
finite-invoice stage (prefix obligation required_prefix < 512 payload; row
obligation physical_row_coefficient < 20161; halving, mass, router, literal,
precision, tape, local-primitive obligations; ad-hoc assert bindings to the
hosted template, owner/profile receipts and provider registry). It has no
mutation-control block. Question: under one-field semantic mutants of its
inputs that stay superficially well-formed, which of run()'s acceptance
predicates reject them; does any mutant pass while violating an obligation the
invoice claims to enforce?

Scope status: refined; reason: pair-collision — the drawn first-choice card
selected-stock-envelope matches philippeVV's fresh live claim (discussions/1166
18:57Z with updates 19:21Z). Second-choice card taken per the collision rule;
refined to the explicit open handoff question 3 of PR1959
(research/t16-audit-mutant-coverage), which is unclaimed and blocked by nothing.

Existing restriction being changed (or exact claim being audited):
Auditing, not changing, the acceptance boundary of the selected invoice stage.
The t16-audit-mutant-coverage package established that audit_allcold.py's
reachable template predicates reject mutants for the selected fixture; it left
invoice_allcold.py's own rejection power untested and noted the 69 admission
controls were not shown to cover the invoice's inputs.

Method; explicit parameter ranges/candidate alphabet:
In-process harness on pinned invoice_allcold.run() over the archived selected
fixture, marshal-copy isolation after PR1939. Positive control: reproduce every
field of the published PREFIX-AND-INVOICE.json. Mutant classes: (A) raw
one-field mutations (hash-binding layer), (B) hash-consistent template
mutations, (C) receipt-field mutations (OWNERS-AND-PROFILE.json,
ASYNC-AUDIT.json), (D) provider registry/check mutations. Single-field changes
only; record first rejecting assertion or acceptance per mutant.

Nearest overlapping PRs and why this adds something:
PR1959 (t16 template mutants, released) explicitly deferred this exact test;
PR1939 (fast copy) supplies the copy observation; #1956/#1965/#1990 audit the
bootstrap cutoffs and stock, a different stage. Refined overlap search found no
invoice-mutation work in open PRs or discussions.

Optimistic full cost budget; required observable improvement:
Not a kappa task. Budget: one session; harness + mutants within ~45 minutes of
compute; no construction budget applies.

Success evidence; falsification test; time/compute cap:
Positive control reproduces the published invoice receipt exactly; each mutant
records its first rejecting line or acceptance; EXPECTED.json pins the census;
unittest failure controls show the harness detects an inverted verdict.
Falsification: a claimed rejection that does not occur, or a claimed acceptance
that the harness cannot reproduce. Cap: ~2 h session, stdlib only.

Predecessor authors; intended artifact and reproduction command:
Jeremy Kothe (#870/PR1087 invoice lineage PR558/PR552/PR531), Hao Yan (#858),
Rohan Arun (#1094), Josie Elliston (PR1959 open question + harness pattern),
jackmgaller (PR1939). Artifact: research/invoice-mutant-coverage/
(verify.py, EXPECTED.json, README.md with Open next questions).
Reproduce: python3 -B research/invoice-mutant-coverage/verify.py
Attribution: Aaron Wang, with help from opencode.
