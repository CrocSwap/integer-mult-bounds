#!/usr/bin/env python3
"""Source-bound full T37 assembly on a finer strict rational objective grid.

Conditional bound, with unchanged native suppliers and invoices. Substantial
OpenAI Codex assistance; Apache-2.0. Retained source authors are in NOTICE.md.
"""
import argparse
import copy
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier942-audit/t37-replay.tar.gz'
OLD = 'research/community-frontier942-audit/ASSEMBLY.json'
INVENTORY = 'research/community-frontier942-audit/SELECTED-SOURCE.json'
ENGINE = 'research/e8-bit-carrier-skeleton/code/pricing/outer.py'
PIVOT = 'research/complex-t21-owners/vendor/pr870/construction/layers_np/PIVOT-SWAP-NP.json'
SOURCE = 'research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold'
GRID = 10**24
EXPECTED = Q('0.001661960547713947858091')
EDITS = [('margin*10**18','margin*10**24'),
         ('ticks.denominator,10**18)','ticks.denominator,10**24)'),
         ('k+Q(1,10**18)','k+Q(1,10**24)')]


def need(condition,message):
    if not condition: raise ValueError(message)


def load(path):
    def pairs(items):
        result = {}
        for key,value in items:
            need(key not in result,'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(),object_pairs_hook=pairs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')


def decimal(value):
    with localcontext() as context:
        context.prec=70
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def pins():
    manifest=load(HERE/'SOURCES.json')
    need(set(manifest['sha256'])=={ARCHIVE,OLD,INVENTORY,ENGINE,PIVOT},'source inventory')
    for name,digest in manifest['sha256'].items():
        need(sha(ROOT/name)==digest,'source pin: '+name)
    selected=load(ROOT/INVENTORY)
    full=selected['files']
    need(len(full)==manifest['source_inventory_count']==876,'selected inventory coverage')
    actual=set()
    for name in selected['package_roots']:
        package=(ROOT/name).resolve()
        for path in package.rglob('*'):
            need(not path.is_symlink() or path.is_file(),'invalid source alias')
            if path.is_file():
                need(path.resolve().is_relative_to(package),'source alias escapes package')
                actual.add(path.relative_to(ROOT).as_posix())
    need(actual==set(full),'closed selected inventory changed')
    for name,digest in full.items():
        need(sha(ROOT/name)==digest,'selected source pin: '+name)
    return manifest


