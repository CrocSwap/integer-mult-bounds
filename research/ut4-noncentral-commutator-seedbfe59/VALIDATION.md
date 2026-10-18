# Validation record

- Environment: CPython 3.14.7, standard library only.
- The exact q<=4 search and certificate generation completed:

~~~sh
python3 -I -B research/ut4-noncentral-commutator-seedbfe59/search.py --write-certificate
~~~

- The direct verifier passed with 360 factors, 129,600 ordered pair words,
  87,016 distinct pair products, all 360 q3 checks, and all 129,600 q4 checks:

~~~sh
python3 -I -B research/ut4-noncentral-commutator-seedbfe59/verify.py
~~~

This verifier also reruns the selected baseline positive control and compares
its complete JSON output to BASELINE.json.

- Package metadata and exact base/source pins passed:

~~~sh
python3 scripts/research_package.py --package research/ut4-noncentral-commutator-seedbfe59 --check-only
~~~

- The selected bit-task baseline positive control returned
  PASS_RESEARCH_BASELINE_BINDINGS_ONLY. Its exact output is preserved in
  BASELINE.json; it confirms source bindings and arithmetic only.
- The exact group table was cross-checked in the verifier for all 4,096
  ordered group-element pairs; both noncentrality witnesses and both
  corruption controls passed.

This metadata command does not validate the mathematical result. The package
replay manifest specifies Python 3.12, as required by the repository replay
system. Python 3.12 is not installed here, so the registered Python 3.12
replay was not run locally. The direct standard-library verifier passed under
Python 3.14.7.

The run changes no selected result, upstream source, existing certificate, or
repository-wide research allocation. Hosted Python 3.12 replay and maintainer
review remain separate.
