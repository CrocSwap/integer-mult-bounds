#!/usr/bin/env python3
"""Source-bound current PR210 preparation with no historical search imports.

This is a focused preparation adapter, not a full scalar or supplier verifier.
The pinned public joint and source471 preparation bodies are retained literally;
only the explicit base source root and terminal-selector source are rebound.
Original source-specific notices remain beside the supplied public inputs.
New path adapter and semantic fingerprints: assisted with ChatGPT.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
import argparse
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
import sys

sys.dont_write_bytecode = True
if not __debug__:
    raise SystemExit('refusing optimized Python: assertions are required')
HERE = Path(__file__).resolve().parent
BASE_PACKAGE = 'research/paired-cube-diagonal-bit-168'
PR210_PACKAGE = 'research/coordinated-crossover-pr200'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def check_sources(pr210_root, base_bit_root):
    """Validate all inputs before importing any source implementation."""
    roots = {'pr210': Path(pr210_root).resolve(), 'base_bit': Path(base_bit_root).resolve()}
    pins = json.loads((HERE/'SOURCE_PINS.json').read_text())
    checked = {}
    for group, root in roots.items():
        checked[group] = {}
        for relative, expected in pins[group]['files'].items():
            path = (root/relative).resolve()
            if not path.is_relative_to(root):
                raise ValueError('source path escapes supplied root')
            got = sha(path.read_bytes())
            if got != expected:
                raise ValueError('source hash mismatch: '+group+'/'+relative)
            checked[group][relative] = got
    return roots, pins, checked


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def terminal_records(word, selectors):
    """Derive terminal data from pinned roots and selectors, never a receipt."""
    writes = defaultdict(list)
    for i, (a, b, node) in enumerate(word.ops):
        writes[a].append(i)
    result = []
    for selected in selectors:
        root = selected['root']; pivot = selected['pivot']
        role = word.w['rootroles'][root]
        entry = word.g['roots'][root]
        assert entry['kind'] == 'side' and pivot in entry['targets']
        assert role not in word.source.values() and role not in word.gauge
        result.append(dict(root=root, pivot=pivot, role=role,
                           targets=entry['targets'], root_frame=word.w['root_frame'][root],
                           writes=writes[role]))
    assert len(result) == 34
    assert len({r['role'] for r in result}) == 34
    return result


def prepare(pr210_root, base_bit_root):
    roots, pins, checked = check_sources(pr210_root, base_bit_root)
    p = roots['base_bit']/BASE_PACKAGE
    package = roots['pr210']/PR210_PACKAGE
    base = import_file('five_stage_public_base_word', p/'bit/word.py')
    joint_path = package/'joint/joint_word.py'
    joint = joint_path.read_text()
    old = "P=ROOT/'research/paired-cube-diagonal-bit-168'\nsys.path.insert(0,str(P/'bit'))\nfrom word import Candidate as Original"
    assert joint.count(old) == 1, 'joint import boundary changed'
    joint = joint.replace(old, 'P=__base_package__\nOriginal=__base_candidate__', 1)
    js = {'__name__': 'five_stage_public_joint', '__file__': str(joint_path),
          '__base_package__': p, '__base_candidate__': base.Candidate}
    exec(compile(joint, str(joint_path)+' [explicit base-root binding]', 'exec'), js)
    word = js['Candidate']()
    c = word.C
    # These are decoder/geometry checks, not all-column payload replay.
    c.decoder(); c.geometry()
    word.changed_frames = [i for i, (a, b) in enumerate(zip(word.original_opframe, word.opframe)) if a != b]
    word.endframe = {r: word.opframe[ii[-1]] for r, ii in word.role_ops.items()}
    selection = json.loads((package/'borrow/selection.json').read_text())
    gauges = json.loads((package/'gaugeb/selection.json').read_text())
    current = json.loads((package/'newg/selection.json').read_text())
    if isinstance(current, dict):
        current = current['selection']
    terminal = terminal_records(word, json.loads((p/'selected/bit/sinks.json').read_text()))
    source_path = package/'newg/replay.py'
    source = source_path.read_text()
    start = source.index('schedule=json.loads')
    stop = source.index('\ndef replay(')
    preparation = source[start:stop]
    # Original input_paths names an output-only joint replay receipt. All actual
    # code/data inputs have already been checked against SOURCE_PINS.json.
    lines = preparation.splitlines()
    removed = [line for line in lines if line.startswith(('input_paths=', 'input_pins='))]
    assert len(removed) == 2, 'source input-list boundary changed'
    preparation = '\n'.join(line for line in lines if line not in removed)+'\n'
    old = "terminal=json.loads((D/'joint-replay.json').read_text())['selected'];"
    assert preparation.count(old) == 1, 'terminal source boundary changed'
    preparation = preparation.replace(old, 'terminal=__terminal_records__;', 1)
    namespace = {'__name__': 'five_stage_public_source471', '__file__': str(source_path),
                 'Path': Path, 'Counter': Counter, 'defaultdict': defaultdict,
                 'json': json, 'sys': sys, 'hashlib': hashlib,
                 'HERE': package/'newg', 'D': package/'joint',
                 'W': word, 'C': c, 'selection': selection,
                 'new_gauge_selection': current, 'gauge_selection': gauges+current,
                 '__terminal_records__': terminal}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(preparation, str(source_path)+' [preparation only; terminal selectors rebound]', 'exec'), namespace)
    assert 'replay' not in namespace, 'payload replay must not be executed or loaded by preparation'
    namespace['SOURCE_TEXT'] = source
    namespace['source_pins'] = checked
    namespace['source_revisions'] = {key: pins[key]['commit'] for key in roots}
    namespace['source_preparation_sha256'] = sha(source[start:stop].encode())
    namespace['loader_scope'] = 'Pinned source preparation and exact geometry only; no all-column payload replay, five-stage supplier admission, or final exponent.'
    return namespace


def semantic_fingerprint(context):
    """Exact-basis semantics; generated frame IDs need not match legacy order."""
    w, c = context['W'], context['C']
    basis_cache = {}
    def basis(f):
        if f not in basis_cache:
            basis_cache[f] = sha(canonical([list(r) for r in c.B[f]]))
        return basis_cache[f]
    def framed(entry):
        out = dict(entry)
        for key in ('frame', 'root_frame', 'mix_frame', 'deliver_frame'):
            if key in out:
                out[key] = basis(out[key])
        for key in ('carrier_chain', 'passive_chain'):
            if key in out:
                out[key] = [basis(f) for f in out[key]]
        return out
    parts = dict(
        partner_chronology=[framed(e) for e in w.k['entries']],
        partner_lookup=[(n,framed(e)) for n,e in sorted(context['kpair'].items())],
        graph=w.g,
        operations=w.ops,
        operation_bases=[basis(f) for f in w.opframe],
        source_bases=[basis(f) for f in w.w['source_frame']],
        root_bases=[basis(f) for f in w.w['root_frame']],
        full_basis=basis(w.w['full_frame']),
        gauge_records=[framed(w.gauge[r]) for r in sorted(w.gauge)],
        gauge_read_order=w.order,
        gauge_readtimes=sorted(w.readtime.items()),
        donor_recipient_pairs=w.pairs,
        physical_role_map=sorted(w.phys.items()),
        phase1=w.phase1,
        rest=w.rest,
        schedule=context['schedule'],
        source_loans=sorted(context['borrow'].items()),
        terminal=[framed(e) for e in context['terminal']],
        dirty_roles=context['regs'],
        target_response=context['adj'],
        live_gauge_reads=sorted(context['at'].items()),
        source_selection=context['selection'],
        gauge_selection=context['gauge_selection'],
    )
    hashes = {key: sha(canonical(value)) for key, value in parts.items()}
    return dict(schema='source471-exact-semantic-fingerprint/1',
                hashes=hashes, combined_sha256=sha(canonical(hashes)),
                source_head='df95878d11190518e45ef9717c9ee05011f88ace',
                h=w.h, v=w.v, logical_roles=w.R,
                independent_dirty_roles=len(context['regs']),
                local_independent_columns=2*w.v+len(context['regs']),
                source_loans=len(context['borrow']),
                terminal_sinks=len(context['terminal']),
                retimed_operations=len(context['deferred']),
                formal_frame_id_equality_required=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pr210-root', type=Path, required=True)
    ap.add_argument('--base-bit-root', type=Path, required=True)
    args = ap.parse_args()
    ctx = prepare(args.pr210_root, args.base_bit_root)
    print(json.dumps(dict(status='PASS_PINNED_PUBLIC_SOURCE_PREPARATION',
                         scope=ctx['loader_scope'],
                         fingerprint=semantic_fingerprint(ctx),
                         source_revisions=ctx['source_revisions']), indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
