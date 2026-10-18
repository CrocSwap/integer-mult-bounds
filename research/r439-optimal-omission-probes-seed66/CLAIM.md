# Round 18: optimal finite omission probes

Assigned seed 66, adversarial mathematical audit. Base abdc6a7002abdbcd9e21bfc5e1a795784deacfdf. Selected PR942 and its actual source/review were inspected; its conditional kappa remains unchanged.

Three candidates: owner event boundaries (rejected because PR675 already audits this blind spot), dirty prefix precision (rejected due PR1085 and prior rounds13/16), and the inference from single-omission detection to correlated faults in PR967 D. The last candidate was refined before a main experiment: full-syndrome uniqueness already supplies a direct two-fault obstruction, so a raw pair census would duplicate PR1017.

The frozen final question is the minimum number of fixed nonadaptive binary input assignments whose FULL 661-coordinate output observations detect every one of the 5,563 elementary ADD omissions in PR967 D. Extract all 761 activation covectors, seek two assignments with at most 10,000 local repair sweeps, prove one impossible by an explicit odd XOR dependency, and replay every literal mutant independently. Whole-word errors, multi-fault detection, output-only targets and arbitrary coefficient faults are outside this test model. PR762 supplies a distinct radius-three coefficient test suite; PR1017 supplies the exact omission syndrome predecessor. No new circuit, supplier admission or kappa.