def outer_module():
    spec=importlib.util.spec_from_file_location('retained_refinement_outer',ROOT/ENGINE)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bridge():
    return {'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},
            'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}


def refined_point(module,assembly,conservative=False):
    prefix='conservative_' if conservative else ''
    a=Q(assembly[prefix+'bootstrap'][-1]['exponent'])
    b=Q(assembly[prefix+'complex_lower'])
    witness=module.assembly(a,b,bridge(),Q(0),eta=Q(1,10**24),beta=Q(1,10**24))
    ticks=witness['minimum_margin']*GRID
    return Q((ticks.numerator-1)//ticks.denominator,GRID)


def unpack(work):
    wanted={'strict/global/audit/OWNERS-AND-PROFILE.json',
            'strict/global/audit/PREFIX-AND-INVOICE.json',
            'strict/global/hosted/HOSTED.json'}
    with tarfile.open(ROOT/ARCHIVE) as archive:
        for member in archive:
            if not member.isfile() or not (member.name.startswith('runtime/') or member.name in wanted):
                continue
            relative=Path(member.name)
            need(not relative.is_absolute() and '..' not in relative.parts,'archive containment')
            target=work/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())


def run_assembly(work,name,expect_pass=True):
    result_path=work/(name+'.json')
    need(not result_path.exists(),'existing assembly output')
    env=dict(os.environ,GAIN_PR564_SOURCE=str(ROOT/SOURCE),MULTICOLD_SOURCE=str(ROOT/SOURCE),
             WITNESS_SPEC=str(work/'runtime/data/SPEC.json'),PYTHONDONTWRITEBYTECODE='1',
             PYTHONINTMAXSTRDIGITS='0')
    for key in ('WITNESS_DISCOVER','WITNESS_RECORD','PYTHONOPTIMIZE'):
        env.pop(key,None)
    result=subprocess.run([sys.executable,'-B',str(work/'runtime/code/assemble.py'),
                           str(ROOT/SOURCE),str(work/'strict/global'),str(result_path)],
                          cwd=ROOT,env=env,capture_output=True,text=True)
    (work/(name+'.log')).write_text(result.stdout+result.stderr)
    if expect_pass:
        need(result.returncode==0,'assembly failed: '+result.stderr[-3000:])
        return load(result_path)
    need(result.returncode!=0 and 'AssertionError' in result.stderr and not result_path.exists(),
         'corrupted invoice was accepted or failed unexpectedly: '+name)


def verify(work):
    need(not sys.flags.optimize,'Retained source assertions must stay enabled')
    manifest=pins()
    work.mkdir(parents=True,exist_ok=False)
    unpack(work)
    assembly_path=work/'runtime/code/assemble.py'
    original_code=assembly_path.read_text()
    spec_path=work/'runtime/data/SPEC.json'
    spec=load(spec_path)
    original_spec=copy.deepcopy(spec)
    need(sha(ROOT/PIVOT)==spec['pivot_swap']['sha256'],'archived pivot recipe binding')
    pivot_path=work/'runtime/construction/layers_np/PIVOT-SWAP-NP.json'
    pivot_path.parent.mkdir(parents=True,exist_ok=True)
    pivot_path.write_bytes((ROOT/PIVOT).read_bytes())
    # Archive metadata contains an obsolete macOS absolute path. Relocate the
    # same pinned bytes; no construction, owner or invoice field changes.
    spec['pivot_swap']['recipe']=str(pivot_path.relative_to(work/'runtime'))
    write(spec_path,spec)
    baseline=run_assembly(work,'BASELINE-ASSEMBLY')
    old=load(ROOT/OLD)
    need(baseline==old,'full original assembly replay mismatch')
    module=outer_module()
    for name in ('moment','base_two_moment','outer'):
        need(sha(ROOT/SOURCE/'engines'/(name+'.py'))==old['input_sha256']['engines/'+name+'.py'],
             'closed supplier engine identity: '+name)
    k=refined_point(module,old)
    conservative=refined_point(module,old,True)
    need(k==EXPECTED and k>Q(old['kappa']),'refined conditional bound')
    adapted=original_code
    for before,after in EDITS:
        need(adapted.count(before)==1,'unexpected original grid source')
        adapted=adapted.replace(before,after)
    assembly_path.write_text(adapted)
    spec['expected']['kappa']=str(k)
    spec['expected']['kappa_decimal']=decimal(k)
    spec['expected']['conservative_kappa_decimal']=decimal(conservative)
    write(spec_path,spec)
    result=run_assembly(work,'REFINED-ASSEMBLY')
    allowed={'kappa','kappa_decimal','gain_over_pr635_percent','conservative_kappa',
             'conservative_kappa_decimal','conservative_outer','native_correction_gain','outer'}
    changed={name for name in old if old[name]!=result[name]}
    need(changed==allowed and set(result)==set(old),'unexpected assembly changes')
    need(Q(result['kappa'])==k and len(result['outer'])==47 and
         all(Q(value)>0 for value in result['outer'].values()),'47 strict constraints')
    need(result['bootstrap']==old['bootstrap'] and result['conservative_bootstrap']==old['conservative_bootstrap'],
         'bootstrap changed')
    need(result['input_sha256']==old['input_sha256'] and result['moments']==old['moments']
         and result['conservative_moments']==old['conservative_moments'],'supplier prices or invoice inputs changed')
    a=Q(old['bootstrap'][-1]['exponent']);b=Q(old['complex_lower'])
    controls=[]
    def reject_outer(name,kk,eta=Q(1,10**24),beta=Q(1,10**24)):
        try: module.assembly(a,b,bridge(),kk,eta=eta,beta=beta)
        except AssertionError: controls.append(name)
        else: raise ValueError('outer control accepted: '+name)
    reject_outer('next_fine_grid',k+Q(1,GRID))
    reject_outer('old_next_coarse_grid',Q(old['kappa'])+Q(1,10**18))
    reject_outer('zero_eta',k,eta=Q(0))
    reject_outer('zero_beta',k,beta=Q(0))
    invoice_path=work/'strict/global/audit/PREFIX-AND-INVOICE.json'
    invoice_raw=invoice_path.read_bytes()
    invoice=load(invoice_path)
    mutations=[('old_512_bit_charge','charged_prefix_bits',512),
               ('old_1024_row_extra','row_prefix_extra',1024),
               ('unpaid_primitive','selected_real_component_primitives',invoice['selected_real_component_primitives']-1)]
    for name,field,value in mutations:
        bad=copy.deepcopy(invoice);bad[field]=value;write(invoice_path,bad)
        try:run_assembly(work,name,False);controls.append(name)
        finally:invoice_path.write_bytes(invoice_raw)
    need(sha(invoice_path)==old['input_sha256']['fresh_invoice'],'invoice restoration')
    # The only spec changes are output expectations and the hash-preserving
    # pivot path relocation. All mathematical construction inputs are fixed.
    expected_keys={'kappa','kappa_decimal','conservative_kappa_decimal'}
    before=copy.deepcopy(original_spec);after=copy.deepcopy(spec)
    for key in expected_keys:before['expected'].pop(key);after['expected'].pop(key)
    before['pivot_swap'].pop('recipe');after['pivot_swap'].pop('recipe')
    need(before==after,'unexpected specification adaptation')
    receipt={'status':'PASS_T37_RATIONAL_REFINEMENT','base_commit':manifest['base_commit'],
             'source_inventory':876,'original_kappa':old['kappa'],'kappa':str(k),
             'decimal':decimal(k),'increase':str(k-Q(old['kappa'])),'objective_grid':GRID,
             'strict_constraints':47,'baseline_complete_assembly_exact_match':True,
             'unchanged_moments_bootstraps_and_invoice_inputs':True,
             'allowed_changed_fields':sorted(allowed),'controls_rejected':controls,
             'original_assembly_code_sha256':hashlib.sha256(original_code.encode()).hexdigest(),
             'adapted_assembly_code_sha256':sha(assembly_path),
             'exact_source_edits':[list(e) for e in EDITS],
             'scope':'Conditional finer rational bound on the same accepted U8/T37 finite construction. Full pricing replay uses frozen maintainer inputs; native emission and inherited all-size/realization/precision/tape/analytic assumptions are retained.'}
    write(work/'RECEIPT.json',receipt)
    return result,receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='fresh directory for logs, inputs and assemblies')
    parser.add_argument('--write-certificate',action='store_true')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='t37-refinement-') as temporary:
        result,receipt=verify(args.output or Path(temporary)/'replay')
    if args.write_certificate:
        need(not (HERE/'ASSEMBLY.json').exists() and not (HERE/'CERTIFICATE.json').exists(),
             'certificate already exists')
        write(HERE/'ASSEMBLY.json',result);write(HERE/'CERTIFICATE.json',receipt)
    else:
        need(result==load(HERE/'ASSEMBLY.json') and receipt==load(HERE/'CERTIFICATE.json'),
             'committed certificate mismatch')
    print('PASS_T37_RATIONAL_REFINEMENT kappa=0.001661960547713947858091 '
          'sources=876 full_assembly=PASS strict_constraints=47 controls=7')
