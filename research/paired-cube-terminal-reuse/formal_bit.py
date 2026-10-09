#!/usr/bin/env python3
"""Bind the PR165/169 all-column verifier to a checked merged, aliased bit word.

The inherited formal replay is by Chafik Boukhalfa / GamingPuzzled, with
their disclosed OpenAI Codex / Anthropic Claude assistance, Apache-2.0.
This adapter is by huxint with substantial OpenAI Codex assistance.
"""
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'research/paired-cube-bit-descent-168/word.py'
spec=importlib.util.spec_from_file_location('inherited_bit_columns',SOURCE)
inherited=importlib.util.module_from_spec(spec)
spec.loader.exec_module(inherited)


class AliasedFormal(inherited.Candidate):
    def __init__(self,experiment):
        experiment.check()
        e=experiment;c=e.c
        self.h,self.v,self.R=e.h,e.v,e.R
        self.w,self.g,self.k=c.w,c.g,c.k
        self.ops=c.w['ops']
        self.source=e.sources
        self.gauge=e.gauges
        self.order=[z['role'] for z in reversed(self.w['gauges'])]
        self.phase1=sorted(self.w['phase1'])
        phase=set(self.phase1)
        self.rest=[i for i in range(len(self.ops)) if i not in phase]
        position={i:j for j,i in enumerate(self.rest)}
        self.donor=dict(e.merge)
        self.pairs=[[b,a] for a,b,t in e.pairs]
        self.phys={s:self.donor.get(s,s) for s in range(self.R)}
        self.readtime={s:(position[e.deadline[s]] if s in e.merge else 0) for s in self.gauge}
        inherited.need(len(set(self.phys.values()))==self.R-len(self.pairs),'independent physical formal coordinates')
        inherited.need(all(self.phys[a]!=self.phys[b] for a,b,_ in self.ops),'formal aliased gate ports')


def certify(experiment):
    formal=AliasedFormal(experiment)
    columns=[formal.formal(ring) for ring in (2,0)]
    controls=[]
    for mutation in ('omit_compensation','missing_partner','stale'):
        if mutation=='stale' and not formal.pairs:continue
        try:formal.formal(2,mutation)
        except ValueError:controls.append(mutation)
        else:raise ValueError('Formal bit mutation accepted: '+mutation)
    return dict(columns=columns,controls=controls,
                all_source_target_and_dirty_columns=True,
                integer_decoder_checked_before_mod_two=True,
                actual_compensated_birth_schedule=True)
