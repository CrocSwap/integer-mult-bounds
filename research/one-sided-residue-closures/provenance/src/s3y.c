// S3FLAT (single implementation, C): three label flats of dims a,b,c + s free lines (per-direction, relaxed superset).
// Direction h qualifies iff Off(h) \ (L(V1) u L(V2) u L(V3)) minus <= s lines lies in a 7-flat G (rank_F2 <= 7).
// Redesign vs MS3c/s3.c:
//  (1) V1 over frame-group orbit reps; V2 over all, with symmetric-pair reduction (orbit(V2) >= orbit(V1)) when a==b;
//  (2) V3 is NOT enumerated: for each direction h and 7-flat G, D = Off(h)\(X1 u X2 u G) must lie (minus s lines) in a c-dim flat,
//      i.e. rank_F2(l(D\T)) <= c  -> requirement subspace S_{h,G}.  Per (V1,h) the G's are precomputed as maximal masks r1&G;
//  (3) V3 = closure of sums of requirement subspaces (dim <= c); evaluated at leaves; incremental real rank stops at 8.
// usage: s3f data a b c s lim target mod rem   [env NOSYM=1 disables pair symmetry; ONLY=ri,ri,..]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef unsigned long long u64;
int LAB[112]; int PC[112][8]; int ND; int hv[20000][8]; int hv2[20000][8]; int htyp[20000]; u128 OFF[20000]; int cap[20000];
static inline int pc(u128 x){ return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64)); }
long long gcdll(long long a,long long b){ if(a<0)a=-a; if(b<0)b=-b; while(b){ long long t=a%b; a=b; b=t;} return a; }
// exact integer real rank of direction vectors (pencils contribute two vectors); stops at 8
int realrank(int *list0,int n0){ long long Bm[8][8]; int piv[8]; int r=0;
  for(int ii=0;ii<n0;ii++){ for(int w=0;w<(htyp[list0[ii]]==2?2:1);w++){ long long v[8]; for(int k=0;k<8;k++) v[k]=w?hv2[list0[ii]][k]:hv[list0[ii]][k];
    int again=1; while(again){ again=0; for(int j=0;j<r;j++){ int q=piv[j]; if(v[q]!=0){ long long a=Bm[j][q], b=v[q]; long long g=0; for(int k=0;k<8;k++) v[k]=a*v[k]-b*Bm[j][k]; for(int k=0;k<8;k++) g=gcdll(g,v[k]); if(g>1) for(int k=0;k<8;k++) v[k]/=g; again=1; } } }
    int p=-1; for(int k=0;k<8;k++) if(v[k]){p=k;break;} if(p<0) continue;
    for(int k=0;k<8;k++) Bm[r][k]=v[k]; piv[r]=p; r++; if(r==8) return 8; } }
  return r; }
// ---------- subspaces (dual enumeration as in s66.c)
u128 *SUB; int NS=0;
int cmp128(const void*a,const void*b){ u128 x=*(u128*)a,y=*(u128*)b; return x<y?-1:x>y; }
static inline int par(int x){ return __builtin_popcount(x)&1; }
int gens[16][112]; int NG=0;
u128 mapmask(u128 m,int g){ u128 o=0; for(int t=0;t<112;t++) if((m>>t)&1) o|=((u128)1)<<gens[g][t]; return o; }
int findidx(u128 m){ int lo=0,hi=NS-1; while(lo<=hi){ int mid=(lo+hi)/2; if(SUB[mid]==m) return mid; if(SUB[mid]<m) lo=mid+1; else hi=mid-1;} return -1; }
int *uf; int fnd(int x){ while(uf[x]!=x){ uf[x]=uf[uf[x]]; x=uf[x];} return x; }
int kk; int w[9];
void rec(int d,int *el,int nel,int last){ if(d==kk){ u128 m=0; for(int t=0;t<112;t++){ int ok=1; for(int i=0;i<kk;i++) if(par(LAB[t]&w[i])){ok=0;break;} if(ok) m|=((u128)1)<<t; } if(m) SUB[NS++]=m; return; }
    for(int x=last+1;x<512;x++){ int in=0; for(int i=0;i<nel;i++) if(el[i]==x){in=1;break;} if(in) continue;
      int ok=1; for(int i=0;i<nel;i++) if((x^el[i])<x){ok=0;break;} if(!ok) continue;
      int el2[512]; for(int i=0;i<nel;i++){ el2[i]=el[i]; el2[nel+i]=el[i]^x; } w[d]=x; rec(d+1,el2,2*nel,x); } }
