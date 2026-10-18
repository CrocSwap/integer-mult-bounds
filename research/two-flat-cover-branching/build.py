"""Source-bound adapter: frozen s4z remains byte-for-byte unchanged."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent

def once(s,old,new):
    if s.count(old)!=1:
        raise ValueError('source adapter anchor absent or ambiguous: '+old[:60])
    return s.replace(old,new)

def source(fast=False,kernel=False,trace=False):
    s=(ROOT/'vendor/s4z.c').read_text()
    if fast:
        a=s.index('int opts4c(');b=s.index('\nint opts4(',a)
        s=s[:a]+(ROOT/'cover.c.inc').read_text()+s[b:]
        s=once(s,'  // prune dominated','  if(FREES==0) return no;\n  // prune dominated')
    if kernel:
        return s[:s.index('int main(')]+(ROOT/'harness.c.inc').read_text()
    if trace:
        anchor='int opts4c(u128 D,int c,int d,int stopfirst,int no0){'
        code='\n  if(getenv("TRACE")){static FILE *f=NULL;if(!f)f=fopen(getenv("TRACE"),"w");if(!f)exit(3);fprintf(f,"%016llx%016llx %d %d\\n",(u64)(D>>64),(u64)D,c,d);}'
        s=once(s,anchor,anchor+code)

    # Only the no-free-line four-flat model is certified by this adapter.
    s=once(s,'int main(int argc,char**argv){','int main(int argc,char**argv){\n  if(argc!=10 || getenv("FREES")){fprintf(stderr,"requires 9 arguments and no FREES override\\n");return 2;}')
    s='#include <time.h>\n'+s
    s=once(s,'      int tot=0;','      clock_t pair_start=clock();\n      int tot=0;')
    s=once(s,'      if(getenv("DBG"))',(ROOT/'export.c.inc').read_text()+'      clock_t closure_start=clock();\n      if(getenv("DBG"))')
    s=once(s,'      free(hs.k); free(W); free(gk);','      fprintf(stderr,"TIMING rep %d j %d options %.6f closure %.6f nw %d\\n",ri,j,(double)(closure_start-pair_start)/CLOCKS_PER_SEC,(double)(clock()-closure_start)/CLOCKS_PER_SEC,nw);\n      free(hs.k); free(W); free(gk);')
    return s

def compile_c(text,path,flags=()):
    path=Path(path);path.with_suffix('.c').write_text(text)
    subprocess.run(['cc','-std=gnu11','-O2',*flags,'-o',str(path),str(path.with_suffix('.c'))],check=True,capture_output=True,text=True)
    return path
