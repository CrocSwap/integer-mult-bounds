"""Independent static review of the proposed candidate-specific payload cap.

Upstream programs are parsed as inert syntax only, never imported or executed.
This confirms the displayed fixed-recipe interface; unknown primitive constants
stay quantified in C_full. Prepared with substantial OpenAI assistance.
Apache-2.0.
"""
from pathlib import Path
import ast,hashlib,json
import reproduce_pr305 as base

CAP_DIR=base.SOURCE/'cap_sources'

def run(forward=432881,inverse=14083738,new_bits=112):
    base.verify_sources()
    manifest=base.read('MANIFEST.json')['files']
    mapped={};texts={}
    for path in sorted(CAP_DIR.iterdir()):
        data=path.read_bytes();raw=data
        matches=[name for name,sha in manifest.items() if hashlib.sha256(raw).hexdigest()==sha]
        extra=0
        if not matches:
            assert data.endswith(b'\n')
            raw=data[:-1];extra=1
            matches=[name for name,sha in manifest.items() if hashlib.sha256(raw).hexdigest()==sha]
        assert len(matches)==1,('Proof source does not match immutable manifest',path)
        name=matches[0];texts[name]=raw.decode('utf-8')
        mapped[name]=dict(manifest_bound_sha256=hashlib.sha256(raw).hexdigest(),
            supplied_copy_sha256=hashlib.sha256(data).hexdigest(),extra_trailing_newlines_in_copy=extra)
    assert len(mapped)==8
    finite=base.SOURCE/'finite_check.py.txt';raw=finite.read_bytes();tree=ast.parse(raw)
    assert hashlib.sha256(raw).hexdigest()==manifest['finite_check.py']
    parents={child:node for node in ast.walk(tree)for child in ast.iter_child_nodes(node)}
    loads={name:[] for name in ('payload','payloadbits')}
    contexts=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Name) and isinstance(node.ctx,ast.Load) and node.id in loads:
            loads[node.id].append(node.lineno)
            ancestor=node
            while not isinstance(ancestor,(ast.Assign,ast.Assert,ast.Return)):
                ancestor=parents[ancestor]
            contexts.append((node.id,type(ancestor).__name__,ancestor.lineno))
            if isinstance(ancestor,ast.Assign):
                assert len(ancestor.targets)==1 and isinstance(ancestor.targets[0],ast.Name)
                assert ancestor.targets[0].id=='payloadbits'
                assert ast.unparse(ancestor.value)=='payload.bit_length()'
            elif isinstance(ancestor,ast.Assert):
                assert ast.unparse(ancestor.test)=='payload < 2 ** 104'
            else:
                assert isinstance(ancestor,ast.Return)
    assert contexts and len(loads['payload'])==3 and len(loads['payloadbits'])==1
    coefficient=next(node for node in ast.walk(tree)if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='coefficient' for t in node.targets))
    dependencies={n.id for n in ast.walk(coefficient.value)if isinstance(n,ast.Name)}
    assert not dependencies&set(loads)
    accounting=texts['proof/FINITE_BIT_ACCOUNTING.md'];parity=texts['proof/PARITY-CONTRACT.md'];rows=texts['proof/three-stage-cover-rows.tex']
    assert 'primitive constant C may depend on q, the fixed source recipe' in accounting
    assert 'does not depend on n,w' in accounting
    assert 'scalar domain need not equal the label field' in parity
    assert 'payload scalars are binary' in parity
    assert 'total\nlogical-volume increase is below $q^2$' in rows
    assert all('104'not in text for text in texts.values())
    payload=64*forward**3*inverse**2
    if (forward,inverse)==(432881,14083738):
        assert payload==1029725389598377713081823232358656 and payload.bit_length()==110
    assert payload>=2**104 and payload<2**new_bits
    assert new_bits==112
    return dict(status='PASS_INDEPENDENT_EXPLICIT_PAYLOAD_CAP_REVIEW',head=base.HEAD,
        finite_source_sha256=hashlib.sha256(raw).hexdigest(),proof_source_bindings=mapped,
        payload_load_contexts=contexts,payload=payload,payload_bits=payload.bit_length(),
        original_cap_bits=104,original_cap_satisfied=False,
        explicit_candidate_cap_bits=new_bits,explicit_candidate_cap_satisfied=True,
        explicit_candidate_cap_gap=2**new_bits-payload,
        direct_payload_consumers=['bit_length diagnostic','original fixed104 assertion','receipt fields'],
        displayed_formula_payload_dependencies=False,
        conclusion='The fixed104 ceiling is not a consumed threshold in the displayed finite formula. A separately named fixed112 candidate certificate is compatible with the retained binary-payload and fixed-recipe quantifiers, subject to a fresh exact norm bound and every other changed obligation. The original104 check fails and is not relabeled as passing.',
        qualification='Changing the reported numeric ceiling alone adds no scalar operation, recursive child, or displayed coefficient term. Any implementation-dependent finite constant remains inside quantified C_full; this review does not give an exact machine cutoff, replay upstream admission, or discharge all-size hypotheses.')

if __name__=='__main__':
    result=run()
    (base.HERE/'payload-cap-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='proof_source_bindings'},indent=2))
