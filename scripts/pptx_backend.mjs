#!/usr/bin/env node
/** Small guarded artifact-tool adapter. It produces drafts, never final decks. */
import fs from 'node:fs/promises';
import { constants } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { requireThat, validatePlan, compareInventories } from './lib/backend-core.mjs';
import { sha256, writeJson, sourceFile, newPath, distinctPaths, loadRuntime, importDeck, inventoryOf, guard, renderAll, preflightSource } from './lib/backend-runtime.mjs';

const HELP = `PPTX backend (all outputs remain drafts)
  node scripts/pptx_backend.mjs inspect source.pptx --output inventory.json
  node scripts/pptx_backend.mjs apply source.pptx --plan operations.json --output candidate.pptx --report execution.json
Options: --runtime-modules ABSOLUTE_NODE_MODULES (or RUNTIME_NODE_MODULES)
         --python ABSOLUTE_PYTHON (or RUNTIME_PYTHON; required for apply)
Parents of output/report paths must exist. Existing outputs are never overwritten.
Apply creates <report>.evidence/ with the baseline, no-op qualification, guards,
before/after PNGs and layouts. No-op failure blocks all planned edits.
Exit 0: inspection/draft created; 1: preservation blocked; 2: input/runtime error.
An exit 0 candidate still requires independent visual/native-object review.`;

function parseArgs(argv) {
  if (argv.length === 0 || argv[0] === '--help') return {help:true};
  const [command, source, ...rest] = argv;
  requireThat(['inspect','apply'].includes(command) && source && !source.startsWith('--'), 'INVALID_ARGUMENTS', HELP);
  const args = {command,source};
  const allowed = new Set(['output','plan','report','runtime-modules','python']);
  for (let i=0;i<rest.length;i+=2) {
    const key = rest[i].replace(/^--/,'');
    requireThat(rest[i].startsWith('--') && allowed.has(key) && rest[i+1] && !rest[i+1].startsWith('--') && !Object.hasOwn(args,key), 'INVALID_ARGUMENTS', `Invalid or repeated option: ${rest[i]}`);
    args[key]=rest[i+1];
  }
  requireThat(args.output && (command === 'inspect' || (args.plan && args.report)), 'INVALID_ARGUMENTS', HELP);
  requireThat(command !== 'inspect' || (!args.plan && !args.report), 'INVALID_ARGUMENTS', 'inspect does not accept --plan or --report');
  return args;
}

