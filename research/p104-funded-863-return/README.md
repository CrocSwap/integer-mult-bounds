# Conditional κ = 0.003646221436446 from a funded public return

This P104 construction gains **0.000000551507748** over exact
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) in the same
signed 17-stage caller. It returns public helper 863 at rank four and
replaces its four late reads with a causal correction that uses one billed
donor split. Per native call the productive change is `T4 +1, T9 −1`; the
paid change is `P1 +1, P6 −1`. The complete invoice retains rank surplus
1,424 and uses no empty-root credits. [PROOF.md](PROOF.md) explains the
construction and assumptions; [WITNESS.json](WITNESS.json) records the
literal correction clocks.

The raw crossing lies between
`0.0036462214364462343366888845568980` and
`0.0036462214364462343366888845568981`. With the productive profile and
17 native words fixed, the ambient-145 remainder packing relaxation gives
a crossing in `[0.00580905464175, 0.00580905464222]`, about `0.002162833206`
above the proposed bound. The candidate realizes about 62.77% of this
relaxed ceiling, which applies only to that fixed profile and remainder mass.

`source.py` authenticates and reconstructs the exact #7277 word from its
complete recursive source archive. `construct.py` rebuilds the emitted
candidate independently of the search. [EARLY-RESULT.json](EARLY-RESULT.json)
records the complete price and exact native adjoint. The remaining receipts
are [NATIVE-RESULT.json](NATIVE-RESULT.json), [RESULT.json](RESULT.json) and
[PROPOSED-CLAIM.json](PROPOSED-CLAIM.json). The last is a proposed record for
review; the upstream selected record stays unchanged.

Run the four registered stages from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-funded-863-return
```

Only the Python standard library is needed. The fast gate alone is
`python3.12 -I -B research/p104-funded-863-return/verify_early.py`.
It does not stand in for the complete physical and caller replay. Scope,
limitations, and sources are in [TASK.json](TASK.json), [SOURCES.json](SOURCES.json)
and [INPUTS.json](INPUTS.json).

## Open next questions

Independently review the cache at source clock 37753 and the two signed
transports through chart 240, then run the registered checks on the exact
published head. This is the smallest useful next check for maintainer
frontier review. The result does not establish a general ceiling or certify
that all possible funded corrections have been found.

See [NOTICE](NOTICE) for the licenses and predecessor credits. The branch
also carries the exact already-published [#7257](https://github.com/CrocSwap/integer-mult-bounds/pull/7257)
CI navigation and historical replay prerequisites.
