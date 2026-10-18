# Verification contracts

The test authoring gate was applied before the checks were added.

| Contract | Credible failure | Check and distinct coverage |
| --- | --- | --- |
| Uniform state and output error | Wrong second difference, chart, or guard width | Direct quadratic residues and full-angle outward rational intervals |
| Exact stream and seed cleanup | Wrong inverse order or omitted arithmetic uncomputation | Both phase-state registers and seed outputs reach exact zero |
| Dirty operator and inverse | Wrong outer phase direction or target-dependent roundoff omitted | Actual leaf and factor calls with odd lowest bits, large dirt, and geometric-sum oracle |
| Complete access bill | An input read, data move, or inverse pass is not charged | Data banks count literal accesses on two physical tapes and reject copies or slices |
| Linear stream work | Term evaluation remains inside each phase site | Executed product, division, and seed-term counts at three lengths and precisions |
| Reproducible package | Missing local dependency, altered source, or unchecked receipt | Source pins, semantic mutations, and relocated full receipt replay |

These checks extend the phase-interface boundary. They do not duplicate
the full selected-frontier replay or claim the inherited dirty solver has
been re-proved. No production export or injection hook was added for tests.
The new public phase lifecycle is also used by each production data pass.

The small phase domain is all residues for moduli 1 through 9 at `W=2`
and `W=24`, with `L=2m+1`. Seven extra cases cover wider precision,
negative or wide numerators, large moduli, and chart boundaries. One long
case uses `a=12345`, `m=65537`, `W=24`, and `L=16384`; all steps execute,
and indices divisible by 257 plus the last index get interval checks.
There is no random seed or open-ended search. Every stated case completes.

The dirty-word domain has lengths 1, 5, 8, and 17, strides 0, 2, -3,
and 7, both signs, and one or three factors. Each call is followed by
its exact inverse. One-factor cases use no borrowed array; three-factor
cases retain two arbitrary borrowed arrays. This is finite coverage of
the written all-length theorem, not an exhaustive input audit.
