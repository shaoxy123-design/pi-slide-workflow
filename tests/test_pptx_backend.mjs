import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { validatePlan, compareInventories } from '../scripts/lib/backend-core.mjs';
import { loadRuntime, inventoryOf, importDeck, sha256, preflightSource } from '../scripts/lib/backend-runtime.mjs';
const execute = promisify(execFile);
const workspace = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const cli = path.join(workspace,'scripts/pptx_backend.mjs');
const geometry = {left:72,top:48,width:1136,height:80};
const inventory = {source:{sha256:'a'.repeat(64)},slides:[{slide:1,slide_id:'sl/source',width:1280,height:720,objects:[
  {object_id:'sh/text',kind:'textbox',chart_type:null,position:geometry,font_size_pt:30,supported_ops:['move_resize','set_font_size']},
  {object_id:'ch/chart',kind:'chart',chart_type:'bar',position:{left:100,top:180,width:1080,height:400},font_size_pt:null,supported_ops:['move_resize']},
  {object_id:'im/image',kind:'image',chart_type:null,position:{left:20,top:620,width:50,height:50},font_size_pt:null,supported_ops:[]},
]}]};
function plan() {return {version:1,source_sha256:'a'.repeat(64),operations:[{id:'R1-text',slide:1,object_id:'sh/text',op:'move_resize',expected_position:{...geometry},position:{...geometry,top:56}}]};}
function rejects(mutate, code) { const p=plan(); mutate(p); assert.throws(()=>validatePlan(p,inventory),e=>e.code===code); }
test('valid source-bound move is accepted',()=>assert.equal(validatePlan(plan(),inventory).operations.length,1));
test('wrong source hash is rejected',()=>rejects(p=>p.source_sha256='b'.repeat(64),'SOURCE_MISMATCH'));
test('version and unrecognized plan fields are rejected',()=>{rejects(p=>p.version=2,'INVALID_PLAN'); rejects(p=>p.script='process.exit()','INVALID_PLAN');});
test('content edits and arbitrary code are never operations',()=>{rejects(p=>p.operations[0].op='replace_text','UNAUTHORIZED_OPERATION');rejects(p=>p.operations[0].op='eval','UNAUTHORIZED_OPERATION');});
test('unknown operation keys are rejected',()=>rejects(p=>p.operations[0].text='Rewrite','INVALID_PLAN'));
test('IDs must belong to the inspected source and slide',()=>{rejects(p=>p.operations[0].object_id='sh/invented','UNKNOWN_OBJECT');rejects(p=>p.operations[0].slide=2,'UNKNOWN_SLIDE');});
test('stale expected geometry is rejected',()=>rejects(p=>p.operations[0].expected_position.left+=1,'GEOMETRY_MISMATCH'));
test('NaN, Infinity, string, negative and zero extents are rejected',()=>{for(const value of [NaN,Infinity,'40',-1,0]) rejects(p=>p.operations[0].position.width=value,'INVALID_GEOMETRY');});
test('off-slide geometry is rejected',()=>{rejects(p=>p.operations[0].position.left=-1,'OUT_OF_BOUNDS'); rejects(p=>p.operations[0].position.top=700,'OUT_OF_BOUNDS');});
test('duplicate requirement IDs and duplicate same-property edits are rejected',()=>{rejects(p=>p.operations.push({...p.operations[0]}),'INVALID_PLAN');rejects(p=>p.operations.push({...p.operations[0],id:'different'}),'INVALID_PLAN');});
test('font changes are limited to native text',()=>{
 const p=plan(); p.operations[0]={id:'R1-font',slide:1,object_id:'sh/text',op:'set_font_size',expected_position:{...geometry},font_size_pt:32};
 assert.equal(validatePlan(p,inventory).operations[0].font_size_pt,32);
 p.operations[0].object_id='ch/chart'; assert.throws(()=>validatePlan(p,inventory),e=>e.code==='UNSUPPORTED_OBJECT');
});
test('unqualified object edits are rejected',()=>rejects(p=>p.operations[0].object_id='im/image','UNSUPPORTED_OBJECT'));
test('roundtrip object loss, reordering and unintended changes fail',()=>{
 assert.equal(compareInventories(inventory,structuredClone(inventory)).passed,true);
 for(const alter of [i=>i.slides[0].objects.pop(),i=>i.slides[0].objects.reverse(),i=>i.slides[0].objects[0].position.top+=5,i=>i.slides[0].objects[1].kind='image']) {
  const next=structuredClone(inventory); alter(next); assert.equal(compareInventories(inventory,next).passed,false);
 }
});
test('expected geometry and font changes survive structural comparison',()=>{
 const next=structuredClone(inventory); next.slides[0].objects[0].position.top=56;
 assert.equal(compareInventories(inventory,next,plan().operations).passed,true);
});

