import os
import sys
from Data.DataPipeline import DataPipeline


if __name__ == "__main__":

    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    pipeline = DataPipeline(dotenv_path)

    try:
        results = pipeline.get_players_by_tier("DIAMOND")
        match_ids = pipeline.get_unique_matches_id_by_puuid(results, "DIAMOND")
        match_data = pipeline.analyze_matches(match_ids)

        for data in match_data:
            print(data)

    except Exception as e:
        print(f"Błąd: {e}")

