// Independent clique census: decision DFS for a clique of size k (no coloring bound; candidate-count pruning only), written separately from WIN12/mc.cpp.
// For each rep r (as R-complement) and each section i: omega(R & A) classified: exact if <= 6, else ">=7" (a 7-clique is exhibited).
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <map>
using namespace std; typedef unsigned __int128 B; typedef unsigned long long u64;
static B adj[112];
static inline int pc(B x){return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64));}
static inline int lo(B x){u64 a=(u64)x; return a?__builtin_ctzll(a):64+__builtin_ctzll((u64)(x>>64));}
// is there a clique of size k inside cand (vertices only above current in index order)?
static bool has(B cand,int k){
  if(k==0) return true;
  if(pc(cand)<k) return false;
  if(k==1) return true;
  while(cand){ if(pc(cand)<k) return false; int v=lo(cand); cand&=~((B)1<<v); if(has(cand&adj[v],k-1)) return true; }
  return false;
}
static B rd(const string&s){B x=0; for(int i=0;i<112;i++) if(s[i]=='1') x|=(B)1<<i; return x;}
int main(int argc,char**argv){
  FILE*f=fopen("graph.txt","r"); int n,nr,ns; fscanf(f,"%d %d %d",&n,&nr,&ns); char buf[256];
  for(int i=0;i<112;i++){fscanf(f,"%s",buf); adj[i]=rd(buf);}
  vector<B> Rz(nr),Z(ns); for(auto&x:Rz){fscanf(f,"%s",buf); x=rd(buf);} for(auto&x:Z){fscanf(f,"%s",buf); x=rd(buf);}
  B all=(((B)1)<<112)-1; int r0=argc>1?atoi(argv[1]):0, r1=argc>2?atoi(argv[2]):nr; int stride=argc>3?atoi(argv[3]):1;
  for(int r=r0;r<r1;r++){ map<int,long> h; B R=all&~Rz[r]; vector<int> ex;
    for(int i=0;i<ns;i+=stride){ B P=R&~Z[i]; int w;
      if(has(P,7)) w=7; else { w=6; while(w>0 && !has(P,w)) w--; ex.push_back(i); }
      h[w]++; if(w<=6) printf("EX %d %d %d %d\n",r,i,w,pc(P)); }
    printf("rep %d |H|=%d |R|=%d:",r,pc(Rz[r]),pc(R)); for(auto&kv:h) printf(" %s%d:%ld",kv.first==7?"w>=":"w",kv.first,kv.second); printf("\n"); fflush(stdout);}
}
