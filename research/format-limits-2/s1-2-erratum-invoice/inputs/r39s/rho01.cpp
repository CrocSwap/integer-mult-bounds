// 0-1 BFS: min #locals to reach each pair-preserving monomial target rho over F2. bridges cost 0 (counted separately: second value = min bridges among min-local words via lexicographic cost nl*1000+nb).
#include <vector>
#include <array>
#include <queue>
#include <unordered_map>
#include <numeric>
#include <algorithm>
#include <cstdio>
#include <cstdlib>
using namespace std;
typedef unsigned long long u64;
int P,NB;
u64 pack(const vector<int>&r){u64 x=0;for(int i=0;i<NB;i++)x|=(u64)r[i]<<(i*NB);return x;}
vector<int> unpack(u64 x){vector<int>r(NB);for(int i=0;i<NB;i++)r[i]=(x>>(i*NB))&((1<<NB)-1);return r;}
int main(int argc,char**argv){P=atoi(argv[1]);NB=2*P;int maxnl=argc>2?atoi(argv[2]):2*P+2;
 vector<pair<int,int>> loc; for(int p=0;p<P;p++){loc.push_back({2*p+1,2*p});loc.push_back({2*p,2*p+1});}
 vector<array<int,4>> br; for(int d=0;d<P;d++)for(int s=0;s<P;s++)if(d!=s)br.push_back({2*d,2*s,2*s+1,2*d+1});
 vector<int> id(NB);for(int i=0;i<NB;i++)id[i]=1<<i;
 unordered_map<u64,int> dist; dist.reserve(4000000);
 priority_queue<pair<int,u64>,vector<pair<int,u64>>,greater<>> pq; // cost=nl*1000+nb
 u64 s0=pack(id);dist[s0]=0;pq.push({0,s0});
 while(!pq.empty()){auto [c,x]=pq.top();pq.pop();if(dist[x]!=c)continue; if(c/1000>maxnl)break;
  auto r=unpack(x);
  for(auto&l:loc){auto q=r;q[l.first]^=q[l.second];int nc=c+1000;u64 y=pack(q);auto it=dist.find(y);if(it==dist.end()||it->second>nc){dist[y]=nc;pq.push({nc,y});}}
  for(auto&b:br){auto q=r;q[b[0]]^=q[b[1]];q[b[2]]^=q[b[3]];int nc=c+1;u64 y=pack(q);auto it=dist.find(y);if(it==dist.end()||it->second>nc){dist[y]=nc;pq.push({nc,y});}}
 }
 vector<int> perm(P);iota(perm.begin(),perm.end(),0);
 do{for(int m=0;m<(1<<P);m++){vector<int>t(NB);for(int p=0;p<P;p++)for(int e=0;e<2;e++)t[2*p+e]=1<<(2*perm[p]+(e^((m>>p)&1)));
   auto it=dist.find(pack(t));printf("perm=");for(int p:perm)printf("%d",p);printf(" swapmask=%d : ",m);if(it==dist.end())printf("unreached<=%d locals\n",maxnl);else printf("locals=%d bridges=%d\n",it->second/1000,it->second%1000);}
 }while(next_permutation(perm.begin(),perm.end()));
 printf("states %zu\n",dist.size());}
