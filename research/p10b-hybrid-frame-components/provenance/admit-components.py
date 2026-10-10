"""Bind the search selection to unchanged W3 admission/replay driver.

The common helper-endpoint guard extension preserves every existing endpoint;
all original per-gate, source-span, nesting and reflected-ledger checks remain.
"""
import sys,pathlib,json,hashlib,subprocess,os
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parent
W3=pathlib.Path('/private/tmp/p10b-hybrid023-w3-fresh-20261010')
INPUT=W3/'joint-final/final/data.pkl'
SEARCH=pathlib.Path(sys.argv[1]).resolve();LABEL=sys.argv[2]
SELECTION=ROOT/(LABEL+'-selection.json');OUT=ROOT/(LABEL+'-admission')
assert not SELECTION.exists() and not OUT.exists()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONPATH='/private/tmp/pr327-pinned-runtime')
py=['/private/tmp/five-stage-verify-venv/bin/python','-B']
subprocess.run(py+['/private/tmp/p10-crossgroup-t300-v3/vendor/pr320/discovery/descent2_freeze.py',str(INPUT),str(SEARCH),str(SELECTION)],env=env,check=True)
selection=json.loads(SELECTION.read_text())
selection['status']='FROZEN_PR340_INSPIRED_UPHILL_HYBRID_FRAME_SELECTION'
selection['provenance']='Independent exact-paid-histogram uphill/neutral annealing with connected-component improvement harvesting, seeded by the separately admitted456-gate transport of PR340 onto the six-direct/four-cache hybrid. PR340 upstream method and frozen490-gate selection: Rohan Arun with Anthropic Claude assistance, pinned head695e703731491f81aa22d51b2def850afd7519c0 and selection Git blob f635f0b0304fab807e5a5449f863c663d4c88cb0. Independent implementation and adaptation by OpenAI Codex. Candidate spaces include operand-chain frames, upstream registered frame bases and bounded depth-two neighbour meet/join closure. Full exact integer source spans, joint nested chains, nondegeneracy, COPY constraints and every endpoint are checked. Relative to the current incumbent, changed-gate components with disjoint edges and unchanged boundary frames may be retained independently when their actual edge-histogram phi improves; the final full histogram and complete chains are rechecked. All changes bind to current raw predecessor a9965c931289d5afcab3c128b349cc2510369ad1bfce246a4c86b3858bb615f6. No global search completeness claim. Inherited PR287/PR291/PR270 and Apache-2.0 credits retained.'
selection['search_bindings']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [INPUT,SEARCH,ROOT/'search-components.py',ROOT/'transfer-combined-selection.json',ROOT/'transfer-combined-mapping.json',ROOT/'transfer-combined-pruning.json',ROOT/'pr340-695e-selection.json',W3/'joint-constructed-selection.json']}
SELECTION.write_text(json.dumps(selection,indent=1)+'\n')
with (ROOT/(LABEL+'-admission.log')).open('w') as log:
    subprocess.run(py+[str(W3/'admit-constructed.py'),str(W3/'joint-final'),str(OUT),str(SELECTION)],env=env,check=True,stdout=log,stderr=subprocess.STDOUT)
print('PASS_ACTUAL_ADMISSION_PROCESS_EXIT_ZERO',json.dumps(json.loads((OUT/'ADMISSION.json').read_text())),flush=True)
