import os
import sys
from Data.DataPipeline import DataPipeline
from Data.DatabaseConnection import DatabaseConnection


def get_and_save_api_info(pipeline, db, tier):
    print("Collecting data about player and matches from {}", tier)
    players_for_tier = pipeline.get_players_by_tier(tier)
    matches_ids = pipeline.get_unique_matches_id_by_puuid(players_for_tier, tier)
    match_data = pipeline.analyze_matches(matches_ids)

    # save to database
    for match in match_data["matches"]:
        db.add_match(match)

    for player in match_data["players"]:
        db.add_player(player)

    for trait in match_data["traits"]:
        db.add_traits(trait)

    for unit in match_data["units"]:
        db.add_unit(unit)

    for item in match_data["items"]:
        db.add_item(item)

    print("Finished collecting data about players and matches from {}", tier)


if __name__ == "__main__":

    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    pipeline = DataPipeline(dotenv_path)
    db = DatabaseConnection(dotenv_path)

    try:
        pipeline.collect_balanced_dataset()



        # results = pipeline.get_players_by_tier("DIAMOND")
        # match_ids = pipeline.get_unique_matches_id_by_puuid(results, "DIAMOND")
        # match_data = pipeline.analyze_matches(["EUN1_3771287739"])
        # for player in match_data.get("players", []):
        #     print(player)
        #
        #
        # db = DatabaseConnection(dotenv_path)
        # print("Connecting to database...")
        # print("ok")

    except Exception as e:
        print(f"Błąd: {e}")
