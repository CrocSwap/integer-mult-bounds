# Split-pair dual-suffix joint frames

The conditional saving is **κ=120777349/2500000000000=4.83109396e-5**,
with exact bit saving **2415663683/50000000000000**. This improves PR60's
conditional saving by approximately **1.3974275711%**.

The producer combines Rohan Garg's PR59 split-pair groups with Rohan Gupta's
PR55 dual-suffix layout and native orders. Eumemic's joint compiler, with
Chafik Boukhalfa's PR60 ranked reclamation, is unchanged. The explicit provider
uses neither paid clones nor PR59's recorded permutations and restores temporary
module/provider substitutions. Original source files and credits are retained.

| Quantity | PR60 | This composition |
|---|---:|---:|
| h23 auxiliary roles | 30,688 | 30,118 |
| h25 auxiliary roles | 40,338 | 39,663 |
| Physical width W | 150,167,598 | 147,661,173 |

The [proof](PROOF.md) explains the local identities, invertible dirty-scratch
construction and exact full-network comparison. The all-size analytic,
residual-compiler, routing and fixed-tape interfaces remain inherited assumptions.
This is neither a formal proof of the complete theorem nor a global optimum
or measured runtime claim. The original PR60 verifier and its immutable
comparison certificate remain available.

```sh
make split-dual-verify
make verify
```

The focused target regenerates both words exactly, independently replays all
source/target/dirty columns in both orientations, reconstructs physical frame
transitions and all actual CRT profiles, and verifies the rational recurrence,
47 strict assembly inequalities, seven margins, eventual cutoffs and rejection
of the next grid points. It explicitly excludes the complete old PR60 profile
at the new bit saving. Repository validation is recorded separately in
`certificates/split-dual-repository-validation.json`.
