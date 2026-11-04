#!/usr/bin/env python3
"""Static lexical preservation check, not an elaborated-type or kernel audit."""
import argparse, hashlib, json, re, subprocess, unicodedata
from pathlib import Path
BASE = 'c4b1560a569f54064608bf88440f9e492c03fba3'
DIRS = ['lean-multi-host-source', 'lean-whole-residual-hosting',
        'lean-multi-host-framework', 'lean-source-invocation-audit',
        'lean-single-stream-obstruction']

def sha(s): return hashlib.sha256(s.encode() if isinstance(s,str) else s).hexdigest()

def clean(s):
    out=[]; i=0; depth=0; quoted=False
    while i<len(s):
        if quoted:
            out.append(s[i])
            if s[i]=='\\' and i+1<len(s):out.append(s[i+1]);i+=2;continue
            if s[i]=='"':quoted=False
            i+=1;continue
        if depth:
            if s.startswith('/-',i):depth+=1;out.extend('  ');i+=2
            elif s.startswith('-/',i):depth-=1;out.extend('  ');i+=2
            else:out.append('\n' if s[i]=='\n' else ' ');i+=1
            continue
        if s.startswith('/-',i):depth=1;out.extend('  ');i+=2;continue
        if s.startswith('--',i):
            j=s.find('\n',i);j=len(s) if j<0 else j;out.extend(' '*(j-i));i=j;continue
        if s[i]=='"':quoted=True
        out.append(s[i]);i+=1
    assert depth==0 and not quoted,'Unclosed comment or string'
    return ''.join(out)

def ident(c):return c=='_' or c=="'" or c.isalnum() or unicodedata.category(c) in ('Lm','Nl','Mn','Mc')
def tokens(s):
    result=[];i=0
    while i<len(s):
        if s[i].isspace():i+=1;continue
        j=i+1
        if s[i]=='"':
            while j<len(s):
                if s[j]=='\\':j+=2;continue
                if s[j]=='"':j+=1;break
                j+=1
        elif s[i]=='«':
            j=s.index('»',i)+1
        elif ident(s[i]):
            while j<len(s) and ident(s[j]):j+=1
        result.append(s[i:j]);i=j
    return result

THM=re.compile(r'^(?:@\[[^\n]*?\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma)\s+([^\s(:{\[]+)')
COMMAND=re.compile(r'^(?:@\[[^\n]*?\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma|def|abbrev|structure|inductive|instance|namespace|section|end|variable|universe|open|include|omit|set_option|attribute|#|import)\b')

def header_end(s,start):
    stack=[];quoted=False;i=start
    pairs={')':'(',']':'[','}':'{','⟩':'⟨'}
    while i<len(s):
        c=s[i]
        if quoted:
            if c=='\\':i+=2;continue
            if c=='"':quoted=False
            i+=1;continue
        if c=='"':quoted=True
        elif c in '([{⟨':stack.append(c)
        elif c in ')]}⟩':
            assert stack and stack.pop()==pairs[c], 'Unbalanced declaration header'
        elif not stack and s.startswith(':=',i):return i
        i+=1
    raise AssertionError('Theorem has no explicit := body separator')

