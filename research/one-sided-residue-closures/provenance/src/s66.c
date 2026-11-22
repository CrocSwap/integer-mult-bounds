// SIX: Lemma S66 (exact). For every 6-dim label subspace V1 (orbit reps) and V2 (all), X = Λ(V1) ∪ Λ(V2) [∪ {t} in mode T]:
// H = {directions h : rank_F2 lab(Off(h) \ X) <= 7}  [mode T: some single line t removed additionally, per h (superset)].
// Report max real rank of span H. Directions: data.txt (|Off|<=77 complete list); mode 0 uses |Off|<=76.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef __int128 i128;
int LAB[112]; int PC[112][8]; int ND; int hv[5000][8]; int hoff_n[5000]; u128 OFF[5000]; int cap[5000];
int nd_use;
static inline int pc(u128 x){ return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64)); }
int f2rank_mask(u128 R){ int B[9]={0}; int r=0; for(int t=0;t<112;t++) if((R>>t)&1){ int x=LAB[t]; for(int k=8;k>=0;k--){ if(!((x>>k)&1)) continue; if(B[k]) x^=B[k]; else { B[k]=x; r++; break; } } } return r; }
// mode T: exists t in R with rank(R\t) <= 7
int rank_minus_one_le7(u128 R){ int r=f2rank_mask(R); if(r<=7) return 1; if(r>8) return 0; for(int t=0;t<112;t++) if((R>>t)&1){ if(f2rank_mask(R&~(((u128)1)<<t))<=7) return 1; } return 0; }
long long gcdll(long long a,long long b){ if(a<0)a=-a; if(b<0)b=-b; while(b){ long long t=a%b; a=b; b=t;} return a; }
int realrank(int *list,int n){ long long Bm[8][8]; int piv[8]; int r=0;
  for(int i=0;i<n;i++){ long long v[8]; for(int k=0;k<8;k++) v[k]=hv[list[i]][k];
    for(int j=0;j<r;j++){ int p=piv[j]; if(v[p]==0) continue; long long a=Bm[j][p], b=v[p]; long long g=0; for(int k=0;k<8;k++){ v[k]=a*v[k]-b*Bm[j][k]; } for(int k=0;k<8;k++) g=gcdll(g,v[k]); if(g>1) for(int k=0;k<8;k++) v[k]/=g; }
    int p=-1; for(int k=0;k<8;k++) if(v[k]){p=k;break;} if(p<0) continue; // also need to clear p in earlier rows? not needed for rank (echelon by distinct pivots)
    // ensure pivots distinct: v reduced against all earlier pivots, so its first nonzero may still coincide with no earlier pivot? reduce until first nonzero not a pivot
    int again=1; while(again){ again=0; for(int j=0;j<r;j++){ int q=piv[j]; if(v[q]!=0){ long long a=Bm[j][q], b=v[q]; long long g=0; for(int k=0;k<8;k++) v[k]=a*v[k]-b*Bm[j][k]; for(int k=0;k<8;k++) g=gcdll(g,v[k]); if(g>1) for(int k=0;k<8;k++) v[k]/=g; again=1; } } }
    p=-1; for(int k=0;k<8;k++) if(v[k]){p=k;break;} if(p<0) continue;
    for(int k=0;k<8;k++) Bm[r][k]=v[k]; piv[r]=p; r++; if(r==8) return 8; }
  return r; }
