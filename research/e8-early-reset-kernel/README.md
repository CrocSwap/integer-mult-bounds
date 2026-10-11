# Early reset and response-kernel composition

Conditional kappa = 0.001133100552284434, above PR436's 0.001128983115440183. Eleven earlier resets give R747. After remapping the PR435/417 kernel selection and rejecting changed/invalid response relations, 110 entries survive with entrance rank 128 and 97 donor slots. There are 731 width-64 helper banks per stage, 14,259 live and 14,268 physical families.

Run `python -B research/e8-early-reset-kernel/verify.py /absolute/new/output` using the Python standard library. The wrapper freshly replays the full earlier-reset package and its parent phases, then applies and checks the kernel composition.

At draft update, exact changed scalar/frames/source-span checks, global banks, independent audit, two moments and full finite assembly passed. Both Python versions passed the earlier-reset parent wrapper. The new combined wrapper and GitHub CI remain pending. These are conditional bounds, retaining every stated all-size interface.

The full uninterrupted wrapper now passes locally on Python 3.11 and Python 3.14 against 98b2d164fe0d51253faa05b8fb14cd82e57ef841. Both regenerate every parent phase and every changed program; receipts are in local-evidence/FULL-PYTHON*.json. GitHub CI remains pending.
