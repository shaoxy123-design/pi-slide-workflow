import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Type } from 'typebox';
import {
  createAgentSession, createExtensionRuntime, getAgentDir, ModelRuntime,
  SessionManager, SettingsManager, type ExtensionAPI,
} from '@earendil-works/pi-coding-agent';
import { SlideHost, workerToolResult } from './core.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const text = (value: unknown) => ({ content: [{ type: 'text' as const, text: JSON.stringify(value, null, 2) }], details: value });

export default function (pi: ExtensionAPI) {
  const runtimes = new Map<string, Promise<ModelRuntime>>();
  const host = new SlideHost({ root, createSession: async options => {
    // Use Pi's existing credentials through its native runtime, never copy or log keys.
    // Cache/model writes are scoped to this run; settings below are memory-only.
    let runtimePromise = runtimes.get(options.run);
    if (!runtimePromise) {
      runtimePromise = ModelRuntime.create({
        allowModelNetwork: false, refreshOnCreate: false,
        modelsStorePath: path.join(options.storage, 'models-store.json'),
      });
      runtimes.set(options.run, runtimePromise);
    }
    const runtime = await runtimePromise;
    const resolved = runtime.getModel(options.model.provider, options.model.id);
    if (!resolved || resolved.id !== options.model.id || resolved.provider !== options.model.provider
      || resolved.api !== options.model.api || resolved.baseUrl !== options.model.baseUrl
      || (options.request.task_kind === 'visual' && !resolved.input?.includes('image'))) {
      throw new Error('Worker runtime cannot resolve the same exact configured model; no fallback is allowed.');
    }
    const rules = await fs.readFile(path.join(root, 'AGENTS.md'), 'utf8');
    const rolePath = path.join(root, 'hosts/pi/agents', `${options.request.role}.md`);
    const role = await fs.readFile(rolePath, 'utf8');
    // A fixed resource loader prevents auto-loading unrelated extensions, skills,
    // global prompts, or package resources into a worker. Workers have no delegate tool.
    const extensions = { extensions: [], errors: [], runtime: createExtensionRuntime() };
    const loader = {
      getExtensions: () => extensions,
      getSkills: () => ({ skills: [], diagnostics: [] }),
      getPrompts: () => ({ prompts: [], diagnostics: [] }),
      getThemes: () => ({ themes: [], diagnostics: [] }),
      getAgentsFiles: () => ({ agentsFiles: [{ path: path.join(root, 'AGENTS.md'), content: rules }] }),
      getSystemPrompt: () => undefined, getSystemPromptSource: () => undefined,
      getAppendSystemPrompt: () => [`Repository root: ${root}\n\n${role}`],
      getAppendSystemPromptSources: () => [{ path: rolePath }],
      extendResources: () => {}, reload: async () => {},
    };
    const settings = SettingsManager.inMemory({
      defaultThinkingLevel: options.thinking,
      images: { blockImages: options.request.task_kind === 'content', autoResize: true },
      enableAnalytics: false, enableInstallTelemetry: false,
    });
    const sessionManager = options.sessionPath
      ? SessionManager.open(options.sessionPath, options.sessionDir, root)
      : SessionManager.create(root, options.sessionDir);
    return createAgentSession({
      cwd: root, agentDir: getAgentDir(), modelRuntime: runtime,
      model: resolved, thinkingLevel: options.thinking, sessionManager,
      settingsManager: settings, resourceLoader: loader,
      tools: options.request.role === 'reviewer' ? ['read', 'bash'] : ['read', 'write', 'edit', 'bash'],
    });
  } });

  pi.registerTool({
    name: 'slide_worker', label: 'Slide worker',
    description: 'Delegate to a reusable independent Executioner or Reviewer context. The Planner uses exact GLM 5.3 Flash or GLM 5.3; content inherits that selected main model and visual tasks always use exact GLM 5.3 Flash. A completed dispatch is not quality approval. Reviewer requires the frozen candidate path/hash. Calls are serialized.',
    executionMode: 'sequential',
    parameters: Type.Object({
      role: Type.Union([Type.Literal('executioner'), Type.Literal('reviewer')]),
      task_kind: Type.Union([Type.Literal('content'), Type.Literal('visual')]),
      mode: Type.Union([Type.Literal('demo'), Type.Literal('create'), Type.Literal('improve')]),
      run_dir: Type.String({ minLength: 1, description: 'Absolute repository runs/<run-id> directory.' }),
      handoff: Type.String({ minLength: 1 }),
      candidate_path: Type.Optional(Type.String({ minLength: 1 })),
      candidate_sha256: Type.Optional(Type.String({ pattern: '^[0-9a-fA-F]{64}$' })),
      source_paths: Type.Optional(Type.Array(Type.String({ minLength: 1 }))),
    }, { additionalProperties: false }),
    async execute(_id, params, signal, onUpdate, ctx) {
      return workerToolResult(await host.dispatch(params, {
        model: ctx.model, thinkingLevel: ctx.thinkingLevel,
        findModel: (provider: string, id: string) => ctx.modelRegistry.find(provider, id),
        signal, onUpdate: progress => onUpdate?.(text(progress)),
      }));
    },
  });
  pi.registerTool({
    name: 'question_me', label: 'Ask professor',
    description: 'Planner-owned clarification. Persist the question before asking; unanswered required questions block workers. No timeout or default supplies consent. Reuse only an unchanged answered question.',
    executionMode: 'sequential',
    parameters: Type.Object({
      run_dir: Type.String({ minLength: 1 }), id: Type.String({ minLength: 1 }),
      question: Type.String({ minLength: 1 }), reason: Type.Optional(Type.String()),
      required: Type.Boolean(), choices: Type.Optional(Type.Array(Type.String({ minLength: 1 }), { minItems: 2 })),
    }, { additionalProperties: false }),
    async execute(_id, params, _signal, _onUpdate, ctx) {
      return text(await host.question(params, {
        hasUI: ctx.hasUI,
        input: (question: string, reason: string) => ctx.ui.input(question, reason),
        select: (question: string, choices: string[]) => ctx.ui.select(question, choices),
      }));
    },
  });
  // Pi 0.84 executes ordinary returns as successes; this native result hook
  // propagates our failed receipt to the actual UI/model tool-error channel.
  pi.on('tool_result', async event => {
    if (event.toolName === 'slide_worker' && (event.details as { status?: string })?.status === 'failed') {
      return { isError: true };
    }
  });
  pi.on('session_shutdown', async () => host.dispose());
}
