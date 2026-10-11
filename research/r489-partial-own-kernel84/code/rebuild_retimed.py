"""Rebuild the partial-own factory, frozen kernel selection and frame retiming.
OpenAI Codex. No search runs and no pinned source is modified.
Usage: rebuild_retimed.py COMPLEX_SOURCE VERIFIED_BASE FRAME_MAP OUT_VARIANT

VERIFIED_BASE is a just-completed pinned PR484 variant. Its fresh Hamming
module outputs are inputs to the new constructor. Both the unretimed and
retimed local words are audited and emitted anew; no cached local output is
used. The retimed word receives a fresh pooled owner/spectator controller.
"""
import gzip,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
if not __debug__:raise RuntimeError('assertions must remain enabled')
assert len(sys.argv)==5,__doc__
S,B,M,O=map(lambda x:Path(x).resolve(),sys.argv[1:])
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
SELECTION=ROOT/'data/KERNEL-SELECTION.json';OWNERS=ROOT/'data/COLORED-OWNERS.json.gz'
assert not O.exists() and not O.is_relative_to(ROOT);O.mkdir(parents=True)
C=S/'code';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
steps=[]
def run(name,script,*args,cwd=None):
    log=O/(name+'.log');t=time.monotonic()
    with log.open('w')as f:
        p=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=cwd or O,env=env,stdout=f,stderr=subprocess.STDOUT)
    steps.append(dict(name=name,exit_code=p.returncode,seconds=round(time.monotonic()-t,3),log_sha256=sha(log)))
    (O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
    assert p.returncode==0,(name,log.read_text()[-4000:])
    print('PASS',name,flush=True)

# The enclosing verifier rebuilds the pinned supplier before invoking us.
# Copy only its fresh workspace and bit-price binding. The old local word,
# sc_base and hosted templates are not construction inputs.
shutil.copytree(B/'work',O/'work')
shutil.copy2(B/'BIT-PRICE.json',O/'BIT-PRICE.json')
modules=O/'work/complex-network/hamming'
module_inputs={name:sha(modules/name)for name in ['PROTOTYPE.json','PACKET-PROGRAMS.json.gz']}
run('construct-partial-own',HERE/'construct_partial.py',modules,O/'sc_base')
run('selection-mutations',C/'controls_sel.py',O/'sc_base/FULL-WORD.json.gz',SELECTION,O/'CONTROLS-SELECTION.json')

# Emit a fresh unretimed canonical baseline for the independent frame-only
# comparison. The helper-kernel builder recomputes every dirty-response column.
U=O/'unretimed';U.mkdir();(U/'split-centres').mkdir()
os.symlink(O/'work',U/'work',target_is_directory=True)
run('apply-kernel-selection',C/'gk_word.py',O/'sc_base/FULL-WORD.json.gz',SELECTION,U/'split-centres/FULL-WORD.json.gz')
run('unretimed-scalar-frame',C/'audit_gk.py',cwd=U)
run('unretimed-emit-both-orientations',C/'emit_gk.py',cwd=U)

sc=O/'split-centres';sc.mkdir()
run('apply-frame-map',HERE/'apply_retime.py',U/'split-centres/FULL-WORD.json.gz',M,sc/'FULL-WORD.json.gz')
run('word-mutations',C/'controls_gk.py',sc/'FULL-WORD.json.gz',O/'CONTROLS-WORD.json')
run('pipeline-mutations',C/'controls_pipeline.py',O,SELECTION,O/'CONTROLS-PIPELINE.json')
run('scalar-frame',C/'audit_gk.py')
run('emit-both-orientations',C/'emit_gk.py')
run('exact-gaussian-phases',S.parent/'split-centres-global/code/complex_phases_full.py')
run('residual-adapters',C/'adapters_gk.py',sc/'CANONICAL-WORD.json.gz',sc/'RESIDUAL-ADAPTERS.json',O/'LEMMA-A.json')
run('integrate-global',C/'integrate_gk.py')
run('independent-program-replay',C/'replay_gk.py')

# The original PR484 hosting selection has a different residual-width stock.
# Build the frozen new owner map directly against this fresh global template.
run('pooled-emitter',HERE/'emit_pooled.py',S,O,OWNERS,O/'hosted')
run('independent-pooled-controller',HERE/'audit_pooled.py',O,O/'hosted',O/'HOSTING-AUDIT.json')
run('lemma-G-identities',C/'lemmaG/check.py',O.parent,O.name,O/'lemmaG')
run('retimed-lemma-G-mutants',HERE/'retimed_lemma_mutants.py',S,O.parent,cwd=O/'lemmaG')

artifacts=[O/'sc_base/FULL-WORD.json.gz',U/'split-centres/FULL-WORD.json.gz',
    U/'split-centres/CANONICAL-WORD.json.gz',U/'split-centres/LOCAL-PROGRAMS.json.gz',
    U/'split-centres/LOCAL-CHECKS.json',sc/'FULL-WORD.json.gz',sc/'CANONICAL-WORD.json.gz',
    sc/'LOCAL-PROGRAMS.json.gz',sc/'LOCAL-CHECKS.json',sc/'CLIFFORD-RECIPES.json',
    sc/'RESIDUAL-ADAPTERS.json',sc/'GLOBAL-TEMPLATE.json.gz',sc/'INTEGRATION.json',sc/'INDEPENDENT-REPLAY.json',
    O/'LEMMA-A.json',O/'HOSTING-AUDIT.json',O/'hosted/HOSTED.json',
    O/'hosted/GLOBAL-TEMPLATE.json.gz',O/'hosted/ACTUAL-SIGMAS.json.gz',
    O/'CONTROLS-SELECTION.json',O/'CONTROLS-WORD.json',O/'CONTROLS-PIPELINE.json',
    O/'lemmaG/LEMMA-G-CHECK.json',O/'lemmaG/MUTANTS.json',O/'lemmaG/MUTANT-ADAPTER-RECEIPT.json']
receipt=dict(status='PASS_FRESH_PARTIAL_OWN_KERNEL_RETIMED_COMPLEX_WORD',
    source_full_word_sha256=sha(B/'split-centres/FULL-WORD.json.gz'),
    fresh_hamming_inputs=module_inputs,constructor_sha256=sha(HERE/'construct_partial.py'),
    selection_sha256=sha(SELECTION),constructed_full_word_sha256=sha(O/'sc_base/FULL-WORD.json.gz'),
    unretimed_full_word_sha256=sha(U/'split-centres/FULL-WORD.json.gz'),
    frame_map_sha256=sha(M),retimed_full_word_sha256=sha(sc/'FULL-WORD.json.gz'),
    owner_map_sha256=sha(OWNERS),steps=steps,
    artifacts={str(p.relative_to(O)):sha(p)for p in artifacts},
    scope='Fresh pinned module construction, recomputed kernel relations, both scalar orientations, new canonical/phase/wrapper/integration artifacts, actual pooled owners and controller, and Lemma G identities/controls. Enclosing verification also executes guarded physical arithmetic, independent source/retiming reviews, complete finite invoice and exact outer assembly.')
(O/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],flush=True)