// subspaces
u128 *SUB; int NS=0;
int cmp128(const void*a,const void*b){ u128 x=*(u128*)a,y=*(u128*)b; return x<y?-1:x>y; }
int par(int x){ return __builtin_popcount(x)&1; }
int gens[16][112]; int NG=0;
u128 mapmask(u128 m,int g){ u128 o=0; for(int t=0;t<112;t++) if((m>>t)&1) o|=((u128)1)<<gens[g][t]; return o; }
int findidx(u128 m){ int lo=0,hi=NS-1; while(lo<=hi){ int mid=(lo+hi)/2; if(SUB[mid]==m) return mid; if(SUB[mid]<m) lo=mid+1; else hi=mid-1;} return -1; }
int *uf; int fnd(int x){ while(uf[x]!=x){ uf[x]=uf[uf[x]]; x=uf[x];} return x; }
int k; int w[9];
void rec(int d,int *el,int nel,int last){ if(d==k){ u128 m=0; for(int t=0;t<112;t++){ int ok=1; for(int i=0;i<k;i++) if(par(LAB[t]&w[i])){ok=0;break;} if(ok) m|=((u128)1)<<t; } if(m) SUB[NS++]=m; return; }
    for(int x=last+1;x<512;x++){ int in=0; for(int i=0;i<nel;i++) if(el[i]==x){in=1;break;} if(in) continue; // x must be min of x+span
      int ok=1; for(int i=0;i<nel;i++) if((x^el[i])<x){ok=0;break;} if(!ok) continue;
      int el2[512]; for(int i=0;i<nel;i++){ el2[i]=el[i]; el2[nel+i]=el[i]^x; } w[d]=x; rec(d+1,el2,2*nel,x); } }
