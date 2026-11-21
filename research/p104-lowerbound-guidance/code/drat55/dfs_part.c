// exists d in {0..8}^(16\I) x {9}^I with d >=lex d o p for all non-identity p in perms (pos 0 most significant)?
// usage: dfs_part  -> for every mask I in 0..65535 prints "I feasible(0/1)"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int ND[16]; static int DM[16][16]; static int NP; static int P[400][16]; static int d[16]; static int I;
typedef struct { short p; signed char j; } AL;
static AL stack[17][400];
static int dfs(int k, int na, AL *alive){
  if(k==16) return 1;
  int lo,hi; if(I>>k&1){lo=hi=9;} else {lo=0;hi=8;}
  for(int a=0;a<ND[k];a++){ if(d[DM[k][a]]<hi) hi=d[DM[k][a]]; }
  for(int u=k+1;u<16;u++) if(I>>u&1) for(int a=0;a<ND[u];a++) if(DM[u][a]==k) lo=9;
  for(int v=hi; v>=lo; v--){
    d[k]=v; int n2=0; int ok=1; AL *out=stack[k+1];
    for(int a=0;a<na;a++){
      int p=alive[a].p, j=alive[a].j; int sat=0;
      while(j<=k && P[p][j]<=k){
        int x=d[j], y=d[P[p][j]];
        if(x>y){sat=1;break;}
        if(x<y){ok=0;break;}
        j++;
      }
      if(ok && !sat && j<16){
        int q=P[p][j];
        if(j<=k){ /* d[j] known, d[q] unknown (q>k) */
          int lb=(I>>q&1)?9:0, ub=(I>>q&1)?9:8;
          if(d[j]<lb) ok=0; else if(d[j]>ub) sat=1;
        } else if(q<=k){ /* d[q] known, d[j] unknown */
          int lb=(I>>j&1)?9:0, ub=(I>>j&1)?9:8;
          if(ub<d[q]) ok=0; else if(lb>d[q]) sat=1;
        }
      }
      if(!ok) break;
      if(!sat){ out[n2].p=p; out[n2].j=j; n2++; }
    }
    if(ok && dfs(k+1,n2,out)) return 1;
  }
  return 0;
}
int main(){
  FILE*f=fopen("perms_nf.txt","r"); fscanf(f,"%d",&NP);
  for(int i=0;i<NP;i++) for(int j=0;j<16;j++) fscanf(f,"%d",&P[i][j]);
  f=fopen("chain.txt","r"); for(int u=0;u<16;u++){fscanf(f,"%d",&ND[u]); for(int a=0;a<ND[u];a++) fscanf(f,"%d",&DM[u][a]);}
  for(I=0;I<65536;I++){
    for(int a=0;a<NP;a++){stack[0][a].p=a;stack[0][a].j=0;}
    int r=dfs(0,NP,stack[0]);
    printf("%d %d\n",I,r); fflush(stdout);
  }
}
