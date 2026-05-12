#!/usr/bin/env python3
"""
Patch v3.3: Density, Amount, Burst, Spawn Shapes, Wind, Attract/Repel, 
Pulse particles, Color Randomize, Size/Speed ranges
"""
import os, sys
sys.path.insert(0, "/home/claude/ashfall-vfx-forge")
from build import log, read_file, write_file

GEN = "/home/claude/ashfall-vfx-forge/generate.py"

def patch():
    c = read_file(GEN)
    
    # ═══ 1: Make MAX_P configurable + add new config keys ═══
    c = c.replace(
        "const MAX_P=400;",
        "// MAX_P is now dynamic via cfg.pMaxP",
        1
    )
    log("Made MAX_P dynamic", "PATCH")

    # Add new keys to config state (find the end of existing particle keys)
    c = c.replace(
        "pStretch:0,pFlicker:0,pBounce:false,pGravDir:90});",
        "pStretch:0,pFlicker:0,pBounce:false,pGravDir:90,"
        "pMaxP:400,pAmount:1,pSizeMin:1,pSizeMax:6,pSpdMin:.5,pSpdMax:3,"
        "pWindX:0,pWindY:0,pAttract:0,pPulse:0,pColRand:0,"
        "pSpawnShape:'point',pSpawnW:40,pSpawnH:40,pShrink:true});",
        1
    )
    log("Added 15 new config keys", "PATCH")

    # Same for the SECOND occurrence (reset button defaults were duplicated)
    c = c.replace(
        "pStretch:0,pFlicker:0,pBounce:false,pGravDir:90});",
        "pStretch:0,pFlicker:0,pBounce:false,pGravDir:90,"
        "pMaxP:400,pAmount:1,pSizeMin:1,pSizeMax:6,pSpdMin:.5,pSpdMax:3,"
        "pWindX:0,pWindY:0,pAttract:0,pPulse:0,pColRand:0,"
        "pSpawnShape:'point',pSpawnW:40,pSpawnH:40,pShrink:true});",
        1
    )

    # ═══ 2: Add SPAWN_SHAPES constant ═══
    c = c.replace(
        "const COMPS=['source-over','screen','lighter','multiply','overlay','color-dodge','hard-light'];",
        "const COMPS=['source-over','screen','lighter','multiply','overlay','color-dodge','hard-light'];\n"
        "const SPAWNS=['point','circle','ring','line','square'];",
        1
    )
    log("Added spawn shape constants", "PATCH")

    # ═══ 3: Upgrade Particle constructor — add wind, attract, pulse, color rand, size range ═══
    c = c.replace(
        "const sv=c.sizeVar||0;const szBase=c.sz||(Math.random()*4+2);",
        "const sv=c.sizeVar||0;"
        "const szMin=c.szMin||1;const szMax=c.szMax||6;"
        "const szBase=c.sz||(szMin+Math.random()*(szMax-szMin));"
        "const spdMin=c.spdMin||.5;const spdMax=c.spdMax||3;",
        1
    )
    # Replace fixed spd with range
    c = c.replace(
        "const spd=c.spd||(Math.random()*3+1);",
        "const spd=c.spd||(spdMin+Math.random()*(spdMax-spdMin));",
        1
    )
    log("Added size/speed ranges to constructor", "PATCH")
    
    # Add new properties at end of constructor
    c = c.replace(
        "this.distort=c.distort||0;this.comp=c.comp||'source-over';this.bounce=c.bounce||false}",
        "this.distort=c.distort||0;this.comp=c.comp||'source-over';this.bounce=c.bounce||false;"
        "this.windX=c.windX||0;this.windY=c.windY||0;this.attract=c.attract||0;"
        "this.pulse=c.pulse||0;this.baseSz=this.sz;this.emOx=c.emOx||0;this.emOy=c.emOy||0;"
        "this.colRand=c.colRand||0;this.shrinkFlag=c.shrinkFlag!==undefined?c.shrinkFlag:true;"
        "if(this.colRand>0&&Math.random()<this.colRand){"
        "const h=Math.random()*360;this.col='hsl('+h+',80%,60%)'}}",
        1
    )
    log("Added wind, attract, pulse, color rand to constructor", "PATCH")

    # ═══ 4: Upgrade update() — add wind, attract, pulse ═══
    # Insert wind force after turbulence
    c = c.replace(
        "if(this.turb>0){this.vx+=(Math.random()-.5)*this.turb*dt*60;this.vy+=(Math.random()-.5)*this.turb*dt*60}",
        "if(this.turb>0){this.vx+=(Math.random()-.5)*this.turb*dt*60;this.vy+=(Math.random()-.5)*this.turb*dt*60}"
        # Wind — constant force
        "this.vx+=this.windX*dt;this.vy+=this.windY*dt;"
        # Attract/repel toward emitter origin
        "if(this.attract!==0){const dx=this.emOx-this.x,dy=this.emOy-this.y;"
        "const dist=Math.sqrt(dx*dx+dy*dy)+.1;"
        "this.vx+=dx/dist*this.attract*dt*60;this.vy+=dy/dist*this.attract*dt*60}",
        1
    )
    log("Added wind + attract/repel to update()", "PATCH")

    # Add pulse (size oscillation) — modify size calc in draw
    c = c.replace(
        "const s=this.sh?this.sz*(this.life/this.ml):this.sz;",
        "let s=this.shrinkFlag?this.sz*(this.life/this.ml):this.sz;"
        "if(this.pulse>0){s*=1+Math.sin(this.life*Math.PI*4*this.pulse)*.3}",
        1
    )
    log("Added pulse oscillation to draw()", "PATCH")

    # ═══ 5: Wire new configs into fire_embers (primary emitter) ═══
    c = c.replace(
        "dr:c.pDrag}}",
        "dr:c.pDrag,windX:c.pWindX,windY:c.pWindY,attract:c.pAttract,pulse:c.pPulse,"
        "szMin:c.pSizeMin,szMax:c.pSizeMax,spdMin:c.pSpdMin,spdMax:c.pSpdMax,"
        "colRand:c.pColRand,emOx:eox,emOy:eoy,shrinkFlag:c.pShrink}}",
        1
    )
    log("Wired new configs into primary emitter", "PATCH")

    # Wire into all other emitter types (they end with distort:c.pDistort}})
    # We need to add shared new props. Each particle config closes with distort:c.pDistort}}
    # Count occurrences
    shared_new = ",windX:c.pWindX,windY:c.pWindY,attract:c.pAttract,pulse:c.pPulse,szMin:c.pSizeMin,szMax:c.pSizeMax,spdMin:c.pSpdMin,spdMax:c.pSpdMax,colRand:c.pColRand,emOx:eox,emOy:eoy,shrinkFlag:c.pShrink"
    count = c.count("distort:c.pDistort}}")
    log(f"Found {count} particle configs to wire", "INFO")
    c = c.replace("distort:c.pDistort}}", "distort:c.pDistort" + shared_new + "}}")
    log("Wired new configs into all emitter types", "PATCH")

    # ═══ 6: Update spawn logic — use pAmount multiplier, dynamic MAX_P, spawn shapes ═══
    old_spawn_loop = (
        "Object.entries(pE).forEach(([eid,pe])=>{"
        "if(!ef.includes(eid)||pts.current.length>=MAX_P)return;"
        "for(let i=0;i<pe.n&&pts.current.length<MAX_P;i++)"
        "pts.current.push(new Pt(eox+(Math.random()-.5)*c.pSpawnR*2,eoy+(Math.random()-.5)*c.pSpawnR*2,pe.cfg))"
        "});"
    )
    new_spawn_loop = (
        "const maxP=c.pMaxP||400;"
        "Object.entries(pE).forEach(([eid,pe])=>{"
        "if(!ef.includes(eid)||pts.current.length>=maxP)return;"
        "const count=Math.max(1,Math.round(pe.n*c.pAmount));"
        "for(let i=0;i<count&&pts.current.length<maxP;i++){"
        # Spawn shape logic
        "let sx,sy;const r=c.pSpawnR,w=c.pSpawnW||40,h=c.pSpawnH||40;"
        "if(c.pSpawnShape==='circle'){const a=Math.random()*Math.PI*2;const d=Math.random()*r;sx=eox+Math.cos(a)*d;sy=eoy+Math.sin(a)*d}"
        "else if(c.pSpawnShape==='ring'){const a=Math.random()*Math.PI*2;sx=eox+Math.cos(a)*r;sy=eoy+Math.sin(a)*r}"
        "else if(c.pSpawnShape==='line'){sx=eox+(Math.random()-.5)*w*2;sy=eoy}"
        "else if(c.pSpawnShape==='square'){sx=eox+(Math.random()-.5)*w*2;sy=eoy+(Math.random()-.5)*h*2}"
        "else{sx=eox+(Math.random()-.5)*r;sy=eoy+(Math.random()-.5)*r}"
        "pts.current.push(new Pt(sx,sy,pe.cfg))"
        "}});"
    )
    c = c.replace(old_spawn_loop, new_spawn_loop, 1)
    log("Upgraded spawn loop with amount multiplier, dynamic cap, spawn shapes", "PATCH")

    # ═══ 7: Update HUD to show dynamic max ═══
    c = c.replace(
        "pts.current.length+'/'+MAX_P",
        "pts.current.length+'/'+(c.pMaxP||400)",
        1
    )
    # Also update the particle cap filter
    c = c.replace(
        "pts.current.length<MAX_P)pts.current.push",
        "pts.current.length<(c.pMaxP||400))pts.current.push",
        1
    )
    log("Updated HUD + heal particle cap to dynamic", "PATCH")

    # ═══ 8: Add new UI controls ═══
    # Add after the Emission Rate slider
    old_rate_ui = '<SL l="Emission Rate" k="pRate" mn={1} mx={8} st={1} sf="/f"/>'
    new_rate_ui = (
        '<SL l="Emission Rate" k="pRate" mn={1} mx={8} st={1} sf="/f"/>\n'
        '<SL l="Amount Multi" k="pAmount" mn={.1} mx={5} st={.1} sf="x"/>\n'
        '<SL l="Max Particles" k="pMaxP" mn={50} mx={2000} st={50}/>\n'
    )
    c = c.replace(old_rate_ui, new_rate_ui, 1)
    log("Added density/amount/max UI", "PATCH")

    # Add size min/max — replace existing Size slider
    c = c.replace(
        '<SL l="Size" k="pSize" mn={1} mx={12} st={.5} sf="px"/>',
        '<SL l="Size" k="pSize" mn={1} mx={12} st={.5} sf="px"/>\n'
        '<SL l="Size Min" k="pSizeMin" mn={.5} mx={10} st={.5}/>\n'
        '<SL l="Size Max" k="pSizeMax" mn={1} mx={20} st={.5}/>\n',
        1
    )
    log("Added size min/max UI", "PATCH")

    # Add speed min/max after Speed slider
    c = c.replace(
        '<SL l="Speed" k="pSpeed" mn={.1} mx={4} st={.1} sf="x"/>',
        '<SL l="Speed" k="pSpeed" mn={.1} mx={4} st={.1} sf="x"/>\n'
        '<SL l="Speed Min" k="pSpdMin" mn={.1} mx={5} st={.1}/>\n'
        '<SL l="Speed Max" k="pSpdMax" mn={.5} mx={10} st={.1}/>\n',
        1
    )
    log("Added speed min/max UI", "PATCH")

    # Add wind, attract, pulse, color rand, spawn shape, shrink controls after Distortion
    old_distort_ui = '<SL l="Distortion" k="pDistort" mn={0} mx={2} st={.1}/>'
    new_distort_ui = (
        '<SL l="Distortion" k="pDistort" mn={0} mx={2} st={.1}/>\n'
        '<div className="sd"/>\n'
        '<div className="cl">Forces</div>\n'
        '<SL l="Wind X" k="pWindX" mn={-3} mx={3} st={.1}/>\n'
        '<SL l="Wind Y" k="pWindY" mn={-3} mx={3} st={.1}/>\n'
        '<SL l="Attract/Repel" k="pAttract" mn={-2} mx={2} st={.05}/>\n'
        '<SL l="Pulse" k="pPulse" mn={0} mx={3} st={.1}/>\n'
        '<SL l="Color Random" k="pColRand" mn={0} mx={1} st={.05}/>\n'
        '<div className="sr"><div className="sh2"><span className="sl2">Spawn Shape</span></div>'
        '<select value={cfg.pSpawnShape} onChange={e=>upCfg(\'pSpawnShape\',e.target.value)}>'
        '{SPAWNS.map(s=><option key={s} value={s}>{s}</option>)}</select></div>\n'
        '{(cfg.pSpawnShape==="line"||cfg.pSpawnShape==="square")&&<>\n'
        '<SL l="Spawn Width" k="pSpawnW" mn={10} mx={200} st={5} sf="px"/>\n'
        '<SL l="Spawn Height" k="pSpawnH" mn={10} mx={200} st={5} sf="px"/>\n'
        '</>}\n'
        '<div className="cr2"><label style={{display:"flex",alignItems:"center",gap:6,cursor:"pointer",color:"var(--txt2)",fontSize:10}}>'
        '<input type="checkbox" checked={cfg.pShrink} onChange={e=>upCfg(\'pShrink\',e.target.checked)}/> Shrink over lifetime</label></div>\n'
    )
    c = c.replace(old_distort_ui, new_distort_ui, 1)
    log("Added wind, attract, pulse, spawn shape, shrink UI controls", "PATCH")

    # ═══ 9: Add burst button before Kill Particles ═══
    c = c.replace(
        """<button className="ab" onClick={()=>{pts.current=[]}}>Kill P</button>""",
        '<button className="ab" onClick={()=>{'
        'const cc=cfgR.current,eox2=(cc.emX-.5)*cvRef.current.getBoundingClientRect().width,'
        'eoy2=(cc.emY-.5)*cvRef.current.getBoundingClientRect().height;'
        'for(let i=0;i<20*cc.pAmount;i++){'
        'const a=Math.random()*Math.PI*2,r=Math.random()*cc.pSpawnR;'
        'pts.current.push(new Pt(eox2+Math.cos(a)*r,eoy2+Math.sin(a)*r,'
        '{angle:cc.pAngle,spread:cc.pSpread,spd:cc.pSpdMin+Math.random()*(cc.pSpdMax-cc.pSpdMin),'
        'spdMul:cc.pSpeed*cc.intensity,life:cc.pLife,sz:cc.pSize,col:cc.partCol,'
        'g:cc.pGrav,gDir:cc.pGravDir,tp:cc.pShape,blur:cc.pBlur,glow:cc.pGlow,'
        'trail:cc.pTrail,colEnd:cc.pColEnd,fs:cc.pFade,turb:cc.pTurb,comp:cc.pComp,'
        'dr:cc.pDrag,sizeVar:cc.pSizeVar,opacity:cc.pOpacity,stretch:cc.pStretch,'
        'flicker:cc.pFlicker,bounce:cc.pBounce,rotSpd:cc.pRotSpd,distort:cc.pDistort,'
        'windX:cc.pWindX,windY:cc.pWindY,attract:cc.pAttract,pulse:cc.pPulse,'
        'szMin:cc.pSizeMin,szMax:cc.pSizeMax,spdMin:cc.pSpdMin,spdMax:cc.pSpdMax,'
        'colRand:cc.pColRand,emOx:eox2,emOy:eoy2,shrinkFlag:cc.pShrink}))'
        '}}>Burst</button>\n'
        '<button className="ab" onClick={()=>{pts.current=[]}}>Kill P</button>',
        1
    )
    log("Added Burst button", "PATCH")

    # ═══ 10: Update reset defaults ═══
    c = c.replace(
        "pShape:'circle',pAngle:270,pSpread:120,pBlur:0,pSize:3,pLife:1.5,pSpeed:1,emX:.5,emY:.5",
        "pShape:'circle',pAngle:270,pSpread:120,pBlur:0,pSize:3,pLife:1.5,pSpeed:1,emX:.5,emY:.5,"
        "pGrav:0,pDrag:.98,pRotSpd:.1,pGlow:0,pTrail:0,pColEnd:'',pFade:.3,"
        "pRate:2,pTurb:0,pComp:'source-over',pSpawnR:20,pDistort:0,pSizeVar:0,pOpacity:1,"
        "pStretch:0,pFlicker:0,pBounce:false,pGravDir:90,"
        "pMaxP:400,pAmount:1,pSizeMin:1,pSizeMax:6,pSpdMin:.5,pSpdMax:3,"
        "pWindX:0,pWindY:0,pAttract:0,pPulse:0,pColRand:0,"
        "pSpawnShape:'point',pSpawnW:40,pSpawnH:40,pShrink:true",
        1
    )
    log("Updated reset defaults", "PATCH")

    # ═══ 11: Update version ═══
    c = c.replace("v3.2 — 44 Effects", "v3.3 — 44 Effects", 1)
    c = c.replace(
        "VFX FORGE v3.2</span><br/>44 FX · 9 Shapes · 18 Particle Controls",
        "VFX FORGE v3.3</span><br/>44 FX · 9 Shapes · 35+ Particle Controls"
    )
    c = c.replace(
        "Trails · Glow · Turbulence · Stretch · Blend Modes<br/>Color Gradient · Distortion · Bounce Physics",
        "Density · Wind · Attract · Burst · Spawn Shapes<br/>Trails · Glow · Pulse · Blend Modes · Color Gradient"
    )
    log("Updated version strings", "PATCH")

    write_file(GEN, c)
    log("All v3.3 patches written", "OK")

