# Discovery metadata portability repair

PR460 reported that Python 3.11 reconstruction rejected a 2.09e-12 difference in an inherited floating-point gain estimate. Both a local control adding 2.1e-12 and the naturally regenerated Python 3.11 parent output reproduced the old failure. The latter differs by -2.0889956431346945e-12 in gain_percent_float. The exact kernel, frames, operator, prices and source pins were unchanged.

The rebuild now requires the two discovery estimates to be finite floats and normalizes them before exact whole-word comparison. Every other field still compares exactly. Eight controls accept the baseline and the two separate small perturbations with identical exact output, and reject NaN, infinity, an altered gate, an altered register count and an unknown report field. They pass under Python 3.11.15 and 3.14.8.

A fresh full Python 3.11.15 replay, including all inherited controls and regenerated exact phases, passed. Its entire RESULT.json is byte-identical to the original Python 3.14.8 result. The new receipt binds the updated manifest; the original validation directory remains historical evidence for head 66f35b7. This directory does not claim a new Linux full replay or completed GitHub CI.

Credit: Rohan Arun with OpenAI Codex reported and isolated the downstream portability failure in PR460. Chafreaky with OpenAI Codex implemented and checked this upstream repair. Apache-2.0.
