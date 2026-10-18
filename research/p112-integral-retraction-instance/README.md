# P112 integral retraction instance

The fixed P112 integer matrices now instantiate the conditional Lean bridge in
[PR1610](https://github.com/CrocSwap/integer-mult-bounds/pull/1610).
Local Lean 4.30.0 replay accepts all 40 positive units and 636 named axiom reports,
including the unchanged dependency. The damaged-W control fails at its intended
false equality. This is a finite matrix certificate and its inherited algebraic
consequences, not a proof of the geometric premises needed to use them.

The complete 65-member canonical payload and checksum inventory authenticate.
All six normal/optimized Python source, integer and tooling checks pass. The
unchanged dedicated replay command also passes locally on the packaged closure;
its evidence is separate from the generic Python hook.

## Exact result

The preserved `source/P112.json` is the complete
`/units/P112/gluing_lattice_certificate` fragment of PR1497's saved certificate.
It defines ordinary integer matrices of shapes

```text
M : 288 x 104, P : 104 x 33, Q : 33 x 104, W : 104 x 288.
```

`P112Cert.certificate` proves, without a matrix-certificate hypothesis,
`MP = 0`, `QP = I_33` and `I_104 - PQ = WM` under the unchanged
`PR1497.MatrixIdentities` definitions. A proved sparse-row adapter connects the
literal coefficients to the dependency's ordinary finite integer matrix product.
The staged ordinary `decide` proofs cover all 21,409 scalar obligations. Neither
a Python result nor an unchecked evaluator is imported as a proof.

`P112Consequences.lean` binds the existing image/kernel equality, surjectivity,
actual image-difference quotient isomorphism and lattice saturation to these
constants. Its multiplicative reconstruction, converse and parameter-uniqueness
statements quantify over an explicitly lawful `PR1497.CommGroup` and retain the
individual relation-row hypotheses where required. They do not supply a field
nonzero-element adapter or prove that geometry establishes those relations.

The coordinate labels, anchors and copied `rankMetadata := 71` remain metadata.
No numeric rank operation or rank-71 theorem is defined. Geometry reconstruction,
generator-to-relation coverage, P120, zero exclusion, local Lemma 5, decoder K,
physical supplier budgets and the multiplication theorem remain outside scope.
The selected frontier is unchanged. See the exact interfaces and exclusions in
the preserved producer `source/SCOPE.md`.

## Sources and repair

The mathematical parents are [PR1497](https://github.com/CrocSwap/integer-mult-bounds/pull/1497)
at `7a1309f18f56d04c2db33bf1607e0332d19f72b3` and PR1610 at
`985fd79ffea7ae7375fe6aa3ce9940b125c7dca2`. `SOURCES.json` pins the public
audit, verifier and exact vendored bridge, and records the operator's extraction
from the authenticated saved numerical certificate. The 13,183-byte fragment
has SHA256 `a1b43a5a7a8dcce0b84858244c512e53e6c344877cc35e87937fedd2601f29d5`;
the 48,758-byte unchanged dependency has SHA256
`a27494b0d40bbf7874fd9a875e468c67d11545b266e17bc98f2ca75c77f6ee40`.

The full input can be regenerated using the pinned PR1497 verifier and its documented `python3 -I -B verify.py --certificate-out certificate.json` command, then reading `/units/P112/gluing_lattice_certificate` and serializing sorted keys with compact JSON separators, UTF-8 and a final newline. The operator rechecked the saved full-certificate hash and exact subobject equality before publication; its reported rank metadata is not promoted to a theorem.

The producer supplied source without running Lean. The original local run stopped
at the certificate's rewrite elaboration error after 37 accepted units; its
printed error-generated `sorryAx` reports were rejected. GPT-6 Pro supplied three
exact source repair sites: normalization before existing rewrites in the
generator and two damaged-certificate proofs. Regeneration updates the certificate
and four declaration line numbers. Statements, matrices, dependency, limits and
the 636-query inventory are unchanged. `REPAIR.diff` contains the complete source
delta with zero context (apply with `git apply --unidiff-zero`); `REPLAY.json` records all six repaired source/inventory hashes.

The canonical files in `source/` are preserved byte-for-byte, including their
historical source-only remarks, producer logs and original execution claims.
Those remarks describe delivery time. The separate root receipt supplies the
later local kernel evidence. No original failed source tree is duplicated here.

## Verification

The registered Python hook performs exact source/manifest binding, inverse literal
parsing, integer checks and tooling controls. It does not provision or invoke Lean:

```sh
python3.12 -I -B scripts/research_package.py --package research/p112-integral-retraction-instance
```

Generic CI acceptance is separate from kernel acceptance; no hosted-CI result
is claimed here. A separate Pro review of the original source candidate reports
no distinct mathematical flaw beyond the known elaboration error. Its compact
response was read locally; the full report and independent checker were not
retrieved, the checker was not replayed locally, and the repair was not reviewed.
See `REVIEW.md` for these boundaries.

For the dedicated kernel replay, use an already installed direct Lean binary at
version 4.30.0, commit `d024af099ca4bf2c86f649261ebf59565dc8c622`, core/Std only:

```sh
env -i PATH="$PATH" LANG=C.UTF-8 python3.12 -B \
  research/p112-integral-retraction-instance/source/replay.py \
  --lean /absolute/path/to/installed/lean \
  --output /tmp/p112-replay-new-directory
```

The output directory must be new. No installation or network download is used.
The clean environment avoids inherited Lean settings; the runner sets only its
fresh scratch import path. Its manifest preflight checks all canonical source
members. It enforces 120 seconds per unit and 600 seconds for the successor,
excluding only the unchanged dependency.

The recorded operator run compiled the same exact Lean closure directly in a
fresh scratch tree, with those limits plus an independent 750-second process-group
watchdog. It accepted the dependency in 3.557 seconds and the successor in
47.591 seconds. All 636 reports (159 inherited, 477 new) are present once; the
observed axiom union is `{propext, Quot.sound}`. `Classical.choice` is allowed but
unused. No positive errors, warnings, `sorryAx` or additional axioms were accepted.
The unchanged delivered parser independently agrees by name and axiom set.

The advertised dedicated runner was then tested on the complete packaged source
with a separate 750-second watchdog covering its compiler sessions. It accepted
the same 40 positive units, 636 reports and intended negative control in 53.657
seconds total (50.120 seconds charged to the successor). Both runs used the same
unchanged source and limits. `REPLAY.json` retains the complete named census,
source hashes, timings and the earlier operator-watchdog limitation.

The W control changes only entry `(5,0)` from `+1` to `-1`. Its positive theorems
prove the residual mismatch and absence of a matrix certificate. The separate
fixture exits 1 at `RejectDamagedW.lean:18:2`, where ordinary `decide` rejects
`1 = -1`, and produces no object file. An import, syntax or timeout failure would
not satisfy that control. No resource limit was raised.

## Open next questions

The remaining application boundary is the geometric generator-to-relation
implication: which exact geometric hypotheses produce the 288 individual
monomial relations? A useful first step is to pin one geometric generator list
and state that implication against `P112Cert.M`. Its blocker is the absence of
that geometric theorem in this numerical package.

A separate lawful nonzero-field-element adapter could connect the explicit
commutative-group interface to field notation. Start with one chosen field API
and prove its group laws independently. No such API is included here. Both
questions are recorded in `TASK.json`; neither is a new reservation.

## Credit

Andrey Mas with substantial GPT-6 Pro mathematical/source development and
diagnostic repair through ChatGPT, using the observed model label. Codex handled
source preparation, execution audit, local kernel replay and mechanical packaging;
it made no mathematical repair. PR1497/1610 retain their separate credit.
Inherited lineage includes Brett Halligan / @burntout76 and Ninefold (PR1212),
DreamingOfClouds (PR717), and themilkman216 (PR968). Apache-2.0; see `LICENSE`.

This follows the [scoped P112 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1527#discussioncomment-18915722),
revision 3 `formal-interface-lemma`. Historical preparation provenance remains
at `c24fb5e6537d19d79c62265e4a12781aef9309cb`; the publication base is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The bounded pre-submission overlap check is recorded in `TASK.json`; publication and local replay do not imply maintainer acceptance.
