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
 int v=g["v"],R=18908;std::vector<Op>ops;for(auto&o:w["ops"])ops.push_back({o[0],o[1],o[2]});int N=ops.size();std::vector<int>phase,rest;std::set<int>ps;for(auto i:w["phase1"]){phase.push_back(i);ps.insert(i.get<int>());}for(int i=0;i<N;i++)if(!ps.count(i))rest.push_back(i);
 std::map<int,int>source;for(auto&[n,s]:w["sources"].items())source[std::stoi(n)]=s;
 std::vector<int>phys(R);for(int i=0;i<R;i++)phys[i]=i;std::set<int>gauges,virtualOnly;for(auto z:w["gauges"])gauges.insert(z["role"].get<int>());
 for(auto p:w["pairs"]){phys[p[1].get<int>()]=p[0];virtualOnly.insert(p[1].get<int>());}
 std::vector<Root>roots;for(int i=0;i<(int)g["roots"].size();i++){auto r=g["roots"][i];roots.push_back({w["rootroles"][i],r["node"],r["kind"]=="center",r["targets"].get<std::vector<int>>()});}
 std::vector<Sink>sinks;std::set<int>removed,deletedRoots;std::map<int,int>bywrite,after;
 for(auto e:sj){int ri=e["root"],p=e["pivot"],s=roots[ri].role;Sink q{ri,s,p,roots[ri].targets,{}};for(int i=0;i<N;i++)if(ops[i].a==s)q.writes.push_back(i);need(!q.writes.empty(),"terminal writes");for(int i:q.writes){need(!ps.count(i),"terminal phase");bywrite[i]=sinks.size();}after[q.writes.back()]=sinks.size();removed.insert(s);deletedRoots.insert(ri);sinks.push_back(q);}
 std::vector<int>live,index(R,-1);for(int r=0;r<R;r++)if(!virtualOnly.count(r)&&!removed.count(r)){index[r]=2*v+live.size();live.push_back(r);}
 need((int)live.size()==17114,"physical stock");int cols=2*v+live.size();
 std::vector<std::vector<int>>at(rest.size()+1);for(auto it=w["gauges"].rbegin();it!=w["gauges"].rend();++it){int s=(*it)["role"];std::string key=std::to_string(s);int t=(w["reads"].contains(key)?w["reads"][key].get<int>():phase.size())-phase.size();need(t>=0&&t<=(int)rest.size(),"gauge read time");at[t].push_back(s);}
 std::map<int,std::vector<Pair>>pairs;for(auto e:k["entries"])pairs[e["deliver_after_root"].get<int>()].push_back({e["carrier"],e["passive"],e["receivers"].get<std::vector<int>>()});
 std::vector<std::vector<int>>adj(R,std::vector<int>(v)),bad(R,std::vector<int>(v));
 for(int ri=0;ri<(int)roots.size();ri++)for(int t:roots[ri].targets){adj[roots[ri].role][t]++;if(!deletedRoots.count(ri))bad[roots[ri].role][t]++;}
 for(int i=N-1;i>=0;i--){auto o=ops[i];for(int t=0;t<v;t++){long long n=(long long)adj[o.b][t]+adj[o.a][t],m=(long long)bad[o.b][t]+bad[o.a][t];need(n<=INT_MAX&&m<=INT_MAX,"adjoint coefficient overflow");adj[o.b][t]=n;bad[o.b][t]=m;}}
 std::vector<std::vector<std::pair<int,int>>>responses(R),badresponses(R);for(int s=0;s<R;s++)for(int t=0;t<v;t++){if(adj[s][t])responses[s].push_back({t,adj[s][t]});if(bad[s][t])badresponses[s].push_back({t,bad[s][t]});}
 adj.clear();adj.shrink_to_fit();bad.clear();bad.shrink_to_fit();
 std::vector<Z>sup(g["args"].size());std::vector<int>sc(sup.size());for(int n=0;n<v;n++){sup[n]=Z(1)<<n;sc[n]=1;}for(int n=v;n<(int)sup.size();n++){int a=g["args"][n][0],b=g["args"][n][1];need((sup[a]&sup[b])==0,"graph summands not source-disjoint");sup[n]=sup[a]|sup[b];sc[n]=sc[a]+sc[b];}
 auto execute=[&](int mode,int direction,int bits,const std::string&mutation)->Z{
  bool major=mode==0,binary=mode==1;auto unit=[&](int i)->Z{return major?Z(1):Z(1)<<(binary?i:bits*i);};
  std::vector<Z>x(v),y(v),z(R);for(int i=0;i<v;i++){x[i]=unit(i);y[i]=unit(v+i);}for(int r:live)z[r]=unit(index[r]);Z top=1;
  auto add=[&](Z&dst,int c,const Z&val){if(major)dst+=Z(c<0?-c:c)*val;else if(binary){if(c&1)dst^=val;}else dst+=Z(c)*val;if(major&&dst>top)top=dst;};
  const auto&resp=mutation=="omit-ancestor-response"?badresponses:responses;
  auto read=[&](int s){int p=phys[s];need(index[p]>=0,"dirty read of nonexistent physical row");for(auto[t,c]:resp[s])add(y[t],-direction*c,z[p]);};
  auto gate=[&](int i,int sign){auto o=ops[i];int a=phys[o.a],b=phys[o.b];need(index[a]>=0&&index[b]>=0,"gate missing physical row");add(z[a],sign,z[b]);};
  for(int s=0;s<R;s++)if(!gauges.count(s)&&!removed.count(s))read(s);
  for(auto[n,s]:source)add(z[phys[s]],1,x[n]);
  std::vector<int>done;for(int i:phase){gate(i,1);done.push_back(i);}
  for(auto&r:roots)if(r.center)for(int t:r.targets)add(y[t],direction,z[phys[r.role]]);
  for(int si=0;si<(int)sinks.size();si++){auto&s=sinks[si];if(mutation=="omit-pre-target"&&si==0)continue;for(int t:s.targets)if(t!=s.pivot)add(y[t],-1,y[s.pivot]);}
  bool omitted=false;for(int p=0;p<(int)rest.size();p++){for(int s:at[p])read(s);int i=rest[p];if(bywrite.count(i)){auto&s=sinks[bywrite[i]];if(mutation=="omit-write"&&!omitted)omitted=true;else add(y[s.pivot],direction,z[phys[ops[i].b]]);}else{gate(i,1);done.push_back(i);}if(after.count(i)){auto&s=sinks[after[i]];for(int t:s.targets)if(t!=s.pivot)add(y[t],1,y[s.pivot]);}}
  for(int s:at[rest.size()])read(s);
  for(int ri=0;ri<(int)roots.size();ri++){auto&r=roots[ri];if(!r.center&&!deletedRoots.count(ri))for(int t:r.targets)add(y[t],direction,z[phys[r.role]]);for(auto&p:pairs[ri]){add(x[p.a],1,x[p.b]);for(int t:p.targets)add(y[t],direction,x[p.a]);}}
  for(auto&[ri,pp]:pairs)for(auto&p:pp)add(x[p.a],-1,x[p.b]);
  for(auto it=done.rbegin();it!=done.rend();++it)gate(*it,-1);
  for(auto[n,s]:source)add(z[phys[s]],-1,x[n]);
  std::vector<Z>want(v);for(int t=0;t<v;t++)want[t]=unit(v+t);
  if(binary){for(int t=0;t<v;t++)want[t]^=unit(t);}
  else {std::map<int,Z>values;for(auto&r:roots){if(!values.count(r.node)){Z val=0;if(major)val=sc[r.node];else{Z mask=sup[r.node];while(mask!=0){int s=boost::multiprecision::lsb(mask);mask&=mask-1;val+=unit(s);}}values[r.node]=val;}for(int t:r.targets)add(want[t],direction,values[r.node]);}for(auto&[ri,pp]:pairs)for(auto&p:pp){Z val=unit(p.a);add(val,1,unit(p.b));for(int t:p.targets)add(want[t],direction,val);}}
  if(major){for(int t=0;t<v;t++)if(y[t]+want[t]>top)top=y[t]+want[t];for(int r:live)if(z[r]+1>top)top=z[r]+1;for(int i=0;i<v;i++)if(x[i]+1>top)top=x[i]+1;return top;}
  for(int t=0;t<v;t++)need(y[t]==want[t],"target formal column failure");
  for(int r:live)need(z[r]==unit(index[r]),"dirty formal restoration failure");
  for(int i=0;i<v;i++)need(x[i]==unit(i),"source formal restoration failure");
  return Z(0);
 };
 Z bound=execute(0,1,0,"");int digits=boost::multiprecision::msb(bound)+3;int bits=8*((digits+7)/8);need((Z(1)<<bits)>2*bound,"packed coefficient injectivity");
 std::cout<<"bound "<<bound<<" bits "<<bits<<" columns "<<cols<<std::endl;
 execute(1,1,0,"");std::cout<<"F2 all columns PASS"<<std::endl;
 execute(2,1,bits,"");std::cout<<"Z forward all columns PASS"<<std::endl;
 execute(2,-1,bits,"");std::cout<<"Z reflected all columns PASS"<<std::endl;
 J controls;for(std::string name:{"omit-ancestor-response","omit-pre-target","omit-write"}){bool rejected=false;try{execute(1,1,0,name);}catch(std::exception&e){rejected=true;}need(rejected,"mutation accepted");controls[name]="REJECTED";}
 J receipt={{"status","PASS_NATIVE_ALL_F2_AND_INTEGER_COLUMNS"},{"source_columns",v},{"target_columns",v},{"dirty_columns",live.size()},{"formal_columns",cols},{"integer_bound",bound.convert_to<std::string>()},{"packed_digit_bits",bits},{"literal_inverse",true},{"source_and_dirty_restoration",true},{"integer_defining_decoder",true},{"F2_identity",true},{"controls",controls},{"scope","Pinned PR200 scalar word with terminal/gauge/alias/partner inventory; operation frame changes preserve this exact scalar execution."},{"milliseconds",std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-started).count()}};
 std::ofstream(argv[2])<<receipt.dump(2)<<"\n";std::cout<<receipt.dump(2)<<"\n";return 0;
}catch(std::exception&e){std::cerr<<"FAIL "<<e.what()<<"\n";return 1;}}