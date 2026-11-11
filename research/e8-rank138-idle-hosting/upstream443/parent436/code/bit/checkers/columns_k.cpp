// Generalization (Dylan Crow, with Anthropic Claude assistance): the copied-centre count is the macro NCOPY, defaulting to
// HDIM, so the unmodified PR #346/#352 build (no -DNCOPY) is exactly the original checker. The E8 bit word has 9
// retained totals at h = 8 (-DNCOPY=9).
// Bridged word B_K (DaysSky, assisted with Claude): the macro KPAIRS (default 2) sets the number of bank pairs; the
// schedule, the twin bridges and the terminal exchange are generated from PR #363's bridged.py rule:
//   stage 0,1,2 pair 1 forward/backward/forward; stage 2p-1, 2p pair p backward/forward (p = 2..K);
//   after stage 2p-3: X(p-1) += Xp, Yp -= Y(p-1); after stage 2p-2: Yp += Y(p-1), X(p-1) -= Xp;
//   after the last stage, for p = K..2: Y(p-1) -= Yp, Xp += X(p-1).
// KPAIRS = 2 reproduces the original five-stage tables and receipt (checked in verify.sh); KPAIRS = 3 is seven stages.
#ifndef NCOPY
#define NCOPY HDIM
#endif
#ifndef KPAIRS
#define KPAIRS 2
#endif
#include "json.hpp"
#include <map>
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;
#include <vector>
#include <array>
#include <fstream>
#include <iostream>
#include <chrono>
#include <stdexcept>
#include <cstring>
using J=nlohmann::json;
struct E{int kind,dst,src,c;};
void need(bool x,const char*s){if(!x)throw std::runtime_error(s);}
int main(int argc,char**argv){try{
need(argc==3,"usage RAW6_RECORDS OUTPUT");std::string pre=argv[1];int v=VPORTS,r=RHELP,loc=2*v+r,global=2*KPAIRS*v+r,temp=global;const int S=2*KPAIRS+1;
struct Raw{int op,a,b,c,f,z;};std::ifstream f(pre,std::ios::binary|std::ios::ate);size_t sz=f.tellg();need(sz%sizeof(Raw)==0,"stream alignment");std::vector<Raw>p(sz/sizeof(Raw));f.seekg(0);f.read((char*)p.data(),sz);std::vector<E>e;std::map<int,long long>H;for(auto q:p){if(q.op==0){if(q.f)H[q.f]++;}else if(q.op==1)e.push_back({0,q.a,q.b,q.c});else if(q.op==2){H[q.z]++;e.push_back({1,loc,q.a,0});}else if(q.op==3)e.push_back({2,loc,q.a,0});else need(false,"opcode");}
J prefix=J::array();cpp_int largestF=0,largestB=0;for(int rev=0;rev<2;rev++){std::vector<cpp_int>norms(loc+1,1);cpp_int maxrow=1;bool isopen=false;for(size_t z=0;z<e.size();z++){auto q=e[rev?e.size()-1-z:z];int k=q.kind;if(rev&&k)k=3-k;if(!k){norms[q.dst]+=std::abs(q.c)*norms[q.src];if(norms[q.dst]>maxrow)maxrow=norms[q.dst];}else if(k==1){need(!isopen,"boundcopy");norms[loc]=norms[q.src];isopen=true;}else {need(isopen,"bounderase");norms[loc]=0;isopen=false;}}need(!isopen,"prefix copy closure");if(rev)largestB=maxrow;else largestF=maxrow;prefix.push_back({{"reverse",bool(rev)},{"cancellation_free_signed_row_l1_upper",maxrow.convert_to<std::string>()},{"bits",boost::multiprecision::msb(maxrow)+1}});}
cpp_int payload=64*largestF*largestF*largestF*largestB*largestB;need(payload<(cpp_int(1)<<104),"payloadfiniteprefix2^104");
long long copies=0,adds=0,odd=0;bool open=false;int center=-1;long long reverseCopies=0;
for(auto q:e){need(q.kind>=0&&q.kind<=2,"kind");need(q.dst>=0&&q.dst<=loc,"local dst");if(q.kind==0){need(q.src>=0&&q.src<=loc&&q.dst!=q.src,"source distinct");need(q.dst!=loc,"copy immutable");need(q.src!=loc||open,"temp not open");if(open)need(q.dst!=center,"source changes inside copied-center block");adds++;odd+=q.c&1;}
else if(q.kind==1){need(!open&&q.dst==loc&&q.src>=0&&q.src<loc,"fresh copy shape");open=true;center=q.src;copies++;}
else{need(open&&q.dst==loc&&q.src==center,"discard original-source binding");open=false;center=-1;}}
need(!open&&copies==NCOPY,"center boundaries");
std::vector<std::array<int,2>>active;std::vector<bool>backward;std::vector<std::vector<std::array<int,3>>>after(S);
auto X=[](int p){return 2*(p-1);};auto Y=[](int p){return 2*(p-1)+1;};
for(int t=0;t<S;t++){int p=t<3?1:(t+1)/2;bool b=(t==1)||(t>=3&&t%2==1);backward.push_back(b);active.push_back(b?std::array<int,2>{Y(p),X(p)}:std::array<int,2>{X(p),Y(p)});}
for(int q=2;q<=KPAIRS;q++){after[2*q-3].push_back({X(q-1),X(q),1});after[2*q-3].push_back({Y(q),Y(q-1),-1});
 after[2*q-2].push_back({Y(q),Y(q-1),1});after[2*q-2].push_back({X(q-1),X(q),-1});}
for(int p=KPAIRS;p>=2;p--){after[S-1].push_back({Y(p-1),Y(p),-1});after[S-1].push_back({X(p),X(p-1),1});}
int nbridges=0;for(auto&a:after)nbridges+=a.size();need(nbridges==6*(KPAIRS-1),"twin bridge count");
size_t words=(global+63)/64;std::vector<unsigned long long>a((size_t)(global+1)*words);auto row=[&](int i){return a.data()+(size_t)i*words;};for(int i=0;i<global;i++)row(i)[i/64]|=1ull<<(i%64);
auto xo=[&](int d,int s){auto*x=row(d);auto*y=row(s);for(size_t j=0;j<words;j++)x[j]^=y[j];};
auto map=[&](int stage,int i){if(i<v)return active[stage][0]*v+i;if(i<2*v)return active[stage][1]*v+i-v;if(i<loc)return 2*KPAIRS*v+i-2*v;return temp;};
auto t0=std::chrono::steady_clock::now();J stages=J::array();
for(int stage=0;stage<S;stage++){bool rev=backward[stage];bool opened=false;long long cp=0,ad=0;auto step=[&](E q){int k=q.kind;if(rev&&k)k=3-k;int d=map(stage,q.dst),s=map(stage,q.src);if(k==0){if(q.c&1)xo(d,s);ad++;}else if(k==1){need(!opened,"fresh physical work opening");std::memcpy(row(temp),row(s),words*8);opened=true;cp++;}else{need(opened,"physical work closing");std::memset(row(temp),0,words*8);opened=false;}};
if(rev){for(auto it=e.rbegin();it!=e.rend();++it)step(*it);reverseCopies+=cp;}else for(auto q:e)step(q);need(!opened&&cp==NCOPY,"stage copied-center endpoint");
if(stage==0){for(int i=0;i<global;i++){auto*x=row(i);for(size_t w=0;w<words;w++){unsigned long long want=(w==(size_t)i/64?1ull<<(i%64):0);if(i>=v&&i<2*v&&w==(size_t)(i-v)/64)want^=1ull<<((i-v)%64);need(x[w]==want,"local defining-decoder full formal column");}}}
for(auto q:after[stage])for(int i=0;i<v;i++)xo(q[0]*v+i,q[1]*v+i);
stages.push_back({{"stage",stage},{"signed_inverse",rev},{"fresh_copies",cp},{"scalar_additions",ad}});std::cerr<<"stage "<<stage<<" PASS elapsed "<<std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count()<<"s\n";}
for(int bank=0;bank<2*KPAIRS;bank+=2)for(int i=0;i<v;i++)for(size_t w=0;w<words;w++)std::swap(row(bank*v+i)[w],row((bank+1)*v+i)[w]);
for(int i=0;i<=global;i++)for(size_t w=0;w<words;w++){unsigned long long want=(i<global&&w==(size_t)i/64?1ull<<(i%64):0);need(row(i)[w]==want,KPAIRS==2?"five-stage all physical formal columns":"bridged all physical formal columns");}
// Independent complete four-bank controls, each omitted bridge must change endpoint.
J controls=J::array();for(int skip=0;skip<nbridges;skip++){std::vector<unsigned>b(2*KPAIRS);for(int z=0;z<2*KPAIRS;z++)b[z]=1u<<z;int j=0;for(int s=0;s<S;s++){b[active[s][1]]^=b[active[s][0]];for(auto q:after[s]){if(j++!=skip)b[q[0]]^=b[q[1]];}}for(int z=0;z<2*KPAIRS;z+=2)std::swap(b[z],b[z+1]);bool failed=false;for(int z=0;z<2*KPAIRS;z++)failed|=b[z]!=(1u<<z);need(failed,"vacuous omitted bridge control");controls.push_back({{"omit_bridge",skip},{"rejected",true}});}
J out={{"status",KPAIRS==2?"PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL":"PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"},{"local_scalar_stream",pre},{"local_registers",loc},{"global_live_registers",global},{"formal_columns_checked",global},{"independent_dirty_registers",r},{"local_scalar_additions",adds},{"local_odd_scalar_additions",odd},{KPAIRS==2?"five_stage_additions":"stage_additions",S*adds},{"bridge_additions",6*(KPAIRS-1)*v},{"fresh_center_copies",S*NCOPY},{"reverse_fresh_center_copies",reverseCopies},{"copied_center_original_source_immutable",true},{"signed_reverse_semantics","Reverse ADD coefficient negated; reverse DISCARD is fresh COPY from recorded unchanged original center; reverse COPY is DISCARD. Each such block is inverse over every commutative coefficient ring, by elementary-shear induction."},{"scope","All independent physical input columns over F2, including all arbitrary helper dirt, restored; external copied-center work closes to zero. New cohort scalar lift uses actual signed coefficients and computed cancellation-free bounds; unchanged source527 signed decoder remains separate defining evidence. Physical projector routing and paid rank/bank receipts are independently bound, not inferred from scalar check."},{"stages",stages},{"signed_lift_prefix",prefix},{"payload_prefix_upper",payload.convert_to<std::string>()},{"payload_prefix_bits",boost::multiprecision::msb(payload)+1},{"new_Q_categories",{28,29}},{"local_raw_H",H},{"negative_controls",controls},{"seconds",std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count()}};std::ofstream(argv[2])<<out.dump(2);std::cout<<out.dump(2)<<"\n";
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 2;}}

