#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <algorithm>
using namespace std;
typedef unsigned __int128 u128;
static int K; static long long nodes;
static inline bool has(u128 s,int e){return (s>>e)&1;}
static bool dfs(const vector<u128>&U, u128 excl, int r, vector<int>&sol){
  nodes++;
  if(U.empty()) return true;
  if(r==0) return false;
  int cnt[128]={0};
  for(u128 s: U){ u128 av=s&~excl; if(!av) return false; uint64_t lo=(uint64_t)av, hi=(uint64_t)(av>>64);
    while(lo){int b=__builtin_ctzll(lo); cnt[b]++; lo&=lo-1;} while(hi){int b=__builtin_ctzll(hi); cnt[64+b]++; hi&=hi-1;} }
  // top-r bound
  int tmp[128]; int m=0; for(int e=0;e<128;e++) if(cnt[e]) tmp[m++]=cnt[e];
  sort(tmp,tmp+m,[](int a,int b){return a>b;});
  long long sum=0; for(int i=0;i<m&&i<r;i++) sum+=tmp[i];
  if(sum<(long long)U.size()) return false;
  int be=-1; for(int e=0;e<128;e++) if(cnt[e]&&(be<0||cnt[e]>cnt[be])) be=e;
  u128 b=((u128)1)<<be;
  vector<u128> U2; U2.reserve(U.size());
  for(u128 s:U) if(!(s&b)) U2.push_back(s);
  if(dfs(U2,excl,r-1,sol)){ sol.push_back(be); return true; }
  return dfs(U,excl|b,r,sol);
}
int main(int argc,char**argv){
  K=atoi(argv[3]); FILE*f=fopen(argv[1],"rb"); vector<u128> fam; uint64_t a,b; while(fread(&a,8,1,f)==1&&fread(&b,8,1,f)==1) fam.push_back(((u128)b<<64)|a); fclose(f);
  FILE*c=fopen(argv[2],"r"); int cs=atoi(argv[4]); // cube size
  u128 base=((u128)1<<0)|((u128)1<<2); long long tot=0; int nc=0, found=0;
  vector<int> cube(cs);
  while(true){ bool ok=true; u128 cm=0; for(int i=0;i<cs;i++){ if(fscanf(c,"%d",&cube[i])!=1){ok=false;break;} cm|=((u128)1)<<cube[i]; } if(!ok)break;
    vector<u128> U; for(u128 s:fam) if(!(s&cm)) U.push_back(s);
    vector<int> sol; nodes=0; bool r=dfs(U,base|cm,K-cs,sol); tot+=nodes; nc++; if(nc%50==0){fprintf(stderr,"cube %d nodes %lld\n",nc,tot);}
    if(r){ found++; if(argc>5){ printf("FOUND cube"); for(int x:cube)printf(" %d",x); printf(" +"); for(int x:sol)printf(" %d",x); printf("\n"); return 0;} printf("FOUND cube"); for(int x:cube)printf(" %d",x); printf(" +"); for(int x:sol)printf(" %d",x); printf("\n"); fflush(stdout); }
  }
  fprintf(stderr,"cubes %d found %d total nodes %lld\n",nc,found,tot);
  printf("DONE cubes %d found %d\n",nc,found);
}