def build_and_deploy():
    log("Generating HTML...", "INFO")
    r = os.system("cd /home/claude/ashfall-vfx-forge && python3 generate.py")
    if r != 0:
        log("Generate failed!", "ERR")
        return
    
    log("Validating...", "INFO")
    r = os.system("cd /home/claude/ashfall-vfx-forge && python3 build.py validate")
    if r != 0:
        log("Validation failed!", "ERR")
        return
    
    log("Committing and pushing...", "INFO")
    os.system('cd /home/claude/ashfall-vfx-forge && git add -A && '
              'git commit -m "v3.3 — Density, amount, burst, spawn shapes, wind, attract, pulse, size/speed ranges, color randomize, shrink toggle" && '
              'git push origin main')
    
    log("Deploying to Vercel...", "INFO")
    os.system("""cd /home/claude/ashfall-vfx-forge && export $(cat .env | xargs) && python3 -c "
import os,json,urllib.request,time
t=os.environ['VERCEL_TOKEN'];g=os.environ['GITHUB_TOKEN']
r=urllib.request.Request('https://api.github.com/repos/MisTAiM/ashfall-vfx-forge',headers={'Authorization':'token '+g})
rid=str(json.loads(urllib.request.urlopen(r).read())['id'])
p=json.dumps({'name':'ashfall-vfx-forge','gitSource':{'type':'github','repoId':rid,'ref':'main'},'projectSettings':{'framework':None}}).encode()
r=urllib.request.Request('https://api.vercel.com/v13/deployments',data=p,headers={'Authorization':'Bearer '+t,'Content-Type':'application/json'})
d=json.loads(urllib.request.urlopen(r).read());di=d['id'];du=d['url']
for i in range(15):
    time.sleep(5)
    r=urllib.request.Request('https://api.vercel.com/v13/deployments/'+di,headers={'Authorization':'Bearer '+t})
    s=json.loads(urllib.request.urlopen(r).read()).get('readyState')
    print(s)
    if s=='READY':print('LIVE: https://'+du);break
    if s in('ERROR','CANCELED'):print('FAILED');break
" """)

if __name__ == "__main__":
    patch()
    build_and_deploy()
