from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qwen_video_experiment.io_utils import infer_category, write_json


@dataclass
class RunConfig:
    model: str
    video: str
    prompt: str
    output: str
    system_prompt: str | None
    fps: float | None
    num_frames: int | None
    max_new_tokens: int
    temperature: float
    top_p: float
    do_sample: bool
    video_backend: str | None
    device_map: str
    torch_dtype: str
    attn_implementation: str | None
    trust_remote_code: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a dynamic prompt against a video using a Qwen multimodal model."
    )
    parser.add_argument("--model", default="Qwen/Qwen3.5-4B", help="Model checkpoint name.")
    parser.add_argument("--video", required=True, help="Path to a local video file.")
    parser.add_argument("--prompt", required=True, help="Prompt to send with the video.")
    parser.add_argument(
        "--output",
        required=True,
        help="Path to a JSON file containing the run result.",
    )
    parser.add_argument(
        "--system-prompt",
        default=None,
        help="Optional system prompt to steer analysis style.",
    )
    sampling_group = parser.add_mutually_exclusive_group()
    sampling_group.add_argument(
        "--fps",
        type=float,
        default=1.0,
        help="Sample video frames at this FPS. Use instead of --num-frames.",
    )
    sampling_group.add_argument(
        "--num-frames",
        type=int,
        default=None,
        help="Optional fixed number of frames to sample from the input video.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=256,
        help="Maximum number of new tokens to generate.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature. Ignored when --do-sample is not set.",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.9,
        help="Top-p sampling parameter. Ignored when --do-sample is not set.",
    )
    parser.add_argument(
        "--do-sample",
        action="store_true",
        help="Enable probabilistic sampling instead of greedy decoding.",
    )
    parser.add_argument(
        "--video-backend",
        default="pyav",
        help="Video loading backend used by Transformers.",
    )
    parser.add_argument(
        "--device-map",
        default="auto",
        help="Device map passed to from_pretrained.",
    )
    parser.add_argument(
        "--torch-dtype",
        default="auto",
        choices=["auto", "bfloat16", "float16", "float32"],
        help="Torch dtype used when loading the model.",
    )
    parser.add_argument(
        "--attn-implementation",
        default=None,
        help="Optional attention implementation passed to from_pretrained.",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Allow custom model code from the model repository if required.",
    )
    return parser.parse_args()


def resolve_torch_dtype(dtype_name: str) -> Any:
    import torch

    if dtype_name == "auto":
        return "auto"
    mapping = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    return mapping[dtype_name]


def load_model_stack(config: RunConfig) -> tuple[Any, Any]:
    from transformers import AutoModelForImageTextToText, AutoProcessor

    load_kwargs: dict[str, Any] = {
        "device_map": config.device_map,
        "torch_dtype": resolve_torch_dtype(config.torch_dtype),
        "trust_remote_code": config.trust_remote_code,
    }
    if config.attn_implementation:
        load_kwargs["attn_implementation"] = config.attn_implementation

    processor = AutoProcessor.from_pretrained(
        config.model,
        trust_remote_code=config.trust_remote_code,
    )
    model = AutoModelForImageTextToText.from_pretrained(config.model, **load_kwargs)
    return processor, model


def build_messages(config: RunConfig, video_path: Path) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    if config.system_prompt:
        messages.append(
            {
                "role": "system",
                "content": [{"type": "text", "text": config.system_prompt}],
            }
        )
    messages.append(
        {
            "role": "user",
            "content": [
                {"type": "video", "path": str(video_path)},
                {"type": "text", "text": config.prompt},
            ],
        }
    )
    return messages


def move_inputs_to_model(inputs: dict[str, Any], model: Any) -> dict[str, Any]:
    device = model.device
    moved: dict[str, Any] = {}
    for key, value in inputs.items():
        if hasattr(value, "to"):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def run_inference(config: RunConfig) -> dict[str, Any]:
    video_path = Path(config.video).expanduser().resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    started = time.time()
    processor, model = load_model_stack(config)
    messages = build_messages(config, video_path)
    processor_kwargs: dict[str, Any] = {
        "add_generation_prompt": True,
        "tokenize": True,
        "return_dict": True,
        "return_tensors": "pt",
    }
    if config.fps is not None:
        processor_kwargs["fps"] = config.fps
    if config.num_frames is not None:
        processor_kwargs["num_frames"] = config.num_frames

    inputs = processor.apply_chat_template(messages, **processor_kwargs)
    model_inputs = move_inputs_to_model(inputs, model)

    generation_kwargs: dict[str, Any] = {
        "max_new_tokens": config.max_new_tokens,
        "do_sample": config.do_sample,
    }
    if config.do_sample:
        generation_kwargs["temperature"] = config.temperature
        generation_kwargs["top_p"] = config.top_p

    generated = model.generate(**model_inputs, **generation_kwargs)
    prompt_length = model_inputs["input_ids"].shape[1]
    generated_text = processor.decode(
        generated[0, prompt_length:],
        skip_special_tokens=True,
    ).strip()

    return {
        "schema_version": 1,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.time() - started, 3),
        "status": "success",
        "model": config.model,
        "video": str(video_path),
        "category": infer_category(video_path),
        "prompt": config.prompt,
        "system_prompt": config.system_prompt,
        "generation": {
            "fps": config.fps,
            "num_frames": config.num_frames,
            "max_new_tokens": config.max_new_tokens,
            "do_sample": config.do_sample,
            "temperature": config.temperature if config.do_sample else None,
            "top_p": config.top_p if config.do_sample else None,
            "video_backend": config.video_backend,
        },
        "runtime": {
            "device_map": config.device_map,
            "torch_dtype": config.torch_dtype,
            "attn_implementation": config.attn_implementation,
            "trust_remote_code": config.trust_remote_code,
        },
        "messages": messages,
        "output_text": generated_text,
    }


def main() -> None:
    args = parse_args()
    config = RunConfig(
        model=args.model,
        video=args.video,
        prompt=args.prompt,
        output=args.output,
        system_prompt=args.system_prompt,
        fps=args.fps,
        num_frames=args.num_frames,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        do_sample=args.do_sample,
        video_backend=args.video_backend,
        device_map=args.device_map,
        torch_dtype=args.torch_dtype,
        attn_implementation=args.attn_implementation,
        trust_remote_code=args.trust_remote_code,
    )
    result = run_inference(config)
    write_json(Path(config.output), result)
    print(json.dumps({"output": config.output, "status": result["status"]}))


if __name__ == "__main__":
    main()
