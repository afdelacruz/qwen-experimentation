from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


DEFAULT_GPU_PREFERENCE = [
    "L4 24GB",
    "A5000 24GB",
    "RTX4090 24GB",
    "A40 48GB",
    "A6000 48GB",
]

DEFAULT_IMAGE = "cuda_12_4_pytorch_2_4"
DEFAULT_DISK_GB = 120


@dataclass
class Candidate:
    id: str
    gpu_type: str
    provider: str
    location: str
    stock_status: str
    price_value: float
    gpu_memory: int
    gpu_count: int
    memory_gb: str
    disk_gb: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recommend a Prime pod configuration for this Qwen experiment."
    )
    parser.add_argument(
        "--gpu-type",
        action="append",
        dest="gpu_types",
        help="Preferred GPU type in priority order. Can be specified multiple times.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of candidates to print.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the ranked candidates as JSON.",
    )
    parser.add_argument(
        "--include-low",
        action="store_true",
        help="Include low-stock options. Enabled by default for preferred GPU types.",
    )
    parser.add_argument(
        "--locations",
        nargs="*",
        default=["US", "CA"],
        help="Preferred locations in priority order.",
    )
    return parser.parse_args()


def load_availability() -> list[dict[str, Any]]:
    result = subprocess.run(
        ["prime", "availability", "list", "-o", "json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    return payload["gpu_resources"]


def to_candidate(resource: dict[str, Any]) -> Candidate:
    return Candidate(
        id=resource["id"],
        gpu_type=resource["gpu_type"],
        provider=resource["provider"],
        location=resource["location"],
        stock_status=resource["stock_status"],
        price_value=float(resource["price_value"]),
        gpu_memory=int(resource["gpu_memory"]),
        gpu_count=int(resource["gpu_count"]),
        memory_gb=str(resource["memory_gb"]),
        disk_gb=str(resource["disk_gb"]),
    )


def filter_candidates(
    resources: list[dict[str, Any]],
    preferred_types: list[str],
    include_low: bool,
) -> list[Candidate]:
    allowed_status = {"Available", "Low"} if include_low else {"Available"}
    out: list[Candidate] = []
    for resource in resources:
        if resource["gpu_type"] not in preferred_types:
            continue
        if int(resource["gpu_count"]) != 1:
            continue
        if resource["stock_status"] not in allowed_status:
            continue
        out.append(to_candidate(resource))
    return out


def rank_candidates(
    candidates: list[Candidate],
    preferred_types: list[str],
    preferred_locations: list[str],
) -> list[Candidate]:
    type_rank = {name: idx for idx, name in enumerate(preferred_types)}
    location_rank = {name: idx for idx, name in enumerate(preferred_locations)}
    stock_rank = {"Available": 0, "Low": 1}

    return sorted(
        candidates,
        key=lambda c: (
            type_rank.get(c.gpu_type, len(type_rank)),
            stock_rank.get(c.stock_status, 99),
            location_rank.get(c.location, len(location_rank)),
            c.price_value,
        ),
    )


def format_table(candidates: list[Candidate]) -> str:
    lines = []
    for idx, candidate in enumerate(candidates, start=1):
        lines.append(
            (
                f"{idx}. {candidate.gpu_type} | id={candidate.id} | "
                f"{candidate.provider}/{candidate.location} | stock={candidate.stock_status} | "
                f"${candidate.price_value:.2f}/hr | RAM={candidate.memory_gb}GB | disk={candidate.disk_gb}"
            )
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    preferred_types = args.gpu_types or DEFAULT_GPU_PREFERENCE
    resources = load_availability()
    candidates = filter_candidates(resources, preferred_types, include_low=args.include_low)
    if not candidates and not args.include_low:
        candidates = filter_candidates(resources, preferred_types, include_low=True)
    ranked = rank_candidates(candidates, preferred_types, args.locations)[: args.max_results]

    if not ranked:
        print("No acceptable single-GPU candidates found for the current preference order.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        payload = {
            "defaults": {
                "image": DEFAULT_IMAGE,
                "disk_gb": DEFAULT_DISK_GB,
            },
            "recommended": ranked[0].__dict__,
            "candidates": [candidate.__dict__ for candidate in ranked],
        }
        print(json.dumps(payload, indent=2))
        return

    print("Recommended pod for Qwen3.5 video experiments:\n")
    print(format_table(ranked))
    print("\nSuggested create command:")
    print(f"prime pods create --id {ranked[0].id}")
    print("\nRecommended interactive choices:")
    print(f"- image: {DEFAULT_IMAGE}")
    print(f"- disk: {DEFAULT_DISK_GB} GB")


if __name__ == "__main__":
    main()
