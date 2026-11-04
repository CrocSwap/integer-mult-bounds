"""All512 columns only for the39 genuinely unmatched current native operators.

The actual current prefix_clifford.py emits each recipe. Literal and dense
interpreters are the separate selected6030 machinery, not that compiler.
Five newly unmatched helper jobs additionally check the complete right-before /
left-after inverse normalizers against the positive Gaussian on all columns.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
import argparse
import ast
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('dense_map_compare',HERE/'compare_maps.py')
B=importlib.util.module_from_spec(spec);sys.modules[spec.name]=B;spec.loader.exec_module(B)


def source_functions(path):
    out={}
    for x in ast.parse(path.read_text()).body:
        if isinstance(x,ast.FunctionDef):out[x.name]=ast.dump(x,include_attributes=False)
        if isinstance(x,ast.ClassDef):
            for m in x.body:
                if isinstance(m,ast.FunctionDef):out[x.name+'.'+m.name]=ast.dump(m,include_attributes=False)
    return out


def run(comparison=None):
    B.authenticate()
    comparison=B.run()if comparison is None else comparison
    oldf=source_functions(HERE/'vendor/old_clifford.py')
    newf=source_functions(HERE/'vendor/current/prefix_clifford.py')
    B.need(set(oldf)==set(newf) and [k for k in oldf if oldf[k]!=newf[k]]==['Op.zero_state'],
           'all27 compiler functions match selected implementation except exact state-evaluator fork')
    sys.path.insert(0,str(HERE/'vendor/current'))
    C=B.load('actual_current_compiler','current/prefix_clifford.py')
    V=B.load('dense_independent_literal','literal.py');D=B.load('dense_independent_columns','dense.py')
    w=B.read('inputs/CURRENT-WORD.json.gz');actual_tasks=set(B.inventory(w));records=[];helper_records=[]
    examples=[]
    for item in comparison['unmatched']:
        kind,a,b,q=t=tuple(item['current'])
        B.need(t in actual_tasks and kind in ('move','helper'),'actual unmatched task from current native')
        literal=V.adjoint(V.frame(tuple(w['frames'][a]),9))+V.frame(tuple(w['frames'][b]),9)
        op=C.canonical_frame(9,tuple(w['frames'][a])).adjoint().then(C.canonical_frame(9,tuple(w['frames'][b])))
        recipe,_=C.lower_child(op)
        B.need(recipe['rank']==item['rank'],'actual current emitted recipe keeps paid rank')
        actual=V.recipe(recipe);ac=D.compile_circuit(actual);expected=D.compile_circuit(literal)
        h=sha256()
        for col in range(512):
            left,right=D.dense_column(ac,col),D.dense_column(expected,col)
            B.need(left==right,'actual current recipe exact full complex column '+str((t,col)))
            re,im,den=left
            B.need(sum(x*x+y*y for x,y in zip(re,im))==1<<(2*den),'exact unitary column norm')
            B.need(sum(bool(x or y)for x,y in zip(re,im))==1<<recipe['rank'],'actual Gaussian rank support')
            h.update(json.dumps([col,den,re,im],separators=(',',':')).encode())
        rec={'task':list(t),'rank':recipe['rank'],'columns':512,'complex_entries':262144,
             'matrix_sha256':h.hexdigest(),
             'actual_current_recipe_sha256':sha256(json.dumps(recipe,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
             'left_phase':recipe['left']['phase'],'right_phase':recipe['right']['phase']}
        records.append(rec);examples.append((recipe,literal))
        if kind=='helper':
            right=V.monomial(recipe['right']);left=V.monomial(recipe['left'])
            B.need(all(x==0 for x,z,p in V.tableau(right)[9:]) and
                   all(x==0 for x,z,p in V.tableau(left)[9:]),'helper normalizers are literal ordinary monomials')
            normalized=V.adjoint(right)+literal+V.adjoint(left)
            positive=V.fourier(recipe['rank'])
            got,want=D.compile_circuit(normalized),D.compile_circuit(positive);hh=sha256()
            for col in range(512):
                x,y=D.dense_column(got,col),D.dense_column(want,col)
                B.need(x==y,'full arbitrary-input helper job with right-before/left-after inverse phases')
                hh.update(json.dumps([col,*x],separators=(',',':')).encode())
            helper_records.append({'task':list(t),'rank':recipe['rank'],'columns':512,
                'identity':'M_left^-1 U M_right^-1 = positive G_rank',
                'normalizer_matrix_sha256':hh.hexdigest(),
                'pre':'literal adjoint of current right monomial','post':'literal adjoint of current left monomial'})
    B.need(len(records)==39 and len(helper_records)==5,'only39 actual unmatched maps and five helper jobs')
    recipe,literal=examples[0];actual=V.recipe(recipe);fault=actual+(('phase',1),)
    B.need(V.tableau(actual)==V.tableau(fault),'phase control preserves every signed Pauli image')
    phase_control=D.first_difference(fault,literal)
    helper_control=None
    for item,(recipe,literal) in zip(comparison['unmatched'],examples):
        if item['current'][0]!='helper':continue
        wrong=V.adjoint(V.monomial(recipe['left']))+literal+V.adjoint(V.monomial(recipe['right']))
        try:column=D.first_difference(wrong,V.fourier(recipe['rank']))
        except ValueError:continue
        helper_control={'task':item['current'],'first_wrong_column':column};break
    B.need(helper_control is not None,'wrong helper inverse placement must be detected')
    return {'schema':'actual-current-unmatched-native-dense/1','status':'PASS_ALL39_UNMATCHED_CURRENT_RECIPES_AND5_HELPER_JOBS',
        'maps':records,'whole_helper_jobs':helper_records,
        'actual_current_compiler_sha256':sha256((HERE/'vendor/current/prefix_clifford.py').read_bytes()).hexdigest(),
        'compiler_function_AST_count':len(oldf),'only_compiler_function_delta':'Op.zero_state',
        'phase_only_fault_first_wrong_column':phase_control,'wrong_helper_inverse_order':helper_control,
        'matched_map_reuse':'Exact full-operator equality and equal paid Gaussian rank identify selected witnesses. The separate SIGNATURES check independently verifies every actual current emitted recipe, including its complete exact zero column and global phase. AST comparison is diagnostic, not the justification for compiler-output reuse. No unchanged map receives a full512-column replay.',
        'scope':'Actual current emitted recipes checked, not recipes emitted only by the old compiler. All512 complex columns and absolute phases; five helper right-before/left-after inverses. No unchanged2939-map dense suite, full caller/price replay or framework/admission claim.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    r=run();raw=json.dumps(r,sort_keys=True,indent=2)+'\n';path=HERE/'DENSE.json'
    if a.write:path.write_text(raw)
    else:B.need(path.read_text()==raw,'read-only unmatched dense receipt')
    print(json.dumps({'status':r['status'],'maps':len(r['maps']),'helper_jobs':len(r['whole_helper_jobs'])},sort_keys=True))