u128 *enumsub(int sdim,int *cnt){ kk=9-sdim; NS=0; SUB=malloc(sizeof(u128)*4000000); int el0[1]={0}; rec(0,el0,1,0);
  qsort(SUB,NS,sizeof(u128),cmp128); int u=0; for(int i=0;i<NS;i++) if(i==0||SUB[i]!=SUB[i-1]) SUB[u++]=SUB[i]; *cnt=u; return SUB; }
// ---------- small subspace algebra on F2^9 : canonical key = RREF basis packed (<=6 vectors x 9 bits)
int rrefv(int *vs,int n,int *out){ int B[9]={0}; int r=0; for(int i=0;i<n;i++){ int x=vs[i]; for(int k=8;k>=0;k--){ if(!((x>>k)&1)) continue; if(B[k]) x^=B[k]; else { B[k]=x; r++; break; } } }
  for(int k=0;k<9;k++) if(B[k]) for(int j=k+1;j<9;j++) if(B[j]&&((B[j]>>k)&1)) B[j]^=B[k];
  int m=0; for(int k=8;k>=0;k--) if(B[k]) out[m++]=B[k]; return m; }
u64 packkey(int *b,int n){ u64 key=0; for(int i=0;i<n;i++) key=(key<<9)|(u64)b[i]; return key; }
int unpackkey(u64 key,int *b){ int n=0; int tmp[8]; while(key){ tmp[n++]=key&511; key>>=9; } for(int i=0;i<n;i++) b[i]=tmp[n-1-i]; return n; }
// span key of the labels of D; returns dim or 99 if > c
int spankey(u128 D,int c,u64 *key){ int vs[112]; int n=0; for(int t=0;t<112;t++) if((D>>t)&1) vs[n++]=LAB[t]; int b[9]; int m=rrefv(vs,n,b); if(m>c) return 99; *key=packkey(b,m); return m; }
void membmap(int *b,int n,u64 *mem){ for(int i=0;i<8;i++) mem[i]=0; int el[64]; int ne=1; el[0]=0; for(int i=0;i<n;i++){ for(int j=0;j<ne;j++) el[ne+j]=el[j]^b[i]; ne*=2; } for(int j=0;j<ne;j++) mem[el[j]>>6]|=1ULL<<(el[j]&63); }
// requirement subspaces for (D, s, c): span(D) and spans after removing <= s (<=2) lines, those of dim <= c
int reqs(u128 D,int s,int c,u64 *outk,int maxo){ int no=0; u64 key; int d=spankey(D,c,&key); if(d<=c){ outk[no++]=key; if(s==0||d==0) return no; }
  if(s==0) return no;
  int lines[112]; int nl=0; for(int t=0;t<112;t++) if((D>>t)&1) lines[nl++]=t;
  for(int i=0;i<nl;i++){ u128 D1=D&~(((u128)1)<<lines[i]); int d1=spankey(D1,c,&key); if(d1<=c && no<maxo) outk[no++]=key;
    if(s>=2) for(int j=i+1;j<nl;j++){ u128 D2=D1&~(((u128)1)<<lines[j]); int d2=spankey(D2,c,&key); if(d2<=c && no<maxo) outk[no++]=key; } }
  return no; }
int feasible(u128 D,int s,int c){ u64 key; if(spankey(D,c,&key)<=c) return 1; if(s==0) return 0;
  int lines[112]; int nl=0; for(int t=0;t<112;t++) if((D>>t)&1) lines[nl++]=t;
  for(int i=0;i<nl;i++){ u128 D1=D&~(((u128)1)<<lines[i]); if(spankey(D1,c,&key)<=c) return 1; if(s>=2) for(int j=i+1;j<nl;j++){ if(spankey(D1&~(((u128)1)<<lines[j]),c,&key)<=c) return 1; } }
  return 0; }
