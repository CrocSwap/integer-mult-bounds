#define BOOST_MP_STANDALONE
#include <boost/multiprecision/cpp_int.hpp>
#include "json.hpp"
#include <fstream>
#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <chrono>
#include <climits>
using Z=boost::multiprecision::cpp_int;using J=nlohmann::json;
void need(bool b,const char*s){if(!b)throw std::runtime_error(s);}J load(const std::string&p){std::ifstream f(p);need(bool(f),"input");J j;f>>j;return j;}
struct Op{int a,b,n;};struct Root{int role,node;bool center;std::vector<int>targets;};struct Sink{int root,role,pivot;std::vector<int>targets,writes;};struct Pair{int a,b;std::vector<int>targets;};
int main(int argc,char**argv){try{
 auto started=std::chrono::steady_clock::now();need(argc==3,"usage bit-columns INPUT_FOLDER OUTPUT");
 std::string D=argv[1];J w=load(D+"/word_p12.json"),g=load(D+"/graph_p12.json"),k=load(D+"/kchron_p12.json"),sj=load(D+"/sinks.json");
 J adapter=load(D+"/ADAPTER.json");std::map<int,int>omitRole;for(auto r:adapter["new_roles"]){int d=r["dim"],s=r["role"];if(!omitRole.count(d))omitRole[d]=s;}J selection=load(D+"/BORROW.json");need(selection.size()==440,"borrow selection size");std::map<int,int>borrow,by_source,early;std::set<int>omitted;for(int k=0;k<(int)selection.size();k++){auto&r=selection[k];int role=r["role"],s=r["source"],i=r["early"],o=r["omit_copy"];need(borrow.emplace(role,s).second&&by_source.emplace(s,k).second&&early.emplace(i,k).second&&omitted.insert(o).second,"duplicate borrow contract");}need(w["borrowed_sources"]==selection,"word borrow metadata mismatch");J gaugeBorrow=load(D+"/GAUGE-BORROW.json");need(gaugeBorrow.size()==29,"gauge borrow selection size");need(w["gauge_source_aliases"]==gaugeBorrow,"typed gauge alias metadata mismatch");int gaugeControl=-1;for(int j=0;j<(int)gaugeBorrow.size();j++){auto&r=gaugeBorrow[j];int role=r["role"],s=r["source"];need(borrow.emplace(role,s).second&&by_source.emplace(s,-1-j).second,"duplicate gauge source contract");if(role==13088)gaugeControl=role;}need(gaugeControl==13088,"missing new source gauge control");std::set<int>wordOmitted;for(auto i:w["omitted_ops"])wordOmitted.insert(i.get<int>());need(wordOmitted==omitted,"omitted metadata mismatch");int v=g["v"],R=18908;std::vector<Op>ops;for(auto&o:w["ops"])ops.push_back({o[0],o[1],o[2]});int N=ops.size();std::vector<int>phase,rest;std::set<int>ps;for(auto i:w["phase1"]){phase.push_back(i);ps.insert(i.get<int>());}for(int i=0;i<N;i++)if(!ps.count(i))rest.push_back(i);
 std::map<int,int>source;for(auto&[n,s]:w["sources"].items())source[std::stoi(n)]=s;
 std::vector<int>phys(R);for(int i=0;i<R;i++)phys[i]=i;std::set<int>gauges,virtualOnly;for(auto z:w["gauges"])gauges.insert(z["role"].get<int>());
 for(auto p:w["pairs"]){phys[p[1].get<int>()]=p[0];virtualOnly.insert(p[1].get<int>());}
 std::vector<Root>roots;for(int i=0;i<(int)g["roots"].size();i++){auto r=g["roots"][i];roots.push_back({w["rootroles"][i],r["node"],r["kind"]=="center",r["targets"].get<std::vector<int>>()});}
 std::vector<Sink>sinks;std::set<int>removed,deletedRoots;std::map<int,int>bywrite,after;
 for(auto e:sj){int ri=e["root"],p=e["pivot"],s=roots[ri].role;Sink q{ri,s,p,roots[ri].targets,{}};for(int i=0;i<N;i++)if(ops[i].a==s)q.writes.push_back(i);need(!q.writes.empty(),"terminal writes");for(int i:q.writes){need(!ps.count(i),"terminal phase");bywrite[i]=sinks.size();}after[q.writes.back()]=sinks.size();removed.insert(s);deletedRoots.insert(ri);sinks.push_back(q);}
 std::vector<int>live,index(R,-1);for(int r=0;r<R;r++)if(!virtualOnly.count(r)&&!removed.count(r)&&!borrow.count(r)){index[r]=2*v+live.size();live.push_back(r);}
 need((int)live.size()==16645,"physical stock");int cols=2*v+live.size();
 std::vector<std::vector<int>>at(rest.size()+1);for(auto it=w["gauges"].rbegin();it!=w["gauges"].rend();++it){int s=(*it)["role"];std::string key=std::to_string(s);int t=(w["reads"].contains(key)?w["reads"][key].get<int>():phase.size())-phase.size();need(t>=0&&t<=(int)rest.size(),"gauge read time");at[t].push_back(s);}
 std::map<int,std::vector<Pair>>pairs;for(auto e:k["entries"])pairs[e["deliver_after_root"].get<int>()].push_back({e["carrier"],e["passive"],e["receivers"].get<std::vector<int>>()});
 std::map<int,std::pair<int,int>>sourceMix;for(auto e:k["entries"])sourceMix[e["passive"].get<int>()]={e["carrier"].get<int>(),e["mix_frame"].get<int>()};std::map<int,std::pair<int,int>>preMix;for(auto e:w["pre_phase1_partner_mixes"]){int s=e["source"];need(preMix.emplace(s,std::pair<int,int>{e["carrier"].get<int>(),e["mix_frame"].get<int>()}).second,"duplicate prephase source mix");}need(preMix.size()==gaugeBorrow.size(),"prephase mix count");std::set<int>mixSourceEndpoints;for(auto r:selection){need(mixSourceEndpoints.insert(r["source"].get<int>()).second&&mixSourceEndpoints.insert(r["partner"].get<int>()).second,"old source mixes overlap");}for(auto r:gaugeBorrow){int role=r["role"],s=r["source"],partner=r["partner"];need(gauges.count(role)&&phys[role]==role&&!removed.count(role),"gauge alias must be a physical live gauge endpoint");need(mixSourceEndpoints.insert(s).second&&mixSourceEndpoints.insert(partner).second,"gauge source mixes overlap");need(sourceMix.at(s).first==partner&&preMix.at(s)==sourceMix.at(s),"gauge prephase mix endpoint/frame mismatch");}
std::vector<std::vector<int>>adj(R,std::vector<int>(v)),bad(R,std::vector<int>(v)),oldadj(R,std::vector<int>(v));
 for(int ri=0;ri<(int)roots.size();ri++)for(int t:roots[ri].targets){adj[roots[ri].role][t]++;oldadj[roots[ri].role][t]++;if(!deletedRoots.count(ri))bad[roots[ri].role][t]++;}
 std::vector<int>executionOrder=phase;executionOrder.insert(executionOrder.end(),rest.begin(),rest.end());for(auto it=executionOrder.rbegin();it!=executionOrder.rend();++it){int i=*it;auto o=ops[i];for(int t=0;t<v;t++){long long old=(long long)oldadj[o.b][t]+oldadj[o.a][t];need(old<=INT_MAX,"old adjoint overflow");oldadj[o.b][t]=old;if(!omitted.count(i)){long long n=(long long)adj[o.b][t]+adj[o.a][t],m=(long long)bad[o.b][t]+bad[o.a][t];need(n<=INT_MAX&&m<=INT_MAX,"adjoint coefficient overflow");adj[o.b][t]=n;bad[o.b][t]=m;}}}long long gaugeCoefficients=0,newCoefficients=0,changedAdjointRows=0;for(int s=0;s<R;s++){bool changed=false;for(int t=0;t<v;t++){need(adj[s][t]<=oldadj[s][t],"new coefficient exceeds old");if(adj[s][t]!=oldadj[s][t])changed=true;if(gauges.count(s)){need(adj[s][t]==oldadj[s][t],"gauge response changed");gaugeCoefficients+=adj[s][t]!=0;}newCoefficients+=adj[s][t]!=0;}changedAdjointRows+=changed;}
 std::vector<std::vector<std::pair<int,int>>>responses(R),badresponses(R),oldresponses(R);for(int s=0;s<R;s++)for(int t=0;t<v;t++){if(oldadj[s][t])oldresponses[s].push_back({t,oldadj[s][t]});if(adj[s][t])responses[s].push_back({t,adj[s][t]});if(bad[s][t])badresponses[s].push_back({t,bad[s][t]});}
 adj.clear();adj.shrink_to_fit();bad.clear();bad.shrink_to_fit();oldadj.clear();oldadj.shrink_to_fit();
 std::vector<Z>sup(g["args"].size());std::vector<int>sc(sup.size());for(int n=0;n<v;n++){sup[n]=Z(1)<<n;sc[n]=1;}for(int n=v;n<(int)sup.size();n++){int a=g["args"][n][0],b=g["args"][n][1];need((sup[a]&sup[b])==0,"graph summands not source-disjoint");sup[n]=sup[a]|sup[b];sc[n]=sc[a]+sc[b];}
 auto execute=[&](int mode,int direction,int bits,const std::string&mutation)->Z{
  bool major=mode==0,binary=mode==1;auto unit=[&](int i)->Z{return major?Z(1):Z(1)<<(binary?i:bits*i);};
  std::vector<Z>x(v),y(v),z(R);for(int i=0;i<v;i++){x[i]=unit(i);y[i]=unit(v+i);}for(int r:live)z[r]=unit(index[r]);Z top=1;
  auto add=[&](Z&dst,int c,const Z&val){if(major)dst+=Z(c<0?-c:c)*val;else if(binary){if(c&1)dst^=val;}else dst+=Z(c)*val;if(major&&dst>top)top=dst;};
  const auto&resp=mutation=="old_adjoint"?oldresponses:mutation=="omit-ancestor-response"?badresponses:responses;auto value=[&](int role)->Z&{int p=phys[role];if(borrow.count(p))return x[borrow.at(p)];need(index[p]>=0,"read of nonexistent dirty slot");return z[p];};
  auto read=[&](int s){if(mutation=="omit_gauge_compensation"&&s==gaugeControl)return;for(auto[d,role]:omitRole)if(mutation=="omit-new"+std::to_string(d)&&s==role)return;for(auto[t,c]:resp[s])add(y[t],-direction*c,value(s));};
  auto gate=[&](int i,int sign){auto o=ops[i];need(phys[o.a]!=phys[o.b],"self-alias gate");Z control=value(o.b);add(value(o.a),sign,control);};
  for(int s=0;s<R;s++)if(!gauges.count(s)&&!removed.count(s)&&!borrow.count(s))read(s);
  for(auto[n,s]:source)add(value(s),1,x[n]);for(auto&r:gaugeBorrow)if(mutation!="omit_gauge_mix"||r["role"].get<int>()!=gaugeControl)add(x[r["partner"].get<int>()],1,x[r["source"].get<int>()]);
  std::vector<int>done;auto forward=[&](int i){if(early.count(i)){int k=early.at(i);auto&r=selection[k];int a=r["partner"],b=r["source"];if(mutation!="omit_early_mix"||k!=0)add(x[a],1,x[b]);}if(!omitted.count(i)){gate(i,1);done.push_back(i);}};for(int i:phase)forward(i);
  for(auto&r:roots)if(r.center)for(int t:r.targets)add(y[t],direction,value(r.role));
  for(int si=0;si<(int)sinks.size();si++){auto&s=sinks[si];if(mutation=="omit-pre-target"&&si==0)continue;for(int t:s.targets)if(t!=s.pivot)add(y[t],-1,y[s.pivot]);}
  bool omitted=false;for(int p=0;p<(int)rest.size();p++){for(int s:at[p])read(s);int i=rest[p];if(bywrite.count(i)){auto&s=sinks[bywrite[i]];if(mutation=="omit-write"&&!omitted)omitted=true;else add(y[s.pivot],direction,value(ops[i].b));}else forward(i);if(after.count(i)){auto&s=sinks[after[i]];for(int t:s.targets)if(t!=s.pivot)add(y[t],1,y[s.pivot]);}}
  for(int s:at[rest.size()])read(s);
  for(int ri=0;ri<(int)roots.size();ri++){auto&r=roots[ri];if(!r.center&&!deletedRoots.count(ri))for(int t:r.targets)add(y[t],direction,value(r.role));for(auto&p:pairs[ri]){if(!by_source.count(p.b))add(x[p.a],1,x[p.b]);for(int t:p.targets)add(y[t],direction,x[p.a]);}}
  for(auto&[ri,pp]:pairs)for(auto&p:pp)if(!by_source.count(p.b))add(x[p.a],-1,x[p.b]);if(mutation=="undo_before_restore")for(auto&[ri,pp]:pairs)for(auto&p:pp)if(by_source.count(p.b))add(x[p.a],-1,x[p.b]);
  for(auto it=done.rbegin();it!=done.rend();++it)gate(*it,-1);if(mutation!="undo_before_restore")for(auto&[ri,pp]:pairs)for(auto&p:pp)if(by_source.count(p.b))add(x[p.a],-1,x[p.b]);
  for(auto[n,s]:source)add(value(s),-1,x[n]);
  std::vector<Z>want(v);for(int t=0;t<v;t++)want[t]=unit(v+t);
  if(binary){for(int t=0;t<v;t++)want[t]^=unit(t);}
  else {std::map<int,Z>values;for(auto&r:roots){if(!values.count(r.node)){Z val=0;if(major)val=sc[r.node];else{Z mask=sup[r.node];while(mask!=0){int s=boost::multiprecision::lsb(mask);mask&=mask-1;val+=unit(s);}}values[r.node]=val;}for(int t:r.targets)add(want[t],direction,values[r.node]);}for(auto&[ri,pp]:pairs)for(auto&p:pp){Z val=unit(p.a);add(val,1,unit(p.b));for(int t:p.targets)add(want[t],direction,val);}}
  if(major){for(int t=0;t<v;t++)if(y[t]+want[t]>top)top=y[t]+want[t];for(int r:live)if(z[r]+1>top)top=z[r]+1;for(int i=0;i<v;i++)if(x[i]+1>top)top=x[i]+1;return top;}
  for(int t=0;t<v;t++)if(y[t]!=want[t]){if(binary){Z difference=y[t]^want[t];throw std::runtime_error("target formal column failure target="+std::to_string(t)+" input_column="+std::to_string(boost::multiprecision::lsb(difference)));}throw std::runtime_error("target formal integer column failure target="+std::to_string(t));}
  for(int r:live)need(z[r]==unit(index[r]),"dirty formal restoration failure");
  for(int i=0;i<v;i++)need(x[i]==unit(i),"source formal restoration failure");
  return Z(0);
 };
 Z bound=execute(0,1,0,"");int digits=boost::multiprecision::msb(bound)+3;int bits=8*((digits+7)/8);need((Z(1)<<bits)>2*bound,"packed coefficient injectivity");
 std::cout<<"bound "<<bound<<" bits "<<bits<<" columns "<<cols<<std::endl;
 execute(1,1,0,"");std::cout<<"F2 all columns PASS"<<std::endl;
 execute(2,1,bits,"");std::cout<<"Z forward all columns PASS"<<std::endl;
 execute(2,-1,bits,"");std::cout<<"Z reflected all columns PASS"<<std::endl;
 J controls,controlFailures;std::vector<std::string>controlNames={"omit-ancestor-response","omit-pre-target","omit-write","omit_early_mix","old_adjoint","undo_before_restore","omit_gauge_mix","omit_gauge_compensation"};for(auto[d,s]:omitRole)controlNames.push_back("omit-new"+std::to_string(d));for(std::string name:controlNames){bool rejected=false;try{execute(1,1,0,name);}catch(std::exception&e){rejected=true;controlFailures[name]=e.what();}if(!rejected)throw std::runtime_error("mutation accepted: "+name);controls[name]="REJECTED";}
 J receipt={{"status","PASS_NATIVE_ALL_F2_AND_INTEGER_COLUMNS"},{"source_columns",v},{"target_columns",v},{"dirty_columns",live.size()},{"formal_columns",cols},{"integer_bound",bound.convert_to<std::string>()},{"borrowed_source_slots",borrow.size()},{"copy_borrow_slots",selection.size()},{"gauge_source_borrow_slots",gaugeBorrow.size()},{"omitted_first_copies",omitted.size()},{"changed_integer_adjoint_rows",changedAdjointRows},{"new_positive_adjoint_coefficients",newCoefficients},{"unchanged_gauge_adjoint_coefficients",gaugeCoefficients},{"packed_digit_bits",bits},{"literal_inverse",true},{"source_and_dirty_restoration",true},{"integer_defining_decoder",true},{"F2_identity",true},{"controls",controls},{"control_failure_witnesses",controlFailures},{"new_gauge_control_role",gaugeControl},{"new_gauge_control_response",responses[gaugeControl]},{"omitted_gauge_roles_by_rank",omitRole},{"scope","Latest PR210 source469 original440 copy-eliding plus29 compensated gauge-source endpoints scalar word; no ghost dirty slots; independently recomputed full adjoint with omitted copies; physical source-frame, aliases, bank endpoints and paid pricing require separate admission."},{"milliseconds",std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-started).count()}};
 std::ofstream(argv[2])<<receipt.dump(2)<<"\n";std::cout<<receipt.dump(2)<<"\n";return 0;
}catch(std::exception&e){std::cerr<<"FAIL "<<e.what()<<"\n";return 1;}}