export async function run(argv = process.argv.slice(2)) {
  let reportPath, report;
  try {
    const args = parseArgs(argv);
    if (args.help) { console.log(HELP); return 0; }
    const source = await sourceFile(args.source);
    const output = await newPath(args.output);
    requireThat(args.command !== 'inspect' || path.extname(output).toLowerCase() === '.json', 'INVALID_ARGUMENTS', 'inspect --output must be a new .json path');
    const sourceHash = await sha256(source);
    let plan, evidence;
    if (args.command === 'apply') {
      requireThat(path.extname(output).toLowerCase() === '.pptx', 'INVALID_ARGUMENTS', '--output must be a new .pptx path');
      const planPath = await fs.realpath(args.plan);
      const safeReportPath = await newPath(args.report);
      requireThat(path.extname(safeReportPath).toLowerCase() === '.json', 'INVALID_ARGUMENTS', '--report must be a new .json path');
      evidence = await newPath(`${safeReportPath}.evidence`);
      distinctPaths([source,planPath,output,safeReportPath,evidence]);
      requireThat(path.isAbsolute(args.python ?? process.env.RUNTIME_PYTHON ?? ''), 'PYTHON_UNAVAILABLE', 'apply requires --python or RUNTIME_PYTHON with an absolute bundled Python path');
      // Report path is safe only after every collision check has passed.
      reportPath = safeReportPath;
      report = {version:1,kind:'pptx-backend-execution',status:'running',source:{path:source,sha256:sourceHash},candidate:null,output_requested:output,source_plan:planPath,evidence_dir:evidence,operations:[],checks:{},visual_review:'required',native_editability_review:'required'};
      plan = JSON.parse((await fs.readFile(planPath,'utf8')).replace(/^\uFEFF/,''));
    } else {
      distinctPaths([source,output]);
    }
    const runtime = await loadRuntime(args['runtime-modules'] ?? process.env.RUNTIME_NODE_MODULES);
    const deck = await importDeck(runtime,source);
    const inventory = await inventoryOf(deck,source,sourceHash,runtime.backendVersion);
    requireThat(await sha256(source) === sourceHash, 'SOURCE_MISMATCH', 'Source changed during inspection');
    if (args.command === 'inspect') { await writeJson(output,inventory); console.log(`Inventory written: ${output}`); return 0; }
    validatePlan(plan,inventory);
    report.backend = inventory.backend;
    report.operations = plan.operations.map(o => ({id:o.id,object_id:o.object_id,op:o.op,status:'pending'}));
    await fs.mkdir(evidence);
    await writeJson(path.join(evidence,'source-inventory.json'),inventory);
    report.checks.source_features = await preflightSource(args.python ?? process.env.RUNTIME_PYTHON,source);
    await writeJson(path.join(evidence,'source-feature-check.json'),report.checks.source_features);
    requireThat(report.checks.source_features.passed, 'UNSUPPORTED_FEATURES', 'Source contains unqualified feature families; see source-feature-check.json. No export or planned edits were executed');
    const baselinePath = path.join(evidence,'baseline.json');
    await guard(args.python ?? process.env.RUNTIME_PYTHON,['snapshot',source],baselinePath);
    const noopPath = path.join(evidence,'noop.pptx');
    await (await runtime.PresentationFile.exportPptx(deck)).save(noopPath);
    const noopGuard = await guard(args.python ?? process.env.RUNTIME_PYTHON,['compare',baselinePath,noopPath,'--source',source],path.join(evidence,'noop-content-check.json'));
    report.checks.noop_content = {passed:noopGuard.passed,report:path.join(evidence,'noop-content-check.json')};
    requireThat(noopGuard.passed === true, 'ROUNDTRIP_BLOCKED', 'Unedited import/export failed the content guard; planned edits were not executed');
    const noopDeck = await importDeck(runtime,noopPath);
    const noopInventory = await inventoryOf(noopDeck,noopPath,await sha256(noopPath),runtime.backendVersion);
    report.checks.noop_objects = compareInventories(inventory,noopInventory);
    requireThat(report.checks.noop_objects.passed, 'ROUNDTRIP_BLOCKED', 'Unedited import/export changed inspected native objects or geometry; planned edits were not executed');
    report.renders = {before:await renderAll(deck,inventory,path.join(evidence,'before'))};
    requireThat(await sha256(source) === sourceHash, 'SOURCE_MISMATCH', 'Source changed before edits');
    for (const operation of plan.operations) {
      const target = deck.resolve(operation.object_id);
      if (operation.op === 'move_resize') target.position = {...operation.position};
      else target.text.fontSize = operation.font_size_pt / 0.75;
    }
    const draftPath = path.join(evidence,'candidate-draft.pptx');
    await (await runtime.PresentationFile.exportPptx(deck)).save(draftPath);
    const candidateGuard = await guard(args.python ?? process.env.RUNTIME_PYTHON,['compare',baselinePath,draftPath,'--source',source],path.join(evidence,'candidate-content-check.json'));
    report.checks.candidate_content = {passed:candidateGuard.passed,report:path.join(evidence,'candidate-content-check.json')};
    requireThat(candidateGuard.passed === true, 'CONTENT_BLOCKED', 'Edited export failed the content guard; the private draft must not be delivered');
    const candidateDeck = await importDeck(runtime,draftPath);
    const candidateHash = await sha256(draftPath);
    const candidateInventory = await inventoryOf(candidateDeck,draftPath,candidateHash,runtime.backendVersion);
    await writeJson(path.join(evidence,'candidate-inventory.json'),candidateInventory);
    report.checks.candidate_objects = compareInventories(inventory,candidateInventory,plan.operations);
    requireThat(report.checks.candidate_objects.passed, 'GEOMETRY_BLOCKED', 'Exported native object types, geometry or font sizes differ from the plan');
    report.renders.after = await renderAll(candidateDeck,candidateInventory,path.join(evidence,'after'));
    requireThat(await sha256(source) === sourceHash, 'SOURCE_MISMATCH', 'Source changed before draft delivery');
    await fs.copyFile(draftPath,output,constants.COPYFILE_EXCL);
    requireThat(await sha256(output) === candidateHash, 'OUTPUT_MISMATCH', 'Copied draft hash differs from the reviewed evidence');
    report.candidate = {path:output,sha256:candidateHash};
    report.status = 'draft_review_required';
    report.operations.forEach(o => {o.status='applied_and_structurally_checked';});
    report.limitations = inventory.limitations;
    await writeJson(reportPath,report);
    console.log(`Draft written: ${output}\nIndependent visual/native-object review required. Report: ${reportPath}`);
    return 0;
  } catch (error) {
    const code = error.code ?? 'BACKEND_ERROR';
    if (reportPath && report) {
      report.status='blocked';
      report.error={code,message:error.message};
      // Never replace evidence or an existing report during error handling.
      try { await writeJson(reportPath,report); } catch {}
    }
    console.error(`${code}: ${error.message}`);
    return ['UNSUPPORTED_FEATURES','ROUNDTRIP_BLOCKED','CONTENT_BLOCKED','GEOMETRY_BLOCKED'].includes(code) ? 1 : 2;
  }
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await run();
