// Brute-force oracle for Theorem 9.3 (new in this package; independent of Camion's theorem).
// For a 0/1 matrix B (v x v) and three blocks B[R_j,A_j] it decides, by trying EVERY +-1 signing of the ones of B and testing
// total unimodularity of each block by computing ALL its square minors (exact integer determinants), whether
//   b_j = some signing makes block j TU,    J = some single signing makes all three blocks TU.
// Gauge: a spanning forest of the bipartite support graph is fixed to +1 (scaling rows/columns by -1 preserves TU of every
// submatrix, so this loses no case).  Input format = jsign: per instance  v, v rows as bitmasks, then per block "nR R.. nA A..".
// Output per instance: "J b0 b1 b2" (1/0) or "-1" if more than MAXFREE free sign bits remain.
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define MAXFREE 22
int v; uint32_t row[32]; int nR[3],nA[3],R[3][32],A[3][32];
int sg[32][32];                       // sign of entry (t,s), 0 if not a one
static long long det(int k,long long m[8][8]){   // Bareiss, exact in int64 for k<=8 and entries in {0,+-1}
  long long a[8][8]; memcpy(a,m,sizeof a); long long prev=1; int sign=1;
  for(int i=0;i<k-1;i++){
    if(a[i][i]==0){int p=-1;for(int r=i+1;r<k;r++)if(a[r][i]){p=r;break;} if(p<0)return 0;
      for(int c=0;c<k;c++){long long t=a[i][c];a[i][c]=a[p][c];a[p][c]=t;} sign=-sign;}
    for(int r=i+1;r<k;r++)for(int c=i+1;c<k;c++)a[r][c]=(a[r][c]*a[i][i]-a[r][i]*a[i][c])/prev;
    prev=a[i][i];}
  return sign*a[k-1][k-1];}
static int tu(int j){   // all square minors of block j in {0,+-1}
  int nr=nR[j],nc=nA[j]; long long M[8][8]; int mn=nr<nc?nr:nc; if(mn>8)mn=8;
  for(int k=1;k<=mn;k++){
    for(uint32_t S=0;S<(1u<<nr);S++){ if(__builtin_popcount(S)!=k)continue;
      int rs[8],q=0;for(int i=0;i<nr;i++)if(S>>i&1)rs[q++]=R[j][i];
      for(uint32_t T=0;T<(1u<<nc);T++){ if(__builtin_popcount(T)!=k)continue;
        int cs[8],w=0;for(int i=0;i<nc;i++)if(T>>i&1)cs[w++]=A[j][i];
        for(int a=0;a<k;a++)for(int b=0;b<k;b++)M[a][b]=sg[rs[a]][cs[b]];
        long long d=det(k,M); if(d>1||d<-1)return 0;}}}
  return 1;}
int par[64]; static int fnd(int x){while(par[x]!=x)x=par[x]=par[par[x]];return x;}
int main(){
  while(scanf("%d",&v)==1){
    for(int i=0;i<v;i++){unsigned x;scanf("%u",&x);row[i]=x;}
    for(int j=0;j<3;j++){scanf("%d",&nR[j]);for(int i=0;i<nR[j];i++)scanf("%d",&R[j][i]);scanf("%d",&nA[j]);for(int i=0;i<nA[j];i++)scanf("%d",&A[j][i]);}
    for(int i=0;i<2*v;i++)par[i]=i;
    int fr[1024][2],nf=0;
    memset(sg,0,sizeof sg);
    for(int t=0;t<v;t++)for(int s=0;s<v;s++)if(row[t]>>s&1){
      int a=fnd(t),b=fnd(v+s);
      if(a!=b){par[a]=b;sg[t][s]=1;} else {fr[nf][0]=t;fr[nf][1]=s;nf++;sg[t][s]=1;}}
    int big=0;for(int j=0;j<3;j++){int m=nR[j]<nA[j]?nR[j]:nA[j];if(m>8)big=1;}
    if(nf>MAXFREE||big){printf("-1\n");fflush(stdout);continue;}
    int J=0,bo[3]={0,0,0};
    for(uint32_t x=0;x<(1u<<nf);x++){
      for(int i=0;i<nf;i++)sg[fr[i][0]][fr[i][1]]=(x>>i&1)?-1:1;
      int ok[3],all=1;
      for(int j=0;j<3;j++){ ok[j]=tu(j); if(ok[j])bo[j]=1; else all=0;}
      if(all)J=1;
      if(J&&bo[0]&&bo[1]&&bo[2])break;}
    printf("%d %d %d %d\n",J,bo[0],bo[1],bo[2]);fflush(stdout);}
  return 0;}
