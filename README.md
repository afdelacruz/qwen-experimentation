# Qwen Video Experimentation

Experiment repo for analyzing videos with Qwen multimodal models using dynamic prompts and Prime Intellect sandbox execution.

See [project_plan.md](./project_plan.md) for the current project plan.

## Local Setup

Create a project-local virtual environment and install the package in editable mode.

```bash
uv venv .venv
source .venv/bin/activate
uv pip install --python .venv/bin/python -e ".[local]"
```

## Single Video Run

The first runner accepts a local video path and a prompt at runtime, then writes a JSON result file.

```bash
qwen-video-run \
  --model Qwen/Qwen3.5-4B \
  --video data/videos/tranquil/example.mp4 \
  --prompt "Describe the scene, motion level, visibility, and likely obstacles." \
  --output outputs/example.json
```

Or with the module entrypoint:

```bash
python -m qwen_video_experiment.run_video_prompt \
  --model Qwen/Qwen3.5-4B \
  --video data/videos/tranquil/example.mp4 \
  --prompt "Describe the scene, motion level, visibility, and likely obstacles." \
  --output outputs/example.json
```

## Notes

- This initial version targets the Transformers multimodal chat-template path.
- The runner expects a model compatible with `AutoModelForImageTextToText`.
- Local installs use the `pyav` backend by default.
- Linux/GPU environments can install `.[remote]` to use `decord`.
- Heavy inference should be run on Prime GPUs rather than the local M1 machine.

## Prime Sandbox Workflow

The repo now includes a first-pass sandbox workflow for GPU execution.

### 1. Build and publish a container image

The sandbox requires a Docker image. This repo includes a GPU-oriented [Dockerfile](./Dockerfile) that installs the project with the `remote` dependency set.

Example build flow:

```bash
docker build -t qwen-video-experiment:latest .
```

You can then push that image to a registry reachable by Prime.

### 2. Create a sandbox

```bash
scripts/prime/create_sandbox.sh <docker-image> [sandbox-name]
```

The script defaults to:
- `1` GPU
- `8` CPU cores
- `32` GB memory
- `80` GB disk
- `180` minute timeout

Override them with:
- `PRIME_GPU_COUNT`
- `PRIME_CPU_CORES`
- `PRIME_MEMORY_GB`
- `PRIME_DISK_SIZE_GB`
- `PRIME_TIMEOUT_MINUTES`

### 3. Upload the project files

```bash
scripts/prime/upload_project.sh <sandbox-id>
```

This uploads:
- `pyproject.toml`
- `README.md`
- the `src/` package

### 4. Run a remote experiment

```bash
scripts/prime/run_experiment.sh <sandbox-id> <remote-video-path> "<prompt>" <remote-output-path> [extra args...]
```

Example:

```bash
scripts/prime/run_experiment.sh sbx_123 \
  /workspace/data/videos/tranquil/example.mp4 \
  "Describe the scene, motion level, visibility, and likely obstacles." \
  /workspace/outputs/example.json \
  --model Qwen/Qwen3.5-4B \
  --video-backend decord
```

### 5. Download the outputs

```bash
scripts/prime/download_outputs.sh <sandbox-id> <remote-output-path> <local-output-path>
```

Example:

```bash
scripts/prime/download_outputs.sh sbx_123 \
  /workspace/outputs/example.json \
  outputs/example.json
```

### Current limitations

- The helper scripts assume the video file already exists inside the sandbox.
- We have not yet added a helper for uploading videos or bulk datasets.
- We have not yet validated the final Qwen3.5 checkpoint API against a live GPU run.
