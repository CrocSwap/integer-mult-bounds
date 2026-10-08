#!/usr/bin/env python3
"""Reproduce the selected splits, local star rewrites and nested-wire compiler.

Every full-size coefficient and rational frame is checked after rewriting.
The physical compiler then checks its complete register allocation. Assembly
inequalities are handled by scripts/ternary_stream_network.py.
"""
from pathlib import Path
import json
import subprocess
import tempfile

from .ternary_split_search import Search, H28_SELECTED_STATES
from .ternary_top_split_search import export, template_builder
from .ternary_star_resynthesis import resynthesize
from .ternary_target_certify import ROOT, file_hash
from .ternary_stream_bilateral_scratch import audit as small_audit, strict_dual_control

PROOF_FILES = (
    'scripts/experiments/ternary_stream_certify.py',
    'scripts/experiments/ternary_split_search.py',
    'scripts/experiments/ternary_top_split_search.py',
    'scripts/experiments/ternary_star_demands.cpp',
    'scripts/experiments/ternary_star_resynthesis.py',
    'scripts/experiments/ternary_dag_audit.cpp',
    'scripts/experiments/ternary_stream_reuse.cpp',
    'scripts/experiments/ternary_stream_scratch.py',
    'scripts/experiments/ternary_stream_saturated_scratch.cpp',
    'scripts/experiments/ternary_stream_saturated_scratch.py',
    'scripts/experiments/ternary_stream_bilateral_scratch.cpp',
    'scripts/experiments/ternary_stream_bilateral_scratch.py',
    'scripts/experiments/ternary_target_span_classes.cpp',
    'scripts/experiments/ternary_target_exact.cpp',
    'scripts/experiments/ternary_target_fingerprint.cpp',
    'scripts/experiments/ternary_target_fingerprint.py',
    'scripts/experiments/ternary_target_dual.cpp',
    'scripts/experiments/ternary_target_certify.py',
    'scripts/experiments/ternary_target_circuit.py',
    'scripts/experiments/ternary_reuse_plateaus.py',
    'scripts/experiments/intersection_circuit.py',
    'scripts/exclusion_circuit.py',
    'scripts/prime_field_circuit.py',
    'docs/research/ternary-targets.md',
    'docs/research/ternary-stream.md',
    'docs/research/ternary-stream-saturated.md',
    'docs/research/ternary-stream-bilateral.md',
    'tests/test_ternary_split_search.py',
    'tests/test_ternary_star_resynthesis.py',
    'tests/test_ternary_stream_scratch.py',
    'tests/test_ternary_stream_saturated_scratch.py',
    'tests/test_ternary_stream_bilateral_scratch.py',
    'tests/test_ternary_top_split_search.py',
)

# These determine the selected plan, star rewrite and rational frame audit.
# A cached producer may use an older register compiler, but every dependency
# that constructed its reused graph/target artifacts must still match.
CONSTRUCTION_FILES = (
    'scripts/experiments/ternary_split_search.py',
    'scripts/experiments/ternary_top_split_search.py',
    'scripts/experiments/ternary_star_demands.cpp',
    'scripts/experiments/ternary_star_resynthesis.py',
    'scripts/experiments/ternary_dag_audit.cpp',
    'scripts/experiments/ternary_target_span_classes.cpp',
    'scripts/experiments/ternary_target_exact.cpp',
    'scripts/experiments/ternary_target_fingerprint.cpp',
    'scripts/experiments/ternary_target_fingerprint.py',
    'scripts/experiments/ternary_target_dual.cpp',
    'scripts/experiments/ternary_target_certify.py',
    'scripts/experiments/ternary_target_circuit.py',
    'scripts/experiments/intersection_circuit.py',
    'scripts/exclusion_circuit.py',
    'docs/research/ternary-targets.md',
)
CONSTRUCTION_ARTIFACTS = dict(
    plan='selected-plan.bin', selected_dag='selected-dag.bin',
    star_templates='star-templates.bin', rewritten_dag='rewritten-dag.bin',
    targets='targets.bin')


def cached_construction(workdir, path):
    """Validate a prior exact construction before reusing any binary artifact."""
    old=json.loads(Path(path).read_text())
    if (old.get('h')!=28 or old.get('top_split')!=[16,12]
            or old.get('template_mode')!='selected'
            or old.get('selected_template_patterns')!=[list(k[1:]) for k in H28_SELECTED_STATES]):
        raise ValueError('Cached producer uses a different construction')
    for name in CONSTRUCTION_FILES:
        if old.get('proof_sha256',{}).get(name)!=file_hash(ROOT/name):
            raise ValueError('Changed cached construction dependency: '+name)
    for name,filename in CONSTRUCTION_ARTIFACTS.items():
        if old.get('artifact_sha256',{}).get(name)!=file_hash(Path(workdir)/filename):
            raise ValueError('Changed cached construction artifact: '+name)
    if (not old['selected_support']['every_output_family_independently_checked']
            or not old['rewritten_support']['every_output_family_independently_checked']):
        raise ValueError('Cached construction lacks exact coefficient checks')
    frames=old['frames']
    if (not frames['every_final_frame_nondegenerate'] or frames['unresolved_source_nodes']
            or not frames['source_region_ancestor_closed'] or not frames['all_centers_in_source_region']):
        raise ValueError('Cached construction lacks a complete frame audit')
    return old


