const tables=[
 {id:'auth',name:'auth.users',kind:'auth',x:30,y:24,fields:[['PK','id','uuid'],['','… managed by Supabase','']]},
 {id:'users',name:'public.users',x:30,y:212,fields:[['PK FK','id','uuid'],['','email','text · NULL'],['','created_at','timestamptz']]},
 {id:'roles',name:'public.app_user_roles',x:418,y:212,fields:[['PK FK','user_id','uuid'],['','role','text'],['','created_at','timestamptz']]},
 {id:'families',name:'public.scent_families',x:805,y:24,fields:[['PK','name','varchar'],['','description','text']]},
 {id:'perfumes',name:'public.perfumes',kind:'central',x:805,y:212,fields:[['PK','id','integer'],['','name','varchar'],['','brand','varchar'],['FK','scent_family','varchar'],['','key_notes','text[]'],['','dupes','text[]'],['','gender','varchar'],['','year_launched','integer'],['','concentration','varchar'],['','best_season','varchar'],['','best_occasion','varchar'],['','dupe_size','varchar'],['','vibe','varchar'],['','dupe_price_php','varchar'],['','price_php_min','integer'],['','where_to_buy','jsonb'],['','other_stores','jsonb'],['','search_text','text'],['FK','created_by','uuid · NULL']]},
 {id:'favorites',name:'public.perfume_favorites',x:418,y:465,fields:[['PK FK','user_id','uuid'],['PK FK','perfume_id','integer'],['','created_at','timestamptz']]}
];
const edges=[
 ['auth','id','users','id','1','0..1','CASCADE','left'],
 ['auth','id','roles','user_id','1','0..1','CASCADE','top'],
 ['users','id','roles','user_id','1','0..1','CASCADE','horizontal'],
 ['roles','user_id','perfumes','created_by','0..1','0..*','SET NULL','creator'],
 ['families','name','perfumes','scent_family','1','0..*','RESTRICT','right'],
 ['roles','user_id','favorites','user_id','1','0..*','CASCADE','left'],
 ['perfumes','id','favorites','perfume_id','1','0..*','CASCADE','favorite']
];
const canvas=document.querySelector('#erdCanvas'), svg=document.querySelector('#erdLines'), viewport=document.querySelector('#erdViewport'), sizer=document.querySelector('#erdSizer');
const nodes=new Map();
for(const t of tables){
 const node=document.createElement('article'); node.className='erd-table '+(t.kind||'');node.style.left=t.x+'px';node.style.top=t.y+'px';node.tabIndex=0;node.setAttribute('role','button');node.setAttribute('aria-label',t.name+' table');node.dataset.table=t.id;
 const h=document.createElement('h3');h.textContent=t.name;node.append(h);
 for(const [keys,name,type] of t.fields){const r=document.createElement('div');r.className='erd-row';r.dataset.field=name;const k=document.createElement('span');for(const key of keys.split(' ').filter(Boolean)){const b=document.createElement('b');b.className='key-'+key.toLowerCase();b.textContent=key;k.append(b);}const n=document.createElement('span');n.textContent=name;const ty=document.createElement('span');ty.className='erd-type';ty.textContent=type;r.append(k,n,ty);node.append(r);}
 canvas.append(node);nodes.set(t.id,node);node.addEventListener('click',()=>select(t.id));node.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select(t.id)}});
}
function point(id,field,side){const n=nodes.get(id),r=[...n.querySelectorAll('.erd-row')].find(x=>x.dataset.field===field);return [n.offsetLeft+(side==='right'?n.offsetWidth:0),n.offsetTop+r.offsetTop+r.offsetHeight/2]}
const NS='http://www.w3.org/2000/svg';function make(tag,attrs){const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);svg.append(e);return e;}
function draw(){svg.replaceChildren();for(let i=0;i<edges.length;i++){const [a,af,b,bf,one,many,action,route]=edges[i];let p,q,mid,points;
 if(route==='left'){p=point(a,af,'left');q=point(b,bf,'left');mid=p[0]-13;points=[p,[mid,p[1]],[mid,q[1]],q];}
 else if(route==='right'){p=point(a,af,'right');q=point(b,bf,'right');mid=p[0]+23;points=[p,[mid,p[1]],[mid,q[1]],q];}
 else if(route==='top'){p=point(a,af,'right');q=point(b,bf,'right');points=[p,[365,p[1]],[365,145],[735,145],[735,q[1]],q];}
 else if(route==='creator'){p=point(a,af,'right');q=point(b,bf,'left');mid=765;points=[p,[mid,p[1]],[mid,q[1]],q];}
 else if(route==='favorite'){p=point(a,af,'left');q=point(b,bf,'right');mid=735;points=[p,[mid,p[1]],[mid,q[1]],q];}
 else{p=point(a,af,'right');q=point(b,bf,'left');mid=(p[0]+q[0])/2;points=[p,[mid,p[1]],[mid,q[1]],q];}
 const path=make('polyline',{points:points.map(p=>p.join(',')).join(' '),class:'erd-wire','data-edge':i});const title=document.createElementNS(NS,'title');title.textContent=`${a}.${af} → ${b}.${bf}: ${one} to ${many}`;path.append(title);
 for(const [j,pt,txt] of [[0,p,one],[1,q,many]]){const neighbor=j?points[points.length-2]:points[1];const right=neighbor[0]>pt[0];const l=make('text',{x:pt[0]+(right?4:-4),y:pt[1]-6,'text-anchor':right?'start':'end',class:'erd-end','data-edge':i});l.textContent=txt;}
 }}
