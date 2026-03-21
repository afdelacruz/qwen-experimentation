from __future__ import annotations

import argparse

from transformers import AutoModelForImageTextToText, AutoProcessor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Debug Qwen3.5 video preprocessing and generation inputs."
    )
    parser.add_argument("--model", default="Qwen/Qwen3.5-4B")
    parser.add_argument("--video", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--fps", type=float, default=1.0)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    processor = AutoProcessor.from_pretrained(args.model)
    model = AutoModelForImageTextToText.from_pretrained(
        args.model,
        device_map="auto",
        torch_dtype="auto",
    )

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "video", "path": args.video},
                {"type": "text", "text": args.prompt},
            ],
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        fps=args.fps,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )

    print("keys:", list(inputs.keys()))
    print("video_grid_thw:", inputs.get("video_grid_thw"))
    if inputs.get("pixel_values_videos") is None:
        print("pixel_values_videos shape: None")
    else:
        print("pixel_values_videos shape:", tuple(inputs["pixel_values_videos"].shape))

    model_inputs = {k: (v.to(model.device) if hasattr(v, "to") else v) for k, v in inputs.items()}
    generated = model.generate(**model_inputs, max_new_tokens=args.max_new_tokens)
    prompt_length = model_inputs["input_ids"].shape[1]
    text = processor.decode(generated[0, prompt_length:], skip_special_tokens=True).strip()

    print("--- output ---")
    print(text)


if __name__ == "__main__":
    main()