const configured = Boolean(process.env.RUNTIME_NODE_MODULES && process.env.RUNTIME_PYTHON);
test('real artifact-tool fixture: no-op qualification, native edits, render, safety failures', {skip:configured?false:'Set RUNTIME_NODE_MODULES and RUNTIME_PYTHON for real PPTX integration',timeout:180000}, async t=>{
 const dir=await fs.mkdtemp(path.join(workspace,'runs/backend-qualification/test-'));
 const runtime=await loadRuntime(process.env.RUNTIME_NODE_MODULES);
 const deck=runtime.Presentation.create({slideSize:{width:1280,height:720}});
 const slide=deck.slides.add();
 const text=slide.shapes.add({geometry:'textbox',position:{...geometry},fill:'none',line:{fill:'none',width:0}});
 text.text='Synthetic backend test fixture'; text.text.style={typeface:'Arial',fontSize:40,bold:true,color:'#142735',autoFit:'none'};
 slide.charts.add('bar',{position:{left:100,top:180,width:1080,height:400},categories:['A','B','C'],series:[{name:'Synthetic only',values:[1,2,3]}],barOptions:{direction:'column',grouping:'clustered'},hasLegend:false});
 slide.speakerNotes.textFrame.setText('Synthetic test note. Preserve exact wording and punctuation.');
 const source=path.join(dir,'source.pptx');
 await (await runtime.PresentationFile.exportPptx(deck)).save(source);
 const originalHash=await sha256(source);
 async function command(args) {
  try { const result=await execute(process.execPath,[cli,...args],{cwd:workspace,env:process.env,timeout:120000,windowsHide:true,maxBuffer:1024*1024}); return {...result,code:0}; }
  catch(e){ return {stdout:e.stdout,stderr:e.stderr,code:e.code}; }
 }
 const invPath=path.join(dir,'inventory.json');
 assert.equal((await command(['inspect',source,'--output',invPath])).code,0);
 const actual=JSON.parse(await fs.readFile(invPath,'utf8'));
 const first=actual.slides[0].objects.find(o=>o.kind==='textbox'), chart=actual.slides[0].objects.find(o=>o.kind==='chart');
 const operationPlan={version:1,source_sha256:originalHash,operations:[
  {id:'R1-layout',slide:1,object_id:first.object_id,op:'move_resize',expected_position:first.position,position:{...first.position,top:56}},
  {id:'R2-font',slide:1,object_id:first.object_id,op:'set_font_size',expected_position:first.position,font_size_pt:32},
  {id:'R3-chart',slide:1,object_id:chart.object_id,op:'move_resize',expected_position:chart.position,position:{...chart.position,left:110,width:1070}},
 ]};
 const planFile=path.join(dir,'operations.json');
 await fs.writeFile(planFile,'\uFEFF'+JSON.stringify(operationPlan));
 const candidate=path.join(dir,'candidate.pptx'), reportFile=path.join(dir,'execution.json');
 const applied=await command(['apply',source,'--plan',planFile,'--output',candidate,'--report',reportFile]);
 assert.equal(applied.code,0,applied.stderr);
 const report=JSON.parse(await fs.readFile(reportFile,'utf8'));
 assert.equal(report.status,'draft_review_required');
 assert.equal(report.checks.noop_content.passed,true);
 assert.equal(report.checks.noop_objects.passed,true);
 assert.equal(report.checks.candidate_content.passed,true);
 assert.equal(report.checks.candidate_objects.passed,true);
 assert.equal(report.visual_review,'required'); assert.equal(report.native_editability_review,'required');
 assert.equal(await sha256(source),originalHash);
 assert.equal(await sha256(candidate),report.candidate.sha256);
 assert.ok((await fs.stat(report.renders.before[0].png)).size>0);
 assert.ok((await fs.stat(report.renders.after[0].png)).size>0);
 const exported=JSON.parse(await fs.readFile(path.join(report.evidence_dir,'candidate-inventory.json'),'utf8'));
 assert.equal(exported.slides[0].objects.find(o=>o.object_id===first.object_id).text,first.text);
 const checked=JSON.parse(await fs.readFile(report.checks.candidate_content.report,'utf8'));
 assert.equal(checked.candidate_editability[0].counts.charts,1);
 assert.equal(checked.differences.length,0);
 await t.test('a fresh import keeps stable IDs',async()=>{
  const repeated=await inventoryOf(await importDeck(runtime,source),source,originalHash,runtime.backendVersion);
  assert.deepEqual(repeated.slides.map(s=>s.objects.map(o=>o.object_id)),actual.slides.map(s=>s.objects.map(o=>o.object_id)));
 });
 await t.test('source and existing destinations cannot be overwritten',async()=>{
  assert.equal((await command(['inspect',source,'--output',source])).code,2);
  assert.equal((await command(['apply',source,'--plan',planFile,'--output',candidate,'--report',path.join(dir,'overwrite-report.json')])).code,2);
  assert.equal(await sha256(source),originalHash); assert.equal(await sha256(candidate),report.candidate.sha256);
 });
 await t.test('JSON output suffixes are enforced',async()=>{
  assert.equal((await command(['inspect',source,'--output',path.join(dir,'inventory.pptx')])).code,2);
  assert.equal((await command(['apply',source,'--plan',planFile,'--output',path.join(dir,'candidate2.pptx'),'--report',path.join(dir,'report.pptx')])).code,2);
 });
 await t.test('bad source hash produces a blocked report without any export',async()=>{
  const badPlan=path.join(dir,'wrong-source-plan.json');
  await fs.writeFile(badPlan,JSON.stringify({...operationPlan,source_sha256:'0'.repeat(64)}));
  const badOutput=path.join(dir,'blocked.pptx'), badReport=path.join(dir,'blocked.json');
  const result=await command(['apply',source,'--plan',badPlan,'--output',badOutput,'--report',badReport]);
  assert.equal(result.code,2); assert.equal(JSON.parse(await fs.readFile(badReport,'utf8')).error.code,'SOURCE_MISMATCH');
  await assert.rejects(fs.stat(badOutput),e=>e.code==='ENOENT');
  await assert.rejects(fs.stat(`${badReport}.evidence`),e=>e.code==='ENOENT');
 });
 await t.test('unqualified original comments are refused before no-op export',async()=>{
  // A real comment demonstrates a feature the minimal adapter does not certify;
  // it is intentionally blocked instead of silently lost.
  deck.comments.setSelf({displayName:'Synthetic Test Author',initials:'ST'});
  deck.comments.addThread({element:text},'Synthetic protected comment for backend preflight.');
  const unsupported=path.join(dir,'unsupported-source.pptx');
  await (await runtime.PresentationFile.exportPptx(deck)).save(unsupported);
  const featureCheck=await preflightSource(process.env.RUNTIME_PYTHON,unsupported);
  assert.equal(featureCheck.passed,false); assert.ok(featureCheck.findings.some(f=>f.part.toLowerCase().includes('comment')));
  const unsupportedInventory=await inventoryOf(await importDeck(runtime,unsupported),unsupported,await sha256(unsupported),runtime.backendVersion);
  const shape=unsupportedInventory.slides[0].objects.find(o=>o.kind==='textbox');
  const unsupportedPlan=path.join(dir,'unsupported-plan.json');
  await fs.writeFile(unsupportedPlan,JSON.stringify({version:1,source_sha256:unsupportedInventory.source.sha256,operations:[{id:'R1',slide:1,object_id:shape.object_id,op:'move_resize',expected_position:shape.position,position:{...shape.position,top:56}}]}));
  const unsupportedReport=path.join(dir,'unsupported-report.json'), unsupportedOutput=path.join(dir,'unsupported-candidate.pptx');
  const result=await command(['apply',unsupported,'--plan',unsupportedPlan,'--output',unsupportedOutput,'--report',unsupportedReport]);
  assert.equal(result.code,1,result.stderr);
  assert.equal(JSON.parse(await fs.readFile(unsupportedReport,'utf8')).error.code,'UNSUPPORTED_FEATURES');
  await assert.rejects(fs.stat(unsupportedOutput),e=>e.code==='ENOENT');
  await assert.rejects(fs.stat(path.join(`${unsupportedReport}.evidence`,'noop.pptx')),e=>e.code==='ENOENT');
 });
 console.log(`Real PPTX integration evidence: ${dir}`);
});
