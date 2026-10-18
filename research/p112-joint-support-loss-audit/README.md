# Exact joint P112 deletion loss through 43 ports

PR1787's two-total support screen uses valid but conservative retained
rank-loss bounds. This audit proves the exact maxima **0,2,3,4** on the
ranges **0..23,24..35,36..39,40..43**, replacing its last two upper bounds
4 and 5. All 42 minimal four-reader supports need 8 extra ports for a fifth
reader and 12 for a second loss in an affected reader.

The full-rank on-column two-total COPY floor consequently rises from
strictly above 64 to **at least 66** through 43 source ports. The broader
64 no-saving result and the support method belong to the predecessor.
This is a scoped bound, not a new decoder, supplier or kappa.

[PROOF.md](PROOF.md) gives the completeness argument and exact assumptions.
[RESULT.json](RESULT.json) contains all 42 supports, 44 sharp deletion
witnesses, per-reader inventory digests and the integer price screen.
The verifier imports no predecessor checker. It uses literal pairing-row
XOR closure and support joins; a second rank implementation checks every
witness. All 511 added-reader rational ranks are certified by modular lower
bounds plus symbolic upper bounds. The selected frontier is unchanged.

## Reproduce

```sh
python3.12 scripts/research_package.py --package research/p112-joint-support-loss-audit
```

Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/p112-joint-support-loss-audit outcome=completed`.
The standalone mathematical marker is `PASS_P112_JOINT_SUPPORT_LOSS`.
Stdlib only. Commands, timeouts and live input pins are in VERIFY.json and
SOURCES.json. The exact base is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`;
OS-random assignment seed 60 selected the donor's adversarial audit track.
PR1787 was reviewed at `2b821b14a7cd5888df95531c98d18ee3797e36c3`;
[its proof](https://github.com/CrocSwap/integer-mult-bounds/blob/2b821b14a7cd5888df95531c98d18ee3797e36c3/research/p112-two-total-support-threshold/PROOF.md)
is the source of the audited 0/2/4/5 ceilings. No pending source package
is required to replay this independently implemented result.

## Open next questions

Finite exhaustive code/support inventories plus a written proof cover all
deletion sets through 43. No proof-assistant, physical supplier, selected
cold replay, hosted CI success or independent human review is claimed.
Deletion sharpness does not establish a cheap realizable two-total decoder.

- Extend the joint loss function past 43 using minimal-support profiles
  involving third losses and five readers. No larger-union search is supplied.
- Test whether the 36- and 40-port witnesses can satisfy the two-column
  complex cancellation equations, then charge both added terms. This
  realizability problem is not solved by deletion geometry alone.

Structured questions and their blockers are in TASK.json.

## Credit

Immediate predecessor: Josie Elliston's PR1787, prepared by OpenAI Codex and
reviewed/published by Claude. Credit also to Philipp / mightyOil PR1197,
Mihir Srivastava #845, woklerx #998, commdata2338 PR1375, Hanson Sun /
bbMisk PR1432, and the DreamingOfClouds / Joel Pulikkan / GamingPuzzled
E8 decoder lineage. See PROOF.md for the dependency distinctions.
Prepared for Philipp / mightyOil with substantial OpenAI Codex GPT-6 Astra
assistance. Apache-2.0; source attribution retained.
