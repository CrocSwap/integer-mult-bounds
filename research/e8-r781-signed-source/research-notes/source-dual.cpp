#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <tuple>
#include <vector>
#include "json.hpp"
using json=nlohmann::json;
struct Event{int t,s,frame,a,b,phase;};
int main(int argc,char**argv){json c;std::ifstream(argv[1])>>c;int v=c["v"],n=2*v+(int)c["R"];std::vector<Event> es;int phase=0;for(auto name:{"A","B"}){for(auto&g:c[name])for(auto&r:g[3]){int s=g[2],t=r[0];if(g[0]=="in")std::swap(s,t);es.push_back({t,s,g[1],r[1],r[2],phase});}phase++;}
 // A target read closes its preceding accumulation interval. Global elementary
 // order matters; immutable source columns let additions inside each such
 // interval be combined, without assuming arbitrary helper preconditioning.
 std::vector<int> reads(n);using Key=std::tuple<int,int,int,int>;std::vector<std::map<Key,int>> cols(v);bool readonly=true;
 for(auto&e:es){if(e.t<v)readonly=false;if(e.s<v){int z=e.a*(6/e.b);if(6%e.b){std::cerr<<"denominator";return 2;}cols[e.s][{e.t,reads[e.t],e.frame,e.phase}]+=z;}reads[e.s]++;}
 if(!readonly){std::cerr<<"source-written";return 2;}
 auto cost=[](auto&row){int k=0;for(auto&[token,a]:row)k+=std::abs(a)/std::gcd(std::abs(a),6);return k;};
 std::vector<json> results;int qs[6][2]={{1,1},{-1,1},{2,1},{-2,1},{1,2},{-1,2}};
 for(int x=0;x<v;x++)for(int y=0;y<v;y++)if(x!=y)for(auto&qd:qs){auto a=cols[x];auto&b=cols[y];int removed=0,created=0;bool valid=true;for(auto&[token,bv]:b){int num=bv*qd[0];if(num%qd[1]){valid=false;break;}int old=a[token];a[token]+=num/qd[1];if(old&&a[token]==0)removed++;if(!old&&a[token])created++;}if(!valid)continue;int gain=cost(cols[x])-cost(a)-2; // two source-source wrapper adds charged at primitive level
 if(gain>0)results.push_back(json{{"x",x},{"y",y},{"q_num",qd[0]},{"q_den",qd[1]},{"original_x_unit_numerator_adds",cost(cols[x])},{"new_x_unit_numerator_adds",cost(a)},{"net_primitive_gain_after_two_wrappers",gain},{"tokens_removed",removed},{"tokens_created",created},{"source_frames_start",{c["start"][x],c["start"][y]}},{"source_frames_final",{c["final"][x],c["final"][y]}}});}
 std::sort(results.begin(),results.end(),[](auto&a,auto&b){return a["net_primitive_gain_after_two_wrappers"].template get<int>()>b["net_primitive_gain_after_two_wrappers"].template get<int>();});
 json out={{"status","BOUNDED_SOURCE_DUAL_ALGEBRAIC_CANDIDATES_NOT_PAID_ADMISSION"},{"pairs_tested",v*(v-1)*6},{"read_only_sources",readonly},{"candidates",results},{"scope","Exact source-token algebra is a sufficient construction when wrappers/frame paths and dirty decoder are explicitly compiled and charged. Primitive savings do not certify paid child saving or kappa; source writes require a changed cleanup/K construction."}};std::ofstream(argv[2])<<out.dump(2)<<"\n";std::cout<<results.size()<<" candidates\n";if(results.size())std::cout<<results[0].dump()<<"\n";
}

