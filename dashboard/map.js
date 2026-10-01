(() => {
  'use strict';
  const canvas = document.getElementById('brazil-map');
  const context = canvas.getContext('2d');
  const status = document.getElementById('map-status');
  const regionNames = {1:'Norte',2:'Nordeste',3:'Sudeste',4:'Sul',5:'Centro-Oeste'};
  const regions = Object.fromEntries(Object.entries(regionNames).map(([id,name])=>[id,{name,value:DATA.regions.values[DATA.regions.labels.indexOf(name)]}]));
  const highestVolume = Math.max(...DATA.regions.values);
  const nationalVolume = DATA.flow.matriculas[DATA.flow.matriculas.length-1];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let selected = 3, angle = -.08, tilt = .40, width = 0, height = 0;
  let shapes = [], hitAreas = [], pointer = null, scheduled = false, pixelRatio = 1;
  const format = new Intl.NumberFormat('pt-BR', {maximumFractionDigits:1});
  const project = (x,y,z=0) => {
    const scale = Math.min((width-40)/43, (height-25)/41);
    const xx = x*Math.cos(angle)-y*Math.sin(angle);
    const yy = x*Math.sin(angle)+y*Math.cos(angle);
    return [width*.49+xx*scale, height*.49+(yy*Math.cos(tilt)-z*Math.sin(tilt))*scale];
  };
  const pathFor = (rings,z) => {
    const path = new Path2D();
    rings.forEach(ring => {
      ring.forEach(([x,y], index) => {
        const [px,py] = project(x,y,z);
        index ? path.lineTo(px,py) : path.moveTo(px,py);
      });
      path.closePath();
    });
    return path;
  };
  const triangle = (points, color) => {
    context.beginPath();
    points.forEach(([x,y],i) => i ? context.lineTo(x,y) : context.moveTo(x,y));
    context.closePath();context.fillStyle=color;context.fill();
    context.strokeStyle='rgba(147,244,204,.10)';context.lineWidth=.55;context.stroke();
  };
  function draw() {
    scheduled=false;
    if (!width || !context) return;
    context.clearRect(0,0,width,height);
    // All vertices are projected from geographic x/y and regional z height.
    context.lineWidth=.5;context.strokeStyle='rgba(67,179,126,.13)';
    for (let p=-24;p<=24;p+=3) {
      [[project(p,-24,-1),project(p,24,-1)],[project(-24,p,-1),project(24,p,-1)]].forEach(([a,b])=>{
        context.beginPath();context.moveTo(...a);context.lineTo(...b);context.stroke();
      });
    }
    hitAreas=[];
    const ordered=[...shapes].sort((a,b)=>project(0,a.centerY)[1]-project(0,b.centerY)[1]);
    ordered.forEach(shape=>{
      const ratio=regions[shape.id].value/highestVolume;
      const z=1.1+ratio*3.2+(shape.id===selected?.5:0);
      const hue=150+ratio*52;
      const top=pathFor(shape.rings,z);
      const shadow=pathFor(shape.rings,-1);
      context.save();context.fillStyle='#0006';context.shadowColor='#0009';context.shadowBlur=18;context.fill(shadow,'evenodd');context.restore();
      shape.rings.forEach(ring=>{
        for(let i=0;i<ring.length-1;i++) {
          const a=ring[i],b=ring[i+1];
          context.beginPath();context.moveTo(...project(...a,z));context.lineTo(...project(...b,z));context.lineTo(...project(...b,0));context.lineTo(...project(...a,0));context.closePath();
          context.fillStyle=`hsla(${hue},65%,33%,.48)`;context.fill();
          context.strokeStyle=`hsla(${hue},65%,65%,.12)`;context.stroke();
        }
      });
      context.save();context.clip(top,'evenodd');
      context.fillStyle=`hsla(${hue},60%,${shape.id===selected?43:27},.88)`;context.fill(top,'evenodd');
      const step=2.1;
      for(let x=shape.minX-step;x<shape.maxX+step;x+=step) {
        for(let y=shape.minY-step;y<shape.maxY+step;y+=step) {
          const light=28+Math.abs(Math.sin(x*2.7+y*4.1))*16+(shape.id===selected?7:0);
          const a=project(x,y,z),b=project(x+step,y,z),c=project(x,y+step,z),d=project(x+step,y+step,z);
          triangle([a,b,c],`hsla(${hue},60%,${light}%,.52)`);
          triangle([b,d,c],`hsla(${hue},62%,${light+6}%,.48)`);
          if(Math.sin(x*7.1+y*3.7)>.76 && context.isPointInPath(top,a[0]*pixelRatio,a[1]*pixelRatio,'evenodd')) {
            const glow=context.createRadialGradient(...a,0,...a,8);
            glow.addColorStop(0,'#8fffd7bb');glow.addColorStop(1,'#6efac900');
            context.fillStyle=glow;context.fillRect(a[0]-8,a[1]-8,16,16);
            context.beginPath();context.arc(...a,1.2,0,Math.PI*2);context.fillStyle='#9efadd';context.fill();
          }
        }
      }
      context.restore();context.lineWidth=shape.id===selected?1.5:.7;
      context.strokeStyle=shape.id===selected?'#a0ffdf':'#91dfbc99';
      context.stroke(top);
      hitAreas.push({id:shape.id,path:top});
    });
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function selectRegion(id){
    selected=Number(id);
    const data=regions[selected];
    document.getElementById('region-name').textContent=data.name;
    document.getElementById('region-value').textContent=`${format.format(data.value/1000)} mil`;
    document.getElementById('region-share').textContent=`${format.format(data.value/nationalVolume*100)}%`;
    document.querySelectorAll('[data-region]').forEach(button=>button.setAttribute('aria-pressed',String(Number(button.dataset.region)===selected)));
    requestDraw();
  }
  const resize=new ResizeObserver(()=>{
    const bounds=canvas.getBoundingClientRect();width=bounds.width;height=bounds.height;
    const dpr=Math.min(window.devicePixelRatio||1,2);pixelRatio=dpr;
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    context.setTransform(dpr,0,0,dpr,0,0);requestDraw();
  });
  if(context){
    resize.observe(canvas);
    fetch('regions.geojson').then(response=>{if(!response.ok)throw Error('Geografia indisponível');return response.json();}).then(geo=>{
      geo.features.forEach(feature=>{
        const polygons=feature.geometry.type==='Polygon'?[feature.geometry.coordinates]:feature.geometry.coordinates;
        polygons.forEach(polygon=>{
          const rings=polygon.map(ring=>ring.map(([lon,lat])=>[(lon+53.2)*.98,-lat-15]));
          const points=rings.flat();const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
          shapes.push({id:feature.properties.region_id,rings,minX:Math.min(...xs),maxX:Math.max(...xs),minY:Math.min(...ys),maxY:Math.max(...ys),centerY:ys.reduce((sum,y)=>sum+y,0)/ys.length});
        });
      });
      status.hidden=true;requestDraw();
    }).catch(()=>{status.textContent='Mapa indisponível. Explore os dados pelos botões abaixo.';});
    canvas.addEventListener('pointerdown',event=>{
      if(event.button!==0)return;
      pointer={id:event.pointerId,x:event.clientX,y:event.clientY,angle,tilt,moved:false,dragging:false};
    });
    canvas.addEventListener('pointermove',event=>{
      if(!pointer || pointer.id!==event.pointerId)return;
      const dx=event.clientX-pointer.x,dy=event.clientY-pointer.y;
      // Vertical touch gestures remain available for scrolling the dashboard.
      if(event.pointerType==='touch' && !pointer.dragging && Math.abs(dy)>Math.abs(dx)+8){pointer=null;return;}
      if(Math.abs(dx)+Math.abs(dy)>6){pointer.moved=true;pointer.dragging=true;canvas.setPointerCapture(event.pointerId);}
      if(pointer.dragging){angle=Math.max(-.65,Math.min(.65,pointer.angle+dx*.004));tilt=Math.max(.12,Math.min(.75,pointer.tilt+dy*.003));requestDraw();}
    });
    canvas.addEventListener('pointerup',event=>{
      if(!pointer || pointer.id!==event.pointerId)return;
      if(!pointer.moved){const bounds=canvas.getBoundingClientRect();const x=event.clientX-bounds.left,y=event.clientY-bounds.top;const hit=[...hitAreas].reverse().find(area=>context.isPointInPath(area.path,x*pixelRatio,y*pixelRatio,'evenodd'));if(hit)selectRegion(hit.id);}
      pointer=null;if(canvas.hasPointerCapture(event.pointerId))canvas.releasePointerCapture(event.pointerId);
    });
    canvas.addEventListener('pointercancel',()=>{pointer=null;});
  }else{status.textContent='Explore os dados de cada região pelos botões abaixo.';}
  document.querySelectorAll('[data-region]').forEach(button=>button.addEventListener('click',()=>selectRegion(button.dataset.region)));
  document.getElementById('map-reset').addEventListener('click',()=>{angle=-.08;tilt=.40;requestDraw();});
  selectRegion(3);
  // Animate once on entry. Respect the operating system's reduced-motion setting.
  if(!reducedMotion){
    const counts=[...document.querySelectorAll('.kpi strong')].map(element=>{
      const [,numeric,suffix]=element.textContent.match(/^([\d,]+)(.*)$/);
      return {value:Number(numeric.replace(',','.')),digits:numeric.includes(',')?numeric.split(',')[1].length:0,suffix};
    });
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
      if(!entry.isIntersecting)return;
      observer.unobserve(entry.target);
      const data=counts[Number(entry.target.dataset.count)];const start=performance.now();
      entry.target.setAttribute('aria-label',entry.target.textContent);
      function tick(now){const progress=Math.min((now-start)/950,1);const value=data.value*(1-Math.pow(1-progress,3));entry.target.textContent=new Intl.NumberFormat('pt-BR',{minimumFractionDigits:data.digits,maximumFractionDigits:data.digits}).format(value)+data.suffix;if(progress<1)requestAnimationFrame(tick);}
      requestAnimationFrame(tick);
    }),{threshold:.4});
    document.querySelectorAll('.kpi strong').forEach((element,index)=>{element.dataset.count=index;observer.observe(element);});
  }
  const links=[...document.querySelectorAll('.topbar nav a')];
  let navigationScheduled=false;
  function updateNavigation(){
    navigationScheduled=false;let current=links[0];
    links.forEach(link=>{if(document.querySelector(link.getAttribute('href')).getBoundingClientRect().top<=window.innerHeight*.33)current=link;});
    links.forEach(link=>{link.classList.toggle('active',link===current);if(link===current)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');});
  }
  window.addEventListener('scroll',()=>{if(!navigationScheduled){navigationScheduled=true;requestAnimationFrame(updateNavigation);}},{passive:true});updateNavigation();
})();
