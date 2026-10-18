#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Charles Bethin; substantial OpenAI Codex assistance.
"""Semantic controls for coverage, credit, and the sharp boundary."""
import copy
from fractions import Fraction as Q
import independent as second
import verify as first


def run(certificate):
    upper,_,count=first.enumerate_bins()
    rejected=[]
    def reject(name,call):
        try:call()
        except (ValueError,KeyError) as error:
            rejected.append(dict(name=name,reason=str(error)))
        else:raise ValueError('accepted negative control: '+name)
    reject('omit legal bin pattern count',lambda:first.certify(upper,count-1))
    changed=dict(upper);changed[32]+=1
    reject('inflate critical signed price',lambda:first.certify(changed,count))
    altered,_,n=first.enumerate_bins(prices=(-1,-20,-8,-2,3))
    reject('change full-width helper price',lambda:first.certify(altered,n))
    reject('all rank48 countermodel omits necessary credit',lambda:first.relaxed_member({0:13731,48:2397},8,upper))
    reject('countermodel violates mass',lambda:first.relaxed_member({0:27460,32:3,48:4793},16,upper))
    reject('countermodel violates bin count',lambda:first.relaxed_member({0:27462,32:3,48:4792},16,upper))
    reject('countermodel uses a fractional count',lambda:first.relaxed_member({0:Q(54923,2),32:3,48:4792},16,upper))
    reject('extend rank-one support to two thirds',lambda:first.need(first.support_bounds(32,800,Q(2,3))[0]>0,'rank32 defeats extended support'))
    reject('extend strict support to b=1',lambda:first.need(first.support_bounds(32,800,Q(1))[0]>0,'rank32 defeats extended support'))
    def tamper(field,value):
        c=copy.deepcopy(certificate);c[field]=value
        return second.check(c)
    bad=copy.deepcopy(certificate['upper']);bad.pop('32')
    reject('omit critical rank from primary table',lambda:tamper('upper',bad))
    bad_credit=copy.deepcopy(certificate['credits']);bad_credit['32']=799
    reject('understate critical credit',lambda:tamper('credits',bad_credit))
    reject('replace exact root bracket',lambda:tamper('root_bracket',['2/3','1']))
    bad_model=copy.deepcopy(certificate['countermodel']);bad_model['idle']['32']=2
    reject('corrupt relaxed competitor',lambda:tamper('countermodel',bad_model))
    # Nontrivial positives: both equality candidates belong to the relaxation.
    first.relaxed_member({0:63500,1:6,48:11086},37,upper)
    first.relaxed_member({0:27461,32:3,48:4792},16,upper)
    first.need(first.support_bounds(32,800,Q(16,25))[0]>0,'lower-side support')
    first.need(first.support_bounds(32,800,Q(13,20))[1]<0,'upper-side failure')
    return dict(status='PASS_T37_SUPPORT_SEMANTIC_CONTROLS',rejected=rejected,
                positive=['T37 belongs to relaxation','T16 competitor belongs to relaxation','critical rank supports at 16/25','critical rank defeats support at 13/20'])
