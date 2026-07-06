import React, { useEffect, useState, useTransition } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  BadgeCheck,
  Boxes,
  Download,
  Film,
  ImageIcon,
  Play,
  RefreshCw,
  Search,
  Settings2,
  Sparkles,
  TriangleAlert
} from "lucide-react";
import { DIRECTML_SAFE_DEFAULT_SIZE, chooseSelectedModel, directmlLabel } from "./modelSelection";
import "./styles.css";

type TaskType = "text-to-image" | "image-to-image" | "inpainting" | "image-to-video";

type RuntimeStatus = {
  providers: string[];
  selected_provider: string | null;
  directml_ready: boolean;
  image_generation_ready: boolean;
  video_generation_ready: boolean;
  optimum_available: boolean;
  torch_directml_available: boolean;
  errors: string[];
};

type ModelPreset = {
  id: string;
  name: string;
  repo_id: string;
  task: TaskType;
  family: string;
  runtime: "onnx-directml" | "torch-directml";
  directml: "ready" | "convert" | "experimental";
  notes: string;
  recommended_vram_gb: number;
};

type InstalledModel = {
  id: string;
  repo_id: string;
  local_path: string;
  task: TaskType;
  runtime: string;
  installed_at: string;
};

type InstallJob = {
  id: string;
  repo_id: string;
  task: TaskType;
  runtime: string;
  status: "pending" | "running" | "succeeded" | "failed";
  model_id?: string;
  error?: string;
};

type HubModel = {
  repo_id: string;
  downloads?: number;
  likes?: number;
  pipeline_tag?: string;
  tags?: string[];
};

type Job = {
  id: string;
  status: "pending" | "running" | "succeeded" | "failed";
  output_url: string;
  error?: string;
  request: {
    prompt: string;
    task: TaskType;
    width: number;
    height: number;
    steps: number;
  };
};

const API = "";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

