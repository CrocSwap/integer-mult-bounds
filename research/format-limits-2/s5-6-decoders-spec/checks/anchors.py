"""Citation anchors for the ARGUED rows S2, S3, S4: every file:line quoted in README.part.md is checked to contain the quoted text.
Spec files of main (base commit 66849e1) are vendored unchanged under inputs/main/ and pinned by git blob id in SOURCES.json;
verifier files are the vendored copies in inputs/.  This checks that the citations are true, not that the arguments built on them are."""
import hashlib, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(ROOT, "inputs", "main")
fails = 0
def ok(tag, cond, info=""):
    global fails
    print(("PASS " if cond else "FAIL ") + tag + (" | " + info if info else ""), flush=True)
    fails += (not cond)
# the main files' pins (git blob ids) are checked by scripts/provenance.py (step 0); here only that they are present
for p in ("upstream/build/sections/03-motifs.tex", "upstream/build/sections/04-swap.tex", "notes/general-clifford-frames.tex"):
    ok("anchors.present." + os.path.basename(p), os.path.isfile(os.path.join(REPO, p)))
SW, MO, GC = "upstream/build/sections/04-swap.tex", "upstream/build/sections/03-motifs.tex", "notes/general-clifford-frames.tex"
CF, HL = "inputs/pr622/coupled_frames_base.py", "inputs/pr626/hpe_audit_local.py"
A = [  # (tag, file, first line, last line, text)
 ("S2.endpoint-operator-on-every-role", SW, 183, 187, "every original row"),
 ("S2.contract-M_out(rho w)-M_in(w)=I", SW, 117, 121, "M_{\\mathrm{out}(\\rho(w))}-M_{\\mathrm{in}(w)}=I_m"),
 ("S2.rho-is-a-permutation", SW, 105, 109, "permutation $\\rho$"),
 ("S2.calls-equal-sum-of-edge-ranks", SW, 197, 199, "sum of the edge ranks, exactly $s$"),
 ("S2.motif-source-is--P_U", MO, 469, 473, "source matrix $-P_{U_a}$"),
 ("S2.interface-proof-P_Uperp-minus-source", MO, 519, 525, "P_{U_a^\\perp}-(-P_{U_a})=I_m"),
 ("S2.common-frame-at-each-gate", MO, 154, 159, "use the same $D_v$"),
 ("S3.R2-identical-exact-representative", GC, 61, 65, "one identical exact representative"),
 ("S3.verifier-common-frame-assert", HL, 75, 75, "assert cur[r[1]]==f"),
 ("S4.centre-descent-nested-chain", CF, 144, 148, "center descent not nested"),
 ("S4.centre-descent-billed-per-step", CF, 148, 148, "self.center_profile[len(current) - len(g)] += 1"),
 ("S4.centre-barrier-node", CF, 95, 99, "'barrier'"),
 ("S4.final-hyperplane-for-ports", CF, 100, 108, "'final'"),
 ("S4.monotone-chains", CF, 163, 163, "'nonmonotone'"),
 ("S4.unbilled-cut-transition-refused", CF, 164, 165, "unbilled cut transition"),
]
for tag, f, a, b, txt in A:
    p = os.path.join(REPO, f) if f.startswith(("upstream", "notes")) else os.path.join(ROOT, f)
    lines = open(p, encoding="utf-8").read().split("\n")[a - 1:b] if os.path.exists(p) else []
    ok("anchors." + tag, txt in "\n".join(lines), "%s:%d-%d" % (os.path.basename(f), a, b))
f = open(os.path.join(ROOT, CF)).read().split("\n")
ok("anchors.S4.final-port-hyperplane-code", any("word['ports']" in l for l in f[100:108]) and any("not (x & port).bit_count() % 2" in l for l in f[100:108]))
raise SystemExit(1 if fails else 0)
