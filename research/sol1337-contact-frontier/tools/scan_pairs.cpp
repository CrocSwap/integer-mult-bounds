// Apache-2.0; substantial OpenAI Codex assistance.
// Bounded immutable baseline scan, not a supplier certificate.
#define main retained_discovery_main
#include "../vendor/dynamic_neighbors.cpp"
#undef main
#include <map>
#include <iomanip>
V pair_axes(const V& a,const V& b){
 V intersection;auto annihilator=ann(b);
 for(unsigned mask=1;mask<512;mask++){unsigned x=0;for(int j=0;j<9;j++)if(mask>>j&1)x^=a[j];if(contains(annihilator,x))intersection.push_back(x);}
 intersection=basis(intersection);V full=intersection,quotient;
 for(int j=0;j<18;j++){V trial=full;trial.push_back(1u<<j);if(basis(trial).size()>full.size()){full.push_back(1u<<j);quotient.push_back(1u<<j);}}
 V sums(1u<<quotient.size()),axes;
 for(unsigned mask=1;mask<sums.size();mask++){unsigned j=std::countr_zero(mask);sums[mask]=sums[mask&(mask-1)]^quotient[j];unsigned x=sums[mask];axes.push_back(x);for(auto i:intersection)if(symp(x,i)){axes.push_back(x^i);break;}}
 unsigned r=9-intersection.size();if(axes.size()!=(1u<<(10+r))-(1u<<(2*r))-1)throw 11;
 return axes;
}
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
 std::map<std::pair<int,int>,int> pairs;
 for(const auto& t:edges)if(!fixed[t.a]&&!fixed[t.b]&&t.a!=t.b){if(t.map)throw 12;pairs[{std::min(t.a,t.b),std::max(t.a,t.b)}]=t.r;}
 int bestsecond=-1;
 for(const auto& [ab,distance]:pairs){
  int node=ab.first,second=ab.second;V affected=adj[node];for(auto ei:adj[second])if(std::find(affected.begin(),affected.end(),ei)==affected.end())affected.push_back(ei);
  auto axes=pair_axes(lags[node],lags[second]);
  for(auto axis:axes){
   std::array<int,10> delta{};V changed=lags[node],changedsecond=lags[second];turn(changed,axis);turn(changedsecond,axis);double score=0;
   for(auto ei:affected){
    const auto& t=edges[ei];const V& left=t.a==node?changed:(t.a==second?changedsecond:lags[t.a]);const V& right=t.b==node?changed:(t.b==second?changedsecond:lags[t.b]);
    V both=map(maps[t.map],left);both.insert(both.end(),right.begin(),right.end());int actual=(int)basis(both).size()-9;
    if((t.a==node&&t.b==second)||(t.a==second&&t.b==node)){if(actual!=t.r)throw 13;}
    delta[actual]++;delta[t.r]--;score+=pw[actual]-pw[t.r];
   }
   classes[delta]++;cases++;if(score< -1e-10)negative++;if(std::abs(score)<1e-12)neutral++;
   if(score<best){best=score;bestnode=node;bestsecond=second;bestaxis=axis;}
  }
 }
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"{\"scope\":\"complete simultaneous-transvection neighbors at all adjacent newly-variable retained-center contacts; every other node fixed\",\"cases\":"<<cases<<",\"negative_float_screen\":"<<negative<<",\"neutral_float_screen\":"<<neutral<<",\"best_float_delta\":"<<best<<",\"best_node\":"<<bestnode<<",\"best_second\":"<<bestsecond<<",\"best_axis\":"<<bestaxis<<",\"rank_delta_classes\":[";
 bool first=true;for(const auto& [d,count]:classes){if(!first)out<<',';first=false;out<<"{\"count\":"<<count<<",\"delta\":[";for(int r=0;r<=9;r++)out<<(r?",":"")<<d[r];out<<"]}";}out<<"]}\n";
 std::cout<<"cases="<<cases<<" classes="<<classes.size()<<" negative="<<negative<<" neutral="<<neutral<<" best="<<best<<"\n";
 return 0;
}
