#!/usr/bin/env python3
"""Reproduce the h30 producer and matching without a saved discovery cache.

Fingerprint interning constructs a candidate only. The final rewritten DAG is
then evaluated by an independent canonical ZDD checker, including every output
family and source core. Only that exact checked DAG reaches the frame/compiler
certificate. No fingerprint collision assumption remains in the result.
"""
from pathlib import Path
import json
import subprocess
import tempfile

from .ternary_dimension_sweep import build_sweep_binaries, matching
from .ternary_split_search import Search, H28_SELECTED_STATES
from .ternary_top_split_search import export, template_builder, append_screening_cores
from .ternary_star_resynthesis import resynthesize
from .ternary_target_certify import ROOT, file_hash
from .ternary_stream_bilateral_scratch import audit as small_audit, strict_dual_control

H, SPLIT, DEPTH, ROLES = 30, 16, 4, 13056812
PROOF_FILES = (
    'scripts/experiments/ternary_dimension_certify.py',
    'scripts/experiments/ternary_dimension_sweep.py',
    'scripts/experiments/ternary_split_search.py',
    'scripts/experiments/ternary_top_split_search.py',
    'scripts/experiments/ternary_star_demands.cpp',
    'scripts/experiments/ternary_star_resynthesis.py',
    'scripts/experiments/ternary_dag_audit.cpp',
    'scripts/experiments/ternary_target_fingerprint.cpp',
    'scripts/experiments/ternary_target_dual.cpp',
    'scripts/experiments/ternary_target_span_classes.cpp',
    'scripts/experiments/ternary_stream_saturated_scratch.cpp',
    'scripts/experiments/ternary_stream_saturated_scratch.py',
    'scripts/experiments/ternary_stream_bilateral_scratch.cpp',
    'scripts/experiments/ternary_stream_bilateral_scratch.py',
    'scripts/experiments/ternary_stream_scratch.py',
    'scripts/experiments/ternary_target_circuit.py',
    'scripts/experiments/ternary_reuse_plateaus.py',
    'scripts/experiments/ternary_target_certify.py',
    'scripts/experiments/ternary_target_fingerprint.py',
    'scripts/experiments/intersection_circuit.py',
    'scripts/exclusion_circuit.py',
    'scripts/prime_field_circuit.py',
    'docs/research/ternary-targets.md',
    'docs/research/ternary-stream.md',
    'docs/research/ternary-stream-saturated.md',
    'docs/research/ternary-stream-bilateral.md',
    'docs/research/dimension30-stream.md',
    'tests/test_ternary_dimension_sweep.py',
    'tests/test_ternary_star_resynthesis.py',
    'tests/test_ternary_stream_saturated_scratch.py',
    'tests/test_ternary_stream_bilateral_scratch.py',
)


def run(binary, *args):
    result = json.loads(subprocess.check_output([str(binary), *map(str, args)], text=True))
    result.pop('seconds', None)
    return result


def reference_manifest():
    folder = ROOT/'references/pr12'
    manifest = json.loads((folder/'SOURCE.json').read_text())
    for name, digest in manifest['sha256'].items():
        if file_hash(folder/name) != digest:
            raise ValueError('Changed pinned PR #12 reference: '+name)
    return manifest


def certificate(workdir=None):
    if workdir is None:
        with tempfile.TemporaryDirectory(prefix='ternary-dimension30-') as folder:
            return certificate(Path(folder))
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    references = reference_manifest()
    images = matching(H)
    binaries = build_sweep_binaries(workdir/'binaries')
    for name in ('target_fingerprint', 'target_dual'):
        binary = workdir/'binaries'/name
        subprocess.run(['c++', '-std=c++17', '-O3',
                        str(ROOT/f'scripts/experiments/ternary_{name}.cpp'),
                        '-o', str(binary)], check=True)
        binaries[name] = binary
    plan, candidate = workdir/'selected-plan.bin', workdir/'candidate-dag.bin'
    export(H, SPLIT, plan, template_builder(Search(), 'selected'))
    discovery = run(binaries['target_fingerprint'], plan, candidate)
    append_screening_cores(candidate)
    demands, templates = workdir/'star-demands.txt', workdir/'star-templates.bin'
    before = run(binaries['star_demands'], candidate, demands)
    stars = resynthesize(demands, H, templates)
    dag = workdir/'rewritten-dag.bin'
    rewrite = run(binaries['star_demands'], candidate, demands, templates, dag)
    # This evaluates the final DAG exactly from its original five-set inputs,
    # independently of the fingerprint equality used in candidate generation.
    checked = run(binaries['dag_audit'], dag)
    if (not checked['every_addition_disjoint'] or not checked['every_source_core_checked']
            or not checked['every_output_family_independently_checked']):
        raise ValueError('Final candidate lacks an exact support audit')
    if checked['retained_additions'] != rewrite['rewritten_additions']:
        raise ValueError('Exact rewritten addition count differs')
    if before['additions']-stars['saved_additions'] < checked['retained_additions']:
        raise ValueError('Star rewrite exceeds its role bound')
    labels, targets = workdir/'family-labels.bin', workdir/'targets.bin'
    frames = run(binaries['target_dual'], dag, workdir/'reassigned.txt', labels, targets)
    if (not frames['every_final_frame_nondegenerate'] or frames['unresolved_source_nodes']
            or not frames['source_region_ancestor_closed'] or not frames['all_centers_in_source_region']):
        raise ValueError('Unresolved h30 frame construction')
    links = workdir/'links.bin'
    stream = run(binaries['stream_bilateral_scratch'], dag, targets, DEPTH, links, 'mixed')
    if (stream['original_roles'] != checked['roles'] or stream['new_roles'] != ROLES
            or stream['physical_roles_allocated'] != ROLES or stream['extra_frame_loss']
            or stream['center_loss'] != 12180
            or stream['dual_frame_links'] != 35652
            or stream['physical_rank_sum_each_orientation'] != 399994068
            or not stream['every_physical_producer_transition_certified']
            or not stream['every_designated_output_protected']):
        raise ValueError('H30 physical compiler contract changed')
    generated = json.loads((workdir/'binaries/SOURCE.json').read_text())
    return dict(status='EXACT H30 PRODUCER, MATCHING AND PHYSICAL COMPILER; ASSEMBLY SEPARATE',
                h=H, top_split=[SPLIT, H-SPLIT], template_mode='selected', depth=DEPTH,
                selected_template_patterns=[list(k[1:]) for k in H28_SELECTED_STATES],
                discovery=discovery, star_extraction=before, star_replacement=stars,
                rewritten_support=checked, frames=frames, stream=stream,
                small_control=small_audit(8, DEPTH), strict_dual_control=strict_dual_control(),
                matching=images,
                matching_reference=references, generated_source=generated,
                global_roles=dict(current=ROLES, center_loss=12180, extra_frame_loss=0),
                artifact_sha256={name: file_hash(path) for name, path in
                                 [('plan', plan), ('candidate_dag', candidate),
                                  ('star_templates', templates), ('rewritten_dag', dag),
                                  ('family_labels', labels), ('targets', targets), ('links', links)]},
                proof_sha256={name: file_hash(ROOT/name) for name in PROOF_FILES},
                scope='Every final coefficient, source core, frame and physical transition is '
                      'checked. Generated source copies enlarge fixed arrays to32 and retain '
                      'a deterministic Hadamard bound5^16<2^61-1. The matching is checked on '
                      'every five-set. General nested-wire, tensor-stage and batching transfer '
                      'arguments remain mathematical dependencies.')
