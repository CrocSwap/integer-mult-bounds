# SPDX-License-Identifier: Apache-2.0
"""Literal transport and omission controls for the #7643 134/329 contact on #7657."""
from copy import deepcopy


def splice(base,plan):
    # The courier contributes a net extra event before role134 returns.
    source_to_courier={41049:41078,41050:41079,41051:41080,41142:41171,42086:42116}
    old={source_to_courier[int(i)]:e for i,e in plan['old_events'].items()}
    new={source_to_courier[int(i)]:e for i,e in plan['proposed_events'].items()}
    tape=base['program']
    assert sorted(old)==sorted(new)==[41078,41079,41080,41171,42116]
    assert all(tape[i]==e for i,e in old.items()) and len(tape)==76673
    assert tape[47995]==['MOVE',46,513,127,False]
    tagged=[(i,new.get(i,e)) for i,e in enumerate(tape) if new.get(i,e) is not None]
    assert len(tagged)==76672 and tagged[47994]==(47995,['MOVE',46,513,127,False])
    return tagged


def faults(word,tagged,prior,checked,audit,native,rejects):
    actual=dict((origin,index) for index,(origin,_) in enumerate(tagged))
    i=actual[41080]
    assert tagged[i][1]==['ADD',134,329,'-1/2',373]
    controls={}
    for name in ('missing_contact_add','wrong_contact_sign','wrong_contact_chart','missing_contact_return'):
        mutant=deepcopy(word)
        mt=list(tagged)
        if name=='missing_contact_return':
            del mutant['program'][actual[41171]]
        elif name=='missing_contact_add':
            del mutant['program'][i]
            del mt[i]
        elif name=='wrong_contact_sign':
            mutant['program'][i][3]='1/2'
            mt[i]=(41080,mutant['program'][i])
        else:
            mutant['program'][i][4]=618
        def check():
            if name in ('wrong_contact_chart','missing_contact_return'):
                native(mutant)
            else:
                observed,_=audit.replay(mutant,mt,checked)
                assert observed==prior
        controls[name]=rejects(check)
    return controls


def courier_versions(base,word,local,audit):
    def scalar_contacts(tagged):
        return {i: e for i,e in tagged if e[0] in ('ADD','COPY','SCALE') and
                {226,990}.intersection(e[1:3] if e[0]!='SCALE' else e[1:2])}
    old=list(enumerate(base['program']))
    contacts=scalar_contacts(old)
    assert list(contacts.items())==list(scalar_contacts(local).items())
    old_trace,_=audit.replay(base,old,set(contacts))
    new_trace,_=audit.replay(word,local,set(contacts))
    assert len(old_trace[1])==len(contacts) and old_trace==new_trace
    return len(contacts)
