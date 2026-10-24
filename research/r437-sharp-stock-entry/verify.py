#!/usr/bin/env python3
"""Opt-in source-authenticated root parameter entry for the known NODE stock.

Brian / JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
The stock theorem and ordinal adapter remain the credited predecessors' work.
"""
import argparse
import ast
import copy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import resource
import shutil
import sys
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def digest(data):return sha256(data).hexdigest()


def integer_receipt(value):
    return {'bits':value.bit_length(),'sha256':digest(value.to_bytes(max(1,(value.bit_length()+7)//8),'big'))}


def authenticate():
    data=json.loads((HERE/'SOURCES.json').read_text())
    for row in data['files']:
        if row['usage']=='input':
            path=ROOT/row['path']
            need(path.is_file() and not path.is_symlink() and digest(path.read_bytes())==row['sha256'],'source hash '+row['path'])
    for row in data['retained']:
        need(digest((HERE/row['path']).read_bytes())==row['sha256'],'retained hash '+row['path'])
    return sum(row['usage']=='input' for row in data['files'])


def opt_in(admission):
    """An isolated function copy: replace precisely one source predicate call."""
    from stock import stock_divisor as divisor
    source=Path(admission.__file__).read_text()
    tree=ast.parse(source)
    original=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='checked_entry')
    modified=copy.deepcopy(original)
    calls=[n for n in ast.walk(modified) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
           and isinstance(n.func.value,ast.Name) and n.func.value.id=='numerical' and n.func.attr=='check_stock_rows']
    need(len(calls)==1,'one exact stock predicate call')
    call=calls[0]
    expected=ast.parse('numerical.check_stock_rows(domain.rows, domain.n, cat.q, domain.w)',mode='eval').body
    need(ast.dump(call)==ast.dump(expected),'exact original stock arguments')
    call.func=ast.copy_location(ast.Name(id='check_guard_stock_rows',ctx=ast.Load()),call.func)
    restored=copy.deepcopy(modified)
    restored_calls=[n for n in ast.walk(restored) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check_guard_stock_rows']
    need(len(restored_calls)==1,'one isolated replacement')
    restored_calls[0].func=expected.func
    need(ast.dump(restored)==ast.dump(original),'all non-stock source AST unchanged')
    # The unchanged source still validates the numerical domain before callback().
    callbacks=[n for n in ast.walk(original) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='callback']
    need(len(callbacks)==1 and not callbacks[0].args and not callbacks[0].keywords,'one zero-argument continuation')
    def check_guard_stock_rows(rows,n,q,w):
        need(isinstance(rows,int) and rows>0,'positive row stock')
        quotient,remainder=divmod(rows,divisor(n,q,w))
        need(quotient>0 and remainder==0,'compatible one-factor NODE stock divisor')
        return quotient
    namespace=dict(vars(admission),check_guard_stock_rows=check_guard_stock_rows)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[modified],type_ignores=[])),str(admission.__file__),'exec'),namespace)
    return namespace['checked_entry'],{'source_function_ast_sha256':digest(ast.dump(original).encode()),
        'adapted_function_ast_sha256':digest(ast.dump(modified).encode()),'replaced_calls':1,
        'non_stock_ast_identical':True,'separate_function_object':namespace['checked_entry'] is not admission.checked_entry}


