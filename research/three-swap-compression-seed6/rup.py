#!/usr/bin/env python3
"""Standard-library reverse-unit-propagation proof checker.
Each added clause must follow by unit propagation under its negation.
Deletion records are safely ignored: retained validated clauses remain consequences.
Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict

class Database:
    def __init__(self,variables,clauses):
        self.variables=variables;self.clauses=[];self.watches=defaultdict(list);self.units=[];self.empty=False
        for clause in clauses:self.add(clause)
    def add(self,clause):
        if any(not isinstance(x,int) or x==0 or abs(x)>self.variables for x in clause):raise ValueError('invalid literal')
        clause=list(dict.fromkeys(clause))
        if not clause:self.empty=True;return
        if len(clause)==1:self.units.append(clause[0]);return
        index=len(self.clauses);self.clauses.append(clause)
        self.watches[clause[0]].append(index);self.watches[clause[1]].append(index)
    def conflict(self,assumptions):
        if self.empty:return True
        values=[0]*(self.variables+1);queue=[]
        def assign(literal):
            index=abs(literal);value=1 if literal>0 else -1
            if values[index]==-value:return False
            if values[index]==0:values[index]=value;queue.append(literal)
            return True
        def evaluate(literal):return values[abs(literal)]*(1 if literal>0 else -1)
        for literal in [*self.units,*assumptions]:
            if not assign(literal):return True
        processed=0
        while processed<len(queue):
            false=-queue[processed];processed+=1;watching=self.watches[false];position=0
            while position<len(watching):
                index=watching[position];clause=self.clauses[index]
                if clause[0]==false:clause[0],clause[1]=clause[1],clause[0]
                if clause[1]!=false:raise RuntimeError('corrupt watch invariant')
                other=clause[0]
                if evaluate(other)>0:position+=1;continue
                replacement=next((i for i in range(2,len(clause)) if evaluate(clause[i])>=0),None)
                if replacement is not None:
                    clause[1],clause[replacement]=clause[replacement],clause[1]
                    watching[position]=watching[-1];watching.pop();self.watches[clause[1]].append(index)
                    continue
                if evaluate(other)<0 or not assign(other):return True
                position+=1
        return False

def check_proof(variables,clauses,proof):
    database=Database(variables,clauses);additions=deletions=0;closed=False
    for line in proof:
        tokens=line.split()
        if not tokens:raise ValueError('empty proof record')
        deletion=tokens[0]=='d'
        if deletion:tokens=tokens[1:]
        literals=[int(x) for x in tokens]
        if not literals or literals[-1]!=0 or 0 in literals[:-1]:raise ValueError('invalid proof terminator')
        clause=literals[:-1]
        if any(abs(x)>variables for x in clause):raise ValueError('proof variable outside CNF')
        if deletion:deletions+=1;continue
        if not database.conflict([-x for x in clause]):raise ValueError('non-RUP proof addition')
        database.add(clause);additions+=1
        if not clause:closed=True
    if not closed:raise ValueError('proof never derives empty clause')
    return {'rup_additions':additions,'ignored_deletions':deletions}

def slow_conflict(clauses,assumptions):
    values={}
    for literal in assumptions:
        if -literal in values:return True
        values[literal]=True
    changed=True
    while changed:
        changed=False
        for clause in clauses:
            if any(x in values for x in clause):continue
            available=[x for x in clause if -x not in values]
            if not available:return True
            if len(available)==1:
                x=available[0]
                if x not in values:values[x]=True;changed=True
    return False
