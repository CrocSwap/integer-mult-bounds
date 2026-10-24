# Clean connector Gray optimum

**Exact local schedule and price theorem; no new kappa.** The paid extra-row
model now uses a classical Gray cycle. For n immutable sources, all nonzero
mask outputs, uniform source price b>0 and readout price a>=b, the map-call
optimum over all finite legal words is `2^n b+(2^n-1)a`. At five sources this
is 32 source calls and 31 readouts, versus 160 and 31 in the prior clean
schedule. A concrete a<b counterexample states the limit of this theorem.

The [proof and full invoice](PROOF.md) give the arbitrary-map endpoint and
unbounded-word lower bound. [connector.py](connector.py) runs the explicit
allocation, zeroing, map calls and release. [RESULT.json](RESULT.json) records
the replay. The retained five-source fixture costs **34944**, with all its
charges: **3712 less than the old clean schedule** and **5810 less than the
proved dirty-connector optimum**. These are declared tariff units, not a
physical supplier or runtime result.

## Replay

From the repository root with standard-library CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/clean-connector-gray-optimum
```

Expected status: `PASS_CLEAN_CONNECTOR_GRAY_OPTIMUM_NO_NEW_KAPPA`.
Normal and optimized checks cover 12 formal words, 18 full-state optima,
192 linear-map cases, 608 retained basis columns, 64 mixed states and 15
mutation controls. Source hashes and a typed receipt are checked. The
standard export supports replay without Git or network. No full predecessor
945-pairing tariff census, physical supplier, selected cold replay, Lean or
Docker run is included. The task card's original 945-pairing positive control
was run separately and passed. No independent human review is claimed.

## Sources and credit

Base `7c472563474e60185e6ca101a17622133d047e56`, priority revision 7.
[SOURCES.json](SOURCES.json) binds runtime inputs; selected-result/catalogue
files are historical provenance. This is a refinement of an existing paid
alphabet extension, recorded as a changed card scope in [TASK.json](TASK.json).

Cinna Davis's [PR #1954](https://github.com/CrocSwap/integer-mult-bounds/pull/1954)
supplies the clean-row fixture, tariff and arbitrary-map contract. Her
[PR #2271](https://github.com/CrocSwap/integer-mult-bounds/pull/2271) has related
Gray-tour work under a different borrowed-source/common-ADD contract. The
classical reflected Gray cycle itself is prior mathematics. Ross Richardson's
[PR #943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) supplies the
original generic dirty connector. Adam Gall's
[PR #2063](https://github.com/CrocSwap/integer-mult-bounds/pull/2063) supplies
the all-tariff dirty optimum. None of those results is claimed as new here.

New analysis, implementation and writing: Ali Romman with substantial OpenAI
Codex assistance, Apache-2.0. Original source notices remain unchanged.

## Open next questions

Identify one recursive caller that can host this extra row and expose uniform
complete map prices. Add its actual allocation, map lowering, descriptor,
precision and contraction bills before comparing complete suppliers. The
present endpoint alone does not supply that caller or a complete kappa gain.
