# Pro source-only binding excerpts

Physical source: /home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028/integration-drafts/native-fields-v1/controls/run_controls_v1.py
Bytes: 6394
SHA-256: 519813f0aca56dfd083449940446e8e719b37b70a3ba195d0eab7d7ae6437bcc

Pre-existing source pin: field-parent-orchestration-v2/TEMPLATE-MODULES.json $.modules.run_controls_v1. The full metadata SHA-256 is 589d883e853270d92679f58f52e4d9f0070bd6039f551a8f5f98fd455a29da28, sealed by SOURCE-MANIFEST.json $.entries[20]. Full copies are frozen under binding/metadata. V3/V4 template and input-pin corroboration is in RUN-CONTROLS-BINDING-v1.json. Admissions remain null; inherited successor pins are not independent semantic approval.

Original constants:

```python
11: SCHEMA = 'h25-indexed-field-additive-controls-v1'
12: STATUS = 'SOURCE_CONTROL_OBSERVATIONS_COMPLETE_RUNTIME_GATE_OPEN'
13: NORMAL_NONMODEL_COUNT = 169
14: OPTIMIZED_NONMODEL_COUNT = 169
15: NORMAL_MODEL_COUNT = 33
16: OPTIMIZED_MODEL_COUNT = 33
17: MAX_CONTEXTS = 41  # native15 + transport14 + collector12; module cap64
18: GROUPS = ('native', 'transport', 'collector', 'elf', 'providers')
19: MODULES = (native, transport, collector, elf, providers)
```

Exact original validator:

```python
81: def validate_all(receipt, mode):
82:     need(type(receipt) is dict and set(receipt) == {'schema', 'status', 'mode',
83:       'nonmodel_observed_count', 'model_observed_count', 'native_fixture_contexts', 'groups',
84:       'root_model', 'kernel_capability_qualified', 'full_finite_union_qualified', 'required_guarded_cases_status'},
85:       'aggregate exact receipt keys')
86:     need(receipt['schema'] == SCHEMA and receipt['status'] == STATUS and receipt['mode'] == mode,
87:          'aggregate status/mode')
88:     need(receipt['kernel_capability_qualified'] is False and receipt['full_finite_union_qualified'] is False and
89:          receipt['required_guarded_cases_status'] == 'REQUIRED_NOT_EXECUTED_BY_THIS_ENTRY',
90:          'source controls cannot substitute for guarded runtime qualification')
91:     need(type(receipt['groups']) is dict and tuple(receipt['groups']) == GROUPS, 'aggregate exact group order')
92:     for name, module in zip(GROUPS, MODULES):
93:         literal = module.NORMAL_CASE_COUNT if mode == 'normal' else module.OPTIMIZED_CASE_COUNT
94:         validate(receipt['groups'][name], module.CASE_IDS, literal, module.expectations(), mode)
95:     models.validate_model_receipt(receipt['root_model'], mode)
96:     nonmodel = NORMAL_NONMODEL_COUNT if mode == 'normal' else OPTIMIZED_NONMODEL_COUNT
97:     model = NORMAL_MODEL_COUNT if mode == 'normal' else OPTIMIZED_MODEL_COUNT
98:     need(type(receipt['nonmodel_observed_count']) is int and receipt['nonmodel_observed_count'] == nonmodel and
99:          type(receipt['model_observed_count']) is int and receipt['model_observed_count'] == model and
100:          receipt['root_model']['observations']['case_count'] == model,
101:          'aggregate literal counts')
102:     need(type(receipt['native_fixture_contexts']) is int and receipt['native_fixture_contexts'] == MAX_CONTEXTS,
103:          'aggregate actual context count')
104:     return receipt
```

Consumer: /home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028/areas/field-negative-child-runtime-v2/negative_observation_v2.py
Bytes: 19353
SHA-256: 8289c2c4059dd31959cafed81df3211ca6c72584a9d018d86cc91d4fd0cd2a30

```python
13: import run_controls_v1 as controls
263:             schema.need(end[6] == 'FULL202_OBSERVED','negative full202 completion phase')
264:             result = _one(rows,'full202-original-return')
265:             controls.validate_all(result,launch['mode'])
266:             schema.need(codec.equal(_one(rows,'full202-actual-fixtures'),(41,41)),'negative complete actual fixture census')
```

The literal GROUPS minus ERRORS and successful mutation groups02/03/04 leaves07 as the structural full202 branch. The unchanged57-module caller requires this logical key at RUNTIME_MODULES (assignment line47, key line50), exact receivers at243 and negative owner inclusion at430-431. This is not an unused string requirement. Runtime/original activity credit remains0.
