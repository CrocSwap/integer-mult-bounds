# Literal selected rank-two MOVE with an owned HOME boundary

This package implements selected event `[MOVE,1526,601,470,true]` at index 28141, from frame `[137]` to `[75,137,265]`. The Boolean denotes ownership. A fixed 115,776-instruction program on 31 tapes executes the complete quotient `T470 T601*`, including its nontrivial phases. A 115,953-state adapter on 35 tapes returns the completed six-Gamma header and DATA to the identical owned HOME.

The new step is the actual source-specific monomial/positive-leaf join in the Gamma6/HOME format. #6978 already supplies rank-two positive children in a different coded ABI; this is not a new rank-two factorization or a first rank-two leaf. Exact source pins, predecessor notices and the bounded overlap report are preserved under [implementation/](implementation/).

## Result and supplied premises

The primitive retains all nine `f`-bit address slots, all spectators and `r` Gaussian coefficients. Two positive first-slot C passes, conjugated by two literal three-CNOT slot swaps, realize `C^(tensor 2f)` without changing the header's `f`. A new physical guard checks `2f <= cutoff`. All 66 CNOTs in the two source factors and slot swaps are paid.

For `V=2PSr 2^(9f) w`, header bit count `E` and complete field length `F=E+V`, the proof gives

```text
T_core <= 2^24 (fV+E+1)
K_core <= K_entry + 1024 (V+E+1)
T_HOME <= 128 (F+1) + 2^24 (fV+E+1)
K_HOME <= K_entry + 1088 (F+1)
```

This direct bill includes descriptors, copies, phase arithmetic, both C passes, every CNOT, returns and cleanup. General B1 full-bank gathering and scattering remain separately charged. Earlier backing is retained after erasure and shorter reuse.

Entry is supplied: an already-reserved live typed owned packet, canonical six-Gamma header, signed `w>=2` fields on a common grid, matching geometry, distinct owners, complete spectators, blank required private windows, phase fit and integrality/range of every central C prefix. The source and receiver must carry the correct frames. No typed INIT, endpoint scaling, packet producer or receiver is synthesized. Rejection protects original DATA/HOME but does not promise private cleanup or retry. See the [proof](implementation/PROOF.md) and [root review](ROOT-REVIEW.md).

## Independent evidence

The root executed a fresh dense width-six packet using a separate sparse signed-origin graph interpreter. Its oracle is a separately written dense rational evaluation of the original frame definition, using span-set basis extension and inverse permutations. It imports neither the author's oracle nor its native verifier or lowered recipe as the arithmetic oracle.

That replay completed **30,838,694** transitions, with exactly **6,156** HOME writes, all after primitive return. It checked all 115,776 embedded instructions and restored all 35 heads, private bodies and opaque exterior sentinels. The author checker additionally exercises smaller same-owner reuse, cutoff rejection, later second-child numerical rejection, complete wrong-phase execution, actual source corruption and original operator binding. These finite checks corroborate the quantified proof.

Author normal and optimized checks were replayed on the frozen publication snapshot. The optional full-source binder authenticated the complete canonical archive and eight proof pins. Receipts and hashes accompany the package. No human or formal-kernel acceptance is claimed.

## Reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B -W error research/literal-owned-rank-two-move/implementation/verify.py
python3 -I -O -B -W error research/literal-owned-rank-two-move/implementation/verify.py
python3 -I -B -W error research/literal-owned-rank-two-move/review/root/check_rank2_root.py research/literal-owned-rank-two-move/implementation
python3 -B scripts/research_package.py --package research/literal-owned-rank-two-move --check-only
python3 -B scripts/research_package.py --package research/literal-owned-rank-two-move
```

Expected markers are `PASS_LITERAL_OWNED_RANK2_HOME` and `PASS_ROOT_RANK2_HOME`. Default replays are read-only; `--write` explicitly regenerates the author's receipt. Runtime inputs are local. The optional full-source command is:

```sh
python3 -I -B research/literal-owned-rank-two-move/implementation/bind_source.py --source-repo /path/to/reference/checkout
```

The top-level `VERIFY.json` is a registered manifest. The nested author freeze remains unchanged, including its historical status and proposed PR description; the current independent review is at the top level.

## Open next questions

[TASK.json](TASK.json) gives first steps and blockers for three questions: bind the actual selected producer and receiver to this supplied entry; close the complete owned interval with INIT, SCALE, dirty CLEAR and every intervening cost; and develop a faster nonleaf mechanism whose full joint-parameter bill meets the selected tariff. The direct `fV` method is a leaf implementation and does not supply that faster tariff.

## Kappa, scope and credit

**No new kappa.** The selected value remains `363005817/100000000000`, and all five framework assumptions remain. This is a source-bound primitive sub-lemma relevant to native execution, ownership and precision/storage; it is not an unconditional multiplication theorem, a full owned lifetime or a complete supplier.

Prepared for **@CubeJerry**, with substantial OpenAI ChatGPT/Codex assistance. One worker developed the implementation and composition proof; the root independently checked graph embedding, the cost sum and original-frame arithmetic. Credit #6978, the retained phase/G/C literal tables, the earlier rank-one join and permanent-HOME dispatcher, and [implementation/NOTICE.md](implementation/NOTICE.md). Apache-2.0.
