// Integer surrogate transport only; every generated physical witness is audited.
#include <algorithm>
#include <cassert>
#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <tuple>
#include <utility>
#include <vector>
using I = long long;
struct Edge { int v, reverse, capacity; I cost; };
struct Tracked { int i, j, index, capacity; I reward; };
int main() {
  std::ios::sync_with_stdio(false); std::cin.tie(nullptr);
  int nl, nr, ne; if (!(std::cin >> nl >> nr >> ne)) return 1;
  int source=nl+nr, sink=source+1, nodes=sink+1;
  std::vector<std::vector<Edge>> graph(nodes);
  auto add = [&](int u,int v,int capacity,I cost) {
    int index=(int)graph[u].size();
    graph[u].push_back({v,(int)graph[v].size(),capacity,cost});
    graph[v].push_back({u,index,0,-cost});
    return index;
  };
  std::vector<int> lc(nl),rc(nr);
  int total=0;
  for(int i=0;i<nl;++i) { std::cin>>lc[i]; assert(lc[i]>=0); total+=lc[i]; add(source,i,lc[i],0); }
  for(int j=0;j<nr;++j) { std::cin>>rc[j]; assert(rc[j]>=0); add(nl+j,sink,rc[j],0); }
  std::vector<I> potential(nodes,0);
  std::vector<Tracked> tracked;
  for(int k=0;k<ne;++k) {
    int i,j; I w; std::cin>>i>>j>>w;
    assert(i>=0 && i<nl && j>=0 && j<nr && w>0);
    int cap=std::min(lc[i],rc[j]); int idx=add(i,nl+j,cap,-w);
    tracked.push_back({i,j,idx,cap,w});
    potential[nl+j]=std::min(potential[nl+j],-w);
  }
  for(int j=0;j<nr;++j) potential[sink]=std::min(potential[sink],potential[nl+j]);
  int sent=0,iterations=0; I gain=0;
  const I INF=std::numeric_limits<I>::max()/4;
  for(;;) {
    std::vector<I> dist(nodes,INF); std::vector<std::pair<int,int>> prev(nodes,{-1,-1});
    using Item=std::pair<I,int>;
    std::priority_queue<Item,std::vector<Item>,std::greater<Item>> queue;
    dist[source]=0; queue.push({0,source});
    while(!queue.empty()) {
      auto [du,u]=queue.top(); queue.pop(); if(du!=dist[u]) continue;
      for(int idx=0;idx<(int)graph[u].size();++idx) {
        const auto &e=graph[u][idx]; if(!e.capacity) continue;
        I reduced=e.cost+potential[u]-potential[e.v]; assert(reduced>=0);
        I nd=du+reduced;
        if(nd<dist[e.v]) { dist[e.v]=nd; prev[e.v]={u,idx}; queue.push({nd,e.v}); }
      }
    }
    if(dist[sink]==INF) break;
    I path_cost=dist[sink]+potential[sink]-potential[source]; if(path_cost>=0) break;
    for(int u=0;u<nodes;++u) if(dist[u]!=INF) potential[u]+=dist[u];
    int amount=total;
    for(int v=sink;v!=source;) { auto [u,idx]=prev[v]; assert(u>=0); amount=std::min(amount,graph[u][idx].capacity); v=u; }
    assert(amount>0);
    for(int v=sink;v!=source;) { auto [u,idx]=prev[v]; auto &e=graph[u][idx]; e.capacity-=amount; graph[v][e.reverse].capacity+=amount; v=u; }
    sent+=amount; gain-=amount*path_cost; ++iterations;
  }
  std::vector<std::tuple<int,int,int>> result; I checkgain=0; int checkflow=0;
  for(const auto &t:tracked) {
    int n=t.capacity-graph[t.i][t.index].capacity;
    if(n) { assert(n>0); result.push_back({t.i,t.j,n}); checkflow+=n; checkgain+=n*t.reward; }
  }
  assert(checkgain==gain && checkflow==sent);
  std::cout<<result.size()<<' '<<sent<<' '<<gain<<' '<<iterations<<'\n';
  for(auto [i,j,n]:result) std::cout<<i<<' '<<j<<' '<<n<<'\n';
}
