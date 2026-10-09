# Precision refinement of the pinned paired-cube witness

This certifies a small arithmetic refinement of PR178 at commit
`2c4a380126640abfcdce398ced255d1dd5d1d007`. The pinned headline is
`13118356069/20000000000000 = 0.00065591780345`; the refined conditional headline is
`655917923729/1000000000000000 = 0.000655917923729`, an increase of
`120279/1000000000000000 = 0.000000000120279`.

The contribution changes precision and positive backoffs. It preserves the
upstream graph, matching, physical word, terminal sinks, and all upstream
files. It does not claim an independently reconstructed local schedule or
a complete integer-multiplication theorem.

From the repository root, with Python 3.12 or later:

```sh
python -B research/precision-certificate/verify.py
python -B research/precision-certificate/test_precision.py
python -O -B research/precision-certificate/verify.py
python -O -B research/precision-certificate/test_precision.py
```

The package also runs by itself: the three inputs and both generic checkers
are included, and the verifier has no imports from upstream scripts. To
recompute the saved certificate, run the first command with `--write`.
The ordinary command recomputes everything and demands exact byte equality
with the checked-in certificate. It requires no third-party packages.

`SOURCE.json` records the exact input revision, raw hashes, checker provenance,
and package source closure. The verifier independently fixes the three input
hashes and the two checker hashes, checks every source byte, and binds the
source manifest hash into the certificate. The supplied controls reject
the next supplier/headline grid points, a missing paid child, invalid ranks,
an underpaid literal guard, a wrong revision label, and altered source bytes.

The independent moment implementation uses the `-log(1-u)` series and
rational exponential bounds; the independent assembly implementation derives
the bridge and 47 slacks from relational inequalities. Both are copied
unchanged from reviewed generic checkers, with their hashes recorded. The
certificate uses the pinned stored component inventories as mathematical
inputs, not imported supplier or assembly answers.

The new terminal-sink schedule and L1 bit aliases require their own geometry
and scalar verification. The upstream sink checker has exhaustive frame and
ledger scans with seeded modular scalar replay; the upstream physical bit
checker uses seeded 64-lane replay. This arithmetic package adds no exhaustive
formal-basis or Gaussian/Pauli phase claim. The retained compiler, analytic,
exact-recovery, and fixed-tape contracts remain explicit in [PROOF.md](PROOF.md).

Prepared by Muhammed Ali Mehmood with substantial OpenAI Codex assistance.
The refined witness retains Rohan Arun's PR178 operation-frame refinement,
prepared with OpenAI Codex assistance, and eumemic's upstream module, physical bit, and
terminal-sink integration, developed with Anthropic Claude assistance. The
terminal-sink lemma is due to jamesyc (PR166); shared-core accounting and the
finite bridge are due to icekylinx (PR144), with earlier local words and
assembly interfaces by eumemic and Zhihao Chen/Swapnil Jain. The balanced
positional transform is from hipotures/RaD. See [NOTICE](NOTICE) for attribution
and [LICENSE](LICENSE) for the unchanged Apache-2.0 license.
