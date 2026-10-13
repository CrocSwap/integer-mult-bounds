# The first cost-six puncture threshold for odd E8 root pairs

For the exact label pairing used in PR717/PR968, the least number of E8
root-line punctures that can lower a term with two distinct nonorthogonal
root normals to F2 pairing rank at most six is **26**. This holds for every
one of the 6,720 ordered odd root-line pairs.

The first support dimension drop beyond PR968's `p <= 24` theorem does not
yet lower the term to six. At 25 punctures there are exactly 126 possible
deletion sets that can make either relevant support span have dimension at
most seven; every one has pairing rank seven. A 26-puncture witness has
support dimensions `(8, 7)` and pairing rank six. Its 25-puncture parent has
dimensions `(9, 7)` and rank seven. The additional deletion lowers the other
support dimension, which is the new mechanism examined here.

This is a term-level threshold, not a minimum for all eight-term decoders.
An exact rational eight-term completion is supplied and fully priced:
term costs are `(6, 9, 9, 9, 9, 9, 9, 9)`, totaling **69 copies on 94 ports**.
Its ratio `69/94` is worse than PR968's `56/104`; it is not a supplier
improvement. No physical circuit, precision admission, native replay or
new kappa value is claimed.

From the repository root, with Python 3.10 or newer and no third-party
dependencies:

```text
python research/root-pair-first-drop-seed48/verify.py
python research/root-pair-first-drop-seed48/check_sources.py
```

Expected final lines:

```text
PASS_ROOT_PAIR_FIRST_DROP_S48 threshold=26 candidates25=126 orbit=6720 rank26=6 completion_cost=69 ports=94 controls=6
PASS_ROOT_PAIR_SOURCE_CROSSCHECK pairing_entries=14400 rejected=3
```

The main replay independently constructs the E8 model, enumerates all
130,305 pairs of nonzero distinct dual functionals on each support, and
checks the ranks with both bitset and dense binary elimination. Eight
explicit reflection permutations preserve the supports and label pairing;
their orbit is compared against the complete set of 6,720 ordered odd
pairs. Thus no unverified group-transitivity assumption is needed. The
separate compatibility replay compares all 14,400 pairing entries with
the retained PR968 model. It is not used by the main proof.

`CERTIFICATE.json` records all 126 candidate masks, the exact puncture,
rational decoder matrices, finite counts and controls. Regenerate with
`python research/root-pair-first-drop-seed48/verify.py --write-certificate`;
ordinary replay recomputes everything and rejects a certificate mismatch.
`SOURCES.json` binds exactly three predecessor files at base
`2921874911956718fcaaaf9396fe8267b3cfa9f0`, with CRLF normalized to LF.
Replay does not depend on the mutable selected-result pointer.

See [PROOF.md](PROOF.md) for the completeness argument,
[VALIDATION.md](VALIDATION.md) for executed checks and limitations,
[OVERLAP.json](OVERLAP.json) for the bounded overlap check and
[NOTICE.md](NOTICE.md) for attribution. Prepared for @woklerx with substantial
OpenAI Codex assistance, under the repository's Apache-2.0 license.
