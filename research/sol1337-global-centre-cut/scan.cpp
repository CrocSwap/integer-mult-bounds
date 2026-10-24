// Apache-2.0. Substantial OpenAI Codex assistance.
// Source-bound mixed-original-group binary move screen; no supplier admission.
#define main retained_discovery_main
#include "vendor/dynamic_neighbors.cpp"
#undef main
#include <queue>
#include <map>
#include <set>
#include <iomanip>
#include <chrono>
#include "cut.hpp"
struct External {int node,rank;Local local;V own,neighbor;};
struct Internal {int a,b,rank;Local local;};
int run(int argc,char**argv){
 if(argc!=4)return 2;
 int limit=std::stoi(argv[3]);if(limit<1||limit>262143)return 3;
 std::ifstream in(argv[1]);int n,f,m,e;in>>n>>f>>m>>e;
 std::vector<int>frame(n),fixed(n),index(n,-1),original;
 for(int i=0;i<n;i++){in>>frame[i]>>fixed[i];if(!fixed[i]){index[i]=original.size();original.push_back(i);}}
 std::vector<V>fs(f,V(9)),maps(m,V(18)),invs;
 for(auto&b:fs)for(auto&x:b)in>>x;
 for(auto&b:maps){for(auto&x:b)in>>x;invs.push_back(inverse(b));}
 std::vector<Edge>edges(e);std::vector<External>ext;std::vector<Internal>internal;
 const int k=original.size();if(k!=184)throw 30;
 std::vector<int>degree(k),leaf(k),nonleaf;
 std::array<int,10> baseline{};
 for(auto&t:edges){in>>t.a>>t.b>>t.r>>t.sign>>t.map;if(t.sign!=1)throw 31;
  if(t.r<0||t.r>9)throw 45;
  baseline[t.r]++;
  int a=index[t.a],b=index[t.b];if(a<0&&b<0)continue;
  if(a>=0&&b>=0){if(t.map)throw 32;internal.push_back({a,b,t.r,make_local(fs[frame[t.a]],fs[frame[t.b]],t.r,1)});degree[a]++;degree[b]++;}
  else {int node=a>=0?a:b;V neighbor=a>=0?map(invs[t.map],fs[frame[t.b]]):map(maps[t.map],fs[frame[t.a]]);ext.push_back({node,t.r,make_local(fs[frame[original[node]]],neighbor,t.r,1),fs[frame[original[node]]],neighbor});}
 }
 if(!in)return 4;
 for(int r=1;r<=9;r++){int expected[10]={0,2201,412,510,127,40,0,0,8,0};if(baseline[r]!=expected[r])throw 46;}
 int leaves=0,rank0=0,rank8=0;
 for(int i=0;i<k;i++){leaf[i]=frame[original[i]]!=0;if(leaf[i]){if(degree[i]!=1)throw 33;leaves++;}else nonleaf.push_back(i);}
 if(leaves!=8||nonleaf.size()!=176)throw 34;
 for(auto&t:internal){if(t.rank==0){rank0++;if(leaf[t.a]||leaf[t.b])throw 35;}else{rank8++;if(t.rank!=8||leaf[t.a]+leaf[t.b]!=1)throw 36;}}
 if(rank0!=256||rank8!=8)throw 37;
 std::vector<int> reduced(k,-1);for(unsigned i=0;i<nonleaf.size();i++)reduced[nonleaf[i]]=i;
 std::set<std::string>seen;std::vector<int>negative(10),minima(10),nonempty(10);long long weights[10][10]{};
 for(int j=1;j<=9;j++)for(int r=0;r<=9;r++)weights[j][r]=std::min(j,r);
 const long long scale=10000000000LL;for(int r=1;r<=9;r++)weights[0][r]=llround(scale*std::pow(r,1-.0030217758));
 long long minimum[10]{};unsigned bestaxis[10]{};std::vector<std::array<int,10>>bestdelta(10);std::vector<V>bestselected(10);
 auto start=std::chrono::steady_clock::now();int cases=0,checks=0;
 for(unsigned axis=1;axis<=unsigned(limit);axis++){
  std::string signature;signature.reserve(ext.size()+internal.size());std::vector<int>ed,td;std::vector<std::array<int,10>>delta(k);
  for(const auto&t:ext){int d=change(t.local,axis);signature+=char(d+1);ed.push_back(d);delta[t.node][t.rank+d]++;delta[t.node][t.rank]--;}
  for(const auto&t:internal){int d=change(t.local,axis);signature+=char(d+1);td.push_back(d);}
  if(!seen.insert(signature).second)continue;
  for(int j=0;j<=9;j++){
   std::vector<long long>unary(k);for(int v=0;v<k;v++)for(int r=0;r<=9;r++)unary[v]+=delta[v][r]*weights[j][r];
   long long offset=0;Flow flow(178);int source=176,sink=177;
   for(unsigned ei=0;ei<internal.size();ei++){const auto&t=internal[ei];long long w=weights[j][t.rank+td[ei]]-weights[j][t.rank];
    if(t.rank==0){if(w<0)throw 38;if(w){flow.add(reduced[t.a],reduced[t.b],w);flow.add(reduced[t.b],reduced[t.a],w);}}
    else{int v=leaf[t.a]?t.a:t.b,u=leaf[t.a]?t.b:t.a;long long e0=std::min(0LL,unary[v]+w),e1=std::min(w,unary[v]);offset+=e0;unary[u]+=e1-e0;}
   }
   for(int v:nonleaf){if(unary[v]<0){flow.add(source,reduced[v],-unary[v]);offset+=unary[v];}else flow.add(reduced[v],sink,unary[v]);}
   long long maximum=flow.maxflow(source,sink),value=maximum+offset;flow.check(source,sink,maximum);
   auto chosen=flow.chosen(source);long long cut=0;for(int u=0;u<178;u++)if(chosen[u])for(auto&t:flow.g[u])if(t.forward&&!chosen[t.to])cut+=t.initial;if(cut!=maximum)throw 39;
   std::vector<int>x(k);for(int v:nonleaf)x[v]=chosen[reduced[v]];
   for(unsigned ei=0;ei<internal.size();ei++){const auto&t=internal[ei];if(t.rank!=8)continue;int v=leaf[t.a]?t.a:t.b,u=leaf[t.a]?t.b:t.a;long long d=0;for(int r=0;r<=9;r++)d+=delta[v][r]*weights[j][r];long long w=weights[j][t.rank+td[ei]]-weights[j][t.rank];x[v]=x[u]?(d<w):(d+w<0);}
   std::array<int,10>actual{};for(int v=0;v<k;v++)if(x[v])for(int r=0;r<=9;r++)actual[r]+=delta[v][r];
   for(unsigned ei=0;ei<internal.size();ei++){const auto&t=internal[ei];if(x[t.a]!=x[t.b]){actual[t.rank+td[ei]]++;actual[t.rank]--;}}
   long long score=0;for(int r=0;r<=9;r++)score+=actual[r]*weights[j][r];if(score!=value)throw 40;
   if(value<0)negative[j]++;
   if(value<minimum[j]){minimum[j]=value;bestaxis[j]=axis;bestdelta[j]=actual;bestselected[j].clear();for(int v=0;v<k;v++)if(x[v])bestselected[j].push_back(original[v]);}
   cases++;
  }
  { // Independently check every retained rank-energy configuration by row elimination.
   for(unsigned ei=0;ei<ext.size();ei++){const auto&t=ext[ei];V own=t.own;turn(own,axis);own.insert(own.end(),t.neighbor.begin(),t.neighbor.end());if(int(basis(own).size())-9!=t.rank+ed[ei])throw 43;}
   for(unsigned ei=0;ei<internal.size();ei++){const auto&t=internal[ei];V left=fs[frame[original[t.a]]],right=fs[frame[original[t.b]]];turn(left,axis);V both=left;both.insert(both.end(),right.begin(),right.end());if(int(basis(both).size())-9!=t.rank+td[ei])throw 41;turn(right,axis);both=left;both.insert(both.end(),right.begin(),right.end());if(int(basis(both).size())-9!=t.rank)throw 42;left=fs[frame[original[t.a]]];both=left;both.insert(both.end(),right.begin(),right.end());if(int(basis(both).size())-9!=t.rank+td[ei])throw 44;}checks++;
  }
  if(axis%16384==0)std::cerr<<"axis="<<axis<<" configs="<<seen.size()<<" cases="<<cases<<" elapsed="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<"\n";
 }
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"{\"axis_limit\":"<<limit<<",\"complete_axis_domain\":"<<(limit==262143?"true":"false")<<",\"distinct_rank_configurations\":"<<seen.size()<<",\"cut_cases\":"<<cases<<",\"independent_rank_configuration_checks\":"<<checks<<",\"moment_theta\":\"0.9969782242\",\"moment_scale\":"<<scale<<",\"results\":[";
 for(int j=0;j<=9;j++){if(j)out<<',';out<<"{\"tariff\":"<<j<<",\"negative_configurations\":"<<negative[j]<<",\"minimum_integer_delta\":"<<minimum[j]<<",\"best_axis\":"<<bestaxis[j]<<",\"best_delta\":[";for(int r=0;r<=9;r++)out<<(r?",":"")<<bestdelta[j][r];out<<"],\"best_selected\":[";for(unsigned i=0;i<bestselected[j].size();i++)out<<(i?",":"")<<bestselected[j][i];out<<"]}";}out<<"]}\n";
 std::cout<<"axes="<<limit<<" configurations="<<seen.size()<<" cases="<<cases<<" elapsed="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<" minima:";for(auto v:minimum)std::cout<<' '<<v;std::cout<<'\n';
 return 0;
}

int main(int argc,char**argv){try{return run(argc,argv);}catch(int code){std::cerr<<"graph/cut invariant rejected: "<<code<<"\n";return 1;}catch(const std::exception&error){std::cerr<<error.what()<<"\n";return 1;}}
