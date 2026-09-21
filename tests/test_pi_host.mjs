import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const modulePath = '../hosts/pi/core.mjs';
async function hostModule() {
  try { return await import(modulePath); }
  catch (error) { assert.fail(`Pi host dispatch implementation must load: ${error.code}`); }
}
async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'pi-slide-test-'));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const run = path.join(root, 'runs', 'sample');
  await fs.mkdir(run, { recursive: true });
  const candidate = path.join(run, 'candidate.pptx');
  await fs.writeFile(candidate, 'synthetic candidate');
  const source = path.join(root, 'source.md');
  await fs.writeFile(source, 'immutable source');
  return { root, run, candidate, source };
}
const digest = data => createHash('sha256').update(data).digest('hex');
const models = {
  'glm-5.3': { provider: 'zai', id: 'glm-5.3', input: ['text'], reasoning: true },
  'glm-5.3-flash': { provider: 'zai', id: 'glm-5.3-flash', input: ['text', 'image'], reasoning: true },
};
function fakeFactory(log, action = async () => {}, responseModel) {
  return async options => {
    log.push(options);
    const listeners = new Set();
    const session = {
      model: options.model, thinkingLevel: 'high', sessionId: `session-${log.length}`,
      sessionFile: options.sessionPath ?? path.join(options.sessionDir, `session-${log.length}.jsonl`),
      subscribe: listener => { listeners.add(listener); return () => listeners.delete(listener); },
      prompt: async () => {
        await fs.writeFile(session.sessionFile, '{}\n');
        await action(options);
        for (const listener of listeners) listener({ type: 'message_end', message: {
          role: 'assistant', provider: options.model.provider, model: responseModel ?? options.model.id,
          stopReason: 'stop', content: [{ type: 'text', text: 'Independent report: inspect required gates.' }],
        } });
      },
      abort: async () => {}, dispose: () => { options.disposed = true; },
    };
    return { session };
  };
}
function request(run, extra = {}) {
  return { role: 'executioner', task_kind: 'visual', mode: 'demo', run_dir: run,
    handoff: 'Build frozen source as native editable objects.', ...extra };
}

test('routes either exact main model; missing models, nonvision Flash and wrong main fail closed', async () => {
  const { selectModel } = await hostModule();
  assert.equal(selectModel(models['glm-5.3'], 'visual', (_, id) => models[id]).id, 'glm-5.3-flash');
  assert.equal(selectModel(models['glm-5.3'], 'content', (_, id) => models[id]).id, 'glm-5.3');
  const flashOnly = (_, id) => id === 'glm-5.3-flash' ? models[id] : undefined;
  assert.equal(selectModel(models['glm-5.3-flash'], 'content', flashOnly).id, 'glm-5.3-flash');
  assert.equal(selectModel(models['glm-5.3-flash'], 'visual', flashOnly).id, 'glm-5.3-flash');
  assert.throws(() => selectModel({ ...models['glm-5.3'], id: 'other-model' }, 'visual', (_, id) => models[id]), /Planner.*glm-5\.3/);
  assert.throws(() => selectModel(models['glm-5.3'], 'content', flashOnly), /unavailable/);
  assert.throws(() => selectModel(models['glm-5.3'], 'visual', () => undefined), /unavailable/);
  assert.throws(() => selectModel(models['glm-5.3'], 'visual', () => ({ ...models['glm-5.3-flash'], input: ['text'] })), /image/);
});

test('Flash-only workers retain separate role and phase sessions', async t => {
  const { SlideHost } = await hostModule();
  const f = await fixture(t), log = [];
  const host = new SlideHost({ root: f.root, createSession: fakeFactory(log) });
  const context = { model: models['glm-5.3-flash'], findModel: (_, id) => id === 'glm-5.3-flash' ? models[id] : undefined };
  const content = await host.dispatch(request(f.run, { task_kind: 'content' }), context);
  const visual = await host.dispatch(request(f.run), context);
  const review = await host.dispatch(request(f.run, { role: 'reviewer', candidate_path: f.candidate,
    candidate_sha256: digest('synthetic candidate') }), context);
  assert.deepEqual([content, visual, review].map(r => r.status), ['completed', 'completed', 'completed']);
  assert.equal(new Set([content, visual, review].map(r => r.session_id)).size, 3);
  assert.ok(log.every(entry => entry.model.id === 'glm-5.3-flash'));
});

