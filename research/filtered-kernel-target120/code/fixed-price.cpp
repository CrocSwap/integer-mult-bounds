#include <boost/multiprecision/cpp_int.hpp>
#include "json.hpp"
#include <fstream>
#include <iostream>
#include <map>
#include <cmath>
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <stdexcept>
using namespace std;using namespace boost::multiprecision;using J=nlohmann::json;using Q=cpp_rational;using I=cpp_int;
Q parse(string s){auto p=s.find('/');return p==string::npos?Q(I(s)):Q(I(s.substr(0,p)))/I(s.substr(p+1));}
Q get(J j){return j.is_string()?parse(j.get<string>()):Q(j.get<long long>());}
J load(string p){ifstream f(p);if(!f)throw runtime_error(p);J j;f>>j;return j;}
Q down(Q x){I d=I(1)<<224;return Q(I(numerator(x)*d/denominator(x)))/d;}
Q up(Q x){I d=I(1)<<224;return Q(I((numerator(x)*d+denominator(x)-1)/denominator(x)))/d;}
pair<Q,Q> logbase(Q x){Q z=(x-1)/(x+1),t=z,s=0;for(int i=0;i<48;i++){s+=2*t/(2*i+1);t*=z*z;}return {down(s),up(s+2*t/(97*(1-z*z)))};}
pair<Q,Q> logbound_raw(Q x){int k=0;while(x>=2){x/=2;k++;}auto [l,u]=logbase(x);auto [a,b]=logbase(Q(2));return {down(l+k*a),up(u+k*b)};}
pair<Q,Q> logbound(Q x){static map<Q,pair<Q,Q>> cache;auto it=cache.find(x);if(it!=cache.end())return it->second;return cache[x]=logbound_raw(x);}
pair<Q,Q> expbound(Q l,Q u){if(l<0||u>=Q(1)/10)throw runtime_error("exp domain");Q tl=1,tu=1,sl=1,su=1;for(int i=1;i<=32;i++){tl=down(tl*l/i);tu=up(tu*u/i);sl=down(sl+tl);su=up(su+tu);}return {sl,up(su+tu*u/33/(1-u/34))};}
pair<Q,Q> moment(map<int,long long>H,int m,int W,Q a){Q lo=0,hi=0;for(auto [r,n]:H){auto[l,u]=logbound(Q(m)/r);auto[e,f]=expbound(a*l,a*u);Q w=Q(r*n)/(m*W);lo+=w*e;hi+=w*f;}return {down(lo),up(hi)};}
map<string,Q> assembly(Q a,Q b,Q k,Q guard,Q rowgap){Q eta=Q(1)/parse("1000000000000000000000000"),beta=Q(1)/parse("1000000000"),tau=1-a,sigma=1-b,q=a*(1-2*eta),lp=1-q,lam=(tau+lp)/2,c=q+eta/4,eps=(1-eta)/(1+q),mi=eps*q,r=(mi+1-eps)/2,delta=eta/8,internal=tau+(1-beta)*max(Q(sigma-tau),Q(0)),leaf=sigma+beta*(1-sigma);map<string,Q>s={
{"bit_positive",a},{"complex_above_bit",b-a},{"complex_below_1_32",Q(1)/32-b},{"beta_positive",beta},{"beta_below_one",1-beta},{"leaf_above_bit",(1-beta)*b-a},
{"q_positive",q},{"q_below_internal",1-internal-q},{"q_below_leaf",1-leaf-q},{"c_positive",c},{"c_below_one",1-c},{"reservations",c-q},{"lambda_tau",lam-tau},{"lambda_sigma",lam-sigma},{"lambda_internal",lam-internal},{"lp_lambda",lp-lam},{"compact_leaf",lp-leaf},{"compact_reservations",lp-(1-c)},{"lp_below_one",q},
{"eps_positive",eps},{"eps_below_one",1-eps},{"guard_width",1-eps},{"K_geometry",1-eps*(1+c)},{"K_log",eps*c},{"record_suffix",1-eps},{"phase_local",1-eps-delta},{"phase_boundary",r-delta},{"gamma_sublinear",1-eps-r},{"cell_band",eps-(1-r)/2},{"prime_pack",1-eps},{"alpha_positive",r},{"alpha_one",1-r},{"alpha_fourth",Q(1)/4-r},{"delta_positive",delta},{"delta_eighth",Q(1)/8-delta},{"record_fallback",eps-a},{"small_field",1-eps-mi},{"artificial",8-eps+r-delta-mi},{"literal_guard",guard},{"row_gap",rowgap}};
vector<Q> margins={1-eps,a,mi,a,min(Q(1-eps-delta),Q(r-delta)),1-eps-delta,eps};for(int i=0;i<7;i++)s["margin"+to_string(i)]=margins[i]-k;return s;}

