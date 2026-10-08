#!/usr/bin/env python3
"""Alternative retained-total/compact patch against the pinned source."""
from pathlib import Path
import difflib

ROOT = Path(__file__).resolve().parents[1]
from make_compact_control_patch import patched_files as compact_files
from make_patch import replace_once
from retained_complex import certificate


def patched_files():
    certificate()
    retained = (ROOT / "notes/retained-complex-construction.tex").read_text()
    for name,old,new in compact_files():
        if name.endswith(("main.tex","00-introduction.tex")):
            new=replace_once(new,r"\kappa=83/10^{12}",r"\kappa=591/10^{12}")
            if name.endswith('main.tex'):
                new = new.replace('Douglas Colkitt (modifications)',
                                  'Douglas Colkitt and dleen (modifications)')
                new = new.replace(r'\small Compact-control modifications: Douglas Colkitt}',
                    r'\small Compact-control modifications: Douglas Colkitt\\'+'\n'+
                    r'\small Retained-total extension: dleen}')
                new = new.replace('and retained project refinements, prepared with assistance from OpenAI Codex.',
                    "and retained project refinements, together with dleen's retained-total\n"
                    'complex extension, prepared with assistance from OpenAI Codex.')
        elif name.endswith("03-motifs.tex"):
            new += "\n"+retained
        elif name.endswith("05-layers.tex"):
            new=new.replace("prop:compact-complex-interface","prop:retained-tree-complex-interface")
            replacements=((r"m=m_{\rm c}=15625",r"m=m_{\rm c}=13824"),
                          (r"W=W_{\rm c}=58645352620000",r"W=W_{\rm c}=3013310215168"),
                          (r"s=s_{\rm c}=916333630984500000",r"s=s_{\rm c}=41655997423981952"),
                          (r"\sigma=1-418/10^{12}",r"\sigma=1-750/10^{11}"))
            for before, after in replacements:
                new = replace_once(new, before, after)
        elif name.endswith("08-assembly.tex"):
            replacements=((r"a_{\rm c}=418/10^{12}",r"a_{\rm c}=750/10^{11}"),
                (r"\chi=\tau+(1-\beta)(\sigma-\tau)",r"\chi=\tau+(1-\beta)\max\{\sigma-\tau,0\}"),
                (r"c=\frac15",r"c=1"),
                (r"\lambda=1-\frac{1671}{4\cdot10^{12}}",r"\lambda=1-\frac{2959}{10^{12}}"),
                (r"\lambda'=1-\frac{167}{4\cdot10^{11}}",r"\lambda'=1-\frac{2958}{10^{12}}"),
                (r"\kappa=\frac{83}{10^{12}}>2^{-34}",r"\kappa=\frac{591}{10^{12}}>2^{-31}"),
                (r"\frac{333833}{4\cdot10^{15}}>\frac{83}{10^{12}}",r"\frac{2956521}{5\cdot10^{15}}>\frac{591}{10^{12}}"),
                (r"K=\Theta(p^{1999/50000})",r"K=\Theta(p^{1999/10000})"))
            for before, after in replacements:
                new = replace_once(new, before, after)
        yield name,old,"% Retained-total compact-control alternative, October 7, 2026.\n"+new


def patch_text():
    return "".join(
        "".join(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=f"a/{name}", tofile=f"b/{name}"))
        for name, old, new in patched_files())


if __name__ == "__main__":
    (ROOT/"patches/retained-complex-31.patch").write_text(patch_text())
    print("PASS pinned-source retained-total alternative; kappa=591/10^12")
