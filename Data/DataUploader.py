import os
import sys
from Data.DataPipeline import DataPipeline


if __name__ == "__main__":

    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    pipeline = DataPipeline(dotenv_path)

    try:
        results = pipeline.get_matches_by_tier("DIAMOND")

        for result in results:
            print(result)

    except Exception as e:
        print(f"Błąd: {e}")

