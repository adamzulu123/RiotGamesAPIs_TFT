import os
import sys
import time

from Data.DataPipeline import DataPipeline
from Data.DatabaseConnection import DatabaseConnection


def save_to_db_api_info(matches_data):
    print("Saving data to database...")

    try:
        db.add_matches_bulk(matches_data["matches"])
        db.add_players_bulk(matches_data["players"])
        db.add_traits_bulk(matches_data["traits"])
        db.add_units_bulk(matches_data["units"])
        db.add_items_bulk(matches_data["items"])

        print("Done! Everything saved successfully!")

    except Exception as e:
        print("Error while saving to the database", e)


if __name__ == "__main__":

    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    pipeline = DataPipeline(dotenv_path)
    db = DatabaseConnection(dotenv_path)

    try:
        for tier in pipeline.tiers:
            analyzed_matches_data = pipeline.collect_data_from_tier(10, 1, tier)
            save_to_db_api_info(analyzed_matches_data)


        print("Data saved successfully!")

    except Exception as e:
        print(f"Błąd: {e}")
