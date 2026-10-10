κ = 7.11191385398487e-4

This composes [PR251](https://github.com/CrocSwap/integer-mult-bounds/pull/251)'s 37 transported entrances with [PR254](https://github.com/CrocSwap/integer-mult-bounds/pull/254)'s 132 response-kernel helper pairs, then compresses target-prefix responses in 217 disjoint groups covering 872 targets. The exact conditional claim is 711191385398487/10^18, or κ ≈ 7.11191385398487 × 10⁻⁴.

For each target group, the checker derives every prefix response from the actual word. A dependent target response is an F₂ sum of retained target responses. Setup at the zero frame subtracts those retained target contents; the dependent prefix reads are removed; restoration at the group's checked common frame adds the retained targets back. No participating target is read as a source before its closing gate. This preserves arbitrary initial target contents and moves the dependent target's work to a cheaper frame path. The 1,081 removed prefix reads are replaced by 1,316 setup/restoration additions. All 217 groups use explicit rational closing bases from `target-selection.json`.

The kernel transform gives 132 rank-one independent entrances. For each pair, the exact prefix responses cancel over F₂ after a two-helper basis change. The omitted dirty compensation is replaced by a checked common-frame setup and full-frame inverse. The transform preserves the original source527 producer context, explicitly rebuilds the word and admits each actual entrance into its own frame registry. Its complete local histogram change is rank1:+132, rank2:+264, rank3:-264. The retained 37 transported entrances are checked independently before this composition.

The final emitted word has 786,594 weighted ADDs (785,274 of absolute coefficient 1 and 1,320 of coefficient 3). All 20,107 formal F₂ columns are checked in both directions, including arbitrary target contents, sources and dirty restoration. Both reflected frame ledgers are reconstructed from actual gate uses. The signed source527 producer retains both defining-integer decoder checks and 25 corruptions; the emitted word has separate cancellation-free signed prefix bounds 37,631 forward and 3,310,716 inverse. The F₂ payload contract does not identify its integer lift with the original target decoder.

Every five-stage path, bank assignment, chart, prime exclusion, route, copied center, cleanup and fallback is charged. There are 120 physical replicas with literal stock 2,606,465, 58,900,800 paid calls, rank mass 312,247,800 and deficit 528,000. All 9,952,200 bank assignments and 377 actual charts are rebuilt. The charts use at most 576 elementary factors and normalizers at most 815 factors; the explicit additional bank selector bill is 1,949,778,076,800. Two independent rational moment engines check the full literal profile. Three ordinary-leaf levels feed 47 strict outer constraints; the adjacent κ grid point is rejected. The bit supplier binds.

Run with Python 3.11+, SymPy 1.14.0 and assertions enabled:

```sh
python3 -m pip install -r requirements.txt
python3 -B verify.py --output /tmp/kernel-target217-verification
```

Use a new output directory outside the package. All eight mandatory stages are reconstructed without network access. The manifest rejects changed or missing package inputs. See PROOF.md, BANK-PROOF.md and the retained source notices for exact obligations and provenance.

This remains conditional on inherited all-size compiler, common weighted charts, restored rows, selectors, tape routing, prime supply, precision/recovery, complex symbolic correctness and analytic reduction. Prepared by eumemic with substantial OpenAI Codex assistance; original licenses and contributor disclosures remain included.
