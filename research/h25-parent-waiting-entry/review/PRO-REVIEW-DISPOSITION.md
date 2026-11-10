# Bounded source review disposition

ChatGPT Pro, verified mode 5 of 5, reviewed initial commit c99f97f652d39c2eedd1bffa3fb3aabaa29d3b93 in the existing consultation. Its completed answer identified first-error custody loss when DeadlineOwner.pop raises during query/root unwind. The working-body exception had not yet reached the enclosing capture.

The corrected source records the raw primary before timer unwind. pop_deadline_preserving records a pop failure after it and rethrows that failure only when no earlier primary exists. controls-v8 executes the actual production inner try/except/finally nodes for both run_property_query and run_root, replacing only the working body by an injected original error. Actual DeadlineOwner.pop expires with inert clock/signal ports. Both cases retain and raise the identical original OSError, followed by the ExecutionDeadline secondary. This test passed locally; it is not a native caller or independent source qualification.

Pro found no premature-release counterexample in the spans it inspected and no envelope exit 125 as original refusal exit 1 acceptance. It supported the intended query ownership separation but explicitly did not give a complete birth/race/retirement proof. It did not complete relay, all loader/bootstrap authentication, external-dependency or whole-assembly review. The correction itself was locally assessed and tested after that answer; it was not sent for a second Pro review.

The original full caller, actual source assembly, environment, funding and execution gates remain open. The scope is a reviewable source archive and bounded controls, with no scientific or original-activity credit.
