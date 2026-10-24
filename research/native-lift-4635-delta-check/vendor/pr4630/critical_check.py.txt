"""Exact p16 critical majorant and finite native-provider absorption replay.
Apache-2.0; Dugongue with substantial OpenAI Codex assistance.
Credits: Dillon's retained critical engine, zxv/Sussman/compiler lineage.
"""
from pathlib import Path
from fractions import Fraction as F
import json

HERE=Path(__file__).resolve().parent


def need(ok,why):
    if not ok:raise ValueError(why)


def check():
    path=HERE/'critical_engine.py';E={'__name__':'frozen_critical_engine','__file__':str(path)}
    exec(compile(path.read_bytes(),str(path),'exec'),E)
    profile=json.loads((HERE/'raw-profile.json').read_text())
    benchmarks=json.loads((HERE/'majorant-benchmarks.json').read_text())
    old=next(row['witness'] for row in benchmarks['cases'] if row['name']=='p16')
    witness={key:old[key] for key in ('a','b','height_base','ell0','s','lambda','p','c')}
    witness['guards']={key:old['guards'][key] for key in ('U','V','Q','d','beta')}
    witness['upper_exponent']='.997067'
    lo,hi=F('.9969798340229'),F('.9969798340230')
    root=E['certify'](profile,lo,hi,F('.564'),F(1))
    majorant=E['critical_guards'](profile,lo,hi,witness)
    need(witness['height_base']==1024 and witness['ell0']==650 and F(witness['c'])==133 and F(witness['p'])==F(2,5),'exact retained majorant parameters')
    log=lambda n:tuple(F(x,E['GRID']) for x in E['logarithm'](n))
    need(log(2)[0]>F(2,3) and log(2)[1]<1,'log2 bracket')
    need(log(145)[1]<8,'log145 bracket')
    log_A_upper=F('.003021')*(8+6500)
    need(log_A_upper<20 and 133+10**12<2**40,'normalization/logarithmic overhead below36')
    uniform=F('.0030201656');gap=(1-hi)-uniform;H=10**12
    margin=gap*H*F(2,3)-36
    need(margin==F(646,3) and margin>0,'finite word absorption')
    need(gap-F(2,5)/(133+F(2,3)*H)>0,'all-larger-rank absorption monotonicity')
    rejected=False
    try:E['certify'](profile,lo,hi,F(0),F(1))
    except ValueError:rejected=True
    need(rejected,'unfunded mirror control')
    return dict(status='PASS',critical_root=root,critical_majorant=majorant,
                fixed_rank_encoding='2^1000000000000',fixed_rank_materialized=False,
                native_provider_saving=str(uniform),finite_absorption_log_margin=str(margin),
                unfunded_mirror_rejected=True,
                scope='Exact source critical-majorant arithmetic and finite absorption; all-column algebraic word identity remains a cited mathematical proof, not this replay')


if __name__=='__main__':print(json.dumps(check(),indent=2))
