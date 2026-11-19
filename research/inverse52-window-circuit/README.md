# Clean finite-window circuit for the denominator-52 sampler

For every positive window length L, one reversible circuit handles all
2,704 actual source residue pairs. It returns the exact ordered label
and first stopping depth, or an explicit censored result. Parameters,
all resident coins and every temporary bit are restored.

The exact bill is **3643+1956L gates** and **610+51L clean work bits**.
It includes weight preparation, the complete prefix, retained states,
answer extraction and cleanup. The circuit uses direct modulus-2704
arithmetic throughout. No new kappa or complete physical sampler follows.

Read [PROOF.md](PROOF.md), [window.py](window.py), [RESULT.json](RESULT.json),
[verify.py](verify.py), [SOURCE-PINS.json](SOURCE-PINS.json) and
[CREDITS.md](CREDITS.md).

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/inverse52-window-circuit
```

Both registered modes print `PASS_INVERSE52_WINDOW_CIRCUIT`. They check
338,910 distinct source/absorbed transitions, every source pair and all
coin strings through length eight, all stopping prefixes at length
sixteen, complete forward/inverse wires and exact bills. The retained
fixed-pair primitive verifier runs unchanged. No network is needed.

## Open next questions

- Bind a caller that explicitly handles the censored output. Include
  fresh coins, owner-to-residue extraction and physical access costs.
- Compare retained-history and boundary-marker implementations under
  that complete caller bill. The present circuit proves one contract;
  it does not claim a minimum gate or storage cost.

Censoring has probability at most 3/2^L under fresh fair coins. It must
not be silently discarded or replaced by a completed label.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
