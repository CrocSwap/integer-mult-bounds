The unchanged PR967 bit word has a tighter signed reverse-prefix estimate: **B=10,394,084 -> 4,525,748**, with F=72,847 unchanged. Exact cancellation is used only inside its common-frame D block; the earlier C/B/scatter/A prefix keeps the existing conservative envelope and peaks at 49,347.

Sparse coefficient propagation and 661 separate one-hot scalar executions agree on **all 5,563 inverse-D prefix bounds**. A backward output-functional check recovers the maximizing row, and a literal signed box-corner replay attains it. Tightness is for the independent entry-box model; physical attainability from earlier unit-bounded inputs is not claimed. The source check binds actual negative inverse ADD emission after the punctured adapter, not just the positive invoice formula.

Exact substitution changes the local expression's strict bit count 102->99 and the nine-stage expression 192->188. **The production allowance remains 192 bits**, and the word's 11,783 ADDs and paid profile are unchanged. No new kappa or native/provider admission is claimed. Inherited syntactic H2 and K_equals_D remain false; the separate semantic D endpoint passes.

Reproduce with Python 3.10+ from the repository root:

```sh
python3 -I -B research/r439-inverse-d-envelope-seed00/verify.py
python3 -I -O -B research/r439-inverse-d-envelope-seed00/verify.py
```

Both modes check the full certificate, six mandatory source pins, every prefix, all 661 input columns, unchanged owning geometry and 10 rejection controls. Native hosted checks, full provider invoices and outer assembly were not run.

Credit Sricharan Vagvala PR967, Gareth Davidson PR915/926, DreamingOfClouds PR589, eumemic PR555/543 and PR496, the signed-lowering lineage, and related complex norm/cancellation work PR395/396/398/821/975. PR1040/1047 retunes are not imported or composed. Full credit and limitations are in README/NOTICE. Prepared for **@woklerx** with substantial **OpenAI Codex assistance**. Apache-2.0.
