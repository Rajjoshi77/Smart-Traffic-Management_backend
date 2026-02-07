import os
import json
from glob import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SPARK_PEAK_HOURS_DIR = os.path.join(
    BASE_DIR,
    "spark",
    "data",
    "analytics_results",
    "peak_hours"
)

def get_peak_hours():
    """
    Reads Spark-generated JSON files and returns peak hours
    """
    results = []

    if not os.path.exists(SPARK_PEAK_HOURS_DIR):
        return []

    json_files = glob(os.path.join(SPARK_PEAK_HOURS_DIR, "*.json"))

    for file in json_files:
        with open(file, "r") as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))

    # sort by avg_volume descending
    results = sorted(results, key=lambda x: x["avg_volume"], reverse=True)

    return results[:6]  # top 6 peak hours
