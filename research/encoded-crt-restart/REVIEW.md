# Independent source and proof review

The root orchestrator independently reviewed `restart.py`, the complete proof,
the exact role layout and source contracts. This is a separate AI review with
substantial OpenAI assistance for @CubeJerry, not human or formal-kernel acceptance.
Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`.

## Mathematical findings

The new claim follows by induction over successful linear-use calls. The entry
premise includes every historical cell being blank. Rearm changes only the
sixteen markers; pinned consumers erase their complete current extents. Cells
past those extents stay blank from the induction hypothesis. Consequently a
shorter call need not rescan old capacity, and later growth preserves the same
physical owner. The two local validation reads do not prove arbitrary unseen
tails clean; no dirty-tail admission or failure recovery is claimed.

The 79 physical roles are stable across calls, including the retained 63-role
bank. Source production, re-encoding, retained prefixes and payload transport
remain caller bills. Direct addition of the displayed role vector yields
`3Ad + 74A + 23d + 223`. Each component is monotone, so summing individual
historical maxima gives the stated `K0+D(Amax,dmax)` bound. The proof does not
replace this sum by a maximum of total fresh footprints. Source-operation
constants remain distinct from a literal binary instruction certificate.

## Independent computation

`independent/check.py` imports the production adapter and pinned runtime, but
neither author verifier nor its exhaustive defining-congruence oracle. It
constructs each expected current-node CRT value using modular inverses and
successive congruence reconstruction, then evaluates forward or reversed
balanced levels independently. Its freshly encoded inputs exercise 32 complete
calls, 96 numerical nodes, both directions, padded values, and 2/4/8/2-axis
geometry changes. Source metadata/tails, full blank private tails, head returns,
identities, meters, nonshortening histories and the storage polynomial are
checked. New physical constructors are sealed after acquisition.

Run from the repository root:

```sh
python3 -I -W error -B research/encoded-crt-restart/independent/check.py
```

The exact receipt is `independent/RESULT.json`: 32 calls, 96 nodes, one 79-role
inventory, 4172 retained cells. Author normal and optimized replays separately
cover 174 calls, 270 nodes and 14 negative controls. These finite cases are
corroboration of the source-relative proof, not a universal theorem by testing.

`independent/SOURCE-BINDINGS.json` records the independent binding of all ten
exported files to their actual commit paths, Git object hashes, SHA-256 values
and byte counts. No predecessor file was edited.

## Reviewed scientific bytes and limits

- `restart.py`: `462fd6f2a0bc0b5eaf5d74d2bda65b0c26ababbbafc06670e2a0cc9e46b5e7d6`
- `PROOF.md`: `40d60f9894bcae292bd35b436efed1d6e53615d6a6782af9e8b6842da2e44772`
- `checks.py`: `43e88fd7426623b71fa33dfe4913d765cc4c7493d55a4c9bec8e34353636bb74`
- `verify.py`: `1d47929cd7bb04e3549b52176cca9b9f1fed2ebf1af064789121e7a0e901f20e`

No critical unresolved issue was found in this scoped restart argument.
Numerical/source predecessor contracts, clean initial history, legal successful
linear use, and source-model refinement remain explicit premises. Actual
exceptional-key caller admission, complete binary lowering and all five global
assumptions remain open. No new kappa is claimed.
