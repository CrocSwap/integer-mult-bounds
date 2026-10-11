"""Build the kernel word from an explicit selection (PR #443's replica kernel, unchanged, 32 replicas) plus the residual isometries,
with PR #436's retiming before and after and PR #443's exact replay and interface checks.  The selection comes from select_kernel.py
(or any file of [[entrance lines], pivot, [donors]]); kernel_rebuild.py in e8-r715-eleven-stage-whole is the same build with PR #443's greedy
search in place of the file.
usage: kernel_from_selection.py REPO_RESEARCH_DIR WORD_IN SELECTION.json OUT_WORD OUT_ISOMETRIES
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kernel_cap as KC
R, wp, selp, out, out_iso = sys.argv[1:6]
U = KC.setup(R); w, ret, mv1 = KC.primitive_retimed(U, wp); G = KC.Geo(U, ret)
sel = json.load(open(selp)); chk = KC.check_selection(G, sel)
ctl = KC.controls(G, sel) if all(len(e[0]) == 1 for e in sel) else []
kw, iso, info = KC.build_kernel(U, ret, sel)
hist = KC.width_rule_check(U, kw, sel)
U.save_word(kw, out); json.dump(iso, open(out_iso, 'w'))
print(json.dumps(dict(info, pre_retime_moves=mv1, selection=chk, helper_widths=hist, controls_rejected=ctl, output_sha256=U.content_sha(kw), input_sha256=U.content_sha(w)), sort_keys=True))
