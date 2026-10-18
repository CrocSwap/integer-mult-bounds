# Exact native payload backing for the selected BIT caller

This package closes the **payload-array component** of PR2882's released native
action storage handoff. It proves exact retained array-length peaks for the
unchanged PR2697 ADD, atom swap and sign bodies, and PR2753's linear sign.
The [proof](PROOF.md) includes the same-phase composition with PR2882's caller
cohort. This is a scoped storage lemma, with no supplier admission or new kappa.

For a complete F-bit primitive fibre, excluding its borrowed input and including
its pending result and LEFTs:

| Native primitive | Exact private payload array peak |
| --- | ---: |
| ADD | 2F+3 |
| Atom swap, w=1 | 2F+q²+1 |
| Atom swap, w>=2 | 3F+q²+2 |
| Original digit sign, w=1 | 3F+4 |
| Original digit sign, w>=2 | 3F+q+2 |
| PR2753 linear sign | F+1 |

F=U(q^w)²GS for ADD/swap; F=Uq^wS for sign. q is an odd prime, w>=1,
and U,G,S are positive spectators. The successful-call, canonical encoding,
private fresh-array and no-external-capture premises are explicit in the proof.
Clearing an array erases its content without shrinking its backing. These bounds
count reachable bytearray lengths, not Python heap capacity or physical tape
placement. Counters, numerical words, callback/program/field records and other
owners remain separate. A_payload alone is not PR2882's total private A.

For N=2,F=9,K=19,D=7,Q=4, the predecessor's structural caller bound is 92.
Joining actual native payload interiors gives restricted upper bounds of 94 for
ADD and 105 for original sign; linear sign stays within 92. This identifies a
concrete extra term before a complete reserve can be claimed.

## Reproduce

Standard-library Python 3.12, from the repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/selected-native-payload-backing
```

Portable direct commands, also valid from a Git-free copy of this directory:

```sh
python3.12 -Werror -I -B verify.py
python3.12 -Werror -I -O -B test_verify.py
```

Run the direct commands inside the package directory, or prefix each script path
with `research/selected-native-payload-backing/`. Normal verification reads the
committed [receipt](RESULT.json) and writes no source/evidence files. Explicit
regeneration uses `verify.py --write /new/path.json` and refuses overwrite.

The primary checker executes 60 complete source fixtures and 22 complete origin
bit planes. Its observation retains weak references and integer size witnesses.
The all-parameter result is the written source/lifetime proof, corroborated by
these finite executions. The controls reject source and accounting defects;
there is no independent human or formal-kernel review claim. See
[TASK.json](TASK.json) for freshness, scoped overlap and remaining questions.

## Open next questions

- **Complete native A at the same cut.** Bound Counter/Natural backing,
  numerical arenas and callback records on the actual reached action paths.
  Start with one ADD callback and join its residents with this payload cohort.
  This is needed before substituting a total A into PR2882. Those source-bound
  categories, rather than payload or caller structural cuts, remain unpriced.
- **Prove physical last-owner reuse.** Join the caller's other owners and place
  or erase scratch at actual release points. Start from the active wrapper
  investigation in Discussion2319 and its exact source pins. Reachable array
  bounds alone do not prove reclamation, fixed backing capacity or movement costs.

## Sources and credit

- Jose Manuel / jmbarrancoml, PR2697 at
  `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, supplied the caller and retained
  primitive/stream/source527 lineage, preserved in [its notice](sources/PR2697-NOTICE.md).
- David Arias, PR2753 at `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`, supplied
  the all-size logical caller and linear sign. Its source description is retained.
- ywz65, PR2566 at `bfe8317a38f03a5693470e873b29101f3f7a55e4`, already proved
  the digit time/ownership audit, three-volume live-bit bound and lane schedule.
  This contribution refines retained reference-array lengths and caller composition.
- kumagi, PR2882 at `02483f1b4414286b86d807bf2e8a8b9ddc7cd487`, supplied the
  complete structural packet envelope and private-action interface, extending
  Ross Richardson's PR2874 return-cut result. starship-s / PR2731 and Nick
  Petalas / PR2743 retain the separate nonblank-content accounting credit.

[SOURCES.json](SOURCES.json) records exact heads, Git blobs, SHA256 hashes and
byte-identical exports. Predecessor packages and the selected record are unchanged.
Nick Petalas. Substantial AI assistance was used; evidence is author-checked.
Apache-2.0, with predecessor notices retained.