typedef struct { u64 *k; int cap; int n; } HS;
void hs_init(HS*h,int cap){ h->cap=cap; h->n=0; h->k=calloc(cap,sizeof(u64)); }
int hs_add(HS*h,u64 key){ u64 kx=key+1; u64 x=(kx*0x9E3779B97F4A7C15ULL)>>20; int p=x%h->cap; while(h->k[p]){ if(h->k[p]==kx) return 0; p=(p+1)%h->cap; } h->k[p]=kx; h->n++; return 1; }
int cmpu64(const void*a,const void*b){ u64 x=*(u64*)a,y=*(u64*)b; return x<y?-1:x>y; }
int main(int argc,char**argv){
  const char*df=argv[1]; int adim=atoi(argv[2]), bdim=atoi(argv[3]), cdim=atoi(argv[4]), s=atoi(argv[5]), lim=atoi(argv[6]), target=atoi(argv[7]);
  int mod=argc>8?atoi(argv[8]):1, rem=argc>9?atoi(argv[9]):0; int nosym=getenv("NOSYM")!=NULL; int nlo=getenv("NEWLO")?atoi(getenv("NEWLO")):-1; int pass1=getenv("PASS1")!=NULL; char*pf=getenv("PAIRS"); static char hitset[200][200000]; /*unused*/ 
  int only[200]; int nonly=0; if(getenv("ONLY")){ char*p=getenv("ONLY"); while(*p){ only[nonly++]=strtol(p,&p,10); if(*p==',') p++; } }
  int gw[10]={0,1,2,4,8,12,20,36,64,112};
  FILE*f=fopen(df,"r"); for(int i=0;i<112;i++) fscanf(f,"%d",&LAB[i]); int z; for(int i=0;i<8;i++) fscanf(f,"%d",&z);
  for(int i=0;i<112;i++) for(int k2=0;k2<8;k2++) fscanf(f,"%d",&PC[i][k2]);
  int nn; fscanf(f,"%d",&nn); ND=0;
  for(int i=0;i<nn;i++){ int typ; fscanf(f,"%d",&typ); htyp[ND]=typ; for(int k2=0;k2<8;k2++) fscanf(f,"%d",&hv[ND][k2]); if(typ==2) for(int k2=0;k2<8;k2++) fscanf(f,"%d",&hv2[ND][k2]); char st[4]; fscanf(f,"%s",st); u128 m=0; int c=0; int t;
    while(1){ int ch; do{ ch=fgetc(f);}while(ch==' '); if(ch=='\n'||ch==EOF) break; ungetc(ch,f); fscanf(f,"%d",&t); m|=((u128)1)<<t; c++; }
    if(c<=lim && c>nlo){ OFF[ND]=m; ND++; } }
  fclose(f);
  f=fopen("gens.txt","r"); while(1){ int ok=1; for(int t=0;t<112;t++) if(fscanf(f,"%d",&gens[NG][t])!=1){ok=0;break;} if(!ok) break; NG++; } fclose(f);
  u128 *G7=malloc(sizeof(u128)*44000); int n7=0;
  for(int w1=1;w1<512;w1++) for(int w2=w1+1;w2<512;w2++){ int w3=w1^w2; if(w3<w2) continue; u128 m=0; for(int t=0;t<112;t++) if(!par(LAB[t]&w1)&&!par(LAB[t]&w2)) m|=((u128)1)<<t; G7[n7++]=m; }
  for(int h=0;h<ND;h++){ int b=0; for(int g=0;g<n7;g++){ int c=pc(OFF[h]&G7[g]); if(c>b) b=c; } cap[h]=b; }
  int na_,nb_; u128 *A=enumsub(adim,&na_); int sameAB=(adim==bdim); u128 *Bs; if(sameAB){ Bs=A; nb_=na_; } else { Bs=enumsub(bdim,&nb_); }
  SUB=A; NS=na_;
  fprintf(stderr,"dirs %d gens %d V1 %d V2 %d\n",ND,NG,na_,nb_);
  uf=malloc(sizeof(int)*NS); for(int i=0;i<NS;i++) uf[i]=i;
  for(int i=0;i<NS;i++) for(int g=0;g<NG;g++){ int j=findidx(mapmask(SUB[i],g)); if(j<0){ fprintf(stderr,"image not a flat!\n"); exit(1);} int a=fnd(i),b=fnd(j); if(a!=b) uf[a]=b; }
  int nrep=0; int *reps=malloc(sizeof(int)*NS); int *osz=calloc(NS,sizeof(int)); int *rid=malloc(sizeof(int)*NS); for(int i=0;i<NS;i++) osz[fnd(i)]++;
  for(int i=0;i<NS;i++) if(fnd(i)==i){ rid[i]=nrep; reps[nrep++]=i; }
  fprintf(stderr,"V1 orbits: %d\n",nrep);
  int *oid=NULL; if(sameAB && !nosym){ oid=malloc(sizeof(int)*NS); for(int i=0;i<NS;i++) oid[i]=rid[fnd(i)]; }
  long long *PL=NULL; int npl=0; if(pf){ FILE*g=fopen(pf,"r"); PL=malloc(sizeof(long long)*4000000); int a_,b_; while(fscanf(g,"%d %d",&a_,&b_)==2) PL[npl++]=(long long)a_*1000000+b_; fclose(g); qsort(PL,npl,sizeof(long long),cmpu64); }
  int overall=0; long long npair=0,nsurv=0,nleaf=0,nover=0; long long hist[9]={0};
  int *act=malloc(sizeof(int)*ND); u128 *R1=malloc(sizeof(u128)*ND); int *capr=malloc(sizeof(int)*ND);
  u128 **LG=malloc(sizeof(u128*)*ND); int *LGn=malloc(sizeof(int)*ND);
  int *cand=malloc(sizeof(int)*ND); u128 *R2=malloc(sizeof(u128)*ND); int *candi=malloc(sizeof(int)*ND);
  int thr2=gw[cdim]+s; int thr1=gw[bdim]+thr2;
  int capS=4000000; u64 *allS=malloc(sizeof(u64)*capS); int *Sstart=malloc(sizeof(int)*(ND+2)); u64 tk[1024];
  u128 *tmp=malloc(sizeof(u128)*n7); u128 *mx=malloc(sizeof(u128)*n7);
  for(int ri=0;ri<nrep;ri++){ if(ri%mod!=rem) continue; if(nonly){ int ff=0; for(int q=0;q<nonly;q++) if(only[q]==ri) ff=1; if(!ff) continue; }
    u128 X1=A[reps[ri]]; int na=0; int vmax=0; long long ps=0; long long maxcl=0; long long sumL=0;
    for(int h=0;h<ND;h++){ u128 r=OFF[h]&~X1; if(pc(r)>cap[h]+thr1) continue;
      int nt=0; for(int g=0;g<n7;g++){ u128 m=r&G7[g]; if(pc(r&~m)<=thr1) tmp[nt++]=m; }
      if(nt==0) continue;
      qsort(tmp,nt,sizeof(u128),cmp128); int u=0; for(int i=0;i<nt;i++) if(i==0||tmp[i]!=tmp[i-1]) tmp[u++]=tmp[i]; nt=u;
      int nm=0; for(int i=0;i<nt;i++){ int dom=0; for(int j=0;j<nt&&!dom;j++) if(j!=i && (tmp[i]&tmp[j])==tmp[i]) dom=1; if(!dom) mx[nm++]=tmp[i]; }
      LG[na]=malloc(sizeof(u128)*nm); memcpy(LG[na],mx,sizeof(u128)*nm); LGn[na]=nm; sumL+=nm; int cp=0; for(int i=0;i<nm;i++){ int c=pc(mx[i]); if(c>cp) cp=c; } capr[na]=cp; act[na]=h; R1[na]=r; na++; }
    fprintf(stderr,"rep %d setup done: active %d avgL %.1f\n",ri,na,na?(double)sumL/na:0.0);
    for(int j=0;j<nb_;j++){ if(oid && oid[j]<ri) continue; if(PL){ long long key=(long long)ri*1000000+j; int lo=0,hi=npl-1,f2=0; while(lo<=hi){ int mid=(lo+hi)/2; if(PL[mid]==key){f2=1;break;} if(PL[mid]<key) lo=mid+1; else hi=mid-1; } if(!f2) continue; } u128 X2=Bs[j]; int nc=0;
      for(int a=0;a<na;a++){ u128 r=R1[a]&~X2; if(pc(r)>capr[a]+thr2) continue; int ok=0; u128 *L=LG[a]; for(int q=0;q<LGn[a];q++){ u128 D=r&~L[q]; if(pc(D)>thr2) continue; if(feasible(D,s,cdim)){ ok=1; break; } }
        if(ok){ cand[nc]=act[a]; candi[nc]=a; R2[nc]=r; nc++; } }
      npair++; if(nc==0) continue; if(pass1){ printf("HIT %d %d %d\n",ri,j,nc); continue; }
      int ub=realrank(cand,nc); if(ub<target) continue; nsurv++; ps++;
      int tot=0;
      for(int ci=0;ci<nc;ci++){ Sstart[ci]=tot; int a=candi[ci]; u128 r=R2[ci]; u128 *L=LG[a]; int base=tot;
        for(int q=0;q<LGn[a];q++){ u128 D=r&~L[q]; if(pc(D)>thr2) continue; int nk=reqs(D,s,cdim,tk,1024); for(int e=0;e<nk;e++){ if(tot<capS){ allS[tot]=tk[e]; tot++; } } }
        qsort(allS+base,tot-base,sizeof(u64),cmpu64); int u=base; for(int e=base;e<tot;e++) if(e==base||allS[e]!=allS[e-1]) allS[u++]=allS[e]; tot=u; }
      Sstart[nc]=tot;
      u64 *gk=malloc(sizeof(u64)*(tot+1)); memcpy(gk,allS,sizeof(u64)*tot); qsort(gk,tot,sizeof(u64),cmpu64); int ng=0; for(int e=0;e<tot;e++) if(e==0||gk[e]!=gk[e-1]) gk[ng++]=gk[e];
      HS hs; hs_init(&hs,1<<22); u64 *W=malloc(sizeof(u64)*(1<<21)); int nw=0; int overflow=0; int pairbest=0;
      hs_add(&hs,0); W[nw++]=0;
      for(int e=0;e<ng;e++) if(hs_add(&hs,gk[e])) W[nw++]=gk[e];
      for(int cwi=0; cwi<nw; cwi++){ u64 wk=W[cwi]; int wb[9]; int wn=unpackkey(wk,wb); int grew=0;
        for(int e=0;e<ng;e++){ int sb[9]; int sn=unpackkey(gk[e],sb); int vs[18]; int m=0; for(int i=0;i<wn;i++) vs[m++]=wb[i]; for(int i=0;i<sn;i++) vs[m++]=sb[i]; int ob[9]; int dn=rrefv(vs,m,ob); if(dn>cdim) continue; if(dn==wn) continue; grew=1; u64 nk=packkey(ob,dn); if(hs_add(&hs,nk)){ if(nw<(1<<21)) W[nw++]=nk; else overflow=1; } }
        if(overflow) break;
        if(!grew){ nleaf++; u64 mem[8]; membmap(wb,wn,mem); int list[512]; int n=0;
          for(int ci=0;ci<nc;ci++){ int ok=0; for(int e=Sstart[ci];e<Sstart[ci+1]&&!ok;e++){ int sb[9]; int sn=unpackkey(allS[e],sb); int inside=1; for(int i=0;i<sn;i++) if(!((mem[sb[i]>>6]>>(sb[i]&63))&1)){ inside=0; break; } if(inside) ok=1; } if(ok && n<512) list[n++]=cand[ci]; }
          if(n){ int rk=realrank(list,n); hist[rk]++; if(rk>vmax) vmax=rk; if(rk>pairbest) pairbest=rk;
            if(rk>=target){ printf("CRACK? target %d span %d rep %d V2idx %d X1=%016llx%016llx X2=%016llx%016llx Wkey=%llx dim %d n %d dirs:",target,rk,ri,j,(u64)(X1>>64),(u64)X1,(u64)(X2>>64),(u64)X2,wk,wn,n); for(int a2=0;a2<n;a2++) printf(" %d",list[a2]); printf("\n"); fflush(stdout); if(getenv("EXITCRACK")){ printf("EXITCRACK\n"); exit(0);} } } } }
      if(getenv("PAIRLOG")) printf("PAIR rep %d V2idx %d nc %d ng %d nw %d bestrank %d X1=%016llx%016llx X2=%016llx%016llx\n",ri,j,nc,ng,nw,pairbest,(u64)(X1>>64),(u64)X1,(u64)(X2>>64),(u64)X2);
      if(overflow){ nover++; printf("OVERFLOW rep %d V2idx %d ng %d\n",ri,j,ng); fflush(stdout); }
      if(nw>maxcl) maxcl=nw;
      free(hs.k); free(W); free(gk); }
    if(vmax>overall) overall=vmax;
    printf("rep %d lines %d orbit %d active %d surviving-pairs %lld maxclosure %lld maxrank %d\n",ri,pc(X1),osz[reps[ri]],na,ps,maxcl,vmax); fflush(stdout);
    for(int a=0;a<na;a++) free(LG[a]);
  }
  printf("OVERALL %s dims %d %d %d s %d lim %d target %d mod %d rem %d: pairs %lld surviving %lld leaves %lld overflow %lld max span %d hist",df,adim,bdim,cdim,s,lim,target,mod,rem,npair,nsurv,nleaf,nover,overall);
  for(int r=1;r<=8;r++) printf(" %d:%lld",r,hist[r]); printf("\n");
}
