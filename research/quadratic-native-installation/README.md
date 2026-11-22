# A quadratic phase compiler for the signed multiplier

The fixed setup of the general signed multiplier now generates its full nine-coordinate Clifford atlas without building a dense state vector at each phase check. It solves for admissible binary paths through the real circuit and sums their quadratic phases exactly. The installed machine also shares the helper/return role descriptions of its 48 chronological invocations and keeps the original port identities.

| Resource | Pinned seven-stage source | Quadratic installation |
| --- | ---: | ---: |
| Conditional complete κ | 0.003890115286594445 | 0.003890115286594445 |
| Fixed serial setup upper bound | 2^513 transitions | 2^241 transitions |
| Stored chronological port records | 334,176 | 25,621 plus 145 segment descriptors |
| Exact rational donor values stored separately | 323,573 occurrences | 60,206 distinct immutable values for the same occurrences |
| Numerical rank exponent log₂ M | 19,000 | 19,000 |
| Largest binary rank exponent log₂ N | 95,600,000,000,000,000 | 95,600,000,000,000,000 |
| Sufficient activation exponent A | 101,973,332,976,357,367 | 101,973,332,976,357,367 |
| Complete recurring upper bound log₂ C | 1,670,731,087,109,379,198,659 | 1,670,731,087,109,379,198,659 |

The setup change applies to all seven installations in the pinned source. The table uses its highest-rate profile. The sufficient input length is still 2^(ceil(2^A/6)−1)+1 bits. The new compiler returned the original atlas byte for byte. Every active chronological label, paid return, independent productive output and numerical precision obligation remains in force. The added work to emit the shared port tags is below 2^52 steps per two-copy source call and fits the existing complete numerical clock. The 2^241 ceiling includes the actual binary and Gaussian generation, serial lookup, exact arithmetic, validation and cleanup. It is conservative. Its reduction combines a changed algorithm with a sharper fixed-tape lookup argument. [Quadratic construction and correctness](PROOF.md) · [Full cost and limits](COST.md) · [Seven-stage source](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/RESOLUTION.md)

Two fresh runs of each implementation on the same seven-stage profile averaged 82.20 seconds for the original fixed initialization and 5.20 seconds for its replacement, a 15.79-fold reduction. Mean process high-water memory fell from 307,552,256 to 280,141,824 bytes. Measurements cover both suppliers. The procedure restores each signed machine separately and times its actual imports, source authentication, chart reconstruction, ordered label and grade generation and creation of all eight receiver recipes. The bootstrap of the comparison harness is separately outside that timed interval. The resulting program still faces an astronomical sufficient input scale. Production throughput and a performance crossover remain unmeasured. See the [measurements, environment and checks](EVIDENCE.json).

The competing fixed-inventory endpoint is κ=0.003890115286594461. It uses a different fixed installation. The comparison above holds the actual seven-stage machine fixed and claims a setup improvement at its reported κ. The five inherited scientific premises are native action on all columns, owned erasure, compiler correctness, precision/tape lowering and analytic recovery. The phase result supplies a complete construction for this particular fixed atlas. [Competing endpoint](https://github.com/Clear1nsight/integer-mult-bounds/blob/328b858e24709495843abc751fcbf5df35a89da8/research/p104-retimed-dyadic-endpoint/README.md) · [Predecessor credit](NOTICE.md)

## Reproduction

Use CPython 3.12 with assertions enabled and Git on PATH. These commands work from a clean checkout. Each creates a new temporary signed machine. The precursor archive, its members, the original runtime files and the installed delta have separate digest checks. No network connection is required.

```sh
cd research/quadratic-native-installation
python3.12 -I -B verify.py phase
python3.12 -I -B verify.py cost
python3.12 -I -B verify.py physical
python3.12 -I -B verify.py product
python3.12 -I -B verify.py original-setup
python3.12 -I -B verify.py setup
```

Each successful command prints `PASS_QUADRATIC_INSTALLATION` and its mode. The phase check covers all 2,971 paid charts and both sides of all 104 external ports using a separate signed-tableau and exact-state implementation. A phase mutation fails that check. The full native word on two independent nonzero witnesses returns all 105,216 owners after traversing every one of the 564,144 cuts, including 16 and 15 nonzero cuts in the two copies. It uses an exact compact state representation for these verification inputs. A separate unchanged finite Fourier geometry returns −345550037539 with the five expected coefficients and both input heads restored. This small signed product executes its inherited local Fourier kernels. The native word check supplies the separate evidence for the two nontrivial provider invocations.

To use the new installed machine directly, give the bootstrap an empty directory. The construction uses normal Python imports for all emitted modules.

```sh
python3.12 -I -B bootstrap.py /tmp/quadratic-multiplier
python3.12 -B /tmp/quadratic-multiplier/band_product.py --profile resolution -741503 466013
```

The second command prints `-345550037539`. To check the three Lean theorems, use Lean 4.34.1 and mathlib at the revision in [the receipt](EVIDENCE.json). The runner builds the source in a temporary directory, prints its axioms and calls leanchecker. The phase formulas and arbitrary weighted binary elimination steps are formal. The signed compiler, raw path, timing and complete multiplier remain outside Lean.

```sh
python3.12 -I -B verify_lean.py /path/to/lean-4.34.1 /path/to/mathlib
```

## Open next questions

Can a different physical source use the lower setup cost to make a larger useful word verifiable at a better complete rate? A candidate needs an actual ordinary supplier with new productive and paid roles, a restored data path and complete finite pricing. This installation preserves the current word and its crossing.

Can an active-field representation improve the binary rank and connected entrance at the same κ? Label sharing here applies only to immutable descriptions. The arbitrary productive fields and their simultaneous reserves still determine the scale of the running machine.
