# Reject helper endpoint indices before Python list indexing

**Confirmed independent-auditor gap; the native audit already protects this boundary.**
The unchanged `research/gauge44-frames-x/independent/audit_local.py` accepts a
negative `helper_final` key that aliases a target register. It then overwrites
that target's required hyperplane endpoint with FULL, while its helper-domain
sets still contain the negative integer. The all-column scalar endpoint checks
and helper-cone checks do not detect the mismatch.

This package adds a small standalone guard. It requires every `helper_final`
key to be a canonical decimal register number in the actual helper interval
`[2v, 2v+R)`, before any list lookup or endpoint override. It preserves the
frozen auditor. This is a separate missing condition from PR2478's cut-source
guard; the counterexamples pass that guard unchanged.

## Exact counterexample and protection

The genuine PR2478 base word has v=112, R=480 and n=704. It has 704 arbitrary
scalar input columns and 7,208 derived compensation gates. Starting from its
unchanged bytes, make only these two semantic edits:

```python
word['helper_final']['-592'] = [256,128,64,32,16,8,4,2,1]
word['report']['local_profile']['1'] += 1
```

Python interprets `end[-592]` as `end[112]`. Register 112 is the first target,
whose port is 13 and required endpoint is `perp(13)`, of dimension eight.
The override sets it to FULL, of dimension nine. The extra reported rank-one
climb makes the altered profile match the auditor's altered frame sequence.
This example **does not understate that altered profile** and is not a claimed
supplier improvement: it changes the fixed endpoint contract itself.

The same construction works for each target t in 112..223, using key t-704.
The verifier actually calls the unchanged auditor on all 112 mutations, with
`--main` semantics: both exact scalar orientations, all 704 columns, transported
port/centre interface, frames, entrances and cones pass. The helper width
inventory stays unchanged, and the local rank-one count increases by one.
Every mutant passes PR2478's unchanged cut-source guard.

The native `hpe_audit_and_transport.py` explicitly asserts
`all(2*v <= r < n for r in helper_final)`. The registered replay executes the
full native audit on the genuine base, then executes it on the representative
mutation. The base passes; the mutation rejects at that exact assertion before
producing output. The native subprocess always runs with assertions enabled,
even when the new verifier is optimized. No claim is made that the complete
native chain admits an invalid word or that a selected certificate is broken.

## Why the independent checks miss it

The independent auditor constructs `lowends` and `coldends` from integer keys,
then assigns `end[int(key)]`. Those use different notions of identity when a key
is negative: set membership retains -592, while list indexing addresses 112.
Consequently the pre-wrapper exclusion does not see a target touched by the
compensation, and the dirt-column lookup `p[k].get(q)` searches a nonexistent
negative dictionary key. The inverse-row cone is vacuous for the overridden
FULL endpoint because every end-of-B frame lies in FULL.

Replacing -592 by the positive key 112 is rejected by the existing pre-wrapper
check. Keeping the negative key but omitting the invoice increment is rejected
by the existing profile check. These controls isolate the index-alias defect;
they are executed against the original auditor, not a model of its behavior.

## Native frame distinction

The endpoint difference is semantic. In the pinned Clifford convention,
`T_U` is a monomial conjugate of C on dim(U) axes. Its zero-column support is U.
Thus `T_perp(p)` has support 256, whereas `T_FULL=C_[0,9)` has support 512.
Choose any coordinate e_j with p_j=1. At matrix entry (e_j,0), the required
hyperplane operator has coefficient zero; the FULL operator has

    (1+i)^8 (1-i) / 2^9 = (1-i)/32.

`native_witness.py` derives that coefficient by an independent nine-factor
Gaussian product. The unchanged exact Clifford implementation corroborates
the support and coefficient distinction for every actual target port. This
proves the two endpoint labels cannot be interchanged. It is not a claim that
a complete native program with newly supplied adapters has been executed.

## Guard contract and evidence

The new check is an index-domain prerequisite, not a replacement for the
scalar/frame/phase/owner checks. It accepts absent or empty optional maps and
valid helper indices, leaving their frame values to the existing verifier.
Canonical decimal spelling prevents textual aliases such as `0273` or `+273`
from referring to one helper under multiple JSON keys. JSON object keys are
strings; no nonexistent JSON boolean-key case is advertised.

The positive compatibility census reuses PR2478's named collection: 144
retained main words plus its two submitted genuine words, 146 total. All pass
the new guard. Exact hashes and Git blobs bind every consumed word. The census
is not a guarantee about every historical or future word format.

Additional controls reject too-negative and oversized indices, source and
target indices, and leading-zero, signed and whitespace spellings. The public
CLI runs in a Git-free relocated tree under optimization. Corrupting the actual
independent auditor or the retained cut guard is rejected by hash before import.
`RESULT.json` records every accepted negative-key word digest and every native
matrix-entry witness. Whole-auditor receipts omit only elapsed time and temporary
filenames; proof-relevant fields are compared exactly.

## Reproduce

Python 3.12, standard library only, from repository root:

```sh
python3.12 scripts/research_package.py --package research/audit-helper-endpoint-indices
python3.12 -I -O -B research/audit-helper-endpoint-indices/guard.py WORD.json.gz
```

Default verification is read-only; `verify.py --write NEW_PATH` authors a new
receipt and refuses to overwrite one. The full replay calls the old auditor
115 times and separately runs the native positive/rejection pair. Use writable
TEMP/TMP when required by the local sandbox. Hosted CI and a complete supplier
cold replay are separate checks.

## Scope, provenance and credit

Base main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Picker seed `21498ba0c0f0407250d688ef37ba1e64` selected independent verification.
The `independent-moment` card is changed to its missing source-to-certificate
acceptance implication, rather than another moment calculation. The assigned
baseline command passed. PR2464's already documented conditional moment link
was screened and not counted as another result. `TASK.json` records the decision.

PR2478 (`dc83994c2dda28064c902ee970ce47db602224ae`) supplies the named genuine
words, positive-census paths and unchanged cut guard; its exact notices remain.
This package adds the endpoint-index counterexample, full target census,
independent native support witness and helper-domain guard. Consumer integration
of PR2478 and review of other unpriced sections are separate work. Live overlap
has current REST PR coverage but retains the last complete Discussion snapshot
because GitHub's GraphQL quota was exhausted; exact times and limitations are
recorded in `OVERLAP.json`.

DreamingOfClouds' PR1238 already explains why targets must retain their specified
hyperplane ends in this verifier model. The new finding is an accepted index
alias that overwrites that contract, not a new end-cap theorem. PR2409's native
integer-row optimization concerns a different source path and purpose.

Credit icekylinx for the independent auditor; DreamingOfClouds and the retained
PR425/433/484/635 native and Clifford lineage; Jeremy Kothe and predecessors for
the genuine word; and Marius-Paul Dumitrean for PR2478's cut audit and handoff.
Prepared by ywz65 with substantial OpenAI Codex assistance. New work is
Apache-2.0. No independent human review, formal-kernel proof, selected supplier
admission or changed kappa is claimed.

## Open next questions

Can maintainers adopt the guard alongside each independent-only consumer while
preserving its source-invalidation policy? First identify the actual acceptance
entry points and distinguish consumers that already execute the protected native
audit. This package supplies the guard and evidence, not that integration.

Do other register-indexed optional fields preserve one identity convention
through sets, dictionaries and lists? Start with a separately scoped field and
an actual accepted semantic mutation. The present proof is limited to
`helper_final`; it does not establish general schema completeness.
