// Exact source-bound native assembly of the pinned source527 physical word.
// Public finite ordinary-leaf induction is repeated four times, with all gaps checked.
#define main inherited_native_pricing_main
#include "rational-pricing.hpp"
#undef main
int main(int argc,char**argv){try{
 need(argc==7,"source527-assembly RAW BANKS COMPLEX_PROFILE FINITE NATIVE_BANKS OUT");
 J raw=read(argv[1]),banks=read(argv[2]),finite=read(argv[4]);
 need(raw.at("physical_R")==16587&&raw.at("source_aliases")==527,"source527 exact physical binding");
 J bank=banks.contains("banks")?banks["banks"]:banks;
 long long literalW=bank.at("literal_stock");need(literalW==1304935&&bank.at("physical_replicas")==60&&bank.at("assignments")==4976100,"actual stageprivate banks");
 std::map<int,long long> hist;
 for(auto it=raw.at("five_stage_profile").at("histogram").begin();it!=raw.at("five_stage_profile").at("histogram").end();++it)hist[std::stoi(it.key())]=it.value();
 for(auto it=raw.at("auxiliary_entrance_rank_histogram").begin();it!=raw.at("auxiliary_entrance_rank_histogram").end();++it){int rank=5*std::stoi(it.key());need(hist[rank]==it.value().get<long long>(),"literal entrance completion count");hist.erase(rank);}
 J hh;long long mass=0,edges=0;for(auto[k,n]:hist){need(n>0&&k>0&&k<=50,"paid raw rank");hh[std::to_string(k)]=12*n;mass+=12*k*n;edges+=12*n;}
 J pj={{"m",120},{"W",literalW/5},{"N",52800},{"L",0},{"total_rank",mass},{"maxchild",50},{"child_multiplicities",hh}};
 need(literalW%5==0&&mass==31265640&&mass==120*(literalW/5)-52800,"normalization binds physical rank bill");
 P bit=prepare(pj),complex=prepare(read(argv[3]));Saved bs=certify(bit,true),cs=certify(complex,false);
 Q c=bs.a,a(384599,ten(10)),b=cs.a;J chain=J::array(),gaps=J::array();chain.push_back(a.str());
 J nativeBanks=read(argv[5]);Q originalInvoice=jq(bank.at("conservative_extra_selector_calls")),invoice=jq(nativeBanks.at("selector_calls"));need(originalInvoice==Q(525064856400LL)&&invoice==Q(656433896400LL)&&invoice<Q(Z(1)<<40,1),"full fresh native stageprivate selector invoice");need(nativeBanks.at("literal_physical_stock")==literalW&&nativeBanks.at("actual_dirty_roles")==16587&&nativeBanks.at("assignments")==4976100,"fresh native literal bank binding");
 J inventory=finite.at("paid_inventory");need(inventory.at("literal_stock")==literalW&&inventory.at("physical_replicas")==60&&inventory.at("rank_mass")==5*mass&&inventory.at("positive_rank_children")==5*edges,"literal finite profile");
 Z coefficient=Z(jq(inventory["unit_expanded_additions"]).str())+Z(jq(inventory["high_affine_factors"]).str())+Z(jq(inventory["low_transposition_coefficient"]).str())+Z(jq(inventory["generic_wrappers"]).str())+Z(jq(inventory["matrix_preparation"]).str())+16*Z(120)*120*120+120*60+5*edges+525064856400LL+1;
 need(Q(coefficient,1)==jq(finite.at("q_power_bound").at("coefficient")),"public literal finite coefficient independently reproduced");coefficient+=656433896400LL-525064856400LL;need(coefficient<(Z(1)<<80),"larger native setup invoice fully charged");
 need(Q(Z(2)*120*120*120,1)*Q(ten(16),1)<Q(Z(1)<<80,1),"inherited rare-class strict bound");
 for(int j=0;j<4;j++){
  Q next=(Q(1)-c)*c+c*a;
  std::map<std::string,Q> gs={{"atom",c-next},{"borrowing",Q(1)-next-c},{"remainder",Q(1)-next-c*(Q(1)-a)},{"stock",Q(1)-c}};
  Q delta(1);J gd;for(auto[k,v]:gs){need(v>Q(0),"strict ordinary finite gap "+k);delta=mn(delta,v);gd[k]=v.str();}
  need(a<next&&next<c&&c<Q(1)-next,"acyclic finite ordinary-level composition");
  Z logCoef=boost::multiprecision::msb(coefficient)+1;
  Z cut1=ceilz(Q(36)/(delta*delta)),cut2=ceilz(Q(2*(logCoef+4),1)/delta);Z cut=cut1>cut2?cut1:cut2;
  need(Q(cut,1)*delta*delta>=Q(36)&&Q(cut,1)*delta>=Q(2*(logCoef+4),1),"constructive finite cutoff");
  gaps.push_back(J{{"stage",j+1},{"gaps",gd},{"minimum_gap",delta.str()},{"charged_coefficient",coefficient.convert_to<std::string>()},{"cutoff_log2_at_charged_coefficient",cut.convert_to<std::string>()},{"inherited_constant_rule","Multiply the charged coefficient by all primitive and preceding ordinary-level constants before computing the same explicit cutoff; these are conditional inherited finite constants, not functions of input length."}});
  a=next;chain.push_back(a.str());
 }
 Q eta(1,ten(24)),beta=eta;need(a<(Q(1)-beta)*b,"complex supplier above ordinary bit saving");
 Q literal(1),rowgap(1000000);rowgap=rowgap-Q(51*20161,25);
 Q q=a*(Q(1)-Q(2)*eta),minimum=(Q(1)-eta)*q/(Q(1)+q);Q k(ceilz(minimum*Q(ten(18),1))-1,ten(18));
 J root=assembly(a,b,k,eta,beta,literal,rowgap);bool bad=false;try{assembly(a,b,k+Q(1,ten(18)),eta,beta,literal,rowgap);}catch(const std::exception&){bad=true;}need(bad,"adjacent outer grid rejected");
 J result={{"status","PASS_NATIVE_SOURCE527_LITERAL_FINITE_FOUR_LEVEL_ASSEMBLY"},{"bit_profile",profilej(bit)},{"complex_profile",profilej(complex)},{"bit",bs.j},{"complex",cs.j},{"ordinary_chain",chain},{"ordinary_gap_ledger",gaps},{"a_bit",a.str()},{"a_complex",b.str()},{"finite_bridge_guards",{{"literal_scalar_guard",literal.str()},{"row_product_gap",rowgap.str()}}},{"finite_literal_coefficient",coefficient.convert_to<std::string>()},{"native_selector_invoice",invoice.str()},{"physical_replicas",60},{"literal_stock",literalW},{"moment_divisor",5},{"assembly",root},{"adjacent_kappa_rejected",bad},{"kappa",k.str()},{"kappa_decimal_numerator_grid_1e18",(k*Q(ten(18),1)).str()},{"scope","Native source-bound finite assembly, conditional on the unchanged public compiler, ordinary-leaf, row, prime and analytic interfaces; fourth finite leaf follows the same explicit acyclic induction, without assumed gadgets."}};
 std::ofstream(argv[6])<<result.dump(2)<<"\n";std::cout<<result["status"]<<" kappa="<<k.str()<<"\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<"\n";return 1;}}
