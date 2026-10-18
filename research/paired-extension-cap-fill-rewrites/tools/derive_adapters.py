#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generalized PR2917 adapter derivation (Marius-Paul Dumitrean, Claude Code assisted; PR2917/PR2908 derivations by Mason Hale and Jeremy Diviney): PR2908's exact tools -> closed-profile adapters for an
arbitrary derived overlay, buffer count B, source profile and comparator set. With B=82, commit
'paired-helper-extension-pr2908', profile 'paired-extension' and comparisons=pr2908 the output is byte-identical to
PR2917's tools/derive_adapters.py output (checked against its evidence/ADAPTER-DERIVATION.json), except the retained
receipt binding, which is always sha256(--retained-receipt).
usage: derive_adapters_r13.py --parent-package PR2908_PKG --source OVERLAY --retained-receipt FILE --out DIR
       --buffers B --source-commit NAME --source-profile NAME --upstream-head HEX
       [--comparison pr2917=/path/CLAIM.json ...]   (pr2908 is always derived from the parent package's CLAIM.json)
"""
from pathlib import Path
import argparse, gzip, hashlib, json, sys
PARENT_HEAD = '51309592971e3b5be935599eed2a95404dc7781e'
PARENT_MANIFEST = '9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f'
OLD_SOURCE = '56cf455752722051d598a7da1e5ee700637fbaef09189f534413dbe6e0525a83'
OLD_RETAINED = 'dd36443f2789ffa6deca7210c76ada781e2b9b7e622a546b366f51a475faff3e'
HEADS = {'pr2908': PARENT_HEAD, 'pr2917': '224bd5e56041c40078ff6b5fa7393733a215de5c'}
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
        need(name in HEADS, 'known comparator head ' + name)
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
    adapt('admit_channel408.py', 'admit_extension.py', [
        (oldprofile, newprofile),
        ("COMPARISONS = {", comp_text),
        ("ap.add_argument('--source-profile', choices=['channel408'], default='channel408')", "ap.add_argument('--source-profile', choices=['" + profile + "'], default='" + profile + "')"),
        ("ap.add_argument('--comparison-profile', choices=['pr2894'], default='pr2894')", "ap.add_argument('--comparison-profile', choices=" + choices + ", default='pr2908')"),
        ('zero_buffers_allocated_and_cleared=73', f'zero_buffers_allocated_and_cleared={B}'),
        ("len(c.get('zero_buffers',[]))==73, 'helper408 physical ABI including all 73 private buffers'", f"len(c.get('zero_buffers',[]))=={B}, 'paired extension physical ABI including all {B} private buffers'"),
        ("896*T+expected_helpers+8+73+2, 'complete physical cost including all actual helpers and 73 buffers'", f"896*T+expected_helpers+8+{B}+2, 'complete physical cost including all actual helpers and {B} buffers'"),
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
               'buffer_count': B, 'physical_overhead': 418 + B, 'changes': changes}
    (out / 'ADAPTER-DERIVATION.json').write_text(json.dumps(receipt, indent=2) + '\n'); return receipt

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--parent-package', type=Path, required=True); ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--retained-receipt', type=Path, required=True); ap.add_argument('--out', type=Path, required=True); ap.add_argument('--buffers', type=int, required=True)
    ap.add_argument('--source-commit', required=True); ap.add_argument('--source-profile', required=True); ap.add_argument('--upstream-head', required=True)
    ap.add_argument('--comparison', action='append', default=[], help='name=path/to/CLAIM.json (pr2917=...)'); a = ap.parse_args()
    claims = [tuple(c.split('=', 1)) for c in a.comparison]
    r = derive(a.parent_package.resolve(), a.source.resolve(), a.out.resolve(), sha(a.retained_receipt.read_bytes()), a.buffers, a.source_commit, a.source_profile, a.upstream_head, claims)
    print(r['status'], r['source_manifest_sha256'], r['source_files'], {k: v['after_sha256'][:16] for k, v in r['changes'].items()})