test('preflight CLI accepts Flash-only catalog by default and checks both models in 5.3 mode', async t => {
  const f = await fixture(t);
  const packageDir = path.join(f.root, 'fake-pi');
  const aiDir = path.join(packageDir, 'node_modules', '@earendil-works', 'pi-ai');
  await fs.mkdir(path.join(packageDir, 'dist'), { recursive: true });
  await fs.mkdir(path.join(aiDir, 'dist'), { recursive: true });
  await fs.writeFile(path.join(packageDir, 'package.json'), JSON.stringify({ name: '@earendil-works/pi-coding-agent', version: 'fixture', type: 'module' }));
  await fs.writeFile(path.join(aiDir, 'package.json'), JSON.stringify({ name: '@earendil-works/pi-ai', type: 'module', exports: { './compat': { import: './dist/compat.js' } } }));
  await fs.writeFile(path.join(aiDir, 'dist', 'compat.js'), 'export const getSupportedThinkingLevels = model => model.thinkingLevels ?? ["high"];');
  const setCatalog = catalog => fs.writeFile(path.join(packageDir, 'dist', 'index.js'), `
    const catalog = ${JSON.stringify(catalog)};
    export const createAgentSession = () => { throw Error('No sessions in a metadata check'); };
    export const createExtensionRuntime = () => {};
    export class SettingsManager {};
    export class SessionManager {};
    export class ModelRuntime {
      static async create(options) { if (options.allowModelNetwork || options.refreshOnCreate) throw Error('Unexpected refresh'); return new ModelRuntime(); }
      getError() { return undefined; }
      getModel(provider, id) { const model = catalog[id]; return model?.provider === provider ? model : undefined; }
    }
  `);
  const check = (...extra) => {
    const args = [fileURLToPath(new URL('../hosts/pi/check.mjs', import.meta.url)), '--pi-package', packageDir, '--provider', 'zai', ...extra];
    try { return { exit: 0, report: JSON.parse(execFileSync(process.execPath, args, { encoding: 'utf8' })) }; }
    catch (error) { return { exit: error.status, report: JSON.parse(error.stdout) }; }
  };
  await setCatalog({ 'glm-5.3-flash': models['glm-5.3-flash'] });
  const flash = check();
  assert.equal(flash.exit, 0);
  assert.equal(flash.report.main_model, 'glm-5.3-flash');
  assert.deepEqual(flash.report.models.map(m => m.id), ['glm-5.3-flash']);
  assert.equal(check('--main-model', 'glm-5.3').report.ready, false);
  await setCatalog(models);
  const main53 = check('--main-model', 'glm-5.3');
  assert.equal(main53.exit, 0);
  assert.deepEqual(main53.report.models.map(m => m.id), ['glm-5.3', 'glm-5.3-flash']);
  assert.equal(check('--thinking', 'max').report.ready, false);
  await setCatalog({ 'glm-5.3-flash': { ...models['glm-5.3-flash'], input: ['text'] } });
  assert.equal(check().report.ready, false);
  await setCatalog({});
  assert.equal(check().report.ready, false);
});

test('reuses worker within role/phase; Reviewer and content stay independent', async t => {
  const { SlideHost } = await hostModule();
  const f = await fixture(t), log = [];
  const host = new SlideHost({ root: f.root, createSession: fakeFactory(log) });
  const context = { model: models['glm-5.3'], findModel: (_, id) => models[id] };
  const first = await host.dispatch(request(f.run), context);
  const second = await host.dispatch(request(f.run), context);
  const review = await host.dispatch(request(f.run, { role: 'reviewer', candidate_path: f.candidate,
    candidate_sha256: digest('synthetic candidate') }), context);
  await host.dispatch(request(f.run, { task_kind: 'content' }), context);
  assert.equal(first.status, 'completed');
  assert.equal(first.quality_decision, 'not_evaluated_by_dispatch');
  assert.equal(second.session_id, first.session_id);
  assert.notEqual(review.session_id, first.session_id);
  assert.equal(log.length, 3);
  assert.equal(log[2].model.id, 'glm-5.3');
  assert.match(await fs.readFile(review.response_path, 'utf8'), /Independent report/);
  const restarted = new SlideHost({ root: f.root, createSession: fakeFactory(log) });
  await restarted.dispatch(request(f.run), context);
  assert.equal(log[3].sessionPath, first.session_file);
});

test('requires frozen candidate, rejects run escape and detects candidate/source mutation', async t => {
  const { SlideHost } = await hostModule();
  const f = await fixture(t), log = [];
  const context = { model: models['glm-5.3'], findModel: (_, id) => models[id] };
  const host = new SlideHost({ root: f.root, createSession: fakeFactory(log, async options => {
    await fs.writeFile(options.request.role === 'reviewer' ? f.candidate : f.source, 'changed');
  }) });
  await assert.rejects(host.dispatch(request(f.run, { role: 'reviewer' }), context), /candidate/);
  await assert.rejects(host.dispatch(request(path.join(f.root, 'outside')), context), /runs/);
  await assert.rejects(host.dispatch(request(f.run, { role: 'reviewer', candidate_path: f.candidate,
    candidate_sha256: '0'.repeat(64) }), context), /hash/);
  const review = await host.dispatch(request(f.run, { role: 'reviewer', candidate_path: f.candidate,
    candidate_sha256: digest('synthetic candidate') }), context);
  assert.equal(review.status, 'failed');
  assert.match(review.error, /Candidate changed/);
  assert.equal(log[0].disposed, true);
  const edit = await host.dispatch(request(f.run, { source_paths: [f.source] }), context);
  assert.equal(edit.status, 'failed');
  assert.match(edit.error, /Source changed/);
  assert.equal(log[1].disposed, true);
});

