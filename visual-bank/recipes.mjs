/** Native PowerPoint component recipes. No fonts, labels, data, or raster slides.
 * API: addVisual(slide, id, {left,top,width,height,prefix,palette}) -> {id,names,shapes,bounds}
 * Coordinates are CSS pixels. A 120x80 design is fitted without distortion.
 * Native objects remain individually selectable; name prefix selects the motif.
 * Final delivery requires one pre-grouped visual. After export, pass these exact
 * returned names to group_components.py as one topic group specification, then
 * validate its parent selection/movement/resizing in PowerPoint. Drawing-model
 * structure alone does not certify exported adjustment behavior.
 */
export const visualIds = ['teaching-with-ai','agent-configuration','accounting-automation','fluent-uncertain-output','human-review',
 'calculator','spreadsheet','connected-systems','audit-sampling','workflow-steps','document-set','alternative-outputs','training-ladder','classroom-adoption',
 'task-duration','verification-lens','prompt-generation','multi-agent','prompt-goal','reusable-skill','document-memory','tools-permissions','institution-tool','network-access','model-comparison'];
const defaults={ink:'#006B68',accent:'#86BC25',light:'#E5F3EE',paper:'#FFFFFF',muted:'#9ACBC6'};
export function addVisual(slide,id,options={}) {
  if(!visualIds.includes(id)) throw new Error(`Unknown native visual: ${id}`);
  const {left=0,top=0,width=120,height=80,prefix=`visual-${id}`,palette={}}=options;
  if(![left,top,width,height].every(Number.isFinite)||width<=0||height<=0) throw new Error('Invalid visual bounds');
  const c={...defaults,...palette}, scale=Math.min(width/120,height/80), dx=left+(width-120*scale)/2,dy=top+(height-80*scale)/2;
  const shapes=[], names=[];
  const add=(part,geometry,x,y,w,h,fill='none',stroke=c.ink,sw=2,extra={})=>{
    const name=`${prefix}-${part}`;
    const s=slide.shapes.add({name,geometry,position:{left:dx+x*scale,top:dy+y*scale,width:w*scale,height:h*scale},fill,line:{fill:stroke,width:stroke==='none'?0:sw*scale},...extra});
    shapes.push(s);names.push(name);return s;
  };
  const rect=(part,x,y,w,h,fill=c.paper,stroke=c.ink,sw=2)=>add(part,'rect',x,y,w,h,fill,stroke,sw);
  const round=(part,x,y,w,h,fill=c.paper,stroke=c.ink,sw=2)=>add(part,'roundRect',x,y,w,h,fill,stroke,sw,{borderRadius:3*scale});
  const ellipse=(part,x,y,w,h,fill=c.paper,stroke=c.ink,sw=2)=>add(part,'ellipse',x,y,w,h,fill,stroke,sw);
  const line=(part,points,stroke=c.ink,sw=2,fill='none',closed=false)=>{
    const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
    const x=Math.min(...xs),y=Math.min(...ys),w=Math.max(.01,Math.max(...xs)-x),h=Math.max(.01,Math.max(...ys)-y);
    const commands=points.map((p,i)=>({[i?'lineTo':'moveTo']:{x:(p[0]-x)*scale,y:(p[1]-y)*scale}}));if(closed)commands.push({close:{}});
    return add(part,'custom',x,y,w,h,fill,stroke,sw,{customPaths:[{width:w*scale,height:h*scale,commands}]});
  };
  const chip=(p,x,y,w=28)=>{
    round(`${p}-body`,x,y,w,w,c.light);rect(`${p}-core`,x+8,y+8,w-16,w-16,c.accent,'none');
    for(let i=0;i<3;i++){const q=x+7+i*(w-14)/2;line(`${p}-pin-top-${i}`,[[q,y-5],[q,y]]);line(`${p}-pin-bottom-${i}`,[[q,y+w],[q,y+w+5]]);}
    for(let i=0;i<3;i++){const q=y+7+i*(w-14)/2;line(`${p}-pin-left-${i}`,[[x-5,q],[x,q]]);line(`${p}-pin-right-${i}`,[[x+w,q],[x+w+5,q]]);}
  };
  const page=(p,x,y,w=34,h=44,fill=c.paper)=>{
    line(`${p}-sheet`,[[x,y],[x+w-9,y],[x+w,y+9],[x+w,y+h],[x,y+h]],c.ink,2,fill,true);
    line(`${p}-fold`,[[x+w-9,y],[x+w-9,y+9],[x+w,y+9]],c.ink,1.6);
  };
  if(id==='teaching-with-ai'){
    line('book-left',[[8,31],[29,27],[50,33],[50,68],[29,62],[8,66]],c.ink,2,c.paper,true);
    line('book-right',[[50,33],[71,27],[92,31],[92,66],[71,62],[50,68]],c.ink,2,c.light,true);
    line('book-spine',[[50,34],[50,68]],c.ink,2);
    line('page-edge-left',[[13,71],[29,67],[49,73]],c.muted,1.8);
    line('page-edge-right',[[51,73],[71,67],[91,71]],c.muted,1.8);
    chip('ai',79,7,28);
  } else if(id==='agent-configuration'){
    // Tool-shaped tile and a blank task card dock into a configurable central unit.
    line('dock-left',[[36,26],[49,26],[49,40]],c.muted,2.4);
    line('dock-right',[[83,51],[96,51],[96,31]],c.muted,2.4);
    line('dock-bottom',[[59,65],[59,72],[31,72]],c.muted,2.4);
    round('tool-tile',6,7,31,31,c.light);
    line('tool-handle',[[14,28],[25,17]],c.ink,4);
    line('tool-jaw',[[22,13],[21,17],[25,21],[29,20]],c.ink,2.5);
    page('task',91,4,22,27,c.paper);
    round('skill-module',6,57,25,17,c.accent,'none');
    ellipse('skill-socket',15,60,7,7,c.paper,c.ink,1.3);
    chip('agent',44,29,35);
  } else if(id==='accounting-automation'){
    page('ledger',11,12,45,57,c.paper);
    line('ledger-divider',[[32,25],[32,61]],c.muted,1.5);
    for(let i=0;i<3;i++)line(`ledger-row-${i}`,[[17,34+i*10],[48,34+i*10]],c.muted,1.5);
    round('calculator',66,11,41,59,c.light);
    round('calculator-display',73,18,27,12,c.paper,c.ink,1.5);
    for(let y=0;y<3;y++)for(let x=0;x<3;x++)round(`calculator-key-${y}-${x}`,74+x*9,38+y*8,5,4,y===2&&x===2?c.accent:c.paper,c.ink,1);
  } else if(id==='fluent-uncertain-output'){
    // Alternative blank pages symbolize variable output; no fake writing or error verdict.
    page('alternative-back',13,12,27,35,c.light);
    page('alternative-mid',24,18,27,35,c.paper);
    page('alternative-front',35,24,27,35,c.paper);
    line('speech-outline',[[59,11],[110,11],[110,48],[91,48],[79,61],[79,48],[59,48]],c.ink,2,c.light,true);
    for(let i=0;i<3;i++)ellipse(`speech-ellipsis-${i}`,69+i*13,26,5,5,c.ink,'none');
  } else if(id==='human-review'){
    ellipse('reviewer-head',10,7,22,22,c.light);
    line('reviewer-body',[[4,65],[4,49],[10,39],[27,36],[41,47],[47,64]],c.ink,2,c.light,true);
    page('document',62,18,38,49,c.paper);
    line('table',[[35,71],[115,71]],c.ink,2);
    ellipse('lens',66,25,26,26,'none',c.ink,3);
    line('lens-handle',[[67,49],[51,63]],c.ink,4);
    line('reviewer-arm',[[23,46],[37,58],[51,59]],c.ink,3);
  } else if(id==='calculator'){
    round('calculator',31,4,58,72,c.light);round('display',39,12,42,16,c.paper,c.ink,1.6);
    for(let y=0;y<3;y++)for(let x=0;x<3;x++)round(`key-${y}-${x}`,40+x*14,37+y*11,9,7,y===2&&x===2?c.accent:c.paper,c.ink,1.2);
  } else if(id==='spreadsheet'){
    round('screen',9,8,102,58,c.paper);rect('sheet-header',16,16,88,10,c.light,'none');
    for(let i=0;i<4;i++)line(`row-${i}`,[[16,26+i*10],[104,26+i*10]],c.muted,1.5);
    for(let i=0;i<4;i++)line(`column-${i}`,[[16+i*22,16],[16+i*22,56]],c.muted,1.5);
    rect('selected-cell',60,36,22,10,c.accent,'none');line('stand',[[60,66],[60,75],[41,75],[79,75]],c.ink,2);
  } else if(id==='connected-systems'){
    line('bus',[[22,28],[22,43],[99,43],[99,28]],c.muted,2);
    line('central-link',[[60,43],[60,55]],c.muted,2);
    round('left-system',7,6,31,22,c.paper);round('right-system',83,6,31,22,c.paper);
    rect('database-body',43,54,34,19,c.light);ellipse('database-bottom',43,66,34,10,c.light);ellipse('database-top',43,49,34,10,c.paper);
    rect('left-screen',12,11,21,9,c.light,'none');rect('right-screen',88,11,21,9,c.light,'none');
  } else if(id==='audit-sampling'){
    round('records',12,8,62,61,c.paper);for(let y=0;y<4;y++)for(let x=0;x<3;x++)rect(`cell-${y}-${x}`,21+x*15,17+y*12,8,6,c.light,c.muted,1);
    ellipse('lens',57,27,39,39,'none',c.ink,3);line('handle',[[90,60],[111,75]],c.ink,4);
  } else if(id==='workflow-steps'){
    line('flow-top',[[30,22],[63,22],[63,43],[90,43]],c.muted,2.5);
    round('stage-start',4,9,30,25,c.light);round('stage-middle',47,33,31,25,c.paper);round('stage-end',88,48,28,25,c.light);
    for(const[x,y]of [[16,21],[58,45],[98,60]])rect(`stage-detail-${x}`,x,y,9,3,c.accent,'none');
  } else if(id==='document-set'){
    page('back',22,5,39,54,c.light);page('middle',40,13,39,54,c.paper);page('front',58,22,39,54,c.paper);
  } else if(id==='alternative-outputs'){
    chip('prompt-unit',43,23,30);
    page('output-left',3,7,25,33,c.paper);page('output-right',89,39,25,33,c.light);
    line('left-link',[[28,24],[38,24]],c.muted,2);line('right-link',[[78,55],[89,55]],c.muted,2);
  } else if(id==='training-ladder'){
    line('ladder-left',[[53,7],[37,76]],c.ink,3);line('ladder-right',[[86,7],[70,76]],c.ink,3);
    for(let i=0;i<5;i++){const y=17+i*12;line(`rung-${i}`,[[50-i*2.8,y],[84-i*2.8,y]],c.muted,2.5);}
    ellipse('learner-head',13,34,13,13,c.light);line('learner-body',[[20,48],[24,63],[13,76]],c.ink,2.8);line('learner-arm',[[22,52],[39,47]],c.ink,2.8);line('learner-leg',[[24,63],[34,75]],c.ink,2.8);
  } else if(id==='classroom-adoption'){
    round('board',53,7,57,41,c.light);line('board-leg-left',[[64,49],[62,67]],c.ink,2);line('board-leg-right',[[100,49],[102,67]],c.ink,2);
    ellipse('learner',11,27,16,16,c.paper);line('shoulders',[[6,64],[6,55],[13,49],[25,49],[33,56],[33,65]],c.ink,2,c.paper,true);
    round('device',27,46,22,16,c.light);line('desk',[[3,65],[48,65]],c.ink,2);
  } else if(id==='task-duration'){
    line('hourglass-frame-top',[[35,7],[85,7]],c.ink,3);line('hourglass-frame-bottom',[[35,73],[85,73]],c.ink,3);
    line('hourglass',[[41,9],[42,23],[60,40],[78,23],[79,9]],c.ink,2.4,c.light,false);
    line('hourglass-lower',[[41,71],[43,58],[60,41],[77,58],[79,71]],c.ink,2.4,c.paper,false);
    line('sand',[[46,67],[60,53],[74,67]],'none',0,c.accent,true);
  } else if(id==='verification-lens'){
    page('document',21,4,48,66,c.paper);ellipse('lens',48,24,41,41,'none',c.ink,3);line('handle',[[82,59],[105,76]],c.ink,4);
  } else if(id==='prompt-generation'){
    line('prompt-bubble',[[6,7],[63,7],[63,40],[33,40],[20,53],[20,40],[6,40]],c.ink,2,c.light,true);
    page('output',75,26,34,47,c.paper);for(let i=0;i<3;i++)ellipse(`ellipsis-${i}`,18+i*13,21,4,4,c.ink,'none');
  } else if(id==='multi-agent'){
    line('coordination',[[26,24],[94,24],[60,65],[26,24]],c.muted,2);
    chip('agent-left',9,6,27);chip('agent-right',84,6,27);chip('agent-lower',46,46,27);
  } else if(id==='prompt-goal'){
    page('instructions',12,10,40,59,c.paper);ellipse('goal-outer',68,17,43,43,c.light);ellipse('goal-inner',80,29,19,19,c.paper);ellipse('goal-center',87,36,5,5,c.accent,'none');
  } else if(id==='reusable-skill'){
    page('instruction-card',20,6,49,66,c.paper);round('tool-tile',67,34,38,34,c.light);line('tool-handle',[[77,58],[93,43]],c.ink,4);line('tool-jaw',[[89,39],[87,43],[93,49],[99,47]],c.ink,2.5);
  } else if(id==='document-memory'){
    line('folder',[[6,26],[6,18],[41,18],[49,27],[112,27],[112,70],[6,70]],c.ink,2,c.light,true);
    page('stored-left',21,5,31,43,c.paper);page('stored-right',56,9,31,40,c.paper);
    rect('folder-front',7,42,104,28,c.light,c.ink,2);
  } else if(id==='tools-permissions'){
    round('toolcase',11,27,70,42,c.light);line('handle',[[28,27],[28,15],[63,15],[63,27]],c.ink,2);line('case-division',[[11,43],[81,43]],c.muted,1.6);
    round('lock',82,40,27,26,c.paper);line('lock-shackle',[[87,40],[87,28],[90,23],[101,23],[105,28],[105,40]],c.ink,2.4);ellipse('keyhole',93,49,6,6,c.accent,'none');
  } else if(id==='institution-tool'){
    line('institution-roof',[[5,23],[34,5],[63,23]],c.ink,2,c.light,true);line('base',[[5,70],[64,70]],c.ink,3);
    for(let i=0;i<3;i++)rect(`column-${i}`,13+i*17,29,7,35,c.paper,c.ink,1.7);
    round('approved-tool',73,22,39,43,c.light);rect('tool-screen',79,29,27,23,c.paper,c.ink,1.5);
  } else if(id==='network-access'){
    ellipse('network',7,13,52,52,c.paper);ellipse('meridian',21,13,24,52,'none',c.muted,1.6);line('equator',[[7,39],[59,39]],c.muted,1.6);
    line('connection',[[59,39],[73,39]],c.ink,2);round('device',76,21,37,40,c.light);rect('screen',82,28,25,21,c.paper,c.ink,1.4);
  } else if(id==='model-comparison'){
    round('device-left',7,15,44,49,c.paper);round('device-right',69,15,44,49,c.light);
    rect('screen-left',14,23,30,24,c.light,c.ink,1.5);rect('screen-right',76,23,30,24,c.paper,c.ink,1.5);
    line('left-stand',[[16,71],[42,71]],c.ink,2);line('right-stand',[[78,71],[104,71]],c.ink,2);
  }
  return {id,names,shapes,bounds:{left:dx,top:dy,width:120*scale,height:80*scale},editability:'native_individual_components'};
}
