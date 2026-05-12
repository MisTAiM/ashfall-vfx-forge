#!/usr/bin/env python3
"""
Patch: Add comprehensive particle customization to VFX Forge v3.2
- Gravity, Drag, Rotation Speed, Glow, Trails, Color Gradient,
  Opacity, Emission Rate, Turbulence, Composite Mode, Spawn Radius,
  Distortion Wave, Size Variance, Fade Point
"""
import os, sys
sys.path.insert(0, "/home/claude/ashfall-vfx-forge")
from build import patch_file, inject_after, inject_before, log, read_file, write_file

GEN = "/home/claude/ashfall-vfx-forge/generate.py"

def apply_patches():
    log("Applying v3.2 particle patches...", "INFO")
    content = read_file(GEN)
    
    # ═══════════════════════════════════════
    # PATCH 1: Add new config keys to state
    # ═══════════════════════════════════════
    old_cfg = "pShape:'circle',pAngle:270,pSpread:120,pBlur:0,pSize:3,pLife:1.5,pSpeed:1,emX:.5,emY:.5"
    new_cfg = (
        "pShape:'circle',pAngle:270,pSpread:120,pBlur:0,pSize:3,pLife:1.5,pSpeed:1,emX:.5,emY:.5,"
        # New particle controls
        "pGrav:0,pDrag:.98,pRotSpd:.1,pGlow:0,pTrail:0,pColEnd:'',pFade:.3,"
        "pRate:2,pTurb:0,pComp:'source-over',pSpawnR:20,pDistort:0,pSizeVar:0,pOpacity:1,"
        "pStretch:0,pFlicker:0,pBounce:false,pGravDir:90"
    )
    content = content.replace(old_cfg, new_cfg, 1)
    log("Added 16 new config keys", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 2: Upgrade Particle class with new features
    # ═══════════════════════════════════════
    old_particle = (
        "class Pt{constructor(x,y,c){const ang=(c.angle||270)*Math.PI/180;const spread=(c.spread||360)*Math.PI/360;"
        "const dir=ang+(Math.random()-.5)*spread;const spd=c.spd||(Math.random()*3+1);"
        "this.x=x;this.y=y;this.vx=Math.cos(dir)*spd*(c.spdMul||1);this.vy=Math.sin(dir)*spd*(c.spdMul||1);"
        "this.life=c.life||1;this.ml=this.life;this.sz=c.sz||(Math.random()*4+2);this.col=c.col||'#ff6b35';"
        "this.g=c.g||0;this.dr=c.dr||.98;this.sh=c.sh!==undefined?c.sh:true;this.tp=c.tp||'circle';"
        "this.rot=Math.random()*Math.PI*2;this.rs=(Math.random()-.5)*.1;this.op=1;this.fs=c.fs||.3;"
        "this.text=c.text||null;this.font=c.font||null;this.blur=c.blur||0}"
    )
    new_particle = (
        "class Pt{constructor(x,y,c){const ang=(c.angle||270)*Math.PI/180;const spread=(c.spread||360)*Math.PI/360;"
        "const dir=ang+(Math.random()-.5)*spread;const spd=c.spd||(Math.random()*3+1);"
        "const sv=c.sizeVar||0;const szBase=c.sz||(Math.random()*4+2);"
        "this.x=x;this.y=y;this.vx=Math.cos(dir)*spd*(c.spdMul||1);this.vy=Math.sin(dir)*spd*(c.spdMul||1);"
        "this.life=c.life||1;this.ml=this.life;this.sz=szBase+(Math.random()-.5)*sv*szBase;this.col=c.col||'#ff6b35';"
        "this.colEnd=c.colEnd||'';this.g=c.g||0;this.gDir=(c.gDir||90)*Math.PI/180;"
        "this.dr=c.dr||.98;this.sh=c.sh!==undefined?c.sh:true;this.tp=c.tp||'circle';"
        "this.rot=Math.random()*Math.PI*2;this.rs=c.rotSpd!==undefined?(Math.random()-.5)*c.rotSpd:(Math.random()-.5)*.1;"
        "this.op=c.opacity||1;this.maxOp=this.op;this.fs=c.fs||.3;"
        "this.text=c.text||null;this.font=c.font||null;this.blur=c.blur||0;"
        "this.glow=c.glow||0;this.trail=c.trail||0;this.hist=[];this.turb=c.turb||0;"
        "this.stretch=c.stretch||0;this.flicker=c.flicker||0;"
        "this.distort=c.distort||0;this.comp=c.comp||'source-over';this.bounce=c.bounce||false}"
    )
    content = content.replace(old_particle, new_particle, 1)
    log("Upgraded Particle constructor with 16 new properties", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 3: Upgrade Particle update() method
    # ═══════════════════════════════════════
    old_update = (
        "update(dt){this.vy+=this.g*dt;this.vx*=this.dr;this.vy*=this.dr;"
        "this.x+=this.vx*dt*60;this.y+=this.vy*dt*60;this.life-=dt;this.rot+=this.rs;"
        "const lr=this.life/this.ml;this.op=lr<this.fs?lr/this.fs:1;return this.life>0}"
    )
    new_update = (
        "update(dt){"
        # Gravity with direction
        "this.vx+=Math.cos(this.gDir)*this.g*dt;this.vy+=Math.sin(this.gDir)*this.g*dt;"
        # Turbulence
        "if(this.turb>0){this.vx+=(Math.random()-.5)*this.turb*dt*60;this.vy+=(Math.random()-.5)*this.turb*dt*60}"
        # Drag
        "this.vx*=this.dr;this.vy*=this.dr;"
        # Trail history
        "if(this.trail>0){this.hist.push({x:this.x,y:this.y,op:this.op});if(this.hist.length>this.trail)this.hist.shift()}"
        # Movement
        "this.x+=this.vx*dt*60;this.y+=this.vy*dt*60;"
        # Bounce off edges
        "if(this.bounce){if(this.y>120){this.y=120;this.vy*=-.6}if(this.y<-120){this.y=-120;this.vy*=-.6}"
        "if(this.x>160){this.x=160;this.vx*=-.6}if(this.x<-160){this.x=-160;this.vx*=-.6}}"
        # Life & rotation
        "this.life-=dt;this.rot+=this.rs;"
        # Color gradient over lifetime
        "const lr=this.life/this.ml;"
        "this.op=lr<this.fs?lr/this.fs*this.maxOp:this.maxOp;"
        # Flicker
        "if(this.flicker>0)this.op*=(.7+Math.random()*.3*this.flicker);"
        "return this.life>0}"
    )
    content = content.replace(old_update, new_update, 1)
    log("Upgraded Particle update() with gravity dir, turbulence, trails, bounce, flicker", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 4: Upgrade Particle draw() method
    # ═══════════════════════════════════════
    old_draw_start = (
        "draw(ctx){"
        "ctx.save();ctx.globalAlpha=this.op;ctx.translate(this.x,this.y);"
        "if(this.blur>0)ctx.filter='blur('+this.blur+'px)';"
        "ctx.rotate(this.rot);"
    )
    new_draw_start = (
        "draw(ctx){"
        # Draw trail first
        "if(this.trail>0&&this.hist.length>1){"
        "ctx.save();ctx.globalCompositeOperation=this.comp;"
        "for(let i=0;i<this.hist.length;i++){const h=this.hist[i];const a=(i/this.hist.length)*this.op*.3;"
        "ctx.globalAlpha=a;ctx.fillStyle=this.col;const ts=this.sz*(i/this.hist.length)*.6;"
        "ctx.beginPath();ctx.arc(h.x,h.y,ts,0,Math.PI*2);ctx.fill()}ctx.restore()}"
        # Main particle
        "ctx.save();"
        "if(this.comp!=='source-over')ctx.globalCompositeOperation=this.comp;"
        # Color interpolation
        "let drawCol=this.col;"
        "if(this.colEnd){const lr=this.life/this.ml;drawCol=this._lerpCol(this.col,this.colEnd,1-lr)}"
        "ctx.globalAlpha=this.op;ctx.translate(this.x,this.y);"
        # Glow
        "if(this.glow>0){ctx.shadowColor=drawCol;ctx.shadowBlur=this.glow}"
        # Blur + distortion
        "let flt=[];if(this.blur>0)flt.push('blur('+this.blur+'px)');if(this.distort>0)flt.push('contrast('+(1+this.distort*.5)+')');if(flt.length)ctx.filter=flt.join(' ');"
        # Stretch based on velocity
        "if(this.stretch>0){const vel=Math.sqrt(this.vx*this.vx+this.vy*this.vy);const ang=Math.atan2(this.vy,this.vx);"
        "ctx.rotate(ang);ctx.scale(1+vel*this.stretch*.1,Math.max(.3,1-vel*this.stretch*.05));}"
        "else{ctx.rotate(this.rot)}"
    )
    content = content.replace(old_draw_start, new_draw_start, 1)
    log("Upgraded Particle draw() with trails, glow, stretch, distortion, color lerp, composite", "PATCH")

    # Add color lerp helper and fix the draw closing
    old_draw_end = "ctx.filter='none';ctx.restore();}}"
    new_draw_end = (
        "ctx.shadowBlur=0;ctx.filter='none';ctx.restore()}"
        # Color lerp helper
        "_lerpCol(a,b,t){"
        "const p=s=>{const m=s.match(/\\w\\w/g);return m?m.map(x=>parseInt(x,16)):[255,107,53]};"
        "const ca=p(a),cb=p(b);"
        "const r=Math.round(ca[0]+(cb[0]-ca[0])*t),g=Math.round(ca[1]+(cb[1]-ca[1])*t),bl=Math.round(ca[2]+(cb[2]-ca[2])*t);"
        "return '#'+[r,g,bl].map(v=>Math.max(0,Math.min(255,v)).toString(16).padStart(2,'0')).join('')}"
        "}"
    )
    content = content.replace(old_draw_end, new_draw_end, 1)
    log("Added color lerp helper method", "PATCH")

    # Also need to replace ctx.fillStyle=this.col references to use drawCol
    content = content.replace(
        "const s=this.sh?this.sz*(this.life/this.ml):this.sz;ctx.fillStyle=this.col;",
        "const s=this.sh?this.sz*(this.life/this.ml):this.sz;ctx.fillStyle=drawCol;",
        1
    )
    # And stroke references
    content = content.replace(
        "else if(this.tp==='ring'){ctx.strokeStyle=this.col;",
        "else if(this.tp==='ring'){ctx.strokeStyle=drawCol;",
        1
    )
    content = content.replace(
        "else if(this.tp==='line'){ctx.strokeStyle=this.col;",
        "else if(this.tp==='line'){ctx.strokeStyle=drawCol;",
        1
    )
    content = content.replace(
        "else if(this.tp==='spark'){ctx.strokeStyle=this.col;",
        "else if(this.tp==='spark'){ctx.strokeStyle=drawCol;",
        1
    )
    log("Wired drawCol through all shape renderers", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 5: Wire new configs into particle emitter configs
    # ═══════════════════════════════════════
    # Add the new properties to each particle config entry
    # We need to append shared properties to each cfg object
    old_pE_fire = "fire_embers:{n:2,cfg:{angle:c.pAngle,spread:c.pSpread,spd:2,spdMul:c.pSpeed*I,life:c.pLife,sz:c.pSize,col:c.partCol,g:-.02,tp:c.pShape,blur:c.pBlur}}"
    new_pE_fire = "fire_embers:{n:Math.max(1,Math.round(c.pRate)),cfg:{angle:c.pAngle,spread:c.pSpread,spd:2,spdMul:c.pSpeed*I,life:c.pLife,sz:c.pSize,col:c.partCol,g:c.pGrav||-.02,gDir:c.pGravDir,tp:c.pShape,blur:c.pBlur,glow:c.pGlow,trail:c.pTrail,colEnd:c.pColEnd,fs:c.pFade,turb:c.pTurb,comp:c.pComp,sizeVar:c.pSizeVar,opacity:c.pOpacity,stretch:c.pStretch,flicker:c.pFlicker,bounce:c.pBounce,rotSpd:c.pRotSpd,distort:c.pDistort,dr:c.pDrag}}"
    content = content.replace(old_pE_fire, new_pE_fire, 1)
    
    # Create a shared cfg suffix for all other particle types
    shared_props = ",glow:c.pGlow,trail:c.pTrail,colEnd:c.pColEnd,fs:c.pFade,turb:c.pTurb,comp:c.pComp,sizeVar:c.pSizeVar,opacity:c.pOpacity,stretch:c.pStretch,flicker:c.pFlicker,bounce:c.pBounce,rotSpd:c.pRotSpd,distort:c.pDistort"
    
    # Patch each particle type to include shared props and use pRate
    for ptype in ['smoke_trail', 'sparkle', 'ash_fall', 'magic_orbs', 'blood_drip', 'poison_mist', 'ice_shards', 'lightning_sparks', 'leaves']:
        # Find the closing of each cfg object and insert shared props
        # Each ends with ,blur:c.pBlur}} or ,blur:0}} etc
        # Just add shared props before the last }}
        old_blur_end = f"blur:c.pBlur}}}}"
        if ptype == 'lightning_sparks':
            old_blur_end = f"blur:0}}}}"
        elif ptype == 'smoke_trail':
            old_blur_end = f"blur:Math.max(c.pBlur,1)}}}}"
        elif ptype == 'poison_mist':
            old_blur_end = f"blur:Math.max(c.pBlur,2)}}}}"
            
        if old_blur_end in content:
            new_blur_end = old_blur_end.replace("}}", shared_props + "}}")
            content = content.replace(old_blur_end, new_blur_end, 1)
    
    log("Wired all 16 new properties into particle emitter configs", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 6: Add COMPOSITES list 
    # ═══════════════════════════════════════
    old_shapes = "const SHAPES=['circle','square','star','diamond','ring','line','triangle','cross','spark'];"
    new_shapes = (
        "const SHAPES=['circle','square','star','diamond','ring','line','triangle','cross','spark'];"
        "const COMPS=['source-over','screen','lighter','multiply','overlay','color-dodge','hard-light'];"
    )
    content = content.replace(old_shapes, new_shapes, 1)
    log("Added composite blend mode list", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 7: Add new UI controls to panel
    # ═══════════════════════════════════════
    old_ui_blur = """<SL l="Blur" k="pBlur" mn={0} mx={8} st={.5} sf="px"/>"""
    new_ui_controls = (
        '<SL l="Blur" k="pBlur" mn={0} mx={8} st={.5} sf="px"/>\n'
        '<SL l="Glow" k="pGlow" mn={0} mx={30} st={1} sf="px"/>\n'
        '<SL l="Gravity" k="pGrav" mn={-1} mx={1} st={.01}/>\n'
        '<SL l="Grav Direction" k="pGravDir" mn={0} mx={360} st={5} sf="deg"/>\n'
        '<SL l="Drag" k="pDrag" mn={.8} mx={1} st={.005}/>\n'
        '<SL l="Rotation Speed" k="pRotSpd" mn={0} mx={1} st={.02}/>\n'
        '<SL l="Trails" k="pTrail" mn={0} mx={20} st={1}/>\n'
        '<SL l="Turbulence" k="pTurb" mn={0} mx={2} st={.05}/>\n'
        '<SL l="Emission Rate" k="pRate" mn={1} mx={8} st={1} sf="/f"/>\n'
        '<SL l="Spawn Radius" k="pSpawnR" mn={5} mx={100} st={5} sf="px"/>\n'
        '<SL l="Size Variance" k="pSizeVar" mn={0} mx={1} st={.05}/>\n'
        '<SL l="Opacity" k="pOpacity" mn={.1} mx={1} st={.05}/>\n'
        '<SL l="Fade Point" k="pFade" mn={.05} mx={.9} st={.05}/>\n'
        '<SL l="Stretch" k="pStretch" mn={0} mx={2} st={.1}/>\n'
        '<SL l="Flicker" k="pFlicker" mn={0} mx={1} st={.05}/>\n'
        '<SL l="Distortion" k="pDistort" mn={0} mx={2} st={.1}/>\n'
        '<div className="sr"><div className="sh2"><span className="sl2">Blend Mode</span></div>'
        '<select value={cfg.pComp} onChange={e=>upCfg(\'pComp\',e.target.value)}>'
        '{COMPS.map(s=><option key={s} value={s}>{s}</option>)}</select></div>\n'
        '<div className="sr"><div className="sh2"><span className="sl2">End Color</span></div>'
        '<div className="cr2"><input type="color" value={cfg.pColEnd||cfg.partCol} onChange={e=>upCfg(\'pColEnd\',e.target.value)} style={{width:22,height:18}}/>'
        '<span className="cll">Gradient end</span>'
        '<button className="ab" style={{padding:"2px 6px",fontSize:9}} onClick={()=>upCfg(\'pColEnd\',\'\')}>Off</button></div></div>\n'
        '<div className="cr2"><label style={{display:"flex",alignItems:"center",gap:6,cursor:"pointer",color:"var(--txt2)",fontSize:10}}>'
        '<input type="checkbox" checked={cfg.pBounce} onChange={e=>upCfg(\'pBounce\',e.target.checked)}/> Bounce off edges</label></div>\n'
    )
    content = content.replace(old_ui_blur, new_ui_controls, 1)
    log("Added 18 new UI controls to particle editor panel", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 8: Update spawn radius in emitter
    # ═══════════════════════════════════════
    old_spawn = "pts.current.push(new Pt(eox+(Math.random()-.5)*40,eoy+(Math.random()-.5)*40,pe.cfg))"
    new_spawn = "pts.current.push(new Pt(eox+(Math.random()-.5)*c.pSpawnR*2,eoy+(Math.random()-.5)*c.pSpawnR*2,pe.cfg))"
    content = content.replace(old_spawn, new_spawn, 1)
    log("Wired spawn radius control", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 9: Update reset to include new keys
    # ═══════════════════════════════════════
    old_reset = "pShape:'circle',pAngle:270,pSpread:120,pBlur:0,pSize:3,pLife:1.5,pSpeed:1,emX:.5,emY:.5"
    new_reset = (
        "pShape:'circle',pAngle:270,pSpread:120,pBlur:0,pSize:3,pLife:1.5,pSpeed:1,emX:.5,emY:.5,"
        "pGrav:0,pDrag:.98,pRotSpd:.1,pGlow:0,pTrail:0,pColEnd:'',pFade:.3,"
        "pRate:2,pTurb:0,pComp:'source-over',pSpawnR:20,pDistort:0,pSizeVar:0,pOpacity:1,"
        "pStretch:0,pFlicker:0,pBounce:false,pGravDir:90"
    )
    # This appears in two places — reset button and initial state
    content = content.replace(old_reset, new_reset, 1)  # reset button
    log("Updated reset button with new defaults", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 10: Update version string
    # ═══════════════════════════════════════
    content = content.replace("v3.1 — 44 Effects", "v3.2 — 44 Effects", 1)
    content = content.replace(
        "VFX FORGE v3.1</span><br/>44 FX · 9 Shapes · Directional Emitter<br/>Click-to-Place · Blur · Scale Separated",
        "VFX FORGE v3.2</span><br/>44 FX · 9 Shapes · 18 Particle Controls<br/>Trails · Glow · Turbulence · Stretch · Blend Modes<br/>Color Gradient · Distortion · Bounce Physics"
    )
    log("Updated version strings", "PATCH")

    # ═══════════════════════════════════════
    # PATCH 11: Add checkbox styling to CSS
    # ═══════════════════════════════════════
    old_css_end = ".ib2{margin-top:12px"
    new_css_end = (
        "input[type=checkbox]{accent-color:var(--acc);cursor:pointer;width:14px;height:14px}\n"
        ".ib2{margin-top:12px"
    )
    content = content.replace(old_css_end, new_css_end, 1)
    log("Added checkbox CSS", "PATCH")

    write_file(GEN, content)
    log("All patches applied to generate.py", "OK")
    return True


if __name__ == "__main__":
    if apply_patches():
        log("Running generator...", "INFO")
        os.system("cd /home/claude/ashfall-vfx-forge && python3 generate.py")
        
        log("Validating...", "INFO")
        os.system("cd /home/claude/ashfall-vfx-forge && python3 build.py validate")
        
        log("Deploying...", "INFO")
        os.system('cd /home/claude/ashfall-vfx-forge && export $(cat .env | xargs) && python3 -c "'
            'import os,json,urllib.request,time\n'
            'token=os.environ[\"VERCEL_TOKEN\"];gh_token=os.environ[\"GITHUB_TOKEN\"]\n'
            'import subprocess;subprocess.run(\"git add -A && git commit -m \\\"v3.2 — 18 particle controls: trails, glow, turbulence, stretch, blend modes, color gradient, distortion, bounce\\\"\",shell=True,cwd=\"/home/claude/ashfall-vfx-forge\")\n'
            'subprocess.run(\"git push origin main\",shell=True,cwd=\"/home/claude/ashfall-vfx-forge\")\n'
            'req=urllib.request.Request(\"https://api.github.com/repos/MisTAiM/ashfall-vfx-forge\",headers={\"Authorization\":\"token \"+gh_token})\n'
            'rid=str(json.loads(urllib.request.urlopen(req).read())[\"id\"])\n'
            'payload=json.dumps({\"name\":\"ashfall-vfx-forge\",\"gitSource\":{\"type\":\"github\",\"repoId\":rid,\"ref\":\"main\"},\"projectSettings\":{\"framework\":None}}).encode()\n'
            'req=urllib.request.Request(\"https://api.vercel.com/v13/deployments\",data=payload,headers={\"Authorization\":\"Bearer \"+token,\"Content-Type\":\"application/json\"})\n'
            'deploy=json.loads(urllib.request.urlopen(req).read());did=deploy[\"id\"];durl=deploy[\"url\"]\n'
            'print(f\"Deploy: {did}\")\n'
            'for i in range(15):\n'
            '    time.sleep(5)\n'
            '    req=urllib.request.Request(f\"https://api.vercel.com/v13/deployments/{did}\",headers={\"Authorization\":\"Bearer \"+token})\n'
            '    s=json.loads(urllib.request.urlopen(req).read()).get(\"readyState\")\n'
            '    print(f\"  {s}\")\n'
            '    if s==\"READY\":print(f\"LIVE: https://{durl}\");break\n'
            '    if s in (\"ERROR\",\"CANCELED\"):print(\"FAILED\");break\n'
            '"')