test('serializes workers and rejects wrong response-model evidence', async t => {
  const { SlideHost } = await hostModule();
  const f = await fixture(t), log = [];
  let finish;
  const wait = new Promise(resolve => { finish = resolve; });
  const host = new SlideHost({ root: f.root, createSession: fakeFactory(log, () => wait) });
  const context = { model: models['glm-5.3'], findModel: (_, id) => models[id] };
  const pending = host.dispatch(request(f.run), context);
  await assert.rejects(host.dispatch(request(f.run), context), /active/);
  finish(); await pending;
  const broken = new SlideHost({ root: f.root, createSession: async options => {
    const built = await fakeFactory([])(options);
    built.session.model = models['glm-5.3']; return built;
  } });
  const result = await broken.dispatch(request(f.run), context);
  assert.equal(result.status, 'failed');
  assert.match(result.error, /binding/);
  const misreported = new SlideHost({ root: f.root, createSession: fakeFactory([], async () => {}, 'other-model') });
  const wrongResponse = await misreported.dispatch(request(f.run), context);
  assert.equal(wrongResponse.status, 'failed');
  assert.match(wrongResponse.error, /Response model binding/);
});

test('cancelled dispatch and crashed worker remain failed; review rejects outside-run candidate', async t => {
  const { SlideHost } = await hostModule();
  const f = await fixture(t), log = [];
  const context = { model: models['glm-5.3'], findModel: (_, id) => models[id] };
  const host = new SlideHost({ root: f.root, createSession: fakeFactory(log) });
  await assert.rejects(host.dispatch(request(f.run, { role: 'reviewer', candidate_path: f.source,
    candidate_sha256: digest('immutable source') }), context), /inside this run/);
  const abort = new AbortController(); abort.abort();
  const cancelled = await host.dispatch(request(f.run), { ...context, signal: abort.signal });
  assert.equal(cancelled.status, 'failed');
  assert.match(cancelled.error, /cancelled/);
  const crashed = new SlideHost({ root: f.root, createSession: fakeFactory([], async () => { throw new Error('Backend unavailable'); }) });
  const result = await crashed.dispatch(request(f.run), context);
  assert.equal(result.status, 'failed');
  assert.match(result.error, /Backend unavailable/);
  assert.equal(JSON.parse(await fs.readFile(result.receipt_path, 'utf8')).status, 'failed');
});

test('question cancellation/headless stays pending; unchanged answers reused and changed scope reasks', async t => {
  const { SlideHost } = await hostModule();
  const f = await fixture(t), log = [];
  const host = new SlideHost({ root: f.root, createSession: fakeFactory(log) });
  const question = { run_dir: f.run, id: 'audience', question: 'Which audience?', required: true };
  const pending = await host.question(question, { hasUI: false });
  assert.equal(pending.status, 'pending');
  await assert.rejects(host.dispatch(request(f.run), { model: models['glm-5.3'], findModel: (_, id) => models[id] }), /question/);
  const cancelled = await host.question(question, { hasUI: true, input: async () => undefined });
  assert.equal(cancelled.status, 'pending');
  const originalAnswer = '  Beginners\n';
  const answered = await host.question(question, { hasUI: true, input: async () => originalAnswer });
  assert.equal(answered.answer, originalAnswer);
  const reused = await host.question(question, { hasUI: true, input: async () => assert.fail('must reuse answer') });
  assert.equal(reused.answer, originalAnswer);
  const changed = await host.question({ ...question, question: 'Which language?' }, { hasUI: false });
  assert.equal(changed.status, 'pending');
  assert.equal(changed.answer, undefined);
});

test('failed worker receipts are native tool errors without changing receipt contents', async () => {
  const { workerToolResult } = await hostModule();
  const failed = { status: 'failed', error: 'Candidate changed during independent review.' };
  const result = workerToolResult(failed);
  assert.equal(result.isError, true);
  assert.deepEqual(result.details, failed);
  assert.deepEqual(JSON.parse(result.content[0].text), failed);
  assert.equal(workerToolResult({ status: 'completed' }).isError, false);
});
