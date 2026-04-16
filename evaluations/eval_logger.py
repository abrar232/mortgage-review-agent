"""
Evaluation result logger — saves eval outputs to evaluations/results/
"""

import json
import os
from datetime import datetime


def save_eval_results(eval_name: str, results: dict) -> str:
    """Save evaluation results to a timestamped JSON file."""
    os.makedirs("evaluations/results", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"evaluations/results/{eval_name}_{timestamp}.json"

    output = {
        "eval_name": eval_name,
        "timestamp": datetime.now().isoformat(),
        "summary": results["summary"],
        "cases": results["cases"],
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {filename}")
    return filename