def run():
    inputs=authenticate()
    sys.path.insert(0,str(HERE/'retained'))
    from stock import stock_divisor,row_factor,Node,certify_path
    from ordinal import install_ordinal_counts
    sys.path.insert(0,str(ROOT/'research/selected-bit-physical-caller'))
    import loader
    with TemporaryDirectory(prefix='r437-root-stock-source-') as directory:
        projection=Path(directory)
        for row in json.loads((loader.CALLER/'SOURCES.json').read_text())['files']:
            if row['usage']!='input':continue
            target=projection/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            source=HERE/'retained/selected-result.json' if row['path']=='certificates/selected-result.json' else ROOT/row['path']
            shutil.copyfile(source,target)
        loader.REPOSITORY=projection
        loader.compatibility_controls()
        sys.path.insert(0,str(ROOT/'research/r437-carrier-integration'))
        import admission,compiler,numerical
        cat,top=admission.load_certified('D')
        import macro_binding
        need(macro_binding.SelectedBinding.stock_multiple==9475,'actual fixed NODE stock guard')
        binding_tree=ast.parse(Path(macro_binding.__file__).read_text())
        binding_class=next(x for x in binding_tree.body if isinstance(x,ast.ClassDef) and x.name=='SelectedBinding')
        residual_stock=next(x for x in binding_class.body if isinstance(x,ast.FunctionDef) and x.name=='check_stock')
        need(len(residual_stock.body)==1 and isinstance(residual_stock.body[0],ast.Pass),'no extra selected residual stock predicate')
        admission.authenticate_certified(cat)
        install_ordinal_counts(cat.codes)
        import oracle
        from catalogue import Specifications
        source=compiler.early_source87(cat,top,0,0)
        preparation=oracle.reduce_rational(cat.template_for(source['identifier'],True).preparation,cat.q)
        low=tuple(map(tuple,oracle.inverse(preparation,cat.q)))
        need(oracle.multiply(low,preparation,cat.q)==oracle.eye(64),'actual common inverse chart')
        specs=Specifications(cat)
        handle=compiler.source_handle(cat,source['identifier'],True,low)
        spec=compiler.resolve_handle(cat,specs,handle)
        need(spec.good and spec.template.rank==2 and cat.q==2**127-1,'actual certified fresh common source')
        decoded=cat.codes.decode(handle.code)
        need(decoded==(source['identifier'],True,low),'adapted common source roundtrip')
        q,w,n=cat.q,2,128
        need(numerical.depth(n)==2 and top.families==28416,'depth-two separating source context')
        A=row_factor(q,w);sharp=stock_divisor(n,q,w);old=numerical.stock_unit(q,w)**numerical.depth(n)
        need(sharp==9475*A*A and old==9475*sharp,'credited one-factor separating divisors')
        domain=admission.RootDomain(n,n,w,0,(q**w).bit_length()+1,n.bit_length()+1,cat.codes.bits,sharp)
        entry,adapter=opt_in(admission)
        original=admission.checked_entry
        controls=[];hits=[]
        def invoke(fn=entry,d=domain,h=handle,table=specs,expected_key=handle.request_key,common=True):
            def continuation():hits.append((h.code,d.rows));return 'ROOT_PARAMETER_CONTINUATION'
            return fn(cat,table,h,d,continuation,mode='numerical',expected_key=expected_key,expected_common=common)
        def reject(name,operation):
            before=len(hits)
            try:operation()
            except ValueError as error:
                need(len(hits)==before,'reject before continuation '+name)
                controls.append({'name':name,'error':str(error),'continuation_called':False})
            else:raise ValueError('negative control accepted '+name)
        reject('unchanged_entry_rejects_sharp_stock',lambda:invoke(fn=original))
        returned,receipt=invoke()
        need(returned=='ROOT_PARAMETER_CONTINUATION' and len(hits)==1,'one accepted continuation')
        need(receipt['numerical_admitted'] is True and receipt['production_payload_execution'] is False,'parameter versus payload admission')
        need(receipt['row_multiplier']==admission.integer_receipt(1),'minimal one-factor stock multiplier')
        old_return,old_receipt=invoke(fn=original,d=replace(domain,rows=old))
        new_return,new_receipt=invoke(d=replace(domain,rows=old))
        need(old_return==new_return and len(hits)==3,'old accepted domain preserved')
        allowed_difference={'row_multiplier'}
        need({k:v for k,v in old_receipt.items() if k not in allowed_difference}==
             {k:v for k,v in new_receipt.items() if k not in allowed_difference},'old-domain receipts differ only by divisor multiplier')
        for name,d in [
            ('missing_9475',replace(domain,rows=A*A)),
            ('missing_depth_factor',replace(domain,rows=9475*A)),
            ('incompatible_rows',replace(domain,rows=sharp+1)),
            ('zero_rows',replace(domain,rows=0)),
            ('reset_root_precision',replace(domain,w=1,L=q.bit_length()+1)),
            ('descendant_not_original_root',replace(domain,n=64)),
            ('nonzero_root_history',replace(domain,h=1)),
            ('wrong_residue_width',replace(domain,L=domain.L+1)),
            ('wrong_root_index_width',replace(domain,I=domain.I-1)),
            ('wrong_code_width',replace(domain,Q=domain.Q-1)),
        ]:reject(name,lambda d=d:invoke(d=d))
        reject('wrong_handle_identity',lambda:invoke(h=replace(handle,identity='0'*64)))
        reject('wrong_expected_request',lambda:invoke(expected_key=('MOVE',0,0,0)))
        reject('wrong_expected_view',lambda:invoke(common=False))
        reject('foreign_specifications_context',lambda:invoke(table=Specifications(copy.copy(cat))))
        provenance=copy.deepcopy(cat.admission_provenance)
        cat.admission_provenance=dict(provenance,base_compiler_identity='0'*64)
        try:reject('forged_prime_constructor_provenance',lambda:invoke())
        finally:cat.admission_provenance=provenance
        need(admission.checked_entry is original,'default entry object unchanged')
        _,final_receipt=invoke()
        need(final_receipt==receipt and len(hits)==4,'positive repeat after rejected mutations')
        # All-path proof is inherited; this is a source-bound independent rank-ceiling path example.
        path=certify_path(Node(n,sharp,q,w),[Node(n,sharp,q,w),Node(84,sharp//A,q,w),Node(42,sharp//A**2,q,w)])
        return {'status':'PASS_R437_SHARP_STOCK_ENTRY','live_input_count':inputs,
            'source':{'request':source['identifier'],'request_key':list(handle.request_key),'identity':cat.source_identity,
                'rank':spec.template.rank,'common':True,'code':integer_receipt(handle.code),'ordinal_adapter':'PR4734 exact function'},
            'domain':receipt['domain'],'q':str(q),'root_parameter_checks_passed':True,
            'scope':'Opt-in authenticated original-root parameter entry for inherited NODE guard contract; no complete payload, encoded admission tariff or supplier admission.',
            'stock':{'sharp':integer_receipt(sharp),'conservative':integer_receipt(old),'exact_ratio':9475,'sharp_multiplier':1,
                'old_domain_new_multiplier':9475,'abstract_max_rank_path':path,'path_is_actual_program':False},
            'entry_adapter':adapter,'residual_stock_ast_sha256':digest(ast.dump(residual_stock).encode()),'accepted_continuations':len(hits),'controls':controls,
            'production_payload_execution':False,'frozen_default_entry_unchanged':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed deterministic receipt')
    print(result['status'])
    print('peak_rss_bytes',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024),file=sys.stderr)


if __name__=='__main__':main()
