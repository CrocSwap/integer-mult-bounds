# R1 words at their packing cap (T740): conditional κ = 0.001729152756004330934535 − 10⁻⁴⁶ − 10⁻⁷⁰

```text
Status / UTC update / priority revision: DONE (moment nomination; see "Scope") · 2026-10-16 · priority revision 6 · base main d8e0f83f
Concrete question and changed premise: PR3015's R1 restore edit keeps every helper width, window and the 91-buffer
    namespace of PR2979, and its fixed-capacity cap certificate has the same optimal basis as PR2979's. So an allocation
    that attains PR2979's cap also attains R1's. Can that be done literally?
Established result and evidence status: yes. A literal T740 allocation is ten lockstep copies of PR2979's T74 fill
    (which PR3015 uses unchanged) plus 332 whole-role relocations. Its idle histogram is exactly 740 x the optimal basic
    idle profile, and with the R1 words its exact root equals the R1 cap. Gains: about 1.5520e-9 over PR3021's released
    headline (R1 + PR3018 packing) and 1.7825e-9 over PR3015. Packing only; author-checked (AI-assisted); not
    maintainer-reviewed.
Public artifact URL + exact commit: this package (see the PR).
Next useful task: the complete T740 admission/outer release. Further gains need more word edits (R2, ...).
Active claim / expiry: released.
```

## Result

| | κ (headline; each − 10⁻⁴⁶ − 10⁻⁷⁰) | words | T | packing |
|---|---|---|---:|---|
| PR #3015 (Jeremy Kothe) | 0.001729150973534224428695 | PR2979 + R1 | 74 | PR2979's fill, 1.78e-9 below the R1 cap |
| PR #3021 (Nick Petalas) | 0.001729151203983018442998 | PR2979 + R1 | 74 | PR3018's journal, 1.55e-9 below |
| **this package** | **0.001729152756004330934535** | **PR2979 + R1** | **740** | **attains the R1 cap** |

- Exact gains are `1552021312491537/10^24` over PR3021 and `178247010650584/10^23` over PR3015 (CLAIM.json).
- The words are PR3015's two R1 words, used unchanged (`data/R1-WORD-*.json.gz`; provenance in VENDOR.json).
  - Local profile per call: {1:2443, 2:707, 3:232, 4:108, 5:18, 8:8}.
  - Width inventory: {4:26, 5:2, 6:16, 7:52, 8:99, 9:213}.
  - 91 private buffers.
- The allocation has 740 replicas, 6,660 calls and 2,717,280 helper roles.
- Complete paid profile: {1:16441320, 2:4708620, 3:1594737, 4:719280, 5:137085, 8:53280, 48:281903}.
- Physical stock: 663,040 live + 408 helpers + 8 centres + 91 buffers + 2 guards = **663,549**.
- The exact root bracket [0.001729152756004330934535, 0.0017291527560043309345351] is exactly PR3015's certified R1
  cap.

**Concurrent work.** Nick Petalas' [PR3024](https://github.com/CrocSwap/integer-mult-bounds/pull/3024) attains the same
kind of cap at T740 for PR2979's words without R1. It uses a 550-row journal on PR3018's fill. This package's 332
relocations were found independently from PR2979's own fill; they reach the same idle histogram. PR3024 records the R1
composition as a separate obligation, and that composition is what this package adds.

## Why T740 and why it composes with R1

**Why T740.** On the optimal face (12 tight patterns), exact row multipliers fix three counts per replica:

| pattern | count per replica |
|---|---|
| [9,9,9]@32 | 93/4 |
| [9,9,9,9,9]@48 | 1341/20 |
| []@48 | 7619/20 |

- Since 1341 = 3²·149 is prime to 20, an integral optimum needs 20 | T.
- T740 is the first multiple of PR2917's T74 order with that property.
- At T74 the best integral mix is 1.55e-9 below the cap, which is where PR3021 sits.

**Why it composes with R1.** R1 changes the local profile by −2H₁ + H₂ per call and nothing else that the allocation
reads: helper widths, entrances, endpoints, windows, order, dispatch and buffers are all unchanged. PR3015's R1 cap
certificate has the same 10-pattern basis and the same idle profile as PR2979's. `verify.py` re-derives:

- the R1 providers from the words;
- the face counts and the optimality of every literal bin pattern;
- the equality of the root and the R1 cap.

## Construction

`lift.py` defines the allocation completely, in two steps.

1. **Lift.** PR2979's literal T74 ORDER, DISPATCH and FILL (PR3015 uses them unchanged) are copied ten times in
   lockstep, in Dugongue's PR2969 convention. With j = 0, …, 9:
   - call (s, r) at time t → call (s, r + 74j) at time 10t + j;
   - role (t, h, o, c, p, z) → role (10t + j, h, o + 74j, c, p, z).
2. **Relocate.** The roles in `allocation/RELOCATIONS.json` move to their listed bins, and the 263 touched bins are
   repacked as compact prefixes.

### What the relocations change

    60 x [4,8,9,9,9,9]@48  ->  57 x [9,9,9,9,9]@48 + 3 x []@48
    75 x [9,9,9]@32        ->  60 x [4,9,9,9]@32 + 15 x [8,8,8,8]@32

