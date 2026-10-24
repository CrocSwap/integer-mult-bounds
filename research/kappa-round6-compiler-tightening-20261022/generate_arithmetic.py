"""Transcribe the source outer formulas, not just their positive outputs.

The resulting closed rational and integer statements are checked by Lean's
kernel. This does not assert correctness of the source analytic enclosures.
Apache-2.0. Substantial OpenAI Codex assistance; signed Cao Yifan.
"""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import ast
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SOURCE=ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
RECEIPT=HERE/'ARITHMETIC.json'


def rational(q):
    q=Q(q);return f'({q.numerator} / {q.denominator} : ℚ)'


def main():
    data=json.loads(RECEIPT.read_text());module=ast.parse(SOURCE.read_text())
    ledger=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='ledger')
    tables={}
    for node in ledger.body:
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and isinstance(node.value,ast.Dict):
            tables[node.targets[0].id]=node.value
    rename={'kappa':'kappa','b':'b','a':'a','q':'q','epsilon':'epsilon','beta':'beta','r0':'r0','stop':'stop','layout':'layout',
            'sigma':'sigma','tau':'tau','internal':'internal','leaf':'leaf','lam':'lam','c':'capConstant','xi':'xi','key':'key',
            'OLD_BASELINE':'oldBaseline'}
    pnames={'bit_saving':'bitSaving','complex_uniform_saving':'complexUniformSaving'}
    def expr(n):
        if isinstance(n,ast.Constant) and isinstance(n.value,int):return str(n.value)
        if isinstance(n,ast.Name):return rename[n.id]
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return f'(-{expr(n.operand)})'
        if isinstance(n,ast.BinOp):
            op={ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/',ast.Pow:'^'}[type(n.op)]
            return f'({expr(n.left)} {op} {expr(n.right)})'
        if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name):
            key=n.slice.value
            return pnames[key] if n.value.id=='p' else 'margin_'+key
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='Q':
            if len(n.args)==2:return f'({expr(n.args[0])} / {expr(n.args[1])})'
            if isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str):return rational(n.args[0].value)
            return expr(n.args[0])
        raise ValueError(ast.dump(n))
    out=['/- Exact source-formula rational certificates. Apache-2.0.','Substantial OpenAI Codex assistance. Signed Cao Yifan.',
         'No claim here that externally computed enclosures bound real powers. -/',
         'import Mathlib.Tactic.NormNum','import Mathlib.Tactic.Positivity','',
         'set_option maxRecDepth 1000000','set_option maxHeartbeats 0','namespace KappaChangedG.Arithmetic','']
    parameters=[('kappa','kappa'),('tested_saving','tested'),('complex_uniform_saving','complexUniformSaving'),
                     ('b','b'),('a','a'),('q','q'),('epsilon','epsilon'),('beta','beta'),('r0','r0'),('stop','stop'),('layout','layout'),('bit_saving','bitSaving')]
    for key,name in parameters:
        out.append(f'def {name} : ℚ := {rational(data["outer"]["parameters"][key])}')
    out += [f'def oldBaseline : ℚ := {rational(".001730970419199163702738")}',
            'def sigma : ℚ := 1-b','def tau : ℚ := 1-a',
            'def internal : ℚ := tau+(1-stop)*max (sigma-tau) 0',
            'def leaf : ℚ := sigma+stop*(1-sigma)',
            'def lam : ℚ := 1-(q+a)/2','def capConstant : ℚ := 3/32',
            'def xi : ℚ := epsilon*(1+q)-capConstant+layout','def key : ℚ := beta+1-epsilon','']
    margins={k.value:expr(v) for k,v in zip(tables['margins'].keys,tables['margins'].values)}
    for key,value in margins.items():out.append(f'def margin_{key} : ℚ := {value}')
    entries={k.value:expr(v) for k,v in zip(tables['checks'].keys,tables['checks'].values)}
    entries.update({k+'_above_kappa':'margin_'+k+'-kappa' for k in margins})
    functions={k.value:expr(v) for k,v in zip(tables['functional'].keys,tables['functional'].values)}
    functions['actual_new_BIT_stock_sublinear']='beta*(1-(4/1000))'
    assert len(entries)==54 and len(functions)==4
    all_defs=[name for _,name in parameters]+['oldBaseline','sigma','tau','internal','leaf','lam','capConstant','xi','key']
    all_defs+=['margin_'+key for key in margins]
    unfold=', '.join(all_defs)
    for name,rows,key in [('outerSlacks',entries,'strict_checks'),('functionalSlacks',functions,'functional_checks')]:
        out.append(f'def {name} : List (String × ℚ) := [')
        out.append(',\n'.join(f'  ("{k}", {v})' for k,v in rows.items())+']')
        out.append(f'def {name}Recorded : List (String × ℚ) := [')
        out.append(',\n'.join(f'  ("{k}", {rational(data["outer"][key][k])})' for k in rows)+']')
        out += [f'theorem {name}_source_equality : {name} = {name}Recorded := by\n  norm_num [{name}, {name}Recorded, {unfold}]',
                f'theorem {name}_all_positive : {name}.all (fun p => decide (0 < p.2)) = true := by\n  apply List.all_eq_true.mpr\n  norm_num [{name}, {unfold}]',
                f'theorem {name}_count : {name}.length = {len(rows)} := by decide','']
    out += ['theorem claimed_saving : kappa = 15108879/5000000000 := by\n  norm_num [kappa]',
            'theorem strict_improvement : (9443/3125000 : ℚ) < kappa := by\n  norm_num [kappa]',
            'theorem tested_above_kappa : kappa < tested := by\n  norm_num [kappa, tested]',
            'theorem explicit_gap : (tested-kappa)/7 = (1/700000000000 : ℚ) := by\n  norm_num [kappa, tested]',
            'theorem splitting_base_gap : (20:ℕ)^64 < 21^63 := by decide',
            'theorem tail_decay : (97/100 : ℚ)^128 < 1/16 := by norm_num',
            'theorem normalized_completion : (1/(1+1024*(1/100000000000))+4/(2:ℚ)^32) < 1 := by norm_num',
            'theorem shifted_exit_capacity : 2*((20:ℕ)^1024)^64 ≤ ((145:ℕ)^1024)^63 := by decide',
            'theorem finite_threshold : 700000000000*55099 = (38569300000000000:ℕ) := by decide',
            'theorem finite_compiler_wins : ((700000000000:ℕ)*55099+1)^1000 < 2^55099 := by decide',
            'theorem previous_integer_fails : ¬ (((700000000000:ℕ)*55098+1)^1000 < 2^55098) := by decide',
            'theorem local_route_count : (3298+2*408+688)*1000 = (4802000:ℕ) := by decide',
            'theorem local_budget : (158168+4802000:ℕ) < 10000000 := by decide',
            'theorem controller_budget : (181098496:ℕ) < 1000000000 := by decide','',
            'end KappaChangedG.Arithmetic','',
            '#print axioms KappaChangedG.Arithmetic.outerSlacks_source_equality',
            '#print axioms KappaChangedG.Arithmetic.outerSlacks_all_positive',
            '#print axioms KappaChangedG.Arithmetic.functionalSlacks_source_equality',
            '#print axioms KappaChangedG.Arithmetic.functionalSlacks_all_positive',
            '#print axioms KappaChangedG.Arithmetic.claimed_saving',
            '#print axioms KappaChangedG.Arithmetic.strict_improvement',
            '#print axioms KappaChangedG.Arithmetic.tested_above_kappa',
            '#print axioms KappaChangedG.Arithmetic.explicit_gap',
            '#print axioms KappaChangedG.Arithmetic.tail_decay',
            '#print axioms KappaChangedG.Arithmetic.normalized_completion',
            '#print axioms KappaChangedG.Arithmetic.finite_compiler_wins']
    target=HERE/'TightenedArithmetic.lean';target.write_text('\n'.join(out)+'\n',encoding='utf-8',newline='\n')
    (HERE/'ARITHMETIC-TRANSCRIPTION.json').write_text(json.dumps({'status':'TRANSCRIBED_PENDING_LEAN',
        'source_sha256':sha256(SOURCE.read_bytes()).hexdigest(),'receipt_sha256':sha256(RECEIPT.read_bytes()).hexdigest(),
        'lean_sha256':sha256(target.read_bytes()).hexdigest(),'strict_predicates':54,'functional_predicates':4,
        'scope':'Source outer formulas and closed integer compiler arithmetic. Analytic enclosure correctness is outside this file.'},indent=2)+'\n',encoding='utf-8',newline='\n')
    print('GENERATED_ARITHMETIC_SOURCE_FORMULAS',len(entries),len(functions))


if __name__=='__main__':main()
