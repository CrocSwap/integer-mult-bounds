// Apache-2.0; substantial OpenAI Codex assistance.
// Bounded immutable baseline scan, not a supplier certificate.
#define main retained_discovery_main
#include "../vendor/dynamic_neighbors.cpp"
#undef main
#include <map>
#include <iomanip>
int main(int argc,char** argv){
 if(argc!=3)return 2;
 std::ifstream in(argv[1]);int n,f,m,e;in>>n>>f>>m>>e;
 std::vector<int> frame(n),fixed(n);for(int i=0;i<n;i++)in>>frame[i]>>fixed[i];
 std::vector<V> fs(f,V(9)),maps(m,V(18)),invs,lags;
 for(auto& b:fs)for(auto& x:b)in>>x;
 for(auto& b:maps){for(auto& x:b)in>>x;invs.push_back(inverse(b));}
 for(auto k:frame)lags.push_back(fs[k]);
 std::vector<Edge> edges(e);std::vector<V> adj(n);
 for(int i=0;i<e;i++){auto& t=edges[i];in>>t.a>>t.b>>t.r>>t.sign>>t.map;if(t.sign!=1)return 3;adj[t.a].push_back(i);adj[t.b].push_back(i);}
 if(!in)return 4;
 std::map<std::array<int,10>,int> classes;
 double pw[10];for(int r=0;r<=9;r++)pw[r]=std::pow(r,1-.00302177585);
 double best=1e99;int bestnode=-1,bestaxis=0,cases=0,negative=0,neutral=0;
 for(int node=0;node<n;node++)if(!fixed[node]){
  std::vector<Local> local;
  for(int ei:adj[node]){auto& t=edges[ei];auto other=t.a==node?map(invs[t.map],lags[t.b]):map(maps[t.map],lags[t.a]);auto both=other;both.insert(both.end(),lags[node].begin(),lags[node].end());int r=(int)basis(both).size()-9;if(r!=t.r)return 5;local.push_back(make_local(lags[node],other,r,t.sign));}
  auto axes=canonical_transvection_axes(lags[node]);if(axes.size()!=1022)return 6;
  for(auto axis:axes){
   std::array<int,10> delta{};V changed=lags[node];turn(changed,axis);double score=0;
   for(unsigned j=0;j<adj[node].size();j++){
    const auto& t=edges[adj[node][j]];int predicted=local[j].r+change(local[j],axis);
    V both=map(maps[t.map],t.a==node?changed:lags[t.a]);auto& right=t.b==node?changed:lags[t.b];both.insert(both.end(),right.begin(),right.end());int actual=(int)basis(both).size()-9;
    if(actual!=predicted)return 7;
    delta[actual]++;delta[t.r]--;score+=pw[actual]-pw[t.r];
   }
   classes[delta]++;cases++;if(score< -1e-10)negative++;if(std::abs(score)<1e-12)neutral++;
   if(score<best){best=score;bestnode=node;bestaxis=axis;}
  }
 }
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"{\"scope\":\"all single-transvection neighbors at 184 newly variable retained-center contacts; every other node fixed\",\"cases\":"<<cases<<",\"negative_float_screen\":"<<negative<<",\"neutral_float_screen\":"<<neutral<<",\"best_float_delta\":"<<best<<",\"best_node\":"<<bestnode<<",\"best_axis\":"<<bestaxis<<",\"rank_delta_classes\":[";
 bool first=true;for(const auto& [d,count]:classes){if(!first)out<<',';first=false;out<<"{\"count\":"<<count<<",\"delta\":[";for(int r=0;r<=9;r++)out<<(r?",":"")<<d[r];out<<"]}";}out<<"]}\n";
 std::cout<<"cases="<<cases<<" classes="<<classes.size()<<" negative="<<negative<<" neutral="<<neutral<<" best="<<best<<"\n";
 return 0;
}
