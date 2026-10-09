#!/usr/bin/env python3
"""Exact-certificate exporter; random scalar sampling deliberately omitted.

This adapter preserves the original matching, scalar operations, integer
adjoint, exact clean-support replay, every F2 incidence check and full rank
accounting. It replaces two costly random scalar evaluations with a required
separate all-input certificate (verify_deferred_word.py). An exported profile
alone is not acceptance. The original sampled exporter is preserved unchanged.
"""
from pathlib import Path
import sys


def main():
    original=Path(__file__).with_name('defer_complex_graph.py')
    text=original.read_text()
    def once(old,new):
        nonlocal text
        assert text.count(old)==1,old
        text=text.replace(old,new)
    once("choices=('ascending', 'reversed')","choices=('ascending', 'reversed', 'numeric')")
    once("    # Use exact integer adjoint coordinates with common denominator42.",
         "    if a.order == 'numeric':\n"
         "        new = once(new, 'key=lambda i: ((i ^ 1) in (a, b), i)', 'key=lambda i: i')\n"
         "    # Use exact integer adjoint coordinates with common denominator42.")
    once("    marker = \"    (HERE / 'complex-profile.json').write_text\"",
         "    new = once(new, '    rep = [replay(seed) for seed in (1, 2)]',\n"
         "               '    # Random scalar sampling omitted; separate exact all-input audit REQUIRED.')\n"
         "    new = once(new, \"    require(all(r == (True, True) for r in rep), 'replay %s' % rep)\",\n"
         "               \"    print('Exact-only export: random dirty scalar replay not run', flush=True)\")\n"
         "    new = once(new, \"replay=dict(seeds=[1, 2], scratch_restored=True, y_plus_x=True, field='Z/(2^61-1)')\",\n"
         "               \"replay=dict(random_tests_run=False, exact_all_input_audit_required=True)\")\n"
         "    marker = \"    (HERE / 'complex-profile.json').write_text\"")
    # Keep the base adapter and this wrapper in the generated source closure.
    once("    paths = [source, case/'graph.bin', case/'graph.labels', case/'matched.json', Path(__file__)]",
         "    (out/'base-adapter-source.py').write_bytes(Path(__file__).with_name('defer_complex_graph.py').read_bytes())\n"
         "    paths = [source, case/'graph.bin', case/'graph.labels', case/'matched.json', Path(__file__), Path(__file__).with_name('defer_complex_graph.py')]")
    namespace={'__file__':str(Path(__file__).resolve()),'__name__':'exact_only_adapter'}
    exec(compile(text,str(original),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
