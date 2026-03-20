# Qwen Video Capability Experiment Project Plan

## Goal

Build a GitHub-hosted experiment repo that uses a Qwen multimodal model to analyze videos with dynamic prompts and compare model behavior across different video conditions such as tranquil, chaotic, and foggy scenes.

## Current Understanding

- This is an assignment, so the setup should be reproducible and easy to explain.
- The project should use a local `.venv`.
- Source code should live in a GitHub repo.
- We should use `.gitignore` and avoid committing secrets.
- GPU execution should use the Prime Intellect CLI via `prime sandbox`.
- The experiment should support passing prompts dynamically at runtime.
- The main task is video understanding, not just single-image captioning.

## Recommended Technical Direction

### Model

- Default target: `Qwen3.5`
- Reason: current docs indicate multimodal support including video inputs, which fits the assignment better than the Qwen3 text-family baseline.

### Local Development

- Use a project-local `.venv`
- Use Python scripts for reproducibility
- Keep the local machine focused on development and validation, not heavy video inference

### Remote Execution

- Use `prime sandbox` for GPU execution
- Prefer a repo-managed Docker image or Dockerfile for reproducibility
- Keep the command interface consistent between local and remote runs

## Proposed Repository Shape

```text
qwen-experimentation/
  .gitignore
  README.md
  project_plan.md
  pyproject.toml
  Dockerfile
  src/
    qwen_video_experiment/
      run_video_prompt.py
      run_batch_experiment.py
      prompts.py
      io_utils.py
  data/
    videos/
      tranquil/
      chaotic/
      foggy/
  outputs/
  scripts/
    prime/
      create_sandbox.sh
      upload_project.sh
      run_experiment.sh
      download_outputs.sh
```

## Initial Functional Requirements

1. Run a single video through a Qwen video-capable model.
2. Accept a prompt dynamically from the command line.
3. Save the model output with metadata.
4. Run batch experiments across categorized video folders.
5. Support comparison across video conditions using the same prompt.
6. Keep outputs out of git by default.

## Initial CLI Shape

### Single video runner

```bash
python -m qwen_video_experiment.run_video_prompt \
  --model Qwen/Qwen3.5-4B \
  --video data/videos/tranquil/example.mp4 \
  --prompt "Describe the scene, motion level, visibility, and likely obstacles." \
  --output outputs/result.json
```

### Batch runner

```bash
python -m qwen_video_experiment.run_batch_experiment \
  --model Qwen/Qwen3.5-4B \
  --video-root data/videos \
  --prompt "Analyze the video and summarize the environment." \
  --output outputs/results.jsonl
```

## Logging and Output

Each run should capture:

- model name
- input video path
- category
- prompt
- generation parameters
- timestamp
- raw model output
- optional parsed or structured output

Recommended output format:

- `JSON` for single runs
- `JSONL` for batch experiments

## Git and Secret Safety

The repo should be safe to publish if we follow these rules:

- commit source code only
- do not commit `.env`
- do not commit API keys or tokens
- do not commit model caches
- do not commit local outputs by default
- do not commit downloaded raw videos unless they are explicitly safe to share

Important caveat:

- `.gitignore` only prevents future accidental adds
- if a secret is committed once, it remains in git history until explicitly removed

## Proposed Work Breakdown

### Phase 1: Project Setup

1. Initialize git repo
2. Create `.gitignore`
3. Create GitHub repo with `gh`
4. Add baseline project files

### Phase 2: Local Experiment Scaffold

1. Create `.venv`
2. Add Python dependencies
3. Implement single-video runner
4. Implement output logging

### Phase 3: Prime Sandbox Workflow

1. Add Dockerfile
2. Add sandbox helper scripts
3. Validate file upload and remote command execution
4. Run a first remote inference test

### Phase 4: Batch Evaluation

1. Add categorized video dataset layout
2. Implement batch runner
3. Save aggregate outputs
4. Compare responses across categories

### Phase 5: Assignment Packaging

1. Document setup and usage
2. Summarize experiment design
3. Record observations and failure modes

## GitHub Issue Candidates

- Initialize repository and baseline files
- Add `.gitignore` and secret-safe defaults
- Set up `.venv` and Python project metadata
- Implement single-video dynamic prompt runner
- Add structured output logging
- Add Prime sandbox Dockerfile and helper scripts
- Implement batch experiment runner
- Add README usage instructions
- Prepare assignment summary and analysis template

## Open Questions

These do not block planning, but they should be resolved before implementation:

1. Must the assignment use `Qwen3` exactly, or is `Qwen3.5` acceptable?
2. Which specific checkpoint should we target first?
   - likely small-to-mid-size for initial iteration
3. Do you want free-form output only, or also a structured JSON mode?
4. Are the videos already available locally, or do we need a data-ingest plan?
5. Should the repo include only code, or also a small sample video set?
6. Do you want the first remote path to use a custom `Dockerfile`, or a standard base image plus install steps?

## Recommendation

Unless the assignment says otherwise, the first implementation should target:

- `Qwen3.5`
- dynamic prompt input
- one single-video runner
- one batch runner
- Prime sandbox execution
- JSON/JSONL outputs
- a clean public-safe GitHub repo