int main(int argc,char**argv){
  int mode=atoi(argv[1]); // 0: S66 (|Off|<=76), 1: S66+t (|Off|<=77)
  int sdim=argc>2?atoi(argv[2]):6; // dim of V1,V2
  FILE*f=fopen("data.txt","r"); for(int i=0;i<112;i++) fscanf(f,"%d",&LAB[i]); int z; for(int i=0;i<8;i++) fscanf(f,"%d",&z);
  for(int i=0;i<112;i++) for(int k=0;k<8;k++) fscanf(f,"%d",&PC[i][k]);
  int nn; fscanf(f,"%d",&nn); ND=0;
  for(int i=0;i<nn;i++){ int typ; fscanf(f,"%d",&typ); for(int k=0;k<8;k++) fscanf(f,"%d",&hv[ND][k]); if(typ==2){ fprintf(stderr,"pencil unexpected\n"); exit(1);} char s[4]; fscanf(f,"%s",s); u128 m=0; int c=0; int t; 
    while(1){ long pos=ftell(f); int ch; do{ ch=fgetc(f);}while(ch==' '); if(ch=='\n'||ch==EOF) break; ungetc(ch,f); fscanf(f,"%d",&t); m|=((u128)1)<<t; c++; }
    // verify Off from coords
    u128 m2=0; for(int t2=0;t2<112;t2++){ long long d=0; for(int k=0;k<8;k++) d+=(long long)PC[t2][k]*hv[ND][k]; if(d) m2|=((u128)1)<<t2; } if(m2!=m){ fprintf(stderr,"off mismatch\n"); exit(1);} 
    if(c<= (mode==0?76:77)){ OFF[ND]=m; hoff_n[ND]=c; ND++; } }
  fclose(f);
  f=fopen("gens.txt","r"); while(1){ int ok=1; for(int t=0;t<112;t++) if(fscanf(f,"%d",&gens[NG][t])!=1){ok=0;break;} if(!ok) break; NG++; } fclose(f);
  fprintf(stderr,"directions %d, gens %d\n",ND,NG);
  // caps: max |Off(h) ∩ Λ(G)| over 7-dim G (dual 2-dim: pairs w1<w2, w3=w1^w2)
  u128 *G7=malloc(sizeof(u128)*44000); int n7=0;
  for(int w1=1;w1<512;w1++) for(int w2=w1+1;w2<512;w2++){ int w3=w1^w2; if(w3<w2) continue; u128 m=0; for(int t=0;t<112;t++) if(!par(LAB[t]&w1)&&!par(LAB[t]&w2)) m|=((u128)1)<<t; G7[n7++]=m; }
  fprintf(stderr,"7-flats %d\n",n7);
  for(int h=0;h<ND;h++){ int b=0; for(int g=0;g<n7;g++){ int c=pc(OFF[h]&G7[g]); if(c>b) b=c; } cap[h]=b; }
  { int hist[200]={0}; for(int h=0;h<ND;h++) hist[hoff_n[h]*0+cap[h]]++; fprintf(stderr,"cap histogram:"); for(int i=0;i<200;i++) if(hist[i]) fprintf(stderr," %d:%d",i,hist[i]); fprintf(stderr,"\n"); }
  // all subspaces of dim sdim: dual of dim k=9-sdim, canonical basis: w1<w2<.. each = min of coset-new elements; enumerate via spans
  k=9-sdim; SUB=malloc(sizeof(u128)*4000000);
  // enumerate k-dim subspaces by canonical reduced basis: generate all, dedupe by line mask anyway
  // simple recursive: choose basis vectors increasing with w_i = min element of (span_i \ span_{i-1}) -- ensures uniqueness

  // iterative DFS
  int stack_v[9]; int depth=0; stack_v[0]=0;
  // generic recursion via function pointer avoided; use explicit loops for k<=5
  int el0[1]={0}; rec(0,el0,1,0);
  fprintf(stderr,"subspaces with >=1 line: %d\n",NS);
  qsort(SUB,NS,sizeof(u128),cmp128); int u=0; for(int i=0;i<NS;i++) if(i==0||SUB[i]!=SUB[i-1]) SUB[u++]=SUB[i]; NS=u;
  fprintf(stderr,"distinct line sets: %d\n",NS);
  uf=malloc(sizeof(int)*NS); for(int i=0;i<NS;i++) uf[i]=i;
  for(int i=0;i<NS;i++) for(int g=0;g<NG;g++){ int j=findidx(mapmask(SUB[i],g)); if(j<0){ fprintf(stderr,"image not a flat!\n"); exit(1);} int a=fnd(i),b=fnd(j); if(a!=b) uf[a]=b; }
  int nrep=0; int *reps=malloc(sizeof(int)*NS); int *osz=calloc(NS,sizeof(int)); for(int i=0;i<NS;i++) osz[fnd(i)]++; for(int i=0;i<NS;i++) if(fnd(i)==i) reps[nrep++]=i;
  fprintf(stderr,"orbits: %d\n",nrep);
  int overall=0; long long nhits8=0; int maxcnt=0;
  int *act=malloc(sizeof(int)*ND); u128 *R1=malloc(sizeof(u128)*ND);
  int slack=(mode==1)?1:0;
  for(int ri=0;ri<nrep;ri++){ u128 X1=SUB[reps[ri]]; int na=0; int vmax=0;
    for(int h=0;h<ND;h++){ u128 r=OFF[h]&~X1; if(pc(r)<=cap[h]+20+slack){ act[na]=h; R1[na]=r; na++; } }
    for(int j=0;j<NS;j++){ u128 X2=SUB[j]; int list[5000]; int n=0;
      for(int a=0;a<na;a++){ u128 r=R1[a]&~X2; int h=act[a]; if(pc(r)>cap[h]+slack) continue; int ok = (mode==0)? (f2rank_mask(r)<=7) : rank_minus_one_le7(r); if(ok) list[n++]=h; }
      if(n>maxcnt) maxcnt=n;
      if(n>=8){ int rk=realrank(list,n); if(rk>vmax) vmax=rk; if(rk==8){ nhits8++; if(nhits8<=20) printf("RANK8 rep %d j %d n %d\n",ri,j,n);} } else if(n>vmax){ int rk=realrank(list,n); if(rk>vmax) vmax=rk; }
    }
    if(vmax>overall) overall=vmax;
    printf("rep %d lines %d orbit %d active %d maxrank %d\n",ri,pc(X1),osz[reps[ri]],na,vmax); fflush(stdout);
  }
  printf("OVERALL mode %d dim %d: max real rank %d, max #directions %d, rank-8 pairs %lld\n",mode,sdim,overall,maxcnt,nhits8);
}
