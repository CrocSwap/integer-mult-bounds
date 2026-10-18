/* rupc: minimal independent forward RUP checker for text DRAT proofs (KSTAR).
   Usage: rupc F.cnf P.drat
   Every added lemma must be RUP w.r.t. all clauses present (original + earlier lemmas, deletions honoured lazily).
   Top-level implied literals are kept across deletions (sound: every clause ever present is implied by F).
   RAT lemmas are NOT accepted. Prints VERIFIED only if the empty clause is reached (or a top-level conflict arises). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int nvars;
static int *lits; static long nl, capl;             /* literal arena */
static long *cstart; static int *csize; static char *cdel; static long nc, capc;
static long **W; static int *wn, *wc;               /* watches indexed by lit code */
static signed char *val;                            /* per var: 0 unassigned, 1 true, -1 false */
static int *trail; static long tn;
#define CODE(l) ((l)>0 ? 2*(l) : -2*(l)+1)
static int litval(int l){ int v=val[abs(l)]; return l>0? v : -v; }
static void addw(int l,long c){ int k=CODE(l); if(wn[k]==wc[k]){ wc[k]=wc[k]?2*wc[k]:4; W[k]=realloc(W[k],sizeof(long)*wc[k]); } W[k][wn[k]++]=c; }
static void assign(int l){ val[abs(l)]= l>0?1:-1; trail[tn++]=l; }
/* hash table for deletion lookup */
static long *ht; static long hcap;
static uint64_t hclause(const int *a,int n){ uint64_t h=1469598103934665603ULL; uint64_t s=0,x=0; for(int i=0;i<n;i++){ s+= (uint64_t)(a[i]*2654435761u); x^=(uint64_t)a[i]*0x9E3779B97F4A7C15ULL; } h^=s; h*=1099511628211ULL; h^=x; h^=n; return h; }
static void hput(long c){ uint64_t h=hclause(lits+cstart[c],csize[c])%hcap; while(ht[h]>=0) h=(h+1)%hcap; ht[h]=c; }
static int sameset(const int *a,int n,long c){ if(csize[c]!=n) return 0; for(int i=0;i<n;i++){ int f=0; for(int j=0;j<n;j++) if(lits[cstart[c]+j]==a[i]){f=1;break;} if(!f) return 0;} return 1; }
static void hdel(const int *a,int n){ uint64_t h=hclause(a,n)%hcap; while(ht[h]!=-1){ long c=ht[h]; if(c>=0 && !cdel[c] && sameset(a,n,c)){ cdel[c]=1; ht[h]=-2; return; } h=(h+1)%hcap; } }
/* propagate from trail position q; return 1 on conflict */
static int propagate(long q){
  while(q<tn){
    int fl=-trail[q++]; int k=CODE(fl); long *ws=W[k]; int n=wn[k]; int j=0;
    for(int i=0;i<n;i++){
      long c=ws[i]; if(cdel[c]) continue;
      int *cl=lits+cstart[c]; int sz=csize[c];
      if(cl[0]==fl){ cl[0]=cl[1]; cl[1]=fl; }
      if(litval(cl[0])==1){ ws[j++]=c; continue; }
      int found=0;
      for(int m=2;m<sz;m++) if(litval(cl[m])!=-1){ cl[1]=cl[m]; cl[m]=fl; addw(cl[1],c); found=1; break; }
      if(found) continue;
      ws[j++]=c;
      if(litval(cl[0])==-1){ for(i++;i<n;i++) ws[j++]=ws[i]; wn[k]=j; return 1; }
      assign(cl[0]);
    }
    wn[k]=j;
  }
  return 0;
}
static int topconflict=0;
static long addclause(const int *a,int n){
  if(nc==capc){ capc=capc?2*capc:1<<20; cstart=realloc(cstart,sizeof(long)*capc); csize=realloc(csize,sizeof(int)*capc); cdel=realloc(cdel,capc); }
  while(nl+n>capl){ capl=capl?2*capl:1<<24; lits=realloc(lits,sizeof(int)*capl); }
  long c=nc++; cstart[c]=nl; csize[c]=n; cdel[c]=0; memcpy(lits+nl,a,sizeof(int)*n); nl+=n;
  if(nc*2>hcap*1){ /* rehash */ long old=hcap; hcap=hcap?4*hcap:1<<22; free(ht); ht=malloc(sizeof(long)*hcap); for(long i=0;i<hcap;i++) ht[i]=-1; for(long d=0;d<c;d++) if(!cdel[d]) hput(d); (void)old; }
  hput(c);
  if(topconflict) return c;
  int *cl=lits+cstart[c];
  /* move non-false literals to the front */
  int k=0; for(int i=0;i<n;i++) if(litval(cl[i])!=-1){ int t=cl[k]; cl[k]=cl[i]; cl[i]=t; k++; }
  for(int i=0;i<n;i++) if(litval(cl[i])==1) return c;  /* satisfied at top level: watch anyway below */
  if(n==0 || k==0){ topconflict=1; return c; }
  if(k==1){ if(n>=2){ addw(cl[0],c); addw(cl[1],c);} assign(cl[0]); if(propagate(tn-1)) topconflict=1; return c; }
  addw(cl[0],c); addw(cl[1],c); return c;
}
static int *buf; static int bcap;
static int readclause(FILE *f,int *isdel,int *n){
  int c,l; *n=0; *isdel=0;
  for(;;){ c=fgetc(f); if(c==EOF) return 0; if(c=='c'||c=='p'){ while((c=fgetc(f))!='\n'&&c!=EOF); continue; } if(c=='d'){ *isdel=1; break; } if(c=='-'||(c>='0'&&c<='9')){ ungetc(c,f); break; } }
  for(;;){ if(fscanf(f,"%d",&l)!=1) return 0; if(l==0) return 1; if(*n==bcap){ bcap=bcap?2*bcap:64; buf=realloc(buf,sizeof(int)*bcap);} buf[(*n)++]=l; if(abs(l)>nvars){ fprintf(stderr,"var out of range\n"); exit(3);} }
}
int main(int argc,char **argv){
  FILE *f=fopen(argv[1],"r"); char line[256]; long ncl;
  while(fgets(line,256,f)) if(line[0]=='p'){ sscanf(line,"p cnf %d %ld",&nvars,&ncl); break; }
  val=calloc(nvars+1,1); trail=malloc(sizeof(int)*(nvars+1)); W=calloc(2*nvars+2,sizeof(long*)); wn=calloc(2*nvars+2,sizeof(int)); wc=calloc(2*nvars+2,sizeof(int));
  int isdel,n; long cnt=0;
  while(readclause(f,&isdel,&n)){ addclause(buf,n); cnt++; }
  fclose(f); fprintf(stderr,"read %ld clauses, top-level trail %ld, conflict %d\n",cnt,tn,topconflict);
  if(topconflict){ printf("VERIFIED: formula refuted by unit propagation alone\n"); return 0; }
  FILE *p=fopen(argv[2],"r"); long lem=0,dels=0;
  while(readclause(p,&isdel,&n)){
    if(isdel){ hdel(buf,n); dels++; continue; }
    /* RUP check */
    long save=tn; int ok=0;
    for(int i=0;i<n;i++){ int v=litval(buf[i]); if(v==1){ ok=1; break; } }
    if(!ok){ for(int i=0;i<n;i++) if(litval(buf[i])==0) assign(-buf[i]); ok=propagate(save); }
    while(tn>save){ val[abs(trail[--tn])]=0; }
    if(!ok){ printf("FAIL at lemma %ld (size %d)\n",lem,n); return 1; }
    lem++;
    if(n==0){ printf("VERIFIED: empty clause derived by RUP after %ld lemmas (%ld deletions)\n",lem,dels); return 0; }
    addclause(buf,n);
    if(topconflict){ printf("VERIFIED: top-level conflict after %ld lemmas (%ld deletions)\n",lem,dels); return 0; }
  }
  printf("no empty clause\n"); return 2;
}
