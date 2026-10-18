// census/mc.cpp: exact maximum clique (greedy-colouring branch and bound, Tomita-style) of R cap A in the non-orthogonality graph, 47 reps x all distinct sections.
// Unlike cen.cpp it reports exact omega for every pair.  Input data.txt written by lib/common.py write_mcdata.
#include <cstdlib>
#include <cstdio>
#include <map>
#include <vector>
using namespace std; typedef unsigned __int128 u128; typedef unsigned long long u64;
int n; u128 adj[112];
static inline int pc(u128 x){return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64));}
static inline int low(u128 x){u64 a=(u64)x; if(a) return __builtin_ctzll(a); return 64+__builtin_ctzll((u64)(x>>64));}
int best;
void expand(u128 P,int sz){
  if(!P){ if(sz>best) best=sz; return;}
  // greedy coloring bound
  int order[112],col[112],k=0; u128 U=P; int c=0;
  while(U){ c++; u128 Q=U; while(Q){int v=low(Q); Q&=~((u128)1<<v); U&=~((u128)1<<v); Q&=~adj[v]; order[k]=v; col[k]=c; k++;} }
  for(int i=k-1;i>=0;i--){ if(sz+col[i]<=best) return; int v=order[i]; expand(P&adj[v],sz+1); P&=~((u128)1<<v);}
}
int main(int argc,char**argv){ FILE*f=fopen("data.txt","r"); fscanf(f,"%d",&n); for(int i=0;i<n;i++){u64 lo,hi; fscanf(f,"%llu %llu",&lo,&hi); adj[i]=((u128)hi<<64)|lo;}
 int nr; fscanf(f,"%d",&nr); vector<u128> R(nr); for(auto&x:R){u64 lo,hi; fscanf(f,"%llu %llu",&lo,&hi); x=((u128)hi<<64)|lo;}
 int ns; fscanf(f,"%d",&ns); vector<u128> S(ns); for(auto&x:S){u64 lo,hi; fscanf(f,"%llu %llu",&lo,&hi); x=((u128)hi<<64)|lo;}
 int lim = 0; // exact
 int r0=argc>1?atoi(argv[1]):0, r1=argc>2?atoi(argv[2]):nr, stride=argc>3?atoi(argv[3]):1;   // PACKAGE EDIT (only change): optional rep range / section stride; no arguments = the original full run
 for(int r=r0;r<r1;r++){ map<int,long> hist; int arg=-1;
   for(int i=0;i<ns;i+=stride){ best=0; expand(R[r]&S[i],0); hist[best]++; }
   printf("rep %d |R|=%d:",r,pc(R[r])); for(auto&kv:hist) printf(" w%d:%ld",kv.first,kv.second); printf("\n"); fflush(stdout);}
}
