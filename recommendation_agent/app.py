from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from agent import RecommendationAgent
from backend import build_backend


def main() -> None:
    parser = argparse.ArgumentParser(description="Personalized recommendation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    recommend_parser = subparsers.add_parser("recommend")
    recommend_parser.add_argument("customer_id")
    recommend_parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    backend = build_backend()
    agent = RecommendationAgent(backend)
    response = agent.recommend(args.customer_id, limit=args.limit)
    print(json.dumps(asdict(response), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
