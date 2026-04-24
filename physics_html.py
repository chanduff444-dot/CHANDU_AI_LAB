PHYSICS_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;font-family:'Segoe UI',sans-serif;color:#e8eaed;overflow:hidden;user-select:none}
#wrap{display:flex;flex-direction:column;height:100vh}
#toolbar{display:flex;align-items:center;gap:4px;padding:5px 8px;background:#111;border-bottom:1px solid #1e1e1e;flex-wrap:wrap}
.tbtn{background:#1a1a1a;border:1px solid #2a2a2a;color:#888;padding:3px 8px;border-radius:5px;font-size:11px;cursor:pointer;transition:all 0.12s;white-space:nowrap}
.tbtn:hover{background:#252525;color:#e8eaed;border-color:#3a3a3a}
.tbtn.active{background:#1a73e8;border-color:#1a73e8;color:#fff}
.sep{width:1px;height:16px;background:#222;margin:0 2px;flex-shrink:0}
.tlabel{font-size:9px;color:#333;text-transform:uppercase;letter-spacing:0.5px;padding:0 2px;flex-shrink:0}
#controls{padding:4px 8px;background:#0d0d0d;border-bottom:1px solid #181818;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
#controls label{color:#444;font-size:10px}
#controls input[type=range]{width:65px;accent-color:#1a73e8;cursor:pointer}
.ctrl-grp{display:flex;align-items:center;gap:4px}
.val{color:#ccc;font-size:11px;min-width:36px}
#canvas-wrap{flex:1;position:relative;overflow:hidden}
canvas{display:block;width:100%;height:100%;cursor:crosshair}
#hud{position:absolute;top:8px;right:8px;background:rgba(8,8,8,0.92);border:1px solid #1a1a1a;border-radius:8px;padding:8px 12px;font-size:10.5px;color:#555;line-height:1.9;min-width:140px}
#hud span{color:#ccc}
#hud .hud-val{color:#1a73e8}
#mat-panel{position:absolute;top:8px;left:8px;background:rgba(8,8,8,0.92);border:1px solid #1a1a1a;border-radius:8px;padding:8px 12px;font-size:10.5px;color:#555;min-width:140px;display:none}
#mat-panel h4{color:#ccc;margin-bottom:6px;font-size:11px}
.mat-opt{display:flex;align-items:center;gap:6px;padding:3px 0;cursor:pointer}
.mat-dot{width:10px;height:10px;border-radius:50%}
.mat-opt.sel .mat-label{color:#1a73e8}
#inspector{position:absolute;bottom:55px;right:8px;background:rgba(8,8,8,0.94);border:1px solid #1a1a1a;border-radius:8px;padding:8px 12px;font-size:10.5px;display:none;min-width:170px}
#inspector h4{color:#ccc;margin-bottom:5px;font-size:11px}
.ir{display:flex;justify-content:space-between;gap:14px;margin:2px 0;color:#555}
.ir span:last-child{color:#1a73e8}
#prompt-bar{display:flex;gap:6px;padding:6px 8px;background:#111;border-top:1px solid #1a1a1a}
#promptIn{flex:1;background:#0d0d0d;border:1px solid #1e1e1e;border-radius:7px;color:#e8eaed;padding:5px 10px;font-size:12px;outline:none;transition:border-color .15s}
#promptIn:focus{border-color:#1a73e8}
#prompt-bar button{background:#1a73e8;border:none;color:#fff;padding:5px 14px;border-radius:7px;font-size:12px;cursor:pointer;font-weight:600}
</style>
</head>
<body>
<div id="wrap">

<div id="toolbar">
  <span class="tlabel">Spawn</span>
  <button class="tbtn active" id="btn-ball"    onclick="setMode('ball',this)">● Ball</button>
  <button class="tbtn"        id="btn-box"     onclick="setMode('box',this)">■ Box</button>
  <button class="tbtn"        id="btn-poly"    onclick="setMode('poly',this)">◆ Poly</button>
  <button class="tbtn"        id="btn-wall"    onclick="setMode('wall',this)">✏ Wall</button>
  <button class="tbtn"        id="btn-grab"    onclick="setMode('grab',this)">✋ Grab</button>
  <button class="tbtn"        id="btn-erase"   onclick="setMode('erase',this)">✕ Erase</button>
  <button class="tbtn"        id="btn-inspect" onclick="setMode('inspect',this)">🔍 Inspect</button>

  <div class="sep"></div>
  <span class="tlabel">Material</span>
  <button class="tbtn" id="btn-matpanel" onclick="toggleMatPanel()">🎨 Material</button>

  <div class="sep"></div>
  <span class="tlabel">Forces</span>
  <button class="tbtn" id="btn-magnet"  onclick="toggleForce('magnet',this)">🧲 Magnet</button>
  <button class="tbtn" id="btn-anti"    onclick="toggleForce('anti',this)">🔄 Repulse</button>
  <button class="tbtn" id="btn-wind"    onclick="toggleForce('wind',this)">💨 Wind</button>
  <button class="tbtn" id="btn-vortex"  onclick="toggleForce('vortex',this)">🌀 Vortex</button>

  <div class="sep"></div>
  <span class="tlabel">Scenes</span>
  <button class="tbtn" onclick="addPreset('pendulum')">Pendulum</button>
  <button class="tbtn" onclick="addPreset('newtonsCradle')">Newton's</button>
  <button class="tbtn" onclick="addPreset('dominos')">Dominos</button>
  <button class="tbtn" onclick="addPreset('stack')">Stack</button>
  <button class="tbtn" onclick="addPreset('bridge')">Bridge</button>
  <button class="tbtn" onclick="addPreset('cloth')">Cloth</button>
  <button class="tbtn" onclick="addPreset('ragdoll')">Ragdoll</button>
  <button class="tbtn" onclick="addPreset('rope')">Rope</button>
  <button class="tbtn" onclick="addPreset('funnel')">Funnel</button>
  <button class="tbtn" onclick="addPreset('avalanche')">Avalanche</button>
  <button class="tbtn" onclick="addPreset('jenga')">Jenga</button>
  <button class="tbtn" onclick="addPreset('orbit')">Orbit</button>
  <button class="tbtn" onclick="addPreset('blackhole')">Black Hole</button>
  <button class="tbtn" onclick="addPreset('pachinko')">Pachinko</button>
  <button class="tbtn" onclick="addPreset('water')">💧 Water</button>
  <button class="tbtn" onclick="addPreset('softball')">Soft Ball</button>
  <button class="tbtn" onclick="addPreset('gas')">Gas</button>
  <button class="tbtn" onclick="addPreset('collision')">Collisions</button>
  <button class="tbtn" onclick="addPreset('gyro')">Gyroscope</button>
  <button class="tbtn" onclick="addPreset('billiards')">Billiards</button>
  <button class="tbtn" onclick="addPreset('snow')">Snow</button>
  <button class="tbtn" onclick="addPreset('fireworks')">Fireworks</button>

  <div class="sep"></div>
  <button class="tbtn" onclick="clearAll()">🗑 Clear</button>
  <button class="tbtn" onclick="togglePause()" id="pauseBtn">⏸ Pause</button>
  <button class="tbtn" onclick="stepOnce()">⏭ Step</button>
  <button class="tbtn" onclick="explodeAll()">💥 Explode</button>
  <button class="tbtn" onclick="screenshot()">📸 Shot</button>
  <button class="tbtn" onclick="toggleLight()" id="lightBtn">💡 Light</button>
  <button class="tbtn" onclick="toggleTheme()" id="themeBtn">🌙 Theme</button>
</div>

<div id="controls">
  <div class="ctrl-grp"><label>Gravity</label>
    <input type="range" id="gravSlider" min="-30" max="30" value="9.8" step="0.2"
      oninput="GRAVITY=+this.value;document.getElementById('gravVal').textContent=this.value">
    <span class="val" id="gravVal">9.8</span></div>
  <div class="ctrl-grp"><label>Restitution</label>
    <input type="range" id="restSlider" min="0" max="100" value="40" step="1"
      oninput="defaultRestitution=this.value/100;document.getElementById('restVal').textContent=defaultRestitution.toFixed(2)">
    <span class="val" id="restVal">0.40</span></div>
  <div class="ctrl-grp"><label>Friction</label>
    <input type="range" id="fricSlider" min="0" max="100" value="45" step="1"
      oninput="defaultFriction=this.value/100;document.getElementById('fricVal').textContent=defaultFriction.toFixed(2)">
    <span class="val" id="fricVal">0.45</span></div>
  <div class="ctrl-grp"><label>Air Drag</label>
    <input type="range" id="dragSlider" min="0" max="50" value="3" step="1"
      oninput="airDrag=this.value/1000;document.getElementById('dragVal').textContent=(airDrag*1000|0)">
    <span class="val" id="dragVal">3</span></div>
  <div class="ctrl-grp"><label>Size</label>
    <input type="range" id="sizeSlider" min="4" max="40" value="14" step="1"
      oninput="spawnSize=+this.value;document.getElementById('sizeVal').textContent=this.value">
    <span class="val" id="sizeVal">14</span></div>
  <div class="ctrl-grp"><label>Trails</label>
    <input type="range" id="trailSlider" min="0" max="80" value="12" step="1"
      oninput="trailLen=+this.value;document.getElementById('trailVal').textContent=this.value">
    <span class="val" id="trailVal">12</span></div>
  <div class="ctrl-grp"><label>Sim Speed</label>
    <input type="range" id="speedSlider" min="5" max="200" value="100" step="5"
      oninput="simSpeed=this.value/100;document.getElementById('speedVal').textContent=simSpeed.toFixed(1)+'x'">
    <span class="val" id="speedVal">1.0x</span></div>
  <div class="ctrl-grp"><label>SubSteps</label>
    <input type="range" id="subSlider" min="1" max="8" value="3" step="1"
      oninput="subSteps=+this.value;document.getElementById('subVal').textContent=this.value">
    <span class="val" id="subVal">3</span></div>
</div>

<div id="canvas-wrap">
  <canvas id="c"></canvas>
  <div id="hud">
    Bodies: <span id="hBodies">0</span><br>
    Springs: <span id="hSpr">0</span><br>
    Walls: <span id="hWalls">0</span><br>
    FPS: <span class="hud-val" id="hFps">60</span><br>
    Contacts: <span id="hContacts">0</span><br>
    Total KE: <span id="hKE">0</span> J<br>
    Mode: <span id="hMode">ball</span>
  </div>
  <div id="mat-panel">
    <h4>Spawn Material</h4>
  </div>
  <div id="inspector">
    <h4 id="iTitle">Inspector</h4>
    <div class="ir"><span>Mass</span><span id="iMass">-</span></div>
    <div class="ir"><span>Speed</span><span id="iSpeed">-</span></div>
    <div class="ir"><span>ω (rad/s)</span><span id="iOmega">-</span></div>
    <div class="ir"><span>Restitution</span><span id="iRest">-</span></div>
    <div class="ir"><span>Friction</span><span id="iFric">-</span></div>
    <div class="ir"><span>KE</span><span id="iKE">-</span></div>
    <div class="ir"><span>Momentum</span><span id="iMom">-</span></div>
    <div class="ir"><span>Material</span><span id="iMat">-</span></div>
  </div>
</div>

<div id="prompt-bar">
  <input id="promptIn" placeholder='Try: "water" · "billiards" · "gyroscope" · "ragdoll" · "collision demo" · "snow" · or describe a scene...'/>
  <button onclick="runPrompt()">▶ Run</button>
</div>
</div>

<script>
// ═══════════════════════════════════════════════════════════
//  CHANDU AI LAB — Physics Engine v3
//  Maximum Realism: Rigid Body Dynamics, Proper Impulse
//  Resolution, Torque, Rolling, Moment of Inertia,
//  SAT Collision, Friction Cones, Air Resistance, Water
// ═══════════════════════════════════════════════════════════

const canvas = document.getElementById('c');
const ctx    = canvas.getContext('2d');
const wrap   = document.getElementById('canvas-wrap');

function resize(){ canvas.width=wrap.clientWidth; canvas.height=wrap.clientHeight; }
resize(); window.addEventListener('resize',resize);

// ── MATERIALS ────────────────────────────────────────────────
const MATERIALS = {
  default:  { name:'Default',   restitution:0.4, friction:0.45, density:1.0,  color:'#1a73e8', sfx:'mid'  },
  rubber:   { name:'Rubber',    restitution:0.85,friction:0.9,  density:1.2,  color:'#e53935', sfx:'high' },
  metal:    { name:'Metal',     restitution:0.3, friction:0.2,  density:7.8,  color:'#90a4ae', sfx:'clang'},
  wood:     { name:'Wood',      restitution:0.35,friction:0.6,  density:0.7,  color:'#a0522d', sfx:'thud' },
  ice:      { name:'Ice',       restitution:0.05,friction:0.02, density:0.9,  color:'#b3e5fc', sfx:'slide'},
  concrete: { name:'Concrete',  restitution:0.1, friction:0.85, density:2.4,  color:'#78909c', sfx:'thud' },
  glass:    { name:'Glass',     restitution:0.7, friction:0.3,  density:2.5,  color:'#80deea', sfx:'clink'},
  bounce:   { name:'Super Ball',restitution:0.99,friction:0.7,  density:0.5,  color:'#ffee58', sfx:'boing'},
};
let currentMaterial = 'default';

// ── GLOBALS ───────────────────────────────────────────────────
let bodies=[], springs=[], walls=[], pegs=[], specials=[];
let waterSurface=null;
let mode='ball', paused=false;
let GRAVITY=9.8, defaultRestitution=0.4, defaultFriction=0.45;
let airDrag=0.003, spawnSize=14, trailLen=12, simSpeed=1.0, subSteps=3;
let windForce=0, magnetActive=false, repulsorActive=false, vortexActive=false;
let cursorPos={x:0,y:0};
let grabBody=null, grabPointLocal={x:0,y:0};
let inspectedBody=null;
let dynamicLight=false, lightPos={x:400,y:100};
let darkTheme=true;
let frameCount=0, lastFpsTime=Date.now(), fps=60;
let contactCount=0;
let fireworkTimer=0, snowTimer=0;
let drawingWall=false, wallStart=null;
let pendingStep=false;

// ── MATH HELPERS ─────────────────────────────────────────────
const V={
  add:(a,b)=>({x:a.x+b.x,y:a.y+b.y}),
  sub:(a,b)=>({x:a.x-b.x,y:a.y-b.y}),
  scale:(a,s)=>({x:a.x*s,y:a.y*s}),
  dot:(a,b)=>a.x*b.x+a.y*b.y,
  cross:(a,b)=>a.x*b.y-a.y*b.x,
  crossSV:(s,v)=>({x:-s*v.y,y:s*v.x}),
  len:(a)=>Math.sqrt(a.x*a.x+a.y*a.y),
  len2:(a)=>a.x*a.x+a.y*a.y,
  norm:(a)=>{ const l=V.len(a)||1; return{x:a.x/l,y:a.y/l}; },
  perp:(a)=>({x:-a.y,y:a.x}),
  rot:(v,a)=>({x:v.x*Math.cos(a)-v.y*Math.sin(a),y:v.x*Math.sin(a)+v.y*Math.cos(a)}),
  neg:(a)=>({x:-a.x,y:-a.y}),
  zero:()=>({x:0,y:0}),
};
function rnd(a,b){ return a+Math.random()*(b-a); }
function rndColor(mat){ return (MATERIALS[mat]||MATERIALS.default).color; }
const PALETTE=['#1a73e8','#e53935','#00897b','#f29900','#7c4dff','#00acc1','#43a047','#fb8c00','#d81b60','#26c6da','#ab47bc'];
function rndPalette(){ return PALETTE[Math.floor(Math.random()*PALETTE.length)]; }

// ── BODY FACTORY ─────────────────────────────────────────────
let nextId=0;
function makeCircle(x,y,r,mat,colorOverride){
  const m=MATERIALS[mat]||MATERIALS.default;
  const mass=m.density*Math.PI*r*r*0.01;
  const I=0.5*mass*r*r;          // moment of inertia
  return {
    id:nextId++, shape:'circle',
    x,y, vx:0,vy:0, angle:0, omega:0,
    r, mass, invMass:1/mass,
    I, invI:1/I,
    restitution:m.restitution, friction:m.friction,
    material:mat||'default',
    color:colorOverride||m.color,
    trail:[], isStatic:false,
    springForce:{x:0,y:0}
  };
}

function makeRect(x,y,w,h,mat,colorOverride,isStatic){
  const m=MATERIALS[mat]||MATERIALS.default;
  const mass=isStatic?Infinity:m.density*w*h*0.01;
  const I=isStatic?Infinity:(mass*(w*w+h*h)/12);
  return {
    id:nextId++, shape:'rect',
    x,y, vx:0,vy:0, angle:0, omega:0,
    w,h, mass:isStatic?Infinity:mass, invMass:isStatic?0:1/mass,
    I:isStatic?Infinity:I, invI:isStatic?0:1/I,
    restitution:m.restitution, friction:m.friction,
    material:mat||'default',
    color:colorOverride||m.color,
    trail:[], isStatic:!!isStatic,
    springForce:{x:0,y:0}
  };
}

function makeConvex(x,y,verts,mat,colorOverride){
  // verts: array of {x,y} in local space
  const m=MATERIALS[mat]||MATERIALS.default;
  // compute area and centroid
  let area=0;
  for(let i=0;i<verts.length;i++){
    const j=(i+1)%verts.length;
    area+=verts[i].x*verts[j].y-verts[j].x*verts[i].y;
  }
  area=Math.abs(area)/2;
  const mass=m.density*area*0.01;
  const I=mass*area*0.08;
  return {
    id:nextId++, shape:'poly',
    x,y, vx:0,vy:0, angle:0, omega:0,
    verts, mass, invMass:1/mass,
    I, invI:1/I,
    restitution:m.restitution, friction:m.friction,
    material:mat||'default',
    color:colorOverride||m.color,
    trail:[], isStatic:false,
    springForce:{x:0,y:0}
  };
}

function makeStatic(x,y,w,h,mat){
  return makeRect(x,y,w,h,mat||'concrete','#555',true);
}

// get world-space vertices of a rect
function rectVerts(b){
  const hw=b.w/2,hh=b.h/2;
  const local=[{x:-hw,y:-hh},{x:hw,y:-hh},{x:hw,y:hh},{x:-hw,y:hh}];
  return local.map(v=>({x:b.x+v.x*Math.cos(b.angle)-v.y*Math.sin(b.angle), y:b.y+v.x*Math.sin(b.angle)+v.y*Math.cos(b.angle)}));
}
function polyVerts(b){
  return b.verts.map(v=>({x:b.x+v.x*Math.cos(b.angle)-v.y*Math.sin(b.angle), y:b.y+v.x*Math.sin(b.angle)+v.y*Math.cos(b.angle)}));
}
function getVerts(b){
  if(b.shape==='rect') return rectVerts(b);
  if(b.shape==='poly') return polyVerts(b);
  return null;
}

// ── SAT COLLISION ─────────────────────────────────────────────
function projectVerts(verts,axis){
  let min=Infinity,max=-Infinity;
  verts.forEach(v=>{ const d=V.dot(v,axis); min=Math.min(min,d); max=Math.max(max,d); });
  return{min,max};
}
function getEdgeNormals(verts){
  const normals=[];
  for(let i=0;i<verts.length;i++){
    const j=(i+1)%verts.length;
    const edge=V.sub(verts[j],verts[i]);
    normals.push(V.norm({x:-edge.y,y:edge.x}));
  }
  return normals;
}

// circle vs circle
function circleCircle(a,b){
  const dx=b.x-a.x,dy=b.y-a.y,dist2=dx*dx+dy*dy,minD=a.r+b.r;
  if(dist2>=minD*minD) return null;
  const dist=Math.sqrt(dist2)||0.0001;
  return{ normal:{x:dx/dist,y:dy/dist}, depth:minD-dist,
    contacts:[{x:a.x+(dx/dist)*a.r,y:a.y+(dy/dist)*a.r}] };
}

// circle vs polygon (SAT)
function circlePoly(circle,poly){
  const verts=getVerts(poly);
  let minDepth=Infinity,bestNormal=null;
  // polygon face normals
  for(let i=0;i<verts.length;i++){
    const j=(i+1)%verts.length;
    const edge=V.sub(verts[j],verts[i]);
    const n=V.norm({x:-edge.y,y:edge.x});
    const proj=V.dot({x:circle.x-verts[i].x,y:circle.y-verts[i].y},n);
    if(proj>circle.r) return null;
    const depth=circle.r-proj;
    if(depth<minDepth){minDepth=depth;bestNormal=n;}
  }
  // closest vertex axis
  let closestVert=null,closestDist=Infinity;
  verts.forEach(v=>{ const d=V.len2(V.sub({x:circle.x,y:circle.y},v)); if(d<closestDist){closestDist=d;closestVert=v;} });
  const axis=V.norm(V.sub({x:circle.x,y:circle.y},closestVert));
  const pProj=projectVerts(verts,axis);
  const cMin=V.dot({x:circle.x,y:circle.y},axis)-circle.r;
  const cMax=V.dot({x:circle.x,y:circle.y},axis)+circle.r;
  if(cMax<pProj.min||pProj.max<cMin) return null;
  const d=Math.min(cMax-pProj.min,pProj.max-cMin);
  if(d<minDepth){minDepth=d;bestNormal=axis;}
  const contact={x:circle.x-bestNormal.x*circle.r,y:circle.y-bestNormal.y*circle.r};
  return{normal:bestNormal,depth:minDepth,contacts:[contact]};
}

// polygon vs polygon (SAT)
function polyPoly(a,b){
  const va=getVerts(a),vb=getVerts(b);
  let minDepth=Infinity,bestNormal=null;
  const axes=[...getEdgeNormals(va),...getEdgeNormals(vb)];
  for(const axis of axes){
    const pa=projectVerts(va,axis),pb=projectVerts(vb,axis);
    const overlap=Math.min(pa.max-pb.min,pb.max-pa.min);
    if(overlap<=0) return null;
    if(overlap<minDepth){
      minDepth=overlap;
      const d=V.sub({x:(pa.min+pa.max)/2,y:0},{x:(pb.min+pb.max)/2,y:0});
      bestNormal=V.dot(d,axis)<0?V.neg(axis):axis;
    }
  }
  // contact point: average of clipped verts
  const contacts=[];
  va.forEach(v=>{ if(pointInPoly(v,vb)) contacts.push(v); });
  vb.forEach(v=>{ if(pointInPoly(v,va)) contacts.push(v); });
  if(!contacts.length) contacts.push({x:(a.x+b.x)/2,y:(a.y+b.y)/2});
  const cp={x:contacts.reduce((s,c)=>s+c.x,0)/contacts.length,y:contacts.reduce((s,c)=>s+c.y,0)/contacts.length};
  return{normal:bestNormal,depth:minDepth,contacts:[cp]};
}

function pointInPoly(p,verts){
  let inside=false;
  for(let i=0,j=verts.length-1;i<verts.length;j=i++){
    if((verts[i].y>p.y)!=(verts[j].y>p.y)&&p.x<(verts[j].x-verts[i].x)*(p.y-verts[i].y)/(verts[j].y-verts[i].y)+verts[i].x) inside=!inside;
  }
  return inside;
}

function getManifold(a,b){
  if(a.isStatic&&b.isStatic) return null;
  if(a.shape==='circle'&&b.shape==='circle') return circleCircle(a,b);
  if(a.shape==='circle'&&(b.shape==='rect'||b.shape==='poly')) return circlePoly(a,b);
  if((a.shape==='rect'||a.shape==='poly')&&b.shape==='circle'){ const m=circlePoly(b,a); if(m){m.normal=V.neg(m.normal);} return m; }
  return polyPoly(a,b);
}

// ── IMPULSE RESOLUTION ────────────────────────────────────────
function resolveContact(a,b,normal,depth,contact){
  // positional correction (Baumgarte)
  const slop=0.01, percent=0.4;
  const correction=Math.max(depth-slop,0)/(a.invMass+b.invMass)*percent;
  const corr=V.scale(normal,correction);
  if(!a.isStatic){ a.x-=corr.x*a.invMass; a.y-=corr.y*a.invMass; }
  if(!b.isStatic){ b.x+=corr.x*b.invMass; b.y+=corr.y*b.invMass; }

  const ra=V.sub(contact,{x:a.x,y:a.y});
  const rb=V.sub(contact,{x:b.x,y:b.y});
  const raPerp=V.perp(ra), rbPerp=V.perp(rb);

  // relative velocity at contact
  const va2=V.add({x:a.vx,y:a.vy},V.scale(raPerp,a.omega));
  const vb2=V.add({x:b.vx,y:b.vy},V.scale(rbPerp,b.omega));
  const relV=V.sub(vb2,va2);
  const velAlongNormal=V.dot(relV,normal);
  if(velAlongNormal>0) return; // separating

  const e=Math.min(a.restitution,b.restitution);
  const raCrossN=V.cross(ra,normal);
  const rbCrossN=V.cross(rb,normal);
  const denom=a.invMass+b.invMass+raCrossN*raCrossN*a.invI+rbCrossN*rbCrossN*b.invI;
  let j=-(1+e)*velAlongNormal/denom;
  j=Math.max(j,0);

  const impulse=V.scale(normal,j);
  if(!a.isStatic){ a.vx-=impulse.x*a.invMass; a.vy-=impulse.y*a.invMass; a.omega-=V.cross(ra,impulse)*a.invI; }
  if(!b.isStatic){ b.vx+=impulse.x*b.invMass; b.vy+=impulse.y*b.invMass; b.omega+=V.cross(rb,impulse)*b.invI; }

  // ── FRICTION IMPULSE ──────────────────────────────────────
  // recompute relative velocity
  const va3=V.add({x:a.vx,y:a.vy},V.scale(raPerp,a.omega));
  const vb3=V.add({x:b.vx,y:b.vy},V.scale(rbPerp,b.omega));
  const relV2=V.sub(vb3,va3);
  const tangent=V.norm(V.sub(relV2,V.scale(normal,V.dot(relV2,normal))));
  const velAlongT=V.dot(relV2,tangent);
  const raCrossT=V.cross(ra,tangent);
  const rbCrossT=V.cross(rb,tangent);
  const denomT=a.invMass+b.invMass+raCrossT*raCrossT*a.invI+rbCrossT*rbCrossT*b.invI;
  let jt=-velAlongT/denomT;
  const mu=Math.sqrt(a.friction*b.friction); // geometric mean
  // Coulomb friction cone
  const jFric=Math.abs(jt)<=j*mu ? V.scale(tangent,jt) : V.scale(tangent,-j*mu*Math.sign(jt));
  if(!a.isStatic){ a.vx-=jFric.x*a.invMass; a.vy-=jFric.y*a.invMass; a.omega-=V.cross(ra,jFric)*a.invI; }
  if(!b.isStatic){ b.vx+=jFric.x*b.invMass; b.vy+=jFric.y*b.invMass; b.omega+=V.cross(rb,jFric)*b.invI; }
}

// ── BOUNDARY COLLISION ────────────────────────────────────────
const FLOOR=()=>canvas.height-16;
const LWALL=8, RWALL=()=>canvas.width-8;

function boundaryCollide(b){
  const floor=FLOOR(),rw=RWALL();
  if(b.shape==='circle'){
    if(b.y+b.r>floor){
      b.y=floor-b.r;
      const vN=b.vy, vT=b.vx;
      const e=b.restitution, mu=b.friction;
      const j=(1+e)*b.mass*(-vN); // normal impulse
      const jt=Math.min(Math.abs(mu*j),Math.abs(b.mass*vT))*Math.sign(-vT);
      b.vy=-Math.abs(vN)*e;
      b.vx+=jt/b.mass;
      // rolling: torque from friction at contact
      b.omega-=(jt/b.mass)/b.r;
      b.omega*=0.98;
    }
    if(b.y-b.r<0){ b.y=b.r; b.vy=Math.abs(b.vy)*b.restitution; }
    if(b.x-b.r<LWALL){ b.x=LWALL+b.r; b.vx=Math.abs(b.vx)*b.restitution; b.omega*=0.9; }
    if(b.x+b.r>rw){ b.x=rw-b.r; b.vx=-Math.abs(b.vx)*b.restitution; b.omega*=0.9; }
  } else {
    // box/poly: corner-based clamping
    if(b.y+Math.max(b.w||0,b.h||0)*0.8>floor){ b.y=floor-(b.h||b.w||20)*0.7; b.vy=-Math.abs(b.vy)*b.restitution*0.75; b.vx*=(1-b.friction*0.3); b.omega*=0.85; }
    if(b.y<0){ b.y=0; b.vy=Math.abs(b.vy)*b.restitution; }
    if(b.x<LWALL+20){ b.x=LWALL+20; b.vx=Math.abs(b.vx)*b.restitution; b.omega*=-0.7; }
    if(b.x>rw-20){ b.x=rw-20; b.vx=-Math.abs(b.vx)*b.restitution; b.omega*=-0.7; }
  }
}

// wall segment collision
function closestPt(px,py,ax,ay,bx,by){ const dx=bx-ax,dy=by-ay,l2=dx*dx+dy*dy; if(l2<1e-6)return{x:ax,y:ay}; const t=Math.max(0,Math.min(1,((px-ax)*dx+(py-ay)*dy)/l2)); return{x:ax+t*dx,y:ay+t*dy}; }
function segCollide(body){
  if(body.shape!=='circle') return;
  walls.forEach(w=>{
    const cp=closestPt(body.x,body.y,w.x1,w.y1,w.x2,w.y2);
    const dx=body.x-cp.x,dy=body.y-cp.y,d=Math.sqrt(dx*dx+dy*dy);
    if(d<body.r&&d>0.01){
      const nx=dx/d,ny=dy/d;
      body.x=cp.x+nx*(body.r+0.5); body.y=cp.y+ny*(body.r+0.5);
      const dot=body.vx*nx+body.vy*ny;
      if(dot<0){ body.vx-=(1+body.restitution)*dot*nx; body.vy-=(1+body.restitution)*dot*ny; body.vx*=(1-body.friction*0.3); body.vy*=(1-body.friction*0.3); }
    }
  });
}

// peg collision
function pegCollide(b){
  if(b.shape!=='circle') return;
  pegs.forEach(p=>{ const dx=b.x-p.x,dy=b.y-p.y,d=Math.sqrt(dx*dx+dy*dy),md=b.r+p.r; if(d<md&&d>0.01){ const nx=dx/d,ny=dy/d; b.x=p.x+nx*(md+0.5);b.y=p.y+ny*(md+0.5); const dot=b.vx*nx+b.vy*ny; if(dot<0){b.vx-=2*dot*nx*b.restitution;b.vy-=2*dot*ny*b.restitution;} }});
}

// ── SPRING SYSTEM ─────────────────────────────────────────────
function makeSpring(a,b,k,damp,restLen,color){ const dx=b.x-a.x,dy=b.y-a.y; return{a,b,k:k||0.12,damp:damp||0.04,restLen:restLen!=null?restLen:Math.sqrt(dx*dx+dy*dy),color:color||'#333'}; }
function updateSprings(){
  springs.forEach(s=>{
    if(!bodies.includes(s.a)||!bodies.includes(s.b)) return;
    const dx=s.b.x-s.a.x,dy=s.b.y-s.a.y,d=Math.sqrt(dx*dx+dy*dy)||0.001;
    const stretch=d-s.restLen,nx=dx/d,ny=dy/d;
    const force=s.k*stretch;
    const dvx=s.b.vx-s.a.vx,dvy=s.b.vy-s.a.vy;
    const damp=s.damp*(dvx*nx+dvy*ny);
    const fx=(force+damp)*nx,fy=(force+damp)*ny;
    if(!s.a.isStatic){s.a.vx+=fx;s.a.vy+=fy;}
    if(!s.b.isStatic){s.b.vx-=fx;s.b.vy-=fy;}
  });
  springs=springs.filter(s=>bodies.includes(s.a)&&bodies.includes(s.b));
}

// ── WATER SIMULATION ─────────────────────────────────────────
function makeWater(y, nPts){
  const pts=[], spacing=canvas.width/(nPts-1);
  for(let i=0;i<nPts;i++) pts.push({x:i*spacing,y,vy:0,baseY:y});
  return{pts,spacing,tension:0.025,damping:0.98,spread:0.18,baseY:y};
}
function updateWater(dt){
  if(!waterSurface) return;
  const w=waterSurface, pts=w.pts, n=pts.length;
  // object interaction
  bodies.forEach(b=>{
    if(b.isStatic) return;
    if(b.shape==='circle'){
      const i=Math.round(b.x/w.spacing); if(i<0||i>=n) return;
      if(b.y+b.r>w.baseY-20&&b.y<w.baseY+40&&Math.abs(b.vy)>1){
        pts[i].vy-=b.vy*0.08*Math.min(1,b.mass*0.1);
        if(b.y+b.r>w.baseY){ b.vy=-Math.abs(b.vy)*0.3; b.vx*=0.9; }
        // buoyancy
        const submerge=Math.max(0,Math.min(b.r*2,(b.y+b.r)-w.baseY));
        const buoy=submerge/b.r*GRAVITY*b.mass*0.7;
        b.vy-=buoy*dt;
      }
    }
  });
  // spring dynamics
  for(let i=0;i<n;i++){
    const dy=pts[i].y-pts[i].baseY;
    pts[i].vy+=(-w.tension*dy - w.damping*pts[i].vy);
  }
  // propagate
  const left=new Array(n).fill(0), right=new Array(n).fill(0);
  for(let iter=0;iter<8;iter++){
    for(let i=1;i<n;i++) left[i]=w.spread*(pts[i].y-pts[i-1].y);
    for(let i=0;i<n-1;i++) right[i]=w.spread*(pts[i].y-pts[i+1].y);
    for(let i=0;i<n;i++){ pts[i].vy+=left[i]+right[i]; }
  }
  for(let i=0;i<n;i++) pts[i].y+=pts[i].vy;
}
function drawWater(){
  if(!waterSurface) return;
  const pts=waterSurface.pts, H=canvas.height;
  ctx.beginPath();
  ctx.moveTo(0,H);
  ctx.lineTo(pts[0].x,pts[0].y);
  for(let i=1;i<pts.length-1;i++){
    const mx=(pts[i].x+pts[i+1].x)/2,my=(pts[i].y+pts[i+1].y)/2;
    ctx.quadraticCurveTo(pts[i].x,pts[i].y,mx,my);
  }
  ctx.lineTo(pts[pts.length-1].x,pts[pts.length-1].y);
  ctx.lineTo(canvas.width,H); ctx.closePath();
  const wg=ctx.createLinearGradient(0,waterSurface.baseY-40,0,H);
  wg.addColorStop(0,'rgba(26,115,232,0.55)');
  wg.addColorStop(1,'rgba(0,60,130,0.85)');
  ctx.fillStyle=wg; ctx.fill();
  // surface shimmer
  ctx.beginPath();
  ctx.moveTo(pts[0].x,pts[0].y);
  for(let i=1;i<pts.length-1;i++){
    const mx=(pts[i].x+pts[i+1].x)/2,my=(pts[i].y+pts[i+1].y)/2;
    ctx.quadraticCurveTo(pts[i].x,pts[i].y,mx,my);
  }
  ctx.strokeStyle='rgba(100,180,255,0.5)'; ctx.lineWidth=2; ctx.stroke();
}

// ── PRESETS ───────────────────────────────────────────────────
function addPreset(p){
  clearAll();
  const W=canvas.width,H=canvas.height;

  if(p==='pendulum'){
    const pivot={x:W/2,y:80,isStatic:true};
    [0,1,2,3].forEach(i=>{
      const angle=Math.PI/3-i*0.12, len=120+i*18;
      const b=makeCircle(W/2+Math.sin(angle)*len,80+Math.cos(angle)*len,14,'rubber');
      b.isPendulum=true; b.pivotX=W/2; b.pivotY=80; b.armLen=len; b.angle=angle; b.omega=0.015+i*0.005;
      b.color=PALETTE[i]; bodies.push(b);
    });

  } else if(p==='newtonsCradle'){
    const cx=W/2,py=80,len=160,r=22,n=5,sp=r*2+1;
    for(let i=0;i<n;i++){
      const ang=i===0?Math.PI/2.2:0;
      const b=makeCircle(cx+(i-(n-1)/2)*sp+Math.sin(ang)*len,py+Math.cos(ang)*len,r,'metal');
      b.isPendulum=true; b.pivotX=cx+(i-(n-1)/2)*sp; b.pivotY=py; b.armLen=len; b.angle=ang; b.omega=0;
      b.color='#b0bec5'; bodies.push(b);
    }

  } else if(p==='dominos'){
    for(let i=0;i<16;i++){ const b=makeRect(120+i*52,H-90,14,72,'wood'); b.vx=0;b.vy=0;b.angle=0; bodies.push(b); }
    const ball=makeCircle(40,H-200,20,'rubber','#e53935'); ball.vx=9; bodies.push(ball);

  } else if(p==='stack'){
    for(let row=0;row<7;row++) for(let col=0;col<7-row;col++){
      const b=makeRect(W/2-120+col*44+row*22,H-50-row*46,40,40,'wood'); b.angle=0; bodies.push(b);
    }

  } else if(p==='bridge'){
    const n=14,sp=44,y=H*0.44,sx=(W-n*sp)/2,nodes=[];
    for(let i=0;i<=n;i++){
      const b=makeCircle(sx+i*sp,y,7,'metal','#c8960c');
      if(i===0||i===n) b.isStatic=true,b.invMass=0,b.invI=0;
      nodes.push(b); bodies.push(b);
    }
    for(let i=0;i<n;i++) springs.push(makeSpring(nodes[i],nodes[i+1],0.22,0.07,sp,'#7a5c00'));
    for(let i=0;i<n-1;i+=2){
      const top=makeCircle(nodes[i+1].x,y-85,4,'metal','#444'); top.isStatic=true;top.invMass=0;top.invI=0;
      bodies.push(top);
      springs.push(makeSpring(nodes[i],top,0.1,0.04,null,'#2a2a2a'));
      springs.push(makeSpring(nodes[i+2],top,0.1,0.04,null,'#2a2a2a'));
    }
    for(let i=2;i<n-1;i+=3){ const b=makeCircle(nodes[i].x,y-40,10,'default'); bodies.push(b); }

  } else if(p==='cloth'){
    const cols=12,rows=9,sp=45,sx=(W-cols*sp)/2,sy=40,grid=[];
    for(let r=0;r<rows;r++){ grid[r]=[]; for(let c=0;c<cols;c++){
      const b=makeCircle(sx+c*sp,sy+r*sp,5,'default','#4a9eff');
      if(r===0){b.isStatic=true;b.invMass=0;b.invI=0;}
      grid[r][c]=b; bodies.push(b);
    }}
    for(let r=0;r<rows;r++) for(let c=0;c<cols;c++){
      if(c<cols-1) springs.push(makeSpring(grid[r][c],grid[r][c+1],0.15,0.05,sp,'#1a4a88'));
      if(r<rows-1) springs.push(makeSpring(grid[r][c],grid[r+1][c],0.15,0.05,sp,'#1a4a88'));
      if(c<cols-1&&r<rows-1){ springs.push(makeSpring(grid[r][c],grid[r+1][c+1],0.05,0.02,null,'#0a2a55')); springs.push(makeSpring(grid[r][c+1],grid[r+1][c],0.05,0.02,null,'#0a2a55')); }
    }

  } else if(p==='ragdoll'){
    const cx=W/2,cy=H*0.22;
    function rb(x,y,r,m){ const b=makeCircle(x,y,r,'default','#f5cba7'); b.mass=m;b.invMass=1/m;b.I=0.5*m*r*r;b.invI=1/b.I; return b; }
    const head=rb(cx,cy,15,1),torso=rb(cx,cy+44,10,3),hips=rb(cx,cy+84,8,2);
    const ls=rb(cx-22,cy+34,7,1),rs=rb(cx+22,cy+34,7,1);
    const le=rb(cx-36,cy+60,6,0.8),re=rb(cx+36,cy+60,6,0.8);
    const lh=rb(cx-46,cy+82,5,0.5),rh=rb(cx+46,cy+82,5,0.5);
    const lk=rb(cx-15,cy+114,7,1),rk=rb(cx+15,cy+114,7,1);
    const lf=rb(cx-15,cy+144,6,0.6),rf=rb(cx+15,cy+144,6,0.6);
    const all=[head,torso,hips,ls,rs,le,re,lh,rh,lk,rk,lf,rf];
    all.forEach(b=>{b.vx=0;b.vy=0;bodies.push(b);});
    const sk=0.38,sd=0.1;
    [[head,torso],[torso,hips],[torso,ls],[torso,rs],[ls,le],[rs,re],[le,lh],[re,rh],[hips,lk],[hips,rk],[lk,lf],[rk,rf],[ls,rs],[lk,rk]].forEach(([a,b])=>springs.push(makeSpring(a,b,sk,sd,null,'#666')));
    head.vx=12; head.vy=-10;

  } else if(p==='rope'){
    const n=22,x1=W*0.22,x2=W*0.78,y=H*0.18,nodes=[];
    for(let i=0;i<=n;i++){
      const t=i/n, b=makeCircle(x1+(x2-x1)*t,y+Math.sin(t*Math.PI)*70,6,'default','#f29900');
      if(i===0||i===n){b.isStatic=true;b.invMass=0;b.invI=0;}
      nodes.push(b); bodies.push(b);
    }
    for(let i=0;i<n;i++) springs.push(makeSpring(nodes[i],nodes[i+1],0.35,0.1,null,'#a06000'));
    const ball=makeCircle(W/2,y-80,20,'rubber','#1a73e8'); ball.vy=0; bodies.push(ball);

  } else if(p==='funnel'){
    for(let i=0;i<32;i++){ const b=makeCircle(W/2+(rnd(-1,1)*40),30+i*8,8,currentMaterial); b.vx=rnd(-2,2); bodies.push(b); }
    walls.push({x1:W/2-160,y1:200,x2:W/2-22,y2:360},{x1:W/2+160,y1:200,x2:W/2+22,y2:360});

  } else if(p==='avalanche'){
    for(let i=0;i<10;i++) for(let j=0;j<6-Math.floor(i/2);j++){ const b=makeRect(80+i*50,H-60-j*44,42,38,'wood'); bodies.push(b); }
    const ball=makeCircle(30,H*0.3,22,'rubber','#e53935'); ball.vx=16;ball.vy=-2; bodies.push(ball);

  } else if(p==='jenga'){
    const bw=82,bh=18,cx=W/2;
    for(let i=0;i<14;i++){
      if(i%2===0){ const b1=makeRect(cx-bw/2-2,H-24-i*bh,bw/2-2,bh-2,'wood'); const b2=makeRect(cx+2,H-24-i*bh,bw/2-2,bh-2,'wood'); bodies.push(b1,b2); }
      else { const b=makeRect(cx,H-24-i*bh,bw+4,bh-2,'wood'); bodies.push(b); }
    }
    const ball=makeCircle(W*0.14,H*0.25,17,'rubber','#e53935'); ball.vx=20; bodies.push(ball);

  } else if(p==='orbit'){
    const cx=W/2,cy=H/2;
    const sun=makeCircle(cx,cy,28,'metal','#f29900'); sun.isStatic=true;sun.invMass=0;sun.invI=0; bodies.push(sun);
    [80,130,185,240].forEach((r,i)=>{ const speed=Math.sqrt(GRAVITY*10/r)*2.5; const b=makeCircle(cx+r,cy,8+i*2,currentMaterial); b.vx=0;b.vy=speed; bodies.push(b); });

  } else if(p==='blackhole'){
    specials.push({type:'blackhole',x:W/2,y:H/2,r:22,strength:700});
    for(let i=0;i<55;i++){ const b=makeCircle(rnd(20,W-20),rnd(20,H-20),rnd(4,12),currentMaterial); b.vx=rnd(-8,8);b.vy=rnd(-8,8); bodies.push(b); }

  } else if(p==='pachinko'){
    GRAVITY=15; document.getElementById('gravSlider').value=15; document.getElementById('gravVal').textContent='15';
    const rows=8,cols=7;
    for(let row=0;row<rows;row++){ const off=row%2===0?0:(W/(cols))/2; for(let col=0;col<cols;col++) pegs.push({x:off+col*(W/(cols-1))*0.85+W*0.08,y:110+row*65,r:8}); }
    for(let i=0;i<10;i++){ const b=makeCircle(rnd(W*0.2,W*0.8),rnd(-80,-10),rnd(7,11),'rubber'); bodies.push(b); }

  } else if(p==='water'){
    waterSurface=makeWater(H*0.55,80);
    // wall ledges
    walls.push({x1:W*0.05,y1:H*0.35,x2:W*0.28,y2:H*0.45},{x1:W*0.72,y1:H*0.35,x2:W*0.95,y2:H*0.45});
    for(let i=0;i<12;i++){
      const b=makeCircle(rnd(W*0.1,W*0.9),rnd(H*0.05,H*0.4),rnd(8,18),i%2===0?'rubber':'metal');
      b.vy=0; bodies.push(b);
    }

  } else if(p==='softball'){
    const cx=W/2,cy=H*0.28,n=16,R=52,pts=[];
    for(let i=0;i<n;i++){
      const a=i*Math.PI*2/n, b=makeCircle(cx+Math.cos(a)*R,cy+Math.sin(a)*R,7,'rubber','#e53935');
      b.vx=0;b.vy=0; pts.push(b); bodies.push(b);
    }
    for(let i=0;i<n;i++){
      springs.push(makeSpring(pts[i],pts[(i+1)%n],0.28,0.09,null,'#992222'));
      springs.push(makeSpring(pts[i],pts[(i+2)%n],0.1,0.04,null,'#661111'));
      springs.push(makeSpring(pts[i],pts[(i+n/2|0)%n],0.08,0.03,null,'#441111'));
    }

  } else if(p==='gas'){
    GRAVITY=0; document.getElementById('gravSlider').value=0; document.getElementById('gravVal').textContent='0';
    for(let i=0;i<80;i++){
      const b=makeCircle(rnd(20,W-20),rnd(20,H-80),rnd(4,8),'bounce');
      const speed=rnd(6,16),angle=rnd(0,Math.PI*2); b.vx=Math.cos(angle)*speed;b.vy=Math.sin(angle)*speed;
      bodies.push(b);
    }

  } else if(p==='collision'){
    GRAVITY=0; document.getElementById('gravSlider').value=0; document.getElementById('gravVal').textContent='0';
    const mats=['rubber','metal','ice','bounce'];
    mats.forEach((mat,i)=>{
      const r=10+i*4, y=H*0.2+i*(H*0.18);
      const a=makeCircle(80,y,r,mat); a.vx=14; bodies.push(a);
      const b=makeCircle(W-80,y,r+4,mat); b.vx=-10; bodies.push(b);
      // label
    });
    // also some rects
    const box1=makeRect(W/2-60,H*0.82,50,50,'wood'); box1.vx=8; bodies.push(box1);
    const box2=makeRect(W/2+60,H*0.82,50,50,'metal'); box2.vx=-6; bodies.push(box2);

  } else if(p==='gyro'){
    // spinning tops that precess
    for(let i=0;i<4;i++){
      const b=makeCircle(W*0.2+i*W*0.2,H*0.4,18,'metal');
      b.omega=20-i*4; // high angular velocity
      b.vx=rnd(-1,1); bodies.push(b);
    }
    for(let i=0;i<3;i++){
      const b=makeRect(W*0.25+i*W*0.25,H*0.5,30,30,'metal'); b.omega=15-i*4; bodies.push(b);
    }

  } else if(p==='billiards'){
    GRAVITY=0; document.getElementById('gravSlider').value=0; document.getElementById('gravVal').textContent='0';
    airDrag=0.008; document.getElementById('dragSlider').value=8; document.getElementById('dragVal').textContent='8';
    const cx=W/2+60,cy=H/2,r=14,mats='metal';
    // rack triangle
    let row=0,col=0;
    for(let n=0;n<15;n++){
      const b=makeCircle(cx+row*r*1.75,cy+(col-row/2)*r*2,r,mats,PALETTE[n%PALETTE.length]);
      b.vx=0;b.vy=0;b.restitution=0.96;b.friction=0.05; bodies.push(b);
      col++; if(col>row){row++;col=0;}
    }
    // cue ball
    const cue=makeCircle(W*0.22,H/2,r,'metal','#eee'); cue.vx=28;cue.vy=rnd(-1.5,1.5);cue.restitution=0.96;cue.friction=0.05; bodies.push(cue);

  } else if(p==='snow'){
    GRAVITY=2.5; document.getElementById('gravSlider').value=2.5; document.getElementById('gravVal').textContent='2.5';
    snowTimer=1;
    walls.push({x1:W*0.1,y1:H*0.55,x2:W*0.38,y2:H*0.68},{x1:W*0.62,y1:H*0.5,x2:W*0.9,y2:H*0.65},{x1:W*0.3,y1:H*0.72,x2:W*0.7,y2:H*0.82});

  } else if(p==='fireworks'){
    fireworkTimer=1;
  }
}

// ── FIREWORK ─────────────────────────────────────────────────
function spawnFirework(){
  const W=canvas.width,H=canvas.height;
  const x=rnd(W*0.15,W*0.85),y=rnd(H*0.06,H*0.5),col=rndPalette();
  for(let i=0;i<30;i++){
    const a=rnd(0,Math.PI*2),s=rnd(5,22);
    const b=makeCircle(x,y,rnd(3,7),'default',col); b.vx=Math.cos(a)*s;b.vy=Math.sin(a)*s;b.life=1;b.decay=rnd(0.013,0.027); bodies.push(b);
  }
  for(let i=0;i<16;i++){ const a=i*Math.PI*2/16,s=rnd(9,16); const b=makeCircle(x,y,4,'default','#f29900'); b.vx=Math.cos(a)*s;b.vy=Math.sin(a)*s;b.life=1;b.decay=rnd(0.02,0.04); bodies.push(b); }
}

// ── UI ────────────────────────────────────────────────────────
function setMode(m,el){
  mode=m; grabBody=null; inspectedBody=null;
  document.querySelectorAll('.tbtn').forEach(b=>b.classList.remove('active'));
  if(el) el.classList.add('active');
  document.getElementById('hMode').textContent=m;
  canvas.style.cursor=m==='grab'?'grab':m==='erase'?'not-allowed':m==='inspect'?'zoom-in':'crosshair';
  document.getElementById('inspector').style.display=m==='inspect'?'block':'none';
}
function toggleForce(f,el){
  if(f==='magnet'){ magnetActive=!magnetActive; repulsorActive=false; vortexActive=false; }
  if(f==='anti'){ repulsorActive=!repulsorActive; magnetActive=false; vortexActive=false; }
  if(f==='wind'){ windForce=windForce===0?8:0; document.getElementById('windSlider') && (()=>{})(); }
  if(f==='vortex'){ vortexActive=!vortexActive; magnetActive=false; repulsorActive=false; }
  document.querySelectorAll('[id^=btn-mag],[id^=btn-anti],[id^=btn-vor]').forEach(b=>b.classList.remove('active'));
  if(el) el.classList.toggle('active',magnetActive||repulsorActive||vortexActive);
}
function toggleMatPanel(){ const p=document.getElementById('mat-panel'); p.style.display=p.style.display==='none'?'block':'none'; }
function togglePause(){ paused=!paused; document.getElementById('pauseBtn').textContent=paused?'▶ Resume':'⏸ Pause'; }
function stepOnce(){ if(paused) pendingStep=true; }
function explodeAll(){ bodies.forEach(b=>{ if(!b.isStatic){b.vx+=(Math.random()-0.5)*60;b.vy+=(Math.random()-0.5)*60;} }); }
function screenshot(){ const l=document.createElement('a'); l.download='physics_'+Date.now()+'.png'; l.href=canvas.toDataURL(); l.click(); }
function toggleLight(){ dynamicLight=!dynamicLight; document.getElementById('lightBtn').classList.toggle('active',dynamicLight); }
function toggleTheme(){ darkTheme=!darkTheme; document.body.style.background=darkTheme?'#0a0a0a':'#f0f2f5'; }
function clearAll(){
  bodies=[]; springs=[]; walls=[]; pegs=[]; specials=[]; waterSurface=null;
  fireworkTimer=0; snowTimer=0; GRAVITY=9.8;
  document.getElementById('gravSlider').value=9.8; document.getElementById('gravVal').textContent='9.8';
  grabBody=null; inspectedBody=null;
  document.getElementById('inspector').style.display='none';
}

// ── MATERIAL PANEL ────────────────────────────────────────────
(function buildMatPanel(){
  const p=document.getElementById('mat-panel');
  Object.entries(MATERIALS).forEach(([key,mat])=>{
    const row=document.createElement('div'); row.className='mat-opt'+(key===currentMaterial?' sel':'');
    row.innerHTML=`<div class="mat-dot" style="background:${mat.color}"></div><span class="mat-label">${mat.name}</span>`;
    row.onclick=()=>{ currentMaterial=key; document.querySelectorAll('.mat-opt').forEach(r=>r.classList.remove('sel')); row.classList.add('sel'); };
    p.appendChild(row);
  });
})();

// ── MOUSE ────────────────────────────────────────────────────
function canvasXY(e){ const rect=canvas.getBoundingClientRect(),sx=canvas.width/rect.width,sy=canvas.height/rect.height; const src=e.touches?e.touches[0]:e; return{x:(src.clientX-rect.left)*sx,y:(src.clientY-rect.top)*sy}; }
function bodyAt(x,y){ return bodies.find(b=>{ if(b.shape==='circle') return Math.hypot(b.x-x,b.y-y)<b.r+8; if(b.shape==='rect') return Math.abs(b.x-x)<b.w/2+8&&Math.abs(b.y-y)<b.h/2+8; return false; }); }

canvas.addEventListener('mousedown',e=>{
  const {x,y}=canvasXY(e);
  if(mode==='wall'){ drawingWall=true; wallStart={x,y}; }
  else if(mode==='erase'){ eraseAt(x,y); }
  else if(mode==='grab'){ grabBody=bodyAt(x,y); if(grabBody&&!grabBody.isStatic){ grabBody._prevX=grabBody.x; grabBody._prevY=grabBody.y; canvas.style.cursor='grabbing'; } else grabBody=null; }
  else if(mode==='inspect'){ inspectedBody=bodyAt(x,y); }
  else if(magnetActive||repulsorActive||vortexActive){ applyForce(x,y); }
  else { spawnAt(x,y); }
});
canvas.addEventListener('mousemove',e=>{
  const {x,y}=canvasXY(e); cursorPos={x,y};
  if(e.buttons===1){
    if(mode==='grab'&&grabBody){ grabBody._prevX=grabBody.x; grabBody._prevY=grabBody.y; grabBody.x=x; grabBody.y=y; grabBody.vx=0;grabBody.vy=0; }
    else if(mode==='erase') eraseAt(x,y);
    else if(mode==='ball'&&Math.random()<0.2){ const b=makeCircle(x,y,spawnSize,currentMaterial); bodies.push(b); }
    else if(mode==='box'&&Math.random()<0.12){ const b=makeRect(x,y,spawnSize*2,spawnSize*2,currentMaterial); bodies.push(b); }
    else if(magnetActive||repulsorActive||vortexActive) applyForce(x,y);
    // water ripple on hover
    if(waterSurface&&mode==='ball'){ const i=Math.round(x/waterSurface.spacing); if(i>=0&&i<waterSurface.pts.length) waterSurface.pts[i].vy-=0.5; }
  }
});
canvas.addEventListener('mouseup',e=>{
  if(mode==='grab'&&grabBody){ canvas.style.cursor='grab'; grabBody=null; }
  if(drawingWall&&wallStart){ const {x,y}=canvasXY(e); if(Math.hypot(x-wallStart.x,y-wallStart.y)>10) walls.push({x1:wallStart.x,y1:wallStart.y,x2:x,y2:y}); drawingWall=false; wallStart=null; }
});

function spawnAt(x,y){
  if(mode==='ball'){ const b=makeCircle(x,y,spawnSize,currentMaterial); bodies.push(b); }
  else if(mode==='box'){ const b=makeRect(x,y,spawnSize*2,spawnSize*2,currentMaterial); b.omega=rnd(-0.05,0.05); bodies.push(b); }
  else if(mode==='poly'){
    const sides=Math.floor(rnd(3,8)), r=spawnSize+4, verts=[];
    for(let i=0;i<sides;i++){ const a=i*Math.PI*2/sides; verts.push({x:Math.cos(a)*r,y:Math.sin(a)*r}); }
    bodies.push(makeConvex(x,y,verts,currentMaterial));
  }
}
function eraseAt(x,y){ bodies=bodies.filter(b=>{ if(b.isStatic)return true; if(b.shape==='circle')return Math.hypot(b.x-x,b.y-y)>b.r+30; return Math.abs(b.x-x)>b.w/2+20||Math.abs(b.y-y)>b.h/2+20; }); springs=springs.filter(s=>bodies.includes(s.a)&&bodies.includes(s.b)); walls=walls.filter(w=>{const mx=(w.x1+w.x2)/2,my=(w.y1+w.y2)/2;return Math.hypot(mx-x,my-y)>35;}); }
function applyForce(cx,cy){
  bodies.forEach(b=>{
    if(b.isStatic) return;
    const dx=cx-b.x,dy=cy-b.y,d=Math.sqrt(dx*dx+dy*dy)||1;
    const sign=magnetActive?1:repulsorActive?-1:0;
    if(magnetActive||repulsorActive){ const f=sign*300/(d*d+1); b.vx+=dx/d*f; b.vy+=dy/d*f; }
    if(vortexActive){ const f=200/(d+1)*0.015; b.vx+=dy/d*f; b.vy+=-dx/d*f; }
  });
}

// ── PROMPT ────────────────────────────────────────────────────
function runPrompt(){
  const txt=document.getElementById('promptIn').value.toLowerCase().trim();
  const n=parseInt(txt.match(/\d+/)?.[0]);
  const map={water:'water',billiard:'billiards',gyro:'gyro',ragdoll:'ragdoll',rope:'rope',cloth:'cloth',bridge:'bridge',softball:'softball',pendulum:'pendulum',newton:'newtonsCradle',domino:'dominos',stack:'stack',funnel:'funnel',avalanche:'avalanche',jenga:'jenga',orbit:'orbit','black hole':'blackhole',pachinko:'pachinko',gas:'gas',collision:'collision',snow:'snow',firework:'fireworks'};
  for(const [k,v] of Object.entries(map)){ if(txt.includes(k)){addPreset(v);document.getElementById('promptIn').value='';return;} }
  if(txt.includes('clear')||txt.includes('reset')){ clearAll(); }
  else if(txt.includes('explode')){ explodeAll(); }
  else if(txt.includes('zero grav')||txt.includes('no grav')){ GRAVITY=0;document.getElementById('gravSlider').value=0;document.getElementById('gravVal').textContent='0'; }
  else if(txt.includes('max grav')){ GRAVITY=30;document.getElementById('gravSlider').value=30;document.getElementById('gravVal').textContent='30'; }
  else if(txt.includes('reverse grav')||txt.includes('flip grav')){ GRAVITY=-Math.abs(GRAVITY);document.getElementById('gravSlider').value=GRAVITY;document.getElementById('gravVal').textContent=GRAVITY; }
  else if(txt.includes('freeze')){ bodies.forEach(b=>{b.vx=0;b.vy=0;b.omega=0;}); }
  else if(txt.includes('spin')){ bodies.forEach(b=>{ if(!b.isStatic)b.omega+=(Math.random()-0.5)*20; }); }
  else{ const cnt=n||10; for(let i=0;i<cnt;i++) bodies.push(makeCircle(rnd(50,canvas.width-50),rnd(20,canvas.height*0.3),spawnSize,currentMaterial)); }
  document.getElementById('promptIn').value='';
}
document.getElementById('promptIn').addEventListener('keydown',e=>{if(e.key==='Enter')runPrompt();});

// ── DRAWING ───────────────────────────────────────────────────
function lighten(hex,amt){ const r=parseInt(hex.slice(1,3)||'80',16),g=parseInt(hex.slice(3,5)||'80',16),b=parseInt(hex.slice(5,7)||'80',16); return`rgb(${Math.min(255,r+(amt*255)|0)},${Math.min(255,g+(amt*255)|0)},${Math.min(255,b+(amt*255)|0)})`; }
function darken(hex,amt){ const r=parseInt(hex.slice(1,3)||'80',16),g=parseInt(hex.slice(3,5)||'80',16),b=parseInt(hex.slice(5,7)||'80',16); return`rgb(${Math.max(0,r-(amt*255)|0)},${Math.max(0,g-(amt*255)|0)},${Math.max(0,b-(amt*255)|0)})`; }

function drawBody(b){
  const alpha=b.life!==undefined?Math.max(0,b.life):1;
  ctx.globalAlpha=alpha;

  if(b.shape==='circle'){
    // trail
    if(b.trail&&b.trail.length>1&&trailLen>0){
      for(let i=1;i<b.trail.length;i++){
        const t=i/b.trail.length;
        ctx.beginPath();ctx.moveTo(b.trail[i-1].x,b.trail[i-1].y);ctx.lineTo(b.trail[i].x,b.trail[i].y);
        ctx.strokeStyle=b.color+(Math.floor(t*120).toString(16).padStart(2,'0'));
        ctx.lineWidth=Math.max(1,b.r*0.35*t); ctx.stroke();
      }
    }
    // pendulum arm
    if(b.isPendulum){ ctx.beginPath();ctx.moveTo(b.pivotX,b.pivotY);ctx.lineTo(b.x,b.y);ctx.strokeStyle='#2a2a2a';ctx.lineWidth=2;ctx.stroke(); }

    // dynamic light shading
    let lightNX=0.6, lightNY=-0.8;
    if(dynamicLight){ const lx=cursorPos.x-b.x,ly=cursorPos.y-b.y,ld=Math.sqrt(lx*lx+ly*ly)||1; lightNX=lx/ld;lightNY=ly/ld; }
    const offX=-lightNX*b.r*0.3, offY=-lightNY*b.r*0.3;
    const grad=ctx.createRadialGradient(b.x+offX,b.y+offY,b.r*0.05,b.x,b.y,b.r);
    grad.addColorStop(0,lighten(b.color,0.55));
    grad.addColorStop(0.5,b.color);
    grad.addColorStop(1,darken(b.color,0.35));
    ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,Math.PI*2);
    ctx.fillStyle=grad; ctx.fill();

    // specular highlight
    const hx=b.x+offX*0.7, hy=b.y+offY*0.7, hr=b.r*0.28;
    const sg=ctx.createRadialGradient(hx,hy,0,hx,hy,hr);
    sg.addColorStop(0,'rgba(255,255,255,0.55)'); sg.addColorStop(1,'rgba(255,255,255,0)');
    ctx.beginPath();ctx.arc(hx,hy,hr,0,Math.PI*2); ctx.fillStyle=sg; ctx.fill();

    // ground shadow
    if(!b.isPendulum){
      const floor=FLOOR(),shadowY=floor,dist=Math.max(0,shadowY-b.y);
      const scaleX=Math.max(0.1,1-dist/400),alpha2=Math.max(0,0.3-dist/600);
      if(alpha2>0.01){ ctx.beginPath();ctx.ellipse(b.x,shadowY,b.r*scaleX*1.2,b.r*0.2*scaleX,0,0,Math.PI*2); ctx.fillStyle=`rgba(0,0,0,${alpha2})`;ctx.fill(); }
    }

    // rolling indicator (rotation line)
    if(b.r>8){
      ctx.beginPath();
      ctx.moveTo(b.x,b.y);
      ctx.lineTo(b.x+Math.cos(b.angle)*b.r*0.85,b.y+Math.sin(b.angle)*b.r*0.85);
      ctx.strokeStyle='rgba(255,255,255,0.25)';ctx.lineWidth=1.5;ctx.stroke();
    }

    // inspect ring
    if(b===inspectedBody){ ctx.beginPath();ctx.arc(b.x,b.y,b.r+5,0,Math.PI*2);ctx.strokeStyle='#fff';ctx.lineWidth=1.5;ctx.stroke(); }

  } else if(b.shape==='rect'){
    ctx.save(); ctx.translate(b.x,b.y); ctx.rotate(b.angle);
    // face shading
    const hw=b.w/2,hh=b.h/2;
    ctx.fillStyle=b.color;ctx.fillRect(-hw,-hh,b.w,b.h);
    // top face lighter
    ctx.fillStyle='rgba(255,255,255,0.12)';ctx.fillRect(-hw,-hh,b.w,hh);
    // right face darker
    ctx.fillStyle='rgba(0,0,0,0.15)';ctx.fillRect(0,-hh,hw,b.h);
    // edge highlight
    ctx.strokeStyle='rgba(255,255,255,0.08)';ctx.lineWidth=1;ctx.strokeRect(-hw,-hh,b.w,b.h);
    if(b===inspectedBody){ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.strokeRect(-hw-4,-hh-4,b.w+8,b.h+8);}
    ctx.restore();
    // shadow
    if(!b.isStatic){const floor=FLOOR(),dist=Math.max(0,floor-b.y);const sa=Math.max(0,0.25-dist/500);if(sa>0.01){ctx.beginPath();ctx.ellipse(b.x,floor,b.w*0.45*(1-dist/500),b.h*0.08,b.angle,0,Math.PI*2);ctx.fillStyle=`rgba(0,0,0,${sa})`;ctx.fill();}}

  } else if(b.shape==='poly'){
    const verts=polyVerts(b);
    ctx.beginPath();ctx.moveTo(verts[0].x,verts[0].y);
    verts.forEach(v=>ctx.lineTo(v.x,v.y));ctx.closePath();
    ctx.fillStyle=b.color;ctx.fill();
    ctx.strokeStyle='rgba(255,255,255,0.1)';ctx.lineWidth=1;ctx.stroke();
    if(b===inspectedBody){ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke();}
  }
  ctx.globalAlpha=1;
}

function drawSprings(){
  springs.forEach(s=>{
    if(!bodies.includes(s.a)||!bodies.includes(s.b)) return;
    const dx=s.b.x-s.a.x,dy=s.b.y-s.a.y,d=Math.sqrt(dx*dx+dy*dy),strain=Math.abs(d-s.restLen)/Math.max(s.restLen,1);
    const col=strain>0.35?'#e53935':strain>0.15?'#f29900':s.color;
    ctx.beginPath();ctx.moveTo(s.a.x,s.a.y);ctx.lineTo(s.b.x,s.b.y);ctx.strokeStyle=col;ctx.lineWidth=1.5;ctx.stroke();
  });
}
function drawWalls(){
  walls.forEach(w=>{
    ctx.beginPath();ctx.moveTo(w.x1,w.y1);ctx.lineTo(w.x2,w.y2);
    ctx.strokeStyle='#666';ctx.lineWidth=5;ctx.lineCap='round';ctx.stroke();
    ctx.strokeStyle='rgba(255,255,255,0.12)';ctx.lineWidth=2;ctx.stroke();
  });
  if(drawingWall&&wallStart){ ctx.beginPath();ctx.moveTo(wallStart.x,wallStart.y);ctx.lineTo(cursorPos.x,cursorPos.y);ctx.strokeStyle='#1a73e8aa';ctx.lineWidth=3;ctx.setLineDash([6,4]);ctx.stroke();ctx.setLineDash([]); }
}
function drawPegs(){ pegs.forEach(p=>{ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle='#3a3a3a';ctx.fill();ctx.strokeStyle='#777';ctx.lineWidth=1;ctx.stroke();}); }
function drawSpecials(){
  specials.forEach(s=>{
    if(s.type==='blackhole'){
      const pulse=Math.sin(Date.now()*0.004)*6;
      const g=ctx.createRadialGradient(s.x,s.y,0,s.x,s.y,s.r*5+pulse);
      g.addColorStop(0,'rgba(0,0,0,1)');g.addColorStop(0.3,'rgba(80,0,140,0.6)');g.addColorStop(1,'rgba(0,0,0,0)');
      ctx.beginPath();ctx.arc(s.x,s.y,s.r*5+pulse,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
    }
  });
}
function drawFloor(){
  const floor=FLOOR(),W=canvas.width;
  // grid pattern on floor
  const bg=darkTheme?'#0f0f0f':'#e8e8e8';
  const fg=darkTheme?'#161616':'#d8d8d8';
  ctx.fillStyle=bg;ctx.fillRect(0,floor,W,canvas.height-floor);
  // subtle grid
  ctx.strokeStyle=fg;ctx.lineWidth=0.5;
  for(let x=0;x<W;x+=40){ ctx.beginPath();ctx.moveTo(x,floor);ctx.lineTo(x,canvas.height);ctx.stroke(); }
  for(let y=floor;y<canvas.height;y+=20){ ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke(); }
  // floor line
  ctx.strokeStyle=darkTheme?'#222':'#bbb';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(LWALL,floor);ctx.lineTo(RWALL(),floor);ctx.stroke();
  // side walls
  ctx.strokeStyle=darkTheme?'#1a1a1a':'#ccc';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(LWALL,0);ctx.lineTo(LWALL,canvas.height);ctx.moveTo(RWALL(),0);ctx.lineTo(RWALL(),canvas.height);ctx.stroke();
}

// ── INSPECTOR UPDATE ──────────────────────────────────────────
function updateInspector(){
  if(!inspectedBody||!bodies.includes(inspectedBody)){ if(mode==='inspect') document.getElementById('inspector').style.display='block'; return; }
  const b=inspectedBody;
  document.getElementById('iTitle').textContent=`${b.shape} #${b.id}`;
  document.getElementById('iMass').textContent=b.isStatic?'static':(b.mass||1).toFixed(2);
  const speed=Math.sqrt((b.vx||0)**2+(b.vy||0)**2);
  document.getElementById('iSpeed').textContent=speed.toFixed(1)+' px/s';
  document.getElementById('iOmega').textContent=(b.omega||0).toFixed(2);
  document.getElementById('iRest').textContent=(b.restitution||0).toFixed(2);
  document.getElementById('iFric').textContent=(b.friction||0).toFixed(2);
  const ke=0.5*(b.mass||1)*speed*speed+0.5*(b.I||1)*(b.omega||0)**2;
  document.getElementById('iKE').textContent=ke.toFixed(1)+' J';
  document.getElementById('iMom').textContent=((b.mass||1)*speed).toFixed(1)+' kg·px/s';
  document.getElementById('iMat').textContent=MATERIALS[b.material]?.name||b.material||'?';
}

// ── MAIN LOOP ─────────────────────────────────────────────────
let last=performance.now();
function loop(){
  requestAnimationFrame(loop);
  const now=performance.now();
  let rawDt=Math.min((now-last)/1000,0.033);
  last=now; frameCount++;
  if(now-lastFpsTime>600){fps=Math.round(frameCount/((now-lastFpsTime)/1000));frameCount=0;lastFpsTime=now;}

  const shouldSim=!paused||pendingStep; pendingStep=false;

  // background
  const bg=darkTheme?'#0a0a0a':'#f0f2f5';
  ctx.fillStyle=bg;ctx.fillRect(0,0,canvas.width,canvas.height);
  drawFloor();
  drawWalls(); drawSpecials(); drawPegs(); drawSprings();
  drawWater();
  bodies.forEach(b=>drawBody(b));

  // cursor force indicator
  if(magnetActive||repulsorActive||vortexActive){
    const col=magnetActive?'#f29900':repulsorActive?'#1a73e8':'#ab47bc';
    ctx.beginPath();ctx.arc(cursorPos.x,cursorPos.y,24,0,Math.PI*2);ctx.strokeStyle=col+'88';ctx.lineWidth=2;ctx.stroke();
    ctx.beginPath();ctx.arc(cursorPos.x,cursorPos.y,6,0,Math.PI*2);ctx.fillStyle=col;ctx.fill();
  }

  if(shouldSim){
    const dt=rawDt*simSpeed;
    const subDt=dt/subSteps;

    if(fireworkTimer>0){fireworkTimer++;if(fireworkTimer%36===0)spawnFirework();if(fireworkTimer>700)fireworkTimer=0;}
    if(snowTimer>0){snowTimer++;if(snowTimer%6===0){const b=makeCircle(rnd(0,canvas.width),-10,rnd(3,8),'ice',darkTheme?'#d0eeff':'#88aacc');b.vx=rnd(-1.5,1.5);b.vy=0;bodies.push(b);}if(snowTimer>1000)snowTimer=0;}

    for(let step=0;step<subSteps;step++){
      // integrate forces
      bodies.forEach(b=>{
        if(b.isStatic) return;
        if(b.life!==undefined){ b.life-=b.decay*simSpeed; if(b.life<=0){b.dead=true;return;} }
        // gravity
        b.vy+=GRAVITY*subDt*60;
        // quadratic air drag
        const speed2=b.vx*b.vx+b.vy*b.vy;
        const drag=airDrag*speed2;
        const spd=Math.sqrt(speed2)||0.001;
        b.vx-=(b.vx/spd)*drag; b.vy-=(b.vy/spd)*drag;
        // angular drag
        b.omega*=(1-0.005*subDt*60);
        // wind
        b.vx+=windForce*subDt*2;
        // blackhole specials
        specials.forEach(s=>{ if(s.type==='blackhole'){ const dx=s.x-b.x,dy=s.y-b.y,d=Math.sqrt(dx*dx+dy*dy)||1; if(d<s.r+b.r){b.x=rnd(20,canvas.width-20);b.y=rnd(20,canvas.height*0.3);b.vx=rnd(-5,5);b.vy=0;return;} const f=s.strength/(d*d); b.vx+=(dx/d)*f*subDt*60; b.vy+=(dy/d)*f*subDt*60; }});
        // pendulum
        if(b.isPendulum){ const g2=GRAVITY*55; b.omega+=(-g2/b.armLen)*Math.sin(b.angle)*subDt; b.omega*=0.9998; b.angle+=b.omega*subDt; b.x=b.pivotX+Math.sin(b.angle)*b.armLen; b.y=b.pivotY+Math.cos(b.angle)*b.armLen; return; }
        b.x+=b.vx*subDt*60; b.y+=b.vy*subDt*60; b.angle+=b.omega*subDt*60;
        segCollide(b); pegCollide(b); boundaryCollide(b);
      });

      // spring forces
      for(let iter=0;iter<2;iter++) updateSprings();

      // body-body collisions (SAT)
      contactCount=0;
      for(let i=0;i<bodies.length;i++){
        for(let j=i+1;j<bodies.length;j++){
          const a=bodies[i],bv=bodies[j];
          if(a.dead||bv.dead) continue;
          const m=getManifold(a,bv);
          if(m){ contactCount++; m.contacts.forEach(cp=>resolveContact(a,bv,m.normal,m.depth,cp)); }
        }
      }

      // water
      updateWater(subDt);
    }

    // trails
    if(trailLen>0){
      bodies.forEach(b=>{ if(b.isPendulum||(!b.isPendulum&&b.shape==='circle')){ if(!b.trail)b.trail=[]; b.trail.push({x:b.x,y:b.y}); if(b.trail.length>trailLen)b.trail.shift(); }});
    }

    bodies=bodies.filter(b=>!b.dead&&b.y<canvas.height+500&&b.x>-500&&b.x<canvas.width+500);
    springs=springs.filter(s=>bodies.includes(s.a)&&bodies.includes(s.b));
  }

  // HUD
  let totalKE=0;
  bodies.forEach(b=>{ if(!b.isStatic){ const s2=b.vx*b.vx+b.vy*b.vy; totalKE+=0.5*(b.mass||1)*s2+0.5*(b.I||0)*(b.omega||0)**2; }});
  document.getElementById('hBodies').textContent=bodies.length;
  document.getElementById('hSpr').textContent=springs.length;
  document.getElementById('hWalls').textContent=walls.length;
  document.getElementById('hFps').textContent=fps;
  document.getElementById('hContacts').textContent=contactCount;
  document.getElementById('hKE').textContent=totalKE.toFixed(0);
  updateInspector();
}

addPreset('stack');
loop();
</script>
</body>
</html>
"""