def run(binary, *args):
    result=json.loads(subprocess.check_output([str(binary),*map(str,args)],text=True))
    result.pop('seconds',None)
    return result


def certificate(workdir=None, depth=4, reuse_certificate=None):
    if workdir is None:
        if reuse_certificate is not None:
            raise ValueError('Cached construction reuse requires its existing workdir')
        with tempfile.TemporaryDirectory(prefix='ternary-stream-') as folder:
            return certificate(Path(folder),depth)
    workdir=Path(workdir);workdir.mkdir(parents=True,exist_ok=True)
    cached=cached_construction(workdir,reuse_certificate) if reuse_certificate is not None else None
    binaries={}
    checker_names=('stream_bilateral_scratch',) if cached else (
        'target_exact','star_demands','dag_audit','target_dual','stream_bilateral_scratch')
    for name in checker_names:
        binary=workdir/name
        subprocess.run(['c++','-O3','-std=c++17',
                        str(ROOT/f'scripts/experiments/ternary_{name}.cpp'),
                        '-o',str(binary)],check=True)
        binaries[name]=binary
    plan=workdir/'selected-plan.bin';original=workdir/'selected-dag.bin'
    demands=workdir/'star-demands.txt';templates=workdir/'star-templates.bin'
    dag=workdir/'rewritten-dag.bin'
    labels=workdir/'family-labels.bin';targets=workdir/'targets.bin'
    if cached:
        support,before,stars,checked,frames=(cached[key] for key in (
            'selected_support','star_extraction','star_replacement','rewritten_support','frames'))
    else:
        export(28,16,plan,template_builder(Search(),'selected'))
        support=run(binaries['target_exact'],plan,original)
        if not support['every_output_family_independently_checked']:
            raise ValueError('Missing selected-plan coefficient check')
        before=run(binaries['star_demands'],original,demands)
        stars=resynthesize(demands,28,templates)
        rewritten=run(binaries['star_demands'],original,demands,templates,dag)
        expected=support['retained_additions']-stars['saved_additions']
        if before['additions']!=support['retained_additions'] or rewritten['rewritten_additions']>expected:
            raise ValueError('Incorrect rewrite accounting')
        checked=run(binaries['dag_audit'],dag)
        if checked['retained_additions']!=rewritten['rewritten_additions']:
            raise ValueError('Independent rewritten-DAG count differs')
        frames=run(binaries['target_dual'],dag,workdir/'reassigned.txt',labels,targets)
    if (not frames['every_final_frame_nondegenerate'] or frames['unresolved_source_nodes']
            or not frames['source_region_ancestor_closed'] or not frames['all_centers_in_source_region']):
        raise ValueError('Unresolved rewritten frame construction')
    links=workdir/'links.bin'
    stream=run(binaries['stream_bilateral_scratch'],dag,targets,depth,links,'mixed')
    if stream['original_roles']!=checked['roles'] or stream['extra_frame_loss']:
        raise ValueError('Stream compiler changed the boundary contract')
    if (stream['new_roles']!=stream['physical_roles_allocated']
            or not stream['every_physical_producer_transition_certified']
            or not stream['every_designated_output_protected']):
        raise ValueError('Unresolved physical allocation')
    small=small_audit(8,depth)
    strict_dual=strict_dual_control()
    if (strict_dual['new_roles']!=6 or strict_dual['dual_frame_links']!=1
            or not strict_dual['dirty_wrapper']['dirty_wrapper_restores_every_scratch']):
        raise ValueError('Strict dual-frame continuation control failed')
    return dict(status='EXACT COMPOSED PRODUCER AND PHYSICAL COMPILER; ASSEMBLY SEPARATE',
                h=28,top_split=[16,12],template_mode='selected',
                selected_template_patterns=[list(k[1:]) for k in H28_SELECTED_STATES],
                selected_support=support,star_extraction=before,star_replacement=stars,
                rewritten_support=checked,frames=frames,stream=stream,small_control=small,
                strict_dual_control=strict_dual,
                global_roles=dict(current=stream['new_roles'],center_loss=9828,extra_frame_loss=0),
                artifact_sha256={name:file_hash(path) for name,path in
                                 [('plan',plan),('selected_dag',original),('star_templates',templates),
                                  ('rewritten_dag',dag),('targets',targets),('links',links)]},
                proof_sha256={name:file_hash(ROOT/name) for name in PROOF_FILES},
                scope='Exact full-size supports, nondegenerate rational frames, all physical '
                      'producer transitions and dirty-scratch small controls. The nested-wire '
                      'compiler argument and inherited tensor/multiplication interfaces remain '
                      'mathematical dependencies. No old fusion saving is added.')
