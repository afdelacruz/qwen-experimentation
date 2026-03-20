# Qwen Video Experimentation

Experiment repo for analyzing videos with Qwen multimodal models using dynamic prompts and Prime Intellect sandbox execution.

See [project_plan.md](./project_plan.md) for the current project plan.

## Local Setup

Create a project-local virtual environment and install the package in editable mode.

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
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
- Video loading defaults to the `decord` backend.
- Heavy inference should be run on Prime GPUs rather than the local M1 machine.
