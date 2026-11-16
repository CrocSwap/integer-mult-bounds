// AUD-1 independent cover search. Usage: ./cov base.txt job.txt
// job: R X1 P  then P*(P-1)/2 target masks (lo hi) in pair order 01,02,..,0(P-1),12,...  (P=2 or 4)
// counts: P=2 -> unordered (A,B) with rank(U\(A|B) [minus <=X1 lines]) <= R ; P=4 -> ordered (M0..M3) with union-of-leftovers rank<=R (global X1 line)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef unsigned __int128 u128;
int lab[120], N; u128 *M;
static int rk(u128 s){ int b[9]={0}; int r=0; for(int t=0;t<120;t++) if((s>>t)&1){ int v=lab[t]; for(int k=8;k>=0;k--) if((v>>k)&1){ if(!b[k]){b[k]=v;r++;break;} v^=b[k]; } } return r; }
static int ok(u128 s,int R,int X1){ int r=rk(s); if(r<=R) return 1; if(!X1||r>R+1) return 0;
  for(int t=0;t<120;t++) if((s>>t)&1) if(rk(s&~(((u128)1)<<t))<=R) return 1; return 0; }
static int pc(u128 x){ return __builtin_popcountll((uint64_t)x)+__builtin_popcountll((uint64_t)(x>>64)); }
int cap;
typedef struct { int i,j; u128 lo; } E;
E* plist(u128 U,int R,int X1,long *n){ long c=0,sz=1<<16; E*a=malloc(sz*sizeof(E));
  for(int i=0;i<N;i++){ u128 r=U&~M[i]; for(int j=0;j<N;j++){ u128 l=r&~M[j]; if(pc(l)>cap+X1) continue; if(!ok(l,R,X1)) continue;
     if(c==sz){sz*=2;a=realloc(a,sz*sizeof(E));} a[c].i=i;a[c].j=j;a[c].lo=l;c++; } } *n=c; return a; }
long *st[6]; E* L[6]; long n[6];
static long find(int p,int i,int j){ long lo=st[p][i],hi=st[p][i+1]-1; while(lo<=hi){ long m=(lo+hi)/2; if(L[p][m].j==j) return m; if(L[p][m].j<j) lo=m+1; else hi=m-1;} return -1; }
int main(int argc,char**argv){ FILE*f=fopen(argv[1],"r"); for(int t=0;t<120;t++) fscanf(f,"%d",&lab[t]); fscanf(f,"%d",&N); M=malloc(N*sizeof(u128));
  for(int i=0;i<N;i++){ unsigned long long a,b; fscanf(f,"%llu %llu",&a,&b); M[i]=((u128)b<<64)|a; } fclose(f);
  FILE*g=fopen(argv[2],"r"); int R,X1,P; fscanf(g,"%d %d %d",&R,&X1,&P); int np=P*(P-1)/2; if(P==3) np=3; u128 U[6];
  for(int p=0;p<np;p++){ unsigned long long a,b; fscanf(g,"%llu %llu",&a,&b); U[p]=((u128)b<<64)|a; }
  // cap = max lines in a rank-R flat (exact: max over R-dim subspaces = max over sets; compute by greedy over kernels)
  cap=0; if(R==6){ for(int a=1;a<512;a++) for(int b=a+1;b<512;b++) for(int c=b+1;c<512;c++){ if(c==(a^b)) continue; int k=0; for(int t=0;t<120;t++) if(!(__builtin_parity(lab[t]&a)|__builtin_parity(lab[t]&b)|__builtin_parity(lab[t]&c))) k++; if(k>cap) cap=k; } }
  else cap=36; // R=7: <= any 7-flat; checked below
  if(R==7){ int mx=0; for(int i=0;i<N;i++) if(pc(M[i])>mx) mx=pc(M[i]); cap=mx; }
  fprintf(stderr,"cap(R=%d)=%d\n",R,cap);
  if(P==2){ long c; E*a=plist(U[0],R,X1,&c); long un=0; for(long k=0;k<c;k++) if(a[k].i<=a[k].j) un++; printf("ordered %ld unordered %ld\n",c,un); return 0; }
  for(int p=0;p<np;p++){ L[p]=plist(U[p],R,X1,&n[p]); st[p]=calloc(N+1,sizeof(long)); for(long k=0;k<n[p];k++) st[p][L[p][k].i+1]++; for(int i=0;i<N;i++) st[p][i+1]+=st[p][i]; fprintf(stderr,"pair %d: %ld\n",p,n[p]); }
  if(P==3){ long sol=0; for(long k=0;k<n[0];k++){ int i0=L[0][k].i,i1=L[0][k].j; for(long k2=st[1][i0];k2<st[1][i0+1];k2++){ int i2=L[1][k2].j; long q=find(2,i1,i2); if(q<0) continue; if(ok(L[0][k].lo|L[1][k2].lo|L[2][q].lo,R,X1)) sol++; } } printf("solutions %ld\n",sol); return 0; }
  // pairs order: 0:01 1:02 2:03 3:12 4:13 5:23
  long sol=0;
  for(long k=0;k<n[0];k++){ int i0=L[0][k].i,i1=L[0][k].j; u128 u0=L[0][k].lo;
    for(long k2=st[1][i0];k2<st[1][i0+1];k2++){ int i2=L[1][k2].j; long q=find(3,i1,i2); if(q<0) continue; u128 u1=u0|L[1][k2].lo|L[3][q].lo; if(!ok(u1,R,X1)) continue;
      for(long k3=st[2][i0];k3<st[2][i0+1];k3++){ int i3=L[2][k3].j; long q4=find(4,i1,i3); if(q4<0) continue; long q5=find(5,i2,i3); if(q5<0) continue;
        u128 u=u1|L[2][k3].lo|L[4][q4].lo|L[5][q5].lo; if(ok(u,R,X1)){ sol++; if(getenv("FIRST")){ printf("first solution M=%d %d %d %d\n",i0,i1,i2,i3); printf("solutions>=1\n"); return 0;} } } } }
  printf("solutions %ld\n",sol); return 0; }