// Native port of PR261 fixed_prime_math.py; physical input is supplied, not assumed proved here.
using D=cpp_dec_float_100;
void need(bool b,string s){if(!b)throw runtime_error(s);}
I integer(J x){return x.is_string()?I(x.get<string>()):I(x.get<long long>());}
I ceilq(Q x){need(x>=0,"ceil domain");return I((numerator(x)+denominator(x)-1)/denominator(x));}
const I prime=(I(1)<<127)-1,grid("1000000000000000000000000000");
const Q rho=Q(3456000)/prime,eta=Q(1)/I("1000000000000000000000000");
Q floor30(Q x){I g("1000000000000000000000000000000");return Q(I(numerator(x)*g/denominator(x)))/g;}
Q ceil30(Q x){I g("1000000000000000000000000000000");return Q(ceilq(x*g))/g;}
pair<Q,Q> log2engine(Q x){static map<Q,pair<Q,Q>>cache;if(cache.count(x))return cache[x];Q original=x;int k=0;while(x>2){x/=2;k++;}auto unit=[](Q x){Q z=(x-1)/(x+1),t=z,s=0;for(int j=0;j<80;j++){s+=2*t/(2*j+1);t*=z*z;}return pair<Q,Q>{s,s+2*t/(161*(1-z*z))};};auto[a,b]=unit(x);auto[c,d]=unit(2);return cache[original]={floor30(a+k*c),ceil30(b+k*d)};}
pair<Q,Q> exp2engine(Q x){need(x>=0&&x<1,"second exp domain");Q t=1,s=1;for(int j=1;j<=12;j++){t*=x/j;s+=t;}return{s,s+t*x/13/(1-x/14)};}
pair<Q,Q> fixedmoment(map<int,long long>H,int W,Q c,int engine){long long count=0;for(auto[r,n]:H)count+=n;if(engine==1){auto[a,b]=moment(H,120,W,c);auto[l,u]=logbound(120);auto[e,f]=expbound(c*l,c*u);Q fallback=Q(3840*count)/W*rho;return{down(a+fallback*e),up(b+fallback*f)};}Q a=0,b=0;for(auto[r,n]:H){auto[l,u]=log2engine(Q(120)/r);a+=Q(r*n)/(120*W)*exp2engine(c*l).first;b+=Q(r*n)/(120*W)*exp2engine(c*u).second;}auto[l,u]=log2engine(120);Q fallback=Q(3840*count)/W*rho;return{floor30(a)+fallback*exp2engine(c*l).first,ceil30(b)+fallback*exp2engine(c*u).second};}
Q kap(Q a){Q q=a*(1-2*eta),v=(1-eta)*q/(1+q);return Q(I((numerator(v)*grid-1)/denominator(v)))/grid;}
J sj(map<string,Q> x){J j=J::object();for(auto[k,v]:x)j[k]=v.str();return j;}
int main(int argc,char**argv){try{
 need(argc==4,"usage: fixed-price PRICE_JSON FINITE_INVOICE_JSON OUTPUT_JSON");J raw=load(argv[1]),invoice=load(argv[2]),profile=raw.contains("cohort_candidate")?raw["cohort_candidate"]:raw;
 I ll=4;for(int k=0;k<125;k++)ll=(ll*ll-2)%prime;need(ll==0,"Lucas Lehmer");for(int p=2;p*p<=127;p++)need(127%p!=0,"exponent primality");need(rho<Q(1)/I("10000000000000000")&&prime>(I(1)<<80),"prime bounds");
 map<int,long long>H;long long count=0,mass=0;int W=profile["stock"].get<int>();need(W>0,"positive stock");for(auto it=profile["histogram"].begin();it!=profile["histogram"].end();it++){int r=stoi(it.key());long long n=integer(it.value()).convert_to<long long>();need(r>0&&r<60&&n>0,"half shrink children");H[r]=n;count+=n;mass+=r*n;}
 need(integer(profile["calls"])==count&&integer(profile["rank_mass"])==mass&&integer(profile["deficit"])==120LL*W-mass,"profile inventory");
 // High precision floating only proposes a point; both exact engines must separate it.
 vector<pair<D,D>>terms;for(auto[r,n]:H)terms.push_back({D(r*n)/D(120LL*W),log(D(120)/D(r))});D fall=D(3840*count)/W*D(3456000)/D(prime.convert_to<string>()),l=0,u=D(".003");for(int i=0;i<240;i++){D c=(l+u)/2,v=fall*exp(c*log(D(120)));for(auto[t,z]:terms)v+=t*exp(c*z);if(v<1)l=c;else u=c;}
 I ticks=(l*D(grid.convert_to<string>())).convert_to<I>();Q c=Q(ticks)/grid,next=c+Q(1)/grid;J bounds=J::array();Q momentupper;
 for(int engine:{1,2}){auto[a,b]=fixedmoment(H,W,c,engine);auto[d,e]=fixedmoment(H,W,next,engine);need(b<1&&d>1,"exact coarse adjacent bracket");bounds.push_back({{"engine",engine},{"lower",a.str()},{"upper",b.str()},{"next_lower",d.str()},{"next_upper",e.str()}});if(engine==1)momentupper=b;}
 I replicas=integer(invoice["physical_replicas"]);need(replicas>0&&replicas%40==0,"replica multiple of 40"); I stock=integer(invoice["literal_stock"]),calls=0,lmass=0;need(stock==5*W&&integer(invoice["normalized_stock"])==W,"literal stock");need(invoice["literal_histogram"].size()==H.size(),"literal histogram size");for(auto[r,n]:H){I nn=integer(invoice["literal_histogram"].at(to_string(r)));need(nn==5*n,"literal histogram");calls+=nn;lmass+=r*nn;}
 need(lmass==integer(invoice["literal_rank_mass"])&&integer(invoice["literal_deficit"])==120*stock-lmass&&calls==integer(invoice["positive_rank_children"]),"literal ledger");
 I chartBound=max(I(548),integer(invoice["new_chart_factor_max"])),normalizerBound=chartBound+239; need(chartBound<=1024,"bounded exact chart arithmetic"); I coeff=integer(invoice["full_counted_primitive_coefficient"]),units=integer(invoice["global_unit_expanded_additions"]),routes=integer(invoice["route_families"]),selectors=integer(invoice["extra_selector_calls"]);
 need(units>=integer(invoice["global_weighted_additions"])&&integer(invoice["global_weighted_additions"])>0,"positive operation costs"); need(integer(invoice["new_chart_factor_max"])>0&&integer(invoice["payload_signed_prefix_upper"])>0,"positive chart payload bounds"); need(selectors==10*replicas*((stock-1)+I(16587)*120*normalizerBound),"selector bill");need(routes==replicas*(24*1760+10*16587),"route bill");
 I computed=units+routes*16*14401*14401+routes*(stock+24)+calls*(8*120*120+8)+calls*(128*I(240)*240*240)+16*I(120)*120*120+120*replicas+calls+selectors+1;
 need(coeff==computed&&coeff<(I(1)<<80)&&stock<prime,"all counted primitive terms");need(integer(invoice["normalizer_factor_bound"])==normalizerBound&&integer(invoice["new_chart_factor_max"])<=chartBound,"normalizer chart bounds");need(integer(invoice["external_complex_row_coefficient"])==20161&&integer(invoice["internal_row_coefficient"])==14401,"row constants");need(integer(invoice["payload_signed_prefix_upper"])<(I(1)<<104),"payload prefix");
 Q bit=parse("384599/10000000000"),cap=kap(c);J chain=J::array({bit.str()}),stages=J::array();int levels=0;while(true){Q old=bit;bit=(1-c)*c+c*old;need(old<bit&&bit<c&&c<1-bit,"ordinary finite induction");map<string,Q> gaps={{"atom",c-bit},{"borrowing",1-bit-c},{"remainder",1-bit-c*(1-old)},{"stock",1-c}};Q delta=1;for(auto[k,v]:gaps){need(v>0,"finite positive gaps");delta=min(delta,v);}int logcoeff=msb(coeff-1)+1;I cut=max(I(1),max(ceilq(36/(delta*delta)),ceilq(2*(4+logcoeff)/delta)));need(Q(cut)*delta*delta>=36&&Q(cut)*delta>=2*(4+logcoeff),"finite cutoff");stages.push_back({{"level",++levels},{"gaps",sj(gaps)},{"minimum_gap",delta.str()},{"log2_cutoff",cut.convert_to<string>()}});chain.push_back(bit.str());if(kap(bit)==cap)break;need(levels<20,"finite levels failed");}
 auto constraints=assembly(bit,parse("747454944651775/1000000000000000000"),cap,1,Q(1000000)-Q(51*20161)/25);need(constraints.size()==47,"47 constraints");for(auto[k,v]:constraints)need(v>0,"constraint "+k);J rejects=J::array();for(Q a:{bit,c}){auto test=assembly(a,parse("747454944651775/1000000000000000000"),cap+Q(1)/grid,1,Q(1000000)-Q(51*20161)/25);J bad=J::array();for(auto[k,v]:test)if(v<=0)bad.push_back(k);need(!bad.empty(),"adjacent kappa");rejects.push_back(bad);}
 Q linear=1-Q(mass)/(120*W)-rho*Q(3840*count)/W;need(linear>0&&momentupper<1,"moment admission");J margins=J::object();for(int i=0;i<7;i++)margins[to_string(i)]=Q(constraints["margin"+to_string(i)]+cap).str();
 J out={{"status","PASS_NATIVE_FIXED_PRIME_FINITE_AND_47_CONSTRAINTS"},{"scope","Conditional arithmetic on supplied physical inventory; counts and inherited all-size, compiler, common chart, restored-row, routing, precision/recovery and complex-reduction interfaces require their separate evidence."},{"prime",prime.convert_to<string>()},{"lucas_lehmer_iterations",125},{"lucas_lehmer_residue",ll.convert_to<string>()},{"rho",rho.str()},{"profile",profile},{"coarse",c.str()},{"coarse_bounds",bounds},{"ordinary_levels",levels},{"ordinary_chain",chain},{"finite_levels",stages},{"ordinary_bit",bit.str()},{"kappa",cap.str()},{"kappa_decimal",cap.convert_to<D>().str(40,std::ios_base::fixed)},{"strict_constraints",sj(constraints)},{"seven_margins",margins},{"adjacent_rejected_at_finite_and_cap",rejects},{"finite_invoice_retained",invoice},{"finite_coefficient_recomputed",computed.convert_to<string>()},{"linear_moment_slack",linear.str()},{"strict_moment_slack",Q(1-momentupper).str()},{"method","Native C++ exact rationals: independent 48-term/32-degree binary224 and 80-term/12-degree decimal30 engines; decimal100 only proposes exact checked coarse point."},{"finite_cutoff_scope","Computed coefficient is the full counted finite invoice. For inherited all-size C_full >= this coefficient, replace ceil(log2 C) with ceil(log2 C_full) in the displayed cutoff formula."}};
 ofstream(argv[3])<<out.dump(2)<<"\n";cout<<"PASS kappa "<<out["kappa_decimal"]<<" levels "<<levels<<"\n";
}catch(exception&e){cerr<<e.what()<<"\n";return 1;}}


