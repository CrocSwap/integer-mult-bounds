# Scope erratum: formal reverse rows in the PR5392 physical audit

This append-only erratum corrects the interpretation of the eight reverse-cut rows in the frozen independent physical audit of PR5392, exact head `329b2ff35d2994b11abbb59f770d12da75c494ac`. It is a prose and evidence-scope correction. No mathematical engine was rerun or changed, and no original report, receipt or inventory was modified.

The original joint `PHYSICAL-RECEIPT.json` has SHA256 `d5a561a8d7aab680f469e7929622d882bcd1a05179feb584a588cba80577ea4b`. Its field `coverage.actual_nonzero_reverse_bridge_rows: 8` is misnamed: the measured count is **eight nonzero formal free-group rows**. It does not certify eight nonzero rows after the physical specialization. The counts remain unchanged and carry this narrower interpretation.

The extra checker starts arbitrary entry columns and propagates exact rational free-group words. At each ghost cut, it records whether the formal row dictionary is empty, its number of formal terms and one first nonzero term. It does not record or verify that the chosen entry's entire coefficient is a singleton nonzero `qU`. Multiple free words for the same entry can become related after substitution by the actual native operators. A nonzero formal row alone therefore supplies neither physical nonzeroness nor physical surjectivity.

The same limitation applies to the original `CONTROL-RECEIPT.json` key `reverse_zero_assumption_falsified_at`, each contained `reverse_input_zero: false`, the joint receipt's `negative_controls.reverse_zero_false_premise` text, and report/handoff sentences calling these rows “actual” or saying that their first terms falsify a physical reverse-zero premise. Read these as statements about the formal replay only. The recorded formal roles and term counts remain L224:98, L288:11, L57:96, L81:98, L240:101, L11:100, L9:101 and L92:95. There is no claim here that any of those physical rows is zero either; physical nonzeroness was not established by this control packet.

The corrected public statement is:

> At all eight ghost cuts, the independent replay has a nonzero formal free-group row. This establishes no nonzero-row or surjectivity claim after physical specialization. The endpoint proof requires no reverse-zero premise: every bridge-dependent term cancels at return for arbitrary operator substitutions.

The main endpoint proof is unchanged. A formal identity remains an identity under every permitted operator substitution. Its complete returned-row calculation cancels all bridge-dependent terms for all 641 entry columns, including the 17 arbitrary owned columns. That positive universal cancellation does not require the reverse rows to be zero or nonzero. The physical transpose of each source identity is still identity. The separate independent actual paid/native phase and caller-interface checks are unaffected.

Consequently this erratum does not weaken an existing endpoint gate or introduce a new physical premise. It removes an unsupported interpretation of one diagnostic. The same five selected assumptions and all previously stated independent-versus-inherited coverage boundaries remain. The historical receipts and code are preserved so that the precise measured evidence remains reviewable.

The companion `SCOPE-ERRATUM-RECEIPT.json` binds the original joint receipt, extra checker, imported independent word checker, control receipt, guard receipt, report, handoff and original inventory. Both erratum files are now frozen. Substantial OpenAI Codex assistance was used in the original audit and this clarification.
