// exists d in {0..8}^(16\I) x {9}^I (9-set exactly I) with d >=lex d o p for all non-identity p (pos 0 most significant)?
// positions in I are known from the start (=9); complement positions are assigned in index order.
#include <stdio.h>
#include <stdlib.h>
static int NP; static int P[400][16]; static int d[16]; static int I; static int K; /* K = number of complement positions decided (index < K known) */
static int ND[16], DM[16][16];
typedef struct { short p; signed char j; } AL;
static AL stk[18][400];
static inline int known(int u){ return (I>>u&1) || u<K; }
/* advance perms; returns count of alive written to out, or -1 if some perm is violated */
static int advance(int na, AL *alive, AL *out){
  int n2=0;
  for(int a=0;a<na;a++){
    int p=alive[a].p, j=alive[a].j, sat=0;
    while(j<16){
      int q=P[p][j];
      if(q==j){ j++; continue; }
      int kj=known(j), kq=known(q);
      if(kj&&kq){ int x=d[j],y=d[q]; if(x>y){sat=1;break;} if(x<y) return -1; j++; continue; }
      /* lookahead: one side unknown, in [0,8] (complement) */
      if(kj){ int x=d[j]; if(x<0) {} if(x>8) {sat=1;} else if(x<0){return -1;} else {
                 /* d[q] in [0,8]: violated only if x < lb(q)=0 never; sat if x>8 */ } }
      else if(kq){ int y=d[q]; /* d[j] in [0,8] */ if(y>8) return -1; }
      break;
    }
    if(!sat){ out[n2].p=p; out[n2].j=j; n2++; }
  }
  return n2;
}
static int dfs(int k, int na, AL *alive){
  while(k<16 && (I>>k&1)){ k++; }   /* I positions are pre-known; K tracks complement prefix, handled via known() */
  if(k==16) return 1;
  int hi=8; for(int a=0;a<ND[k];a++){ if(d[DM[k][a]]<hi) hi=d[DM[k][a]]; }
  int lo=0;
  for(int u=k+1;u<16;u++) if(I>>u&1) for(int a=0;a<ND[u];a++) if(DM[u][a]==k) lo=9;
  int saveK=K;
  for(int v=hi; v>=lo; v--){
    d[k]=v; K=k+1;
    int n2=advance(na,alive,stk[k+1]);
    if(n2>=0 && dfs(k+1,n2,stk[k+1])){ K=saveK; return 1; }
  }
  K=saveK; return 0;
}
int main(){
  FILE*f=fopen("perms_nf.txt","r"); fscanf(f,"%d",&NP);
  for(int i=0;i<NP;i++) for(int j=0;j<16;j++) fscanf(f,"%d",&P[i][j]);
  f=fopen("chain.txt","r"); for(int u=0;u<16;u++){fscanf(f,"%d",&ND[u]); for(int a=0;a<ND[u];a++) fscanf(f,"%d",&DM[u][a]);}
  for(I=0;I<65536;I++){
    for(int u=0;u<16;u++) d[u]=(I>>u&1)?9:-1;
    K=0;
    for(int a=0;a<NP;a++){stk[0][a].p=a;stk[0][a].j=0;}
    int n0=advance(NP,stk[0],stk[1]);
    int r=0;
    if(n0>=0){ r=dfs(0,n0,stk[1]); }
    printf("%d %d\n",I,r); fflush(stdout);
  }
}