def declarations(raw,path):
    s=clean(raw);lines=s.splitlines(keepends=True);offsets=[];off=0
    for line in lines:offsets.append(off);off+=len(line)
    scopes=[]; contexts=[];output={};open_commands=[]
    for number,line in enumerate(lines):
        scope=re.match(r'^(namespace|section)(?:\s+(\S+))?\s*$',line.strip('\n'))
        end=re.match(r'^end(?:\s+(\S+))?\s*$',line.strip('\n'))
        if scope:
            scopes.append((scope[1],scope[2]));contexts.append([]);continue
        if end:
            assert scopes,(path,number,'unexpected end')
            kind,name=scopes.pop();contexts.pop()
            assert end[1] is None or end[1]==name,(path,number,'mismatched end')
            continue
        context=re.match(r'^(variable|universe|include|omit)\b',line)
        if context:
            finish=number+1
            while finish<len(lines) and not COMMAND.match(lines[finish]) and not lines[finish].startswith('#'):
                finish+=1
            ctx=tokens(''.join(lines[number:finish]))
            if contexts:contexts[-1].append(ctx)
            else:open_commands.append(ctx)
        thm=THM.match(line)
        if not thm:continue
        name='.'.join([name for kind,name in scopes if kind=='namespace']+[thm[1]])
        start=offsets[number];stop=header_end(s,start)
        statement=tokens(s[start:stop])
        context_tokens=open_commands+[x for scope_context in contexts for x in scope_context]
        record={'path':path,'line':number+1,'headerTokens':statement,'contextTokens':context_tokens}
        assert name not in output,(path,name,'duplicate')
        output[name]=record
    assert not scopes,(path,'unclosed namespace')
    # Catch unsupported theorem spelling/layout rather than silently skipping it.
    textual=len(re.findall(r'^\s*(?:@\[[^\n]*?\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma)\s+',s,re.M))
    assert textual==len(output),(path,'unparsed theorem declarations',textual,len(output))
    return output

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();repo=a.repo.resolve()
    def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
    originals=[x for x in git('ls-tree','-r','--name-only',BASE,'--',*['research/'+d for d in DIRS]).decode().splitlines() if x.endswith('.lean')]
    archives=[x for x in originals if '/review-receipts/' in x];contribution=[x for x in originals if x not in archives]
    assert len(contribution)==66 and len(archives)==9
    current=[str(p.relative_to(repo)) for d in DIRS for p in sorted((repo/'research'/d).glob('*.lean'))]
    before={};after={};baseline_hashes={};current_hashes={}
    for paths,dest,old in [(contribution,before,True),(current,after,False)]:
        for path in paths:
            blob=git('show',BASE+':'+path) if old else (repo/path).read_bytes()
            (baseline_hashes if old else current_hashes)[path]=sha(blob)
            entries=declarations(blob.decode(),path)
            assert not set(entries)&set(dest),(path,'duplicate qualified theorem names')
            dest.update(entries)
    missing=sorted(set(before)-set(after)); added=sorted(set(after)-set(before));changed=[];moved=[]
    for name in sorted(set(before)&set(after)):
        l,r=before[name],after[name]
        if l['headerTokens']!=r['headerTokens'] or l['contextTokens']!=r['contextTokens']:
            changed.append({'name':name,'baseline':l,'current':r})
        if l['path']!=r['path']:moved.append({'name':name,'from':l['path'],'to':r['path']})
    archive_records=[]
    for path in archives:
        old=git('show',BASE+':'+path);new=(repo/path).read_bytes()
        archive_records.append({'path':path,'baselineSha256':sha(old),'currentSha256':sha(new),'identical':old==new})
    result={'status':'PASS' if not missing and not changed and all(x['identical'] for x in archive_records) else 'FAIL',
        'baselineCommit':BASE,'checkoutCommit':git('rev-parse','HEAD').decode().strip(),
        'scriptSha256':sha(Path(__file__).read_bytes()),'originalContributionFiles':len(contribution),
        'currentTopLevelLeanFiles':len(current),'originalNamedTheorems':len(before),'currentNamedTheorems':len(after),
        'missingTheorems':missing,'addedTheorems':added,'changedHeadersOrContexts':changed,
        'movedTheorems':moved,'archives':archive_records,'baselineSourceSha256':baseline_hashes,'currentSourceSha256':current_hashes,
        'method':'Qualified names, lexical theorem/lemma headers up to top-level :=, and active variable/universe/include/omit context tokens; nested comments stripped; namespace moves tracked.',
        'limitations':'Static source check, not elaborated-type equality. Implicit name resolution, notation/instance changes, imported definitions, and altered defining bodies require separate source review and Lean verification. No Lean compiler was run.'}
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','originalContributionFiles','currentTopLevelLeanFiles','originalNamedTheorems','currentNamedTheorems','missingTheorems','addedTheorems']}))
    print('Changed headers/contexts:',len(changed),'Moved:',len(moved),'Archives unchanged:',sum(r['identical'] for r in archive_records))
    if changed:print('Changed names:',[r['name'] for r in changed])
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
