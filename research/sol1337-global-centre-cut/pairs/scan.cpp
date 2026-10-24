// Apache-2.0. Substantial OpenAI Codex assistance.
// Bounded opposite-neighbour pair grammar; no physical supplier admission.
#define main predecessor_discovery_main
#include "dynamic_neighbors.cpp"
#undef main
#include <map>
#include <set>
#include <iomanip>
int run_pair(int argc,char**argv){
 if(argc!=3)return 2;
 std::ifstream in(argv[1]);int n,f,m,e;in>>n>>f>>m>>e;
 std::vector<int>frames(n),fixed(n);for(int i=0;i<n;i++)in>>frames[i]>>fixed[i];
 std::vector<V>fs(f,V(9)),maps(m,V(18));for(auto&v:fs)for(auto&x:v)in>>x;for(auto&v:maps)for(auto&x:v)in>>x;
 std::vector<Edge>edges(e);std::vector<std::vector<int>>adj(n);std::vector<int>pairs;std::set<std::pair<int,int>>distinct;
 std::array<int,10>baseline{};
 for(int i=0;i<e;i++){auto&t=edges[i];in>>t.a>>t.b>>t.r>>t.sign>>t.map;if(t.sign!=1)throw 10;baseline[t.r]++;adj[t.a].push_back(i);adj[t.b].push_back(i);
  if(!fixed[t.a]&&!fixed[t.b]&&frames[t.a]==0&&frames[t.b]==0){if(t.r||t.map)throw 11;pairs.push_back(i);distinct.insert(std::minmax(t.a,t.b));}}
 if(!in||pairs.size()!=256||distinct.size()!=256)throw 12;
 for(int r=1;r<=9;r++){int expected[10]={0,2201,412,510,127,40,0,0,8,0};if(baseline[r]!=expected[r])throw 13;}
 for(int i=0;i<9;i++)if(fs[0][i]!=(1u<<(9+i)))throw 14;
 std::map<std::string,int>neighbor_keys;int geometry=0;
 auto key=[](V v){v=basis(v);std::string s;for(auto x:v){s+=std::to_string(x);s+=',';}return s;};
 auto rank=[](V left,const V&right){left.insert(left.end(),right.begin(),right.end());return int(basis(left).size())-9;};
 std::map<std::array<int,10>,int>profiles;
 long long count=0,edge_checks=0;double best=1e100;int best_pair=-1,best_x=0,best_order=0;std::array<int,10>best_d{};
 std::array<long long,10>min_prefix;min_prefix.fill(1000000000);std::array<int,10>prefix_negative{};
 for(unsigned x=1;x<512;x++){
  unsigned z=1u<<std::countr_zero(x);V alt[2]={fs[0],fs[0]};turn(alt[0],x);turn(alt[1],x|(z<<9));
  if(rank(fs[0],alt[0])!=1||rank(fs[0],alt[1])!=1||rank(alt[0],alt[1])!=1)throw 15;
  // Both intersections are the same exact kernel, and have dimension eight.
  V kernel;for(unsigned v=1;v<512;v++)if(!(std::popcount(x&v)&1))kernel.push_back(v<<9);kernel=basis(kernel);if(kernel.size()!=8)throw 16;
  for(auto v:kernel)for(auto&l:alt){V both=l;both.push_back(v);if(basis(both).size()!=9)throw 17;}
  for(auto&l:alt){auto k=key(l);if(neighbor_keys.count(k))throw 18;neighbor_keys[k]=x;}
  geometry++;
  for(int pi:pairs){const auto&p=edges[pi];std::vector<int>incident=adj[p.a];incident.insert(incident.end(),adj[p.b].begin(),adj[p.b].end());std::sort(incident.begin(),incident.end());incident.erase(std::unique(incident.begin(),incident.end()),incident.end());
   for(int order=0;order<2;order++){
    std::array<int,10>d{};
    for(int ei:incident){const auto&t=edges[ei];V left=t.a==p.a?alt[order]:t.a==p.b?alt[1-order]:fs[frames[t.a]];
     V right=t.b==p.a?alt[order]:t.b==p.b?alt[1-order]:fs[frames[t.b]];
     int r=rank(map(maps[t.map],left),right);if(r<0||r>9)throw 19;d[t.r]--;d[r]++;edge_checks++;
    }
    long long mass=0;double value=0;for(int r=0;r<=9;r++){mass+=r*d[r];if(r)value+=d[r]*std::pow(r,1-.0030217758);}
    if(value<best){best=value;best_pair=pi;best_x=x;best_order=order;best_d=d;}
    for(int j=1;j<=9;j++){long long w=0;for(int r=0;r<=9;r++)w+=d[r]*std::min(j,r);min_prefix[j]=std::min(min_prefix[j],w);if(w<0)prefix_negative[j]++;}
    profiles[d]++;count++;
   }
  }
 }
 if(count!=261632||geometry!=511||neighbor_keys.size()!=1022)throw 20;
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"{\"cases\":"<<count<<",\"hyperplane_groups\":"<<geometry<<",\"distinct_neighbours\":"<<neighbor_keys.size()<<",\"distinct_internal_pairs\":"<<pairs.size()<<",\"exact_incident_rank_checks\":"<<edge_checks<<",\"theta\":\"0.9969782242\",\"floating_discovery_minimum_paid_delta\":"<<best<<",\"best_edge\":"<<best_pair<<",\"best_endpoints\":["<<edges[best_pair].a<<','<<edges[best_pair].b<<"],\"best_x\":"<<best_x<<",\"best_order\":"<<best_order<<",\"best_delta\":[";
 for(int r=0;r<=9;r++){out<<(r?",":"")<<best_d[r];}
 out<<"],\"minimum_prefix_deltas\":[";for(int j=1;j<=9;j++)out<<(j>1?",":"")<<min_prefix[j];out<<"],\"negative_prefix_cases\":[";for(int j=1;j<=9;j++)out<<(j>1?",":"")<<prefix_negative[j];out<<"],\"profiles\":[";
 bool first=true;for(auto&[d,c]:profiles){if(!first)out<<',';first=false;out<<"{\"count\":"<<c<<",\"delta\":[";for(int r=0;r<=9;r++)out<<(r?",":"")<<d[r];out<<"]}";}out<<"]}\n";
 std::cout<<"cases="<<count<<" exact_edge_checks="<<edge_checks<<" profiles="<<profiles.size()<<" best="<<best<<"\n";return 0;
}
int main(int argc,char**argv){try{return run_pair(argc,argv);}catch(int code){std::cerr<<"exact invariant rejected "<<code<<"\n";return 1;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