The displaced 4s and 8s are late, while almost all [9,9,9] bins close early. So each one travels along a chain of
same-width exchanges (`construction/plan_t740.py`, seeded greedy; `construction/CHAINS.json`):

1. It enters an unlocked bin whose window contains its call.
2. It evicts a same-width role of an earlier call, which moves on in turn.

Every intermediate bin keeps its pattern. In all, 332 roles move: 150 in step A, 45 in B, 80 in C, 12 in D and 45 in E.
The search reads only widths, windows and families, so the same relocations serve PR2979's words and R1's.

## Verification

Both registered commands use the standard library only, under Python 3.12.

**`verify.py` (about 70 seconds)** checks:

- **Pins.**
  - Live pins of the PR2979 inputs on main.
  - Vendored-file pins (VENDOR.json): exact PR heads, Git blob IDs and SHA-256.
- **Providers.** The R1 words re-derive the providers:
  - widths identical to PR2979's registry;
  - local profile = R1;
  - 91 buffers.
- **Allocation.** The deterministic T740 rebuild has pinned canonical payload SHA-256.
- **Owner engine.** PR2979's vendored engine checks all 2,717,280 roles:
  - windows, same-call families, capacities, masks and compact prefixes;
  - the complete paid profile and the rank mass.
- **Physical stock.** 663,549.
- **Cap and optimal face.**
  - PR3015's R1 cap certificate is re-verified with PR2979's `relax_exact.py`.
  - Exact fixed face counts.
  - The idle histogram is 740 × the basic optimum.
  - Every bin pattern is tight.
  - The root bracket equals the cap bracket.
- **Moment.** The dyadic moment auditor is re-pinned to PR3015's headline and shows a strict gain. An exact
  comparison also shows a strict gain over PR3021.
- **Claim.** CLAIM.json is bound to the results.

**`controls.py` (about four minutes)** checks seven controls:

| control | result |
|---|---|
| bare lift | valid, but its root is PR3015's (below the cap) |
| dropped chain link | rejected by the engine |
| window violation | rejected by the engine |
| family collision | rejected by the engine |
| stale profile | rejected by the engine |
| tampered relocations | the payload pin fails |
| wrong moment baseline | rejected |

```sh
python3 scripts/research_package.py --package research/rank7-r1-t740-cap --check-only
python3.12 scripts/research_package.py --package research/rank7-r1-t740-cap
python3 -B research/rank7-r1-t740-cap/construction/plan_t740.py --out /tmp/t740-plan   # provenance: regenerates RELOCATIONS.json
```

## Scope

- **Packing composed with R1.** No word, gate, frame, scalar or cleanup changes are made beyond PR3015's declared R1
  edit.
- **Inherited claims.** PR3015's (and PR2979's) word-level, native and release claims are inherited unchanged. So are
  all of PR2979's inherited all-size, compiler, hosting, precision and analytic hypotheses.
- **Review status.** PR2979 is an archived source package and PR3015/PR3021 are open. None is scientifically admitted,
  and the independent audits they need apply here too.
- **Open finite obligation.** The complete fresh-native admission and modern outer release have not yet been rerun for
  the T740 allocation. PR3015's and PR3021's releases are at T74. This is a moment nomination with literal T740 owners,
  the same status as PR3024 and PR2969.
- **What is not claimed.** No selected-frontier change, no new mechanism, and no independent human review.
- **Optimality.** The R1 cap is the optimum of the fixed-capacity relaxation, so no allocation of the R1 words in this
  model can do better.

## Open next questions

1. **Complete T740 release.**
   - First step: rerun PR3015's reproduce.py chain with the T740 ORDER/DISPATCH/FILL that `verify.py --work DIR` writes.
     T-dependent physical and prefix constants come from the order.
   - Blocked by: replay time and memory at ten times PR3015's 271,728 roles.
2. **More declared edits.**
   - Why it matters: packing is exhausted for these words, so only a changed local profile raises κ further.
   - First step: price candidate edits with PR3015's exhaustive 2-4-gate restore-block search. Each new local profile
     with the same basis inherits this allocation's cap attainment.

These are recorded as structured `open_questions` in TASK.json.

## Credit

- **Jeremy Kothe (PR #3015):** the declared R1 edit, R1 words and R1 cap certificate.
- **Marius-Paul Dumitrean (PR #2979):** the words under R1, the literal T74 fill lifted here and the checkers.
- **Nick Petalas (PR #3018, #3021, #3022, #3024):** the integrality analysis lineage and the concurrent T740 cap for
  PR2979's words.
- **Dugongue (PR #2969):** the lockstep T-lift convention and cross-copy moves.
- **themilkman216:** the observation about the T at which these caps become integral.
- **Mason Hale (PR #2917):** chronology and owner/moment checks.
- **Tekalign:** the independent owner checker.
- **Jeremy Diviney (PR #2908):** the moment auditor arithmetic.
- **Yiyang Lu:** the flow model.
- **icekylinx:** the exact auditor.

New work by Rohan Arun, prepared with substantial AI assistance (Anthropic Claude). Apache-2.0. Retained notices apply.
