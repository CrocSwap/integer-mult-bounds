# Public theorem guide

All names below are under `MultitapeToolkit`. Import the aggregator
`MultitapeToolkit` or the narrow module matching your construction.

| Need | Interface | Evidence required from the caller |
|---|---|---|
| Literal locality | `Locality.step_locality` | One actual successful physical step |
| Fixed finite decision table | `Locality.decisionTable_lookup`, `Locality.decisionTable_card_le` | A fixed finite machine |
| Exact relative/absolute transfer | `Absolute.runs_simulation`, `Absolute.halts_iff` | Actual relative run or halt |
| Concatenate machines | `compose_runs`, `compose_computesWithin` | Actual first run/halt and second run on exactly the returned tapes |
| Protect far cells | `Absolute.Trace.runs_reach_and_frame` | Actual run and distance from its initial heads |
| Preserve a whole parked tape | `Absolute.Trace.IdleOn`, `Absolute.Trace.runs_idle_tape` | A checked predicate on the literal transition table |
| Replay with arbitrary outside dirt | `Absolute.FrameRule.runs_finite_frame_simulation` | An actual run; the theorem constructs its finite footprint |
| Preserve completed runtime and halt | `Absolute.FrameRule.completed_runs_finite_frame` | Actual run and actual terminal halt |
| Compose footprints | `Absolute.FrameRule.FootprintedRuns.compose`, `Absolute.FrameRule.charged_handoff_frame` | Actual runs for every middle/handoff stage, not just endpoint equalities |
| Compile homogeneous source macros | `TM2Compiler.compile_run`, `TM2Compiler.encode_halts`, `TM2Compiler.read_output` | Fixed finite program and exact source run |
| Compile dependent alphabets | `TM2HeterogeneousCompiler.compile_run`, `decode_output` | Fixed finite heterogeneous program and exact source run |
| Keep typed-stack invariants | `TM2HeterogeneousCompiler.WellTagged` and flattening lemmas | The actual mapped configuration; inspect the module for exact binders |
| Compile completed time contracts | `Transport.compiled_computesInTime`, `Transport.compiled_computesInTime_depth` | Actual source executions, halt, output, and optional fixed depth bound |
| Transfer arbitrary asymptotic targets | `Transport.fixed_overhead_isBigO`, `Transport.compiled_and_adapter_isBigO` | Pointwise physical cost bound and established source/adapter Big-O |
| Compile a fixed stage sequence | `Absolute.Subroutines.scheduler_assembly` | Literal runs, halts, and tape/head boundary equalities for all stages |
| Invoice stage volumes | `Absolute.Subroutines.scheduler_affine_volume_bound` | Charged time bound for each supplied stage volume |
| Use the full sufficient compiler/frame result | `VerifiedPipeline.compile_completed_frame` | One fixed source program, depth bound, exact completed source execution |
| Start from a concrete program | `Examples.literal_copy_correct`, `Examples.completed_copy_frame` | Arbitrary initial tape functions and heads; no algorithm premise |

## Routine recipe

For a source TM2 subroutine, prove the source `step` iterate, its `l = none`
terminal condition, and the exact returned lists. Supply the finite type
instances and fixed depth bound, then use `compile_completed_frame`. It gives
the actual absolute-coordinate run and a finite observed set. The output is
the realization of `encode M d`, so `decode_output` recovers each source stack.

For native tape routines, prove `Runs` directly and use `completed_runs_finite_frame`.
The returned `MatchesOn` condition requires equal initial control and head
positions as well as observed symbols. It deliberately permits every other
cell to differ, including arbitrarily long pre-existing parked payloads.

For sequential callers, prove physical entry/exit agreement before invoking
the scheduler. A run of one component ending at the next component's desired
mathematical value is insufficient unless the actual tape bank and heads also
meet that boundary. Every handoff is charged explicitly.

## Uniformity checklist

- Fix tape types, alphabets, control, program, and entry states before varying
  operand lengths or values.
- Bound syntactic statement depth or retain its explicit overhead in the cost.
- A tape can be write-idle while its scanned symbols still influence control.
  Use the observation footprint when runtime independence is needed.
- Include terminal scanned positions when transferring a halt condition.
- Count physical parsing, padding, reversal, relocation, and trimming adapters
  before changing input/output conventions.
- Treat the finite reference fixtures as implementation controls, and the
  complete `replay.py` run as the kernel/axiom evidence.


## Concrete reusable construction extension

| Need | Interface | Actual conclusion |
|---|---|---|
| Tag distinct finite controls | `Absolute.ControlEmbedding.lift_runs`, `lift_halts` | Same physical execution and cost |
| Marked-stream local representation | `Absolute.MarkedStreams.cellView`, `Physical`, `bank2_step` | Literal write/unit-move semantics, arbitrary past |
| Transfer and real child | `Absolute.MarkedStreams.move_runs`, `flip_runs` | Exact2n+2 transitions and head-restored output |
| Push/pop | `Absolute.ParkStack.push_correct`, `pop_correct` | Exact2n+2 /3n+5 and full literal banks |
| Initialize/remove markers | `Absolute.MarkerLifecycle.marker_run`, `install_remove_cells` | Real two-step operations; full-cell restoration under blank marker sites |
| Reusable caller | `Absolute.ParkingController.wrapper_correct` | Actual changing-length child gives cost2|x|+2|z|+5|y|+16+t and true halt |
| Closed finite controller | `Absolute.ParkingController.boundary_machine_correct` | Real bit-flip child, every length, exact6|x|+5|y|+18, full endpoint |
| Copy/flip observed regions | `Absolute.MarkedStreams.move_footprints`, `flip_footprints` | Actual bounded FootprintedRuns and spectator footprints |
| Parking observed regions | `Absolute.ParkFootprints.pop_completed_footprint`, `push_completed_footprint` | Actual finite footprints, marker floors, old-prefix preservation |
| Canonical output | `OutputNormalization.compiled_normalize`, `compiled_output`, `compiled_fixedWidth` | Actual compiled source empty/output and physical bound10(input.length+1) |

Names are taken from actual defining modules; inspect exact binders before use.
The controller assumes marked word banks; the output converter assumes the
compiler's stack representation and a real MSB-first input list. Neither hides
a buffer placement or reversal cost.
