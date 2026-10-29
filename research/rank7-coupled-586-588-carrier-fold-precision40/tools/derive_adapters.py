#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generalized PR2917 adapter derivation (Marius-Paul Dumitrean, Claude Code assisted; PR2917/PR2908 derivations by Mason Hale and Jeremy Diviney): PR2908's exact tools -> closed-profile adapters for an
arbitrary derived overlay, buffer count B, source profile and comparator set. With B=82, commit
'paired-helper-extension-pr2908', profile 'paired-extension' and comparisons=pr2908 the output is byte-identical to
PR2917's tools/derive_adapters.py output (checked against its evidence/ADAPTER-DERIVATION.json), except the retained
receipt binding, which is always sha256(--retained-receipt). Generalized here (r14) beyond PR2942's version: the admission control count
pinned by PR2917's adapter (119, five width classes) is derived from the source's provider width classes (37 + sum over the
two providers of 17 + k(k-1) + 4, freeze_spec's own formula), because the changed words have a sixth width class (6).
usage: derive_adapters_r13.py --parent-package PR2908_PKG --source OVERLAY --retained-receipt FILE --out DIR
       --buffers B --source-commit NAME --source-profile NAME --upstream-head HEX
       [--comparison pr2917=/path/CLAIM.json --comparison pr2969=/path/CLAIM.json ...]   (pr2908 always from the parent package)
Comparator registry: PR2942's version plus 'pr2966' (Jeremy Kothe, head e62d3eb9, research/paired-extension-normal45-rewrites/CLAIM.json)
and 'pr2969' (Dugongue, head e2ca469b, research/paired-swap-normal45/CLAIM.json).
"""
from pathlib import Path
import argparse, gzip, hashlib, json, sys
PARENT_HEAD = '51309592971e3b5be935599eed2a95404dc7781e'
PARENT_MANIFEST = '9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f'
OLD_SOURCE = '56cf455752722051d598a7da1e5ee700637fbaef09189f534413dbe6e0525a83'
OLD_RETAINED = 'dd36443f2789ffa6deca7210c76ada781e2b9b7e622a546b366f51a475faff3e'
# Known full-headline comparators: name -> (head, sha256 of its CLAIM.json). A comparator file must match its pin exactly.
KNOWN = {'pr2908': (PARENT_HEAD, '2406680a07b43a69b0f12f8462cc43f3616f3c8cb0a46bc767541b45945cd2bf'),
         'pr2917': ('224bd5e56041c40078ff6b5fa7393733a215de5c', 'e6c836c0178661a53a69cd91f29d83585e876f2511ff40c6b6204cd270fbdeac'),
         'pr2930': ('81f3b5d12977eba09e06fbff729167d59faabe90', '9c2c14158780a677b3661623d7476acc4f535ac9e0481addfa1d6c4c7633b74b'),
         'pr2966': ('e62d3eb9005117d82a9babcfa937ecc53237c490', '4d4c4800bf3bcb36d09021313b2712aebd4aa0830c74dda30991daf6851c220a'),   # Jeremy Kothe's PR2966 headline (field kappa)
         'pr2969': ('e2ca469b08385d3d5e29a918d66dbefaf889e9f3', '656a4c93411b078753783513e2e71b1722a56e7b70120264a38118811982fa77')}   # Dugongue's PR2969 moment nomination (field kappa, a rational string)
HEADS = {k: v[0] for k, v in KNOWN.items()}
sha = lambda b: hashlib.sha256(b).hexdigest()

def need(p, msg):
    if not p: raise ValueError(msg)

def tree(p):
    need(not any(f.is_symlink() for f in p.rglob('*')), 'no symlinks')
    return {f.relative_to(p).as_posix(): sha(f.read_bytes()) for f in p.rglob('*') if f.is_file() and f != p / 'MANIFEST.json'}

def derive(parent, source, out, retained_sha, B, commit, profile, upstream_head, claims):
    manifest = json.loads((parent / 'MANIFEST.json').read_bytes()); need(tree(parent) == manifest, 'complete exact parent manifest inventory')
    need(sha((parent / 'MANIFEST.json').read_bytes()) == PARENT_MANIFEST, 'exact PR2908 package manifest')
    newsha = sha((source / 'MANIFEST.json').read_bytes())
    files = json.loads((source / 'MANIFEST.json').read_bytes()); need(tree(source) == files, 'complete derived source inventory')
    nfiles = len(files)
    for tag in ('base', 'extra'):
        w = json.loads(gzip.decompress((source / f'new/borrow/words/BORROW-WORD-43{tag}.json.gz').read_bytes()))
        need(len(w['helper_final']) == B, f'declared {B}-buffer word ({tag}: {len(w["helper_final"])})')
        need(len(set(range(224, 704)) - set(w['removed'])) == 408, '408 live helpers')
    need(type(B) is int and 73 <= B <= 200, 'buffer count range')
    need(len(retained_sha) == 64 and all(c in '0123456789abcdef' for c in retained_sha), 'retained receipt SHA256')
    comps = [('pr2908', parent / 'CLAIM.json')] + [(k, Path(v)) for k, v in claims]
    comp_entries = []
    for name, path in comps:
        claim = json.loads(path.read_bytes()); need('headline_kappa_source' not in claim and 'kappa' in claim, 'headline outer comparison ' + name)
        need(name in KNOWN and sha(path.read_bytes()) == KNOWN[name][1], 'known comparator head and exact CLAIM.json pin ' + name)
        comp_entries.append((name, int(name[2:]), HEADS[name], sha(path.read_bytes())))
    out.mkdir(parents=True, exist_ok=False); changes = {}
    def adapt(oldname, newname, pairs):
        p = parent / 'tools' / oldname; body = p.read_text(); oldhash = sha(p.read_bytes()); applied = []
        for old, new in pairs:
            need(body.count(old) == 1, f'exact preimage occurrence {oldname}: {old[:120]}')
            body = body.replace(old, new); applied.append({'old': old, 'new': new})
        q = out / newname; q.write_text(body); compile(body, str(q), 'exec')
        changes[newname] = {'source': str(p), 'before_sha256': oldhash, 'after_sha256': sha(q.read_bytes()), 'replacements': applied}
    adapt('prepare_channel_native.py', 'prepare_extension_native.py', [
        ("SOURCE_SHA='" + OLD_SOURCE + "'", "SOURCE_SHA='" + newsha + "'"),
        ('SOURCE_FILES=610', 'SOURCE_FILES=' + str(nfiles)),
        ("SOURCE_COMMIT='two-sided-helper408-pr2894'", "SOURCE_COMMIT='" + commit + "'"),
        ("OLD_RECEIPT_SHA='" + OLD_RETAINED + "'", "OLD_RECEIPT_SHA='" + retained_sha + "'"),
        ("len(can['zero_buffers'])==73", f"len(can['zero_buffers'])=={B}"),
    ])
    oldprofile = "    'channel408': dict(commit='two-sided-helper408-pr2894',manifest='" + OLD_SOURCE + "',helpers=408,source_file_count=610,upstream_head='18d03c447886895ef9abf888398178e0428533ca'),"
    newprofile = "    '" + profile + "': dict(commit='" + commit + "',manifest='" + newsha + "',helpers=408,source_file_count=" + str(nfiles) + ",upstream_head='" + upstream_head + "'),"
    comp_text = "COMPARISONS = {" + ''.join("\n    '" + n + "': dict(pr=" + str(pr) + ",head='" + h + "',sha256='" + s + "',field='kappa')," for n, pr, h, s in comp_entries)
    choices = "['" + "','".join(n for n, *_ in comp_entries) + "']"
    # Admission control count: assembly_controls emits 37 global controls plus, per provider, 17 + k(k-1) width
    # swap/shift controls over its k width classes + one per spot helper (freeze_spec's own formula). The PR2917
    # adapter pins 119 (five width classes); derive it so a new width class (e.g. width 6) is checked exactly.
    _prov = json.loads((source / 'new/BORROW-PROVIDERS.json').read_bytes())
    _ks = {pid: len(set(_prov[pid]['widths'])) for pid in ('gauge44', 'extra')}
    ADMISSION_CONTROLS = 37 + sum(17 + k * (k - 1) + 4 for k in _ks.values())
    need(ADMISSION_CONTROLS >= 119, 'admission control count')
    adapt('admit_channel408.py', 'admit_extension.py', [
        (oldprofile, newprofile),
        ("COMPARISONS = {", comp_text),
        ("ap.add_argument('--source-profile', choices=['channel408'], default='channel408')", "ap.add_argument('--source-profile', choices=['" + profile + "'], default='" + profile + "')"),
        ("ap.add_argument('--comparison-profile', choices=['pr2894'], default='pr2894')", "ap.add_argument('--comparison-profile', choices=" + choices + ", default='pr2908')"),
        ('zero_buffers_allocated_and_cleared=73', f'zero_buffers_allocated_and_cleared={B}'),
        ("len(c.get('zero_buffers',[]))==73, 'helper408 physical ABI including all 73 private buffers'", f"len(c.get('zero_buffers',[]))=={B}, 'paired extension physical ABI including all {B} private buffers'"),
        ("896*T+expected_helpers+8+73+2, 'complete physical cost including all actual helpers and 73 buffers'", f"896*T+expected_helpers+8+{B}+2, 'complete physical cost including all actual helpers and {B} buffers'"),
        ("\"len(rd(work/'ADMISSION-CONTROLS.json')['rejected_controls'])==119\")", f"\"len(rd(work/'ADMISSION-CONTROLS.json')['rejected_controls'])=={ADMISSION_CONTROLS}\")"),
        ("\"controls=dict(admission=119,", f"\"controls=dict(admission={ADMISSION_CONTROLS},"),
    ])
    adapt('channel_blocknorm.py', 'extension_blocknorm.py', [
        ("len(allocated)==73, 'all73 private zero buffers released'", f"len(allocated)=={B}, 'all{B} private zero buffers released'"),
        ("'zero_buffers_allocated_and_cleared':73", f"'zero_buffers_allocated_and_cleared':{B}"),
        ("r['zero_buffers_returned_to_zero']==73", f"r['zero_buffers_returned_to_zero']=={B}"),
        ('physical==live+8+408+73+2', f'physical==live+8+408+{B}+2'),
        ("'zero_buffers':[live+416,live+489], 'coefficient':[live+489,live+491]", f"'zero_buffers':[live+416,live+{416 + B}], 'coefficient':[live+{416 + B},live+{418 + B}]"),
        ("len(mp)==73 and set(mp.values())==set(range(*ns['zero_buffers'])), '73distinct private Z slots'", f"len(mp)=={B} and set(mp.values())==set(range(*ns['zero_buffers'])), '{B}distinct private Z slots'"),
        ('T=len(order)//9; live=896*T; physical=live+490', f'T=len(order)//9; live=896*T; physical=live+{418 + B}'),
    ])
    # The native address dimension and symplectic stock factor are deliberately retained (as in PR2917).
    b = (out / 'extension_blocknorm.py').read_text(); a = (out / 'admit_extension.py').read_text()
    need("require(d['m']==73" in b and 'Sp(72,2)' in b and 'range(1,37)' in b, 'retained native dimension and symplectic group')
    need('assert m==73' in a, 'retained outer dimension')
    receipt = {'status': f'PASS_CHECKED_{B}_BUFFER_ADAPTER_DERIVATION_R13', 'parent_head': PARENT_HEAD, 'parent_manifest_sha256': PARENT_MANIFEST,
               'source_commit': commit, 'source_profile': profile, 'upstream_head': upstream_head, 'source_manifest_sha256': newsha, 'source_files': nfiles,
               'comparisons': {n: dict(pr=pr, head=h, sha256=s) for n, pr, h, s in comp_entries}, 'retained_receipt_sha256': retained_sha,
               'buffer_count': B, 'physical_overhead': 418 + B, 'width_classes': _ks, 'admission_controls': ADMISSION_CONTROLS, 'changes': changes}
    (out / 'ADAPTER-DERIVATION.json').write_text(json.dumps(receipt, indent=2) + '\n'); return receipt

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--parent-package', type=Path, required=True); ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--retained-receipt', type=Path, required=True); ap.add_argument('--out', type=Path, required=True); ap.add_argument('--buffers', type=int, required=True)
    ap.add_argument('--source-commit', required=True); ap.add_argument('--source-profile', required=True); ap.add_argument('--upstream-head', required=True)
    ap.add_argument('--comparison', action='append', default=[], help='name=path/to/CLAIM.json (pr2917=...)'); a = ap.parse_args()
    claims = [tuple(c.split('=', 1)) for c in a.comparison]
    r = derive(a.parent_package.resolve(), a.source.resolve(), a.out.resolve(), sha(a.retained_receipt.read_bytes()), a.buffers, a.source_commit, a.source_profile, a.upstream_head, claims)
    # Source-bound endpoint precision refinement; keep every generated predicate and check.
    precision_edits = json.loads((Path(__file__).resolve().parents[1] / 'PRECISION-EDITS.json').read_text())
    adapter = a.out.resolve() / 'admit_extension.py'
    adapter_body = adapter.read_text()
    applied = []
    for edit in precision_edits:
        old, new = edit['old'], edit['new']
        need(adapter_body.count(old) == 1, 'exact precision preimage: ' + old[:120])
        adapter_body = adapter_body.replace(old, new)
        applied.append({'old': old, 'new': new})
    adapter.write_text(adapter_body)
    r['changes']['admit_extension.py']['after_sha256'] = sha(adapter.read_bytes())
    r['changes']['admit_extension.py']['replacements'].extend(applied)
    r['precision_refinement'] = {'endpoint_digits': 40, 'edits_sha256': sha((Path(__file__).resolve().parents[1] / 'PRECISION-EDITS.json').read_bytes())}
    (a.out.resolve() / 'ADAPTER-DERIVATION.json').write_text(json.dumps(r, indent=2) + '\n')
    print(r['status'], r['source_manifest_sha256'], r['source_files'], {k: v['after_sha256'][:16] for k, v in r['changes'].items()})
