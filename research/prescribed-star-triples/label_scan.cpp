// Exhaustive normalized decoder-coefficient enumeration; no partition optimizer.
// Invoked by run_independent.py using a temporary executable.
// Prepared for DLamdata with substantial OpenAI Codex assistance; Apache-2.0.
#include <array>
#include <cstdint>
#include <iostream>
#include <vector>
#include <utility>
#include <algorithm>
using namespace std;
struct Scan {
 int p,n,m, best=-1; uint64_t leaves=0;
 array<int,16> lab{}, witness{}; array<int,8> count{};
 vector<vector<pair<int,int>>> groups;
 Scan(int pp):p(pp),n(2*pp),m(2*pp*(pp-1)){lab.fill(-1);}
 int put(int v,int x){int gain=count[x] - (lab[v^1]==x); lab[v]=x; ++count[x]; return gain;}
 void unput(int v,int x){--count[x];lab[v]=-1;}
 void dfs(int depth,int equal){
  if(depth==(int)groups.size()) {++leaves;if(equal>best){best=equal;witness=lab;}return;}
  for(int a=0;a<8;++a){int gain=0;for(auto [v,x]:groups[depth])gain+=put(v,a^x);
   dfs(depth+1,equal+gain);
   for(auto it=groups[depth].rbegin();it!=groups[depth].rend();++it)unput(it->first,a^it->second);
  }
 }
 bool solve(const array<pair<int,int>,3>& t){
  vector<vector<pair<int,int>>> adj(n);
  for(int i=0;i<3;++i){auto [u,v]=t[i];adj[u].push_back({v,1<<i});adj[v].push_back({u,1<<i});}
  array<int,16> offset;offset.fill(-1);
  // Every component gets one free 3-bit coefficient; gauge fix the first to zero.
  for(int root=0;root<n;++root)if(offset[root]<0){
   vector<pair<int,int>> group{{root,0}};offset[root]=0;
   for(size_t j=0;j<group.size();++j){auto [u,x]=group[j];for(auto [v,d]:adj[u]){
    int y=x^d;if(offset[v]>=0){if(offset[v]!=y)return false;}
    else {offset[v]=y;group.push_back({v,y});}
   }}
   groups.push_back(group);
  }
  int equal=0;for(auto [v,x]:groups[0])equal+=put(v,x);
  dfs(1,equal);return true;
 }
};
int main(){int p,q;while(cin>>p>>q){
 if(p<2||p>6||q<1||q>19){cerr<<"Invalid p or orbit count\n";return 2;}
 for(int k=0;k<q;++k){array<pair<int,int>,3>t;
 for(auto&[u,v]:t){if(!(cin>>u>>v)||u<0||v<0||u>=2*p||v>=2*p||u>=v||u/2==v/2){cerr<<"Invalid target edge\n";return 2;}}
 if(t[0]==t[1]||t[0]==t[2]||t[1]==t[2]){cerr<<"Repeated target edge\n";return 2;}
 Scan s(p);bool ok=s.solve(t);cout<<p<<" "<<k<<" "<<(ok?s.m-s.best-3:-1)<<" "<<s.leaves;if(ok)for(int i=0;i<s.n;++i)cout<<" "<<s.witness[i];cout<<"\n";}}}