draw();let selected=null;function select(id){selected=selected===id?null:id;const connected=new Set([selected]);edges.forEach(e=>{if(e[0]===selected)connected.add(e[2]);if(e[2]===selected)connected.add(e[0]);});for(const [key,node] of nodes){node.classList.toggle('selected',key===selected);node.classList.toggle('muted',!!selected&&!connected.has(key));node.setAttribute('aria-pressed',String(key===selected));}svg.querySelectorAll('[data-edge]').forEach(el=>{const e=edges[+el.dataset.edge],active=!!selected&&(e[0]===selected||e[2]===selected);el.classList.toggle('active',active);el.classList.toggle('muted',!!selected&&!active);});document.querySelector('#erdStatus').textContent=selected?tables.find(t=>t.id===selected).name+' — '+edges.filter(e=>e[0]===selected||e[2]===selected).length+' direct relationships. Click again to clear.':'Select any table to inspect its connected relationships. Scroll to pan.';}
let zoom=1;function setZoom(z){zoom=Math.max(.35,Math.min(1.5,z));canvas.style.transform=`scale(${zoom})`;sizer.style.width=1150*zoom+'px';sizer.style.height=830*zoom+'px';document.querySelector('#zoomValue').textContent=Math.round(zoom*100)+'%';}function fit(){setZoom(Math.min(1,viewport.clientWidth/1150));viewport.scrollTo(0,0);}
document.querySelector('#zoomIn').onclick=()=>setZoom(zoom+.15);document.querySelector('#zoomOut').onclick=()=>setZoom(zoom-.15);document.querySelector('#fit').onclick=fit;document.querySelector('#reset').onclick=()=>{if(selected)select(selected);setZoom(1);viewport.scrollTo(0,0)};setZoom(1);if(viewport.clientWidth>=800)fit();
const body=document.querySelector('#relations');for(const [a,af,b,bf,one,many,action] of edges){const tr=document.createElement('tr');for(const value of [tables.find(t=>t.id===a).name,tables.find(t=>t.id===b).name+'.'+bf,`${one} → ${many}`,action]){const td=document.createElement('td');td.textContent=value;tr.append(td);}body.append(tr);}
