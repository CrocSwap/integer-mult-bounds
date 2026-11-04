# Independent review of Task A: multi-host framework

Reviewed 2026-10-11 by a separate Codex agent. The reviewer did not write the
new framework or singleton recovery. No external publication occurred.

**Verdict:** the abstract multi-host extension and exact singleton recovery are
sound. A fresh independent Lean4.33.0 build of both new modules and their three
dependencies passed. `framework-independent-build.json` contains source hashes
and compiler output. This completes the abstract compatibility review only;
no actual source invocation or physical-provider contract is discharged here.

`MultiHosting.WindowState` retains a function from physical-host indices to
whole streams together with all remaining retained state R. The H index is
explicitly a distinct physical stream, including its cover owner when needed,
and must not silently identify all streams with the same source-family label.
The common coefficient/address/payload types do not force all streams to have
the same actual physical chart, but a fixed chart for each stream throughout
the window must be established by source refinement.

Each event has a coordinate-mask action on every host and the same `other`
function on R. The pointwise commuting proof correctly permits multiple hosts
to change in one complete invocation and requires disjoint residual masks and
pending containment separately for every host. The theorem does not discard
any host or any part of R. Arbitrary input correlations are allowed because the
identity holds on every state, and no independence of input values is assumed.

The physical adapter permits distinct auxiliary layouts and quantifies over
every original/relocated bank input. It threads actual bank outputs through
successive calls. It compares only retained outputs. Its documentation correctly
requires any component whose equality/restoration matters to stay retained;
auxiliary outputs need a separate continuation scope/restoration argument.

`SingleHostRecovery.embed` and `collapse` are inverse on all retained state.
The recovered old operator statement genuinely follows by applying the new
`multi_hosting` theorem and collapsing the singleton-host state. The old
physical theorem is recovered using the old adapter's projection lemmas plus
that new derivation, not by invoking the old whole-hosting theorem. Thus this
is an exact conservative extension, not merely an analogous statement.

No logical defect, dropped-state shortcut, initialization assumption, or new
axiom was found. The supplied complete endpoint contracts remain genuine
premises. In particular, an active-pair operation that reads/mixes a selected
host cannot be hidden inside `other : R → R`. For a shared window, every
selected host must have the stipulated independent coordinate action at every
complete event. Wider source schedules may require separate windows or a more
general commutation interface.

Task B remains separate: instantiate concrete distinct owner streams, actual
coordinate/frame transformations, all scratch conventions, and the universal
arbitrary-dirt endpoint of the emitted source word. The new abstract theorem
alone does not count as that source proof.

Reviewed hashes:

- MultiHosting.lean: `dc6188687ac8e089c64bf5ab7cd4c8c1a83f378d3c46bb1265a1b6ad43d199d6`
- SingleHostRecovery.lean: `24590ece7ec72ad5edcdefc9d7f45acffa6dbccd644c95104ab8f2685fbaaf5d`

Two checked negative controls in `MultiHostControls.lean` target source refinement:

- `mixing_does_not_commute` retains both hosts but applies an actual XOR between them; moving a residual past that mix changes the result.
- `alias_breaks_refinement` maps two nominal hosts onto one physical stream; the abstract one-residual-per-host action disagrees with the two sequential physical actions.

Both statements compiled in the independent build and use no axioms. Each is
a proved inequality, so replacing `≠` by `=` produces a false statement that
can be rejected by the corresponding theorem. They are small boundary models,
not claims about the actual source owner map. The source address coordinates
are Bool only for these abstract controls; no prime-admission claim is made.

MultiHostControls.lean SHA256: `4321a232d7e36e0f4417a01ce951c601afde1b283c42c0b8ad24372e25fbc94d`