function App() {
  const [runtime, setRuntime] = useState<RuntimeStatus | null>(null);
  const [presets, setPresets] = useState<ModelPreset[]>([]);
  const [installed, setInstalled] = useState<InstalledModel[]>([]);
  const [hubModels, setHubModels] = useState<HubModel[]>([]);
  const [installJobs, setInstallJobs] = useState<InstallJob[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [task, setTask] = useState<TaskType>("text-to-image");
  const [prompt, setPrompt] = useState("cinematic macro photo of a translucent hummingbird made of glass");
  const [negativePrompt, setNegativePrompt] = useState("blurry, distorted, low detail");
  const [query, setQuery] = useState("stable diffusion xl onnx");
  const [width, setWidth] = useState(DIRECTML_SAFE_DEFAULT_SIZE);
  const [height, setHeight] = useState(DIRECTML_SAFE_DEFAULT_SIZE);
  const [steps, setSteps] = useState(24);
  const [guidance, setGuidance] = useState(7);
  const [seed, setSeed] = useState("42");
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  async function refresh() {
    const [runtimeData, presetData, installedData, installJobData, jobData] = await Promise.all([
      requestJson<RuntimeStatus>("/api/runtime"),
      requestJson<ModelPreset[]>("/api/models/presets"),
      requestJson<InstalledModel[]>("/api/models/installed"),
      requestJson<InstallJob[]>("/api/models/install/jobs"),
      requestJson<Job[]>("/api/generate/jobs")
    ]);
    startTransition(() => {
      setRuntime(runtimeData);
      setPresets(presetData);
      setInstalled(installedData);
      setInstallJobs(installJobData);
      setJobs(jobData);
      setSelectedModel((current) => chooseSelectedModel(current, installedData));
    });
  }

  useEffect(() => {
    refresh().catch((error) => setMessage(error.message));
    const timer = window.setInterval(() => {
      Promise.all([
        requestJson<Job[]>("/api/generate/jobs"),
        requestJson<InstallJob[]>("/api/models/install/jobs"),
        requestJson<InstalledModel[]>("/api/models/installed")
      ])
        .then(([jobData, installJobData, installedData]) => {
          setJobs(jobData);
          setInstallJobs(installJobData);
          setInstalled(installedData);
          setSelectedModel((current) => chooseSelectedModel(current, installedData));
        })
        .catch(() => undefined);
    }, 2500);
    return () => window.clearInterval(timer);
  }, []);

  async function searchHub() {
    setMessage("");
    try {
      const models = await requestJson<HubModel[]>(
        `/api/models/search?query=${encodeURIComponent(query)}&task=${encodeURIComponent(task)}`
      );
      setHubModels(models);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No se pudo buscar en Hugging Face");
    }
  }

  async function installModel(
    repoId: string,
    modelTask: TaskType = task,
    runtime: "onnx-directml" | "torch-directml" = "torch-directml"
  ) {
    setMessage(`Instalando ${repoId}`);
    try {
      const job = await requestJson<InstallJob>("/api/models/install", {
        method: "POST",
        body: JSON.stringify({ repo_id: repoId, task: modelTask, runtime })
      });
      setInstallJobs((current) => [job, ...current]);
      setMessage(`Instalacion en cola: ${repoId}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No se pudo instalar el modelo");
    }
  }

  async function generate() {
    if (!selectedModel) {
      setMessage("Instala o selecciona un modelo primero");
      return;
    }
    setMessage("");
    try {
      const job = await requestJson<Job>("/api/generate/jobs", {
        method: "POST",
        body: JSON.stringify({
          model_id: selectedModel,
          task,
          prompt,
          negative_prompt: negativePrompt,
          width,
          height,
          steps,
          guidance_scale: guidance,
          seed: seed ? Number(seed) : null
        })
      });
      setJobs((current) => [job, ...current]);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No se pudo crear el job");
    }
  }

  return (
    <main className="app-shell">
      <aside className="side-panel">
        <div className="brand-row">
          <div className="brand-mark"><Sparkles size={22} /></div>
          <div>
            <h1>DirectGen</h1>
            <p>Local DirectML studio</p>
          </div>
        </div>

        <section className="status-block">
          <div className="section-title">
            <Activity size={17} />
            <span>Runtime</span>
            <button className="icon-button" onClick={refresh} aria-label="Actualizar runtime">
              <RefreshCw size={16} />
            </button>
          </div>
          <RuntimeBadge runtime={runtime} />
          <div className="provider-list">
            {(runtime?.providers ?? ["sin datos"]).map((provider) => (
              <span key={provider}>{provider}</span>
            ))}
          </div>
          {runtime?.errors?.map((error) => <p className="runtime-error" key={error}>{error}</p>)}
        </section>

        <section className="status-block">
          <div className="section-title">
            <Boxes size={17} />
            <span>Instalados</span>
          </div>
          <select value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)}>
            <option value="">Sin modelo local</option>
            {installed.map((model) => (
              <option key={model.id} value={model.id}>{model.repo_id}</option>
            ))}
          </select>
          <p className="microcopy">{installed.length} modelos en el registro local</p>
        </section>
      </aside>

      <section className="workspace">
        <div className="toolbar">
          <div className="segmented">
            <button className={task === "text-to-image" ? "active" : ""} onClick={() => setTask("text-to-image")}>
              <ImageIcon size={16} /> Imagen
            </button>
            <button className={task === "image-to-video" ? "active" : ""} onClick={() => setTask("image-to-video")}>
              <Film size={16} /> Video
            </button>
          </div>
          <span className="pending-text">{isPending ? "Actualizando" : message}</span>
        </div>

        <div className="prompt-surface">
          <label>
            Prompt
            <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} rows={7} />
          </label>
          <label>
            Negative prompt
            <textarea value={negativePrompt} onChange={(event) => setNegativePrompt(event.target.value)} rows={3} />
          </label>
          <div className="control-grid">
            <NumberField label="Ancho" value={width} min={256} max={2048} step={64} onChange={setWidth} />
            <NumberField label="Alto" value={height} min={256} max={2048} step={64} onChange={setHeight} />
            <NumberField label="Steps" value={steps} min={1} max={150} step={1} onChange={setSteps} />
            <NumberField label="Guidance" value={guidance} min={0} max={30} step={0.5} onChange={setGuidance} />
          </div>
          {(width > DIRECTML_SAFE_DEFAULT_SIZE || height > DIRECTML_SAFE_DEFAULT_SIZE) && (
            <p className="runtime-error">
              DirectML puede fallar en SDXL por encima de {DIRECTML_SAFE_DEFAULT_SIZE}x{DIRECTML_SAFE_DEFAULT_SIZE}. Prueba menor resolucion primero.
            </p>
          )}
          <label className="seed-field">
            Seed
            <input value={seed} onChange={(event) => setSeed(event.target.value)} inputMode="numeric" />
          </label>
          <button className="primary-action" onClick={generate}>
            <Play size={18} /> Generar
          </button>
        </div>

        <div className="library-grid">
          <section>
            <div className="section-title">
              <BadgeCheck size={17} />
              <span>Presets</span>
            </div>
            <div className="model-list">
              {presets.map((model) => (
                <ModelCard key={model.id} model={model} onInstall={() => installModel(model.repo_id, model.task, model.runtime)} />
              ))}
            </div>
          </section>

          <section>
            <div className="section-title">
              <Search size={17} />
              <span>Hugging Face</span>
            </div>
            <div className="search-row">
              <input value={query} onChange={(event) => setQuery(event.target.value)} />
              <button className="icon-button solid" onClick={searchHub} aria-label="Buscar modelos">
                <Search size={18} />
              </button>
            </div>
            <div className="hub-results">
              {hubModels.map((model) => (
                <button key={model.repo_id} onClick={() => installModel(model.repo_id, task, "torch-directml")}>
                  <span>{model.repo_id}</span>
                  <small>{model.downloads?.toLocaleString() ?? "sin"} descargas</small>
                </button>
              ))}
            </div>
          </section>
        </div>
      </section>

      <aside className="jobs-panel">
        <div className="section-title">
          <Settings2 size={17} />
          <span>Jobs</span>
        </div>
        <div className="jobs-list">
          {installJobs.map((job) => (
            <article key={job.id} className={`job-card ${job.status}`}>
              <div>
                <strong>install {job.status}</strong>
                <p>{job.repo_id}</p>
              </div>
              {job.error && <p className="job-error"><TriangleAlert size={14} /> {job.error}</p>}
            </article>
          ))}
          {jobs.map((job) => (
            <article key={job.id} className={`job-card ${job.status}`}>
              <div>
                <strong>{job.status}</strong>
                <p>{job.request.prompt}</p>
              </div>
              {job.status === "succeeded" && <img src={job.output_url} alt="Resultado generado" />}
              {job.error && <p className="job-error"><TriangleAlert size={14} /> {job.error}</p>}
            </article>
          ))}
        </div>
      </aside>
    </main>
  );
}

function RuntimeBadge({ runtime }: { runtime: RuntimeStatus | null }) {
  if (!runtime) return <div className="runtime-badge pending">Detectando</div>;
  if (runtime.directml_ready) return <div className="runtime-badge ready">DirectML listo</div>;
  return <div className="runtime-badge blocked">DirectML no disponible</div>;
}

function NumberField({
  label,
  value,
  min,
  max,
  step,
  onChange
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
}) {
  return (
    <label>
      {label}
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

function ModelCard({ model, onInstall }: { model: ModelPreset; onInstall: () => void }) {
  return (
    <article className="model-card">
      <div>
        <strong>{model.name}</strong>
        <p>{model.repo_id}</p>
      </div>
      <span className={`compat ${model.directml}`}>{directmlLabel(model.directml)}</span>
      <p>{model.notes}</p>
      <div className="model-actions">
        <small>{model.recommended_vram_gb} GB VRAM</small>
        <button onClick={onInstall}><Download size={15} /> Instalar</button>
      </div>
    </article>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
