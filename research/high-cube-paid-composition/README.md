# Complete paid high-cube composition

This closes the local traffic composition handed off by
[PR3265](https://github.com/CrocSwap/integer-mult-bounds/pull/3265), after
[PR3233](https://github.com/CrocSwap/integer-mult-bounds/pull/3233) and
[PR2982](https://github.com/CrocSwap/integer-mult-bounds/pull/2982). Those
packages price setup, ordered ADD and the outer wrapper. This supplies the
missing pooled unit-translation and whole-swap-adapter bounds, transfers
the sign bound to its actual pooled caller, and composes all six kinds
without dropping native B1 work.

For one complete cube of V bits, let a,h,g,c count ADD, doubling/halving,
negation and translation factors; s counts all factors; t counts swaps
plus twice the reversed ADDs. With outer numerical width I, high-bank role
count K, N=d², and B_N=716+1866 bit_length(N),

```text
T_cube <= sum of complete actual native B1 tolls + 27I + 10K
          + [373+s(3B_N+36)+4096a+530h+4096g+32768c+100000t] V.
```

The constants are conservative. The 100000V adapter allowance excludes its
still-paid native interval. If the inherited same-domain B1 tariff holds,
this gives the expected local O(V(1+u^p)) bound and PR2982's linear prefix
lift. [PROOF.md](PROOF.md) states the source derivation and native premises.
This is a conditional local composition, not native or supplier admission.

## Evidence and reproduction

From the repository root with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/high-cube-paid-composition
```

The manifest runs normal and optimized checks. [RESULT.json](RESULT.json)
covers 14 complete reduced packets, 9,654 Boolean coordinates and 48 actual
elementary native calls: all six kinds, both ADD orientations, extreme
carries, nonidentity low rows, complete spectators, multiple prefixes and
occupied dirty scratch roles. Exact partitions agree with a separate
observer and raw physical meters; matrix endpoints, borrowed bytes/heads,
owned output and cleanup are checked. Six radix scans reach 268-bit words
without allocating exponential payloads.

After a checked export with `scripts/export_research_package.py`, the
Git-free direct command is `python3.12 -I -B
research/high-cube-paid-composition/verify.py` from the extracted root.

Six controls cover an extra adapter read, a wrong coefficient, omitted
native charges, one-swap reversed-ADD accounting, source corruption and
receipt types. The loose tariff can tolerate an extra read; its exact
recorded trace detects that mutation.

The finite checks do not execute fitted B1 or selected GL64 payloads.
All-width validity rests on the written argument and pinned component
premises. Full machine-step cost, backing, recursive stock, interrupted-call
recovery and admission remain open. No selected cold replay or new kappa.

## Sources and credit

Base main: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[SOURCES.json](SOURCES.json) pins the activated runtime closure and records
exact, hash-checked copies of the two pending proof dependencies in
`sources/`; no unmerged Git objects are needed for replay. The checker
reuses PR2982's observer and extends its
matrix oracle to nonidentity low rows. Frozen sources remain unchanged.

This is a declared change from the generic stock card to its released local
traffic handoff; no stage coefficient is inferred. The entry overlap scan
covered 336 open PRs, 2,630 closed PRs and 2,129 Discussion records with
complete pagination. Sparse local notes, arbitrary diffs and unpublished
work are outside coverage. See [TASK.json](TASK.json) and the
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19004103).

Credit Jose Manuel/jmbarrancoml (PR2915/2899/2809), David Arias (PR2753),
Nick Petalas (PR2951/2968/2982), commdata2338 (PR3233), Sagar Thakrar
(PR3265), Arham Tahir (PR2877), ywz65, Ross Richardson and the retained
PR2157/PR589/source lineage. Their component bounds and algorithms are reused.

Krzysztof Wójt with substantial OpenAI Codex assistance, including Luna
support for read-only inventories and bounded source counts. Author-checked
automated work, not independent human/formal review. Apache-2.0.

## Open next questions

1. Discharge the fitted B1 contract at a real reached call, including
   complete spectators, borrowed state, output ownership and uniform cost.
   Start at pinned PR2899 and its C0 premises; elementary fixtures cannot
   resolve those dependencies.
2. Join this tape bill to actual backing lifetimes and finite-control
   transitions in the enclosing caller before assigning a stock coefficient.
   A new local constant or cutoff comparison does not resolve that obligation.
