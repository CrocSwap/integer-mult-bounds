# P104 relay and carrier-restoration replay

This kit reconstructs two native graphs from the public #7761 package. The default graph composes nine relay edits with eight additional paid carrier restorations. The two graphs preserve the original 1,262 independent native inputs and outputs and use the identical 2,048-call signed caller from #7761.

| Graph | Paid moves per native call | Directed raw rank-power crossing |
| --- | ---: | --- |
| Public parent #7761 | 5,746 | 0.00382069832565 to 0.00382069832566 |
| Nine relays | 5,739 | 0.00382275513694 to 0.00382275513695 |
| Nine relays plus eight carrier restorations | 5,731 | 0.00382815604916 to 0.00382815604917 |

The strongest raw bracket sits 0.00000254227649 below the target 0.00383069832566 at its upper endpoint. Each variant’s price includes all paid and productive ranks. This replay covers the exact scalar operator, chart locality and the complete signed rank tariff. Guarded physical execution, ordinary resource accounting and the outer compiler are separate qualification checks under the five inherited framework conditions.

## Conditional result

With the same 2,048-call signed caller as #7761, the seventeen edits give **κ ≥ 0.00382815604908** under the original five conditions and BIT pin 0.00385248. This exceeds the comparator’s directed upper endpoint 0.00382069832566 by **0.00000745772342**. The target for this experiment was 0.00383069832566. The conditional lower is **0.00000254227658** short. The nine-edit graph alone qualifies at 0.00382275513686. [Independent application receipt](evidence/application.json) · [Public-source physical replay](physical/README.md)

Seven rank-one bypasses, two historical hub rebindings with four terminal repairs and eight paid carrier restorations preserve every productive rank. Per native call the net paid counts change by −14 at rank 1, +1 at rank 2, −2 at rank 3, −8 at rank 4, +6 at rank 6 and +2 at rank 7. The full finite invoice has 12,130,784 paid and 2,185,472 productive targets. At the round target it still needs between 111.994707697229071044897937 and 111.994707697229071044897938 signed price units. [Signed invoice](REPLAY-SEVENTEEN.json) · [Literal restorations](evidence/restoration-witnesses.json)

Independent replay checked the 400 main and 862 helper inputs in both directions, all 19,456 dense forward and adjoint Gaussian columns on the 19 changed routes, and guarded retirement of 8,260 homes. Against #7761 it charges 136,642,560 additional scalar services, 35,512,320 additional resets and 8,724,480 additional typed transfer legs. Ordinary map slots decrease by 61,440. The new depth and coefficient bounds pass all 54 strict and four functional outer conditions. The bound inherits native all-column execution, owned erasure, compiler correctness, precision-tape realization and analytic recovery. [Signed route controls](evidence/routes.json) · [Ordinary and outer replay](physical/physical-replay.json)

The follow-up screen searched the regenerated seventeen-edit graph in both orientations. Requiring unused starting and pivot legs, the same direct restoration rule yielded zero additional positive candidates among 3,330 forward and 3,321 transpose starts. Further work on this graph needs a different causal relation or caller construction. [Bounded search receipt](evidence/unused-paid-leg-recurrence.json)

## Reproduce

Use CPython 3.12 and its standard library. The source is the public [#7761 package at its pinned head](https://github.com/CrocSwap/integer-mult-bounds/tree/d5219594c9b0e80c002a75e79b85766256496b07/research/p104-mixed-batch-boundary). Point the verifier at that package directory.

```sh
python3.12 -I -B verify.py --parent-package "$parent_package"
```

The default reads seven digest-bound constructor files from the public package, copies their bytes to a fresh private directory and runs the public `pr7756/construction.py` there. It authenticates the compact graph and applies both differentials. The optional snapshot mode only requires the exact `evidence/price.json` from #7761 beneath the supplied package directory. The snapshot may be raw or gzip-compressed JSON.

```sh
python3.12 -I -B verify.py --parent-package "$parent_package" --baseline-graph parent.json.gz
python3.12 -I -B verify.py --parent-package "$parent_package" --variant nine
python3.12 -I -B verify.py --parent-package "$parent_package" --write-graph reconstructed.json
```

The verifier prints the selected result, all input digests, the complete invoice, forward and transposed row counts and the directed price checks as JSON. The last command also writes the reconstructed canonical graph.

## Differential

`DELTA.json` removes seven paid moves, relocates four hub moves, reroutes seven surviving moves and changes 182 retained scalar forms. `STACK-DELTA.json` replaces eight disjoint pairs of rank-four and rank-two moves with eight rank-six moves, and changes 231 retained scalar forms. Each move edit includes its exact chart preimage. Each scalar edit identifies the form clock and the affected donor with its old and new coefficients. A null coefficient denotes absence. Inserted paid moves supply a full new scalar form. Both stages rebuild a stable topological schedule and check its digest.

The verifier checks exact row equality on all independent inputs in each orientation. It validates paid chart nesting, donor availability and integrality of every basis scalar product on the fixed integer grid. Its controls reject scope and preimage changes, changes to the public interface, cyclic schedules and an invalid restoration rank. It also gives a concrete affected input column when each of four terminal corrections is omitted.

The price starts with the digest-bound finite #7761 invoice and adds the exact paid rank difference at every one of the 2,048 calls. The productive side stays fixed. Directed integer square roots bound each rank power. A rational interval calculation verifies that the signed price decreases on the interval through the common BIT pin 0.00385248 and checks the two bracket signs and the target shortfall.

| Artifact | SHA-256 |
| --- | --- |
| Canonical public parent graph | `c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84` |
| Canonical nine-relay graph | `91af585f71ff53cf5771d532f90b5f3f4acb21abaf9381d219539a679f2969db` |
| Canonical seventeen-edit graph | `eb8a9cbf477308f8baa949a780a5a3b6d998ff9a64934591839a4b5690186702` |
| `DELTA.json` | `a0c386cbb7d777cea8638a4b6d99aa60342c69e30683762bf1dae60110253ebf` |
| `STACK-DELTA.json` | `664da8fec58eacb6bb205f5baf884af76af1a98e9bad33edcf764093bb4d2f92` |
| #7761 `evidence/price.json` | `9d7cb0ebcf4a83b9ffa2596c4a1c178b79c9fa91a6a54b195be3083b411726f6` |

## Credit

DreamingOfClouds, with Claude assistance, supplied the archived hub reroutes and the P104 banked-circuit toolkit. Ali Romman supplied the compact native graph, signed caller, physical binding and finite application in #7756. Clear1nsight extended that caller in #7761 and prepared this replay and its graph differentials with OpenAI Codex assistance. The exact power comparison follows the canonical repository method prepared for Ali Romman. The [notice](NOTICE) gives source heads and predecessor credit. [Hub reroutes #7705](https://github.com/CrocSwap/integer-mult-bounds/pull/7705) · [Toolkit #7727](https://github.com/CrocSwap/integer-mult-bounds/pull/7727) · [Native construction #7756](https://github.com/CrocSwap/integer-mult-bounds/pull/7756) · [Caller #7761](https://github.com/CrocSwap/integer-mult-bounds/pull/7761).
