import time

import requests
from dotenv import load_dotenv
import os


class DataPipeline:
    def __init__(self, dotenv_path):
        load_dotenv(dotenv_path)
        self.api_key = os.getenv('RIOT_GAMES_KEY')

        self.eune_base_url = "https://eun1.api.riotgames.com"
        self.europe_base_url = "https://europe.api.riotgames.com"
        self.game_type = ["tft"]
        self.queue_tft = "RANKED_TFT"

        #needed TFT-LEAGUE-V1
        self.tiers = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND"]
        self.divisions = ['I', 'II', 'III', 'IV']

        #we have only 100 request per minute and 20 per sec.
        self.api_requests_made = 0
        self.start_time = time.time()
        self.requests_per_sec = 0
        self.last_request_time = time.time()

    def make_request(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"{url} returned {response.status_code} : {response.text}")

        return response.json()

    """
    This Function will be used to count requests done and if we've done more then 20 in sec, or 95 i minute, 
    then sleep for 1 min and then continue to work normally.
    """

    def rate_limited_requests(self, url):
        # max 20 per sec
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < 0.05:
            time.sleep(0.05 - time_since_last_request)

        # max 100 (95) every 2 minutes
        self.api_requests_made += 1
        if self.api_requests_made >= 95:
            # elapsed_time = time.time() - self.start_time
            # if elapsed_time < 120:
            #     sleep_time = 120 - elapsed_time + 30  # +30s for safety,
            #     print(f"Done 95 requests. Sleeping for {sleep_time} seconds")
            #     time.sleep(sleep_time)
            #
            # # reset counters after sleeping
            # self.api_requests_made = 0
            # self.start_time = time.time()
            print("Done 95 requests. Sleeping for 130 seconds.") #always sleep for 130s
            time.sleep(130)
            self.api_requests_made = 0

        self.last_request_time = time.time()
        return self.make_request(url)

    """
    This function retrieves basic player data for each rank, including: puuid, tier, division, wins, and losses.
    Important note: according to Riot's API, a 'win' only refers to a 1st place finish, 
    while 'losses' include placements from 2nd to 8th.

    However, in practice, players can still gain LP by finishing in the top 4 (1st–4th place). 
    To evaluate performance more accurately, we should make additional API calls to fetch the exact placement for each match.
    This will allow us to redefine what we consider a 'win' based on actual in-game results rather than Riot's strict definition.
    """

    def get_players_by_tier(self, tier, player_per_division):
        # retrieving data from every division in each tier
        # https://eun1.api.riotgames.com/tft/league/v1/entries/EMERALD/II?queue=RANKED_TFT&page=2&api_key=.....
        division_players_data = []
        for division in self.divisions:
            #for page in range(1, 2):
            url = "{}/{}/league/v1/entries/{}/{}?queue={}&page={}&api_key={}".format(self.eune_base_url,
                                                                                     self.game_type[0],
                                                                                     tier,
                                                                                     division,
                                                                                     self.queue_tft,
                                                                                     1,
                                                                                     str(self.api_key))

            try:
                #response = self.make_request(url)
                response = self.rate_limited_requests(url)
                for player in response[:player_per_division]:
                    player_data = {
                        'puuid': player.get('puuid'),
                        'tier': player.get('tier'),
                        'division': player.get('rank'),
                        'wins': player.get('wins'),
                        'losses': player.get('losses'),
                    }
                    division_players_data.append(player_data)

                print("Collected data about players from {} {}", tier, division)

                #If page is empty the next one will also be empty
                if len(response) == 0:
                    break

            except Exception as e:
                print(f"Error while downloading data ... : {e}")

        return division_players_data

    """
    Function to get unique match_ids 
    """

    def get_unique_matches_id_by_puuid(self, players_data, tier, matches_per_player):
        matches_ids = set()  # only unique match ids

        for player in players_data:
            if not player.get('puuid'):
                continue

            # https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/....
            url = "{}/{}/match/v1/matches/by-puuid/{}/ids?start=0&count={}&api_key={}".format(self.europe_base_url,
                                                                                              self.game_type[0],
                                                                                              player.get('puuid'),
                                                                                              matches_per_player,
                                                                                              str(self.api_key))
            try:
                #response = self.make_request(url)
                response = self.rate_limited_requests(url)
                for match_id in response:
                    matches_ids.add(match_id)

                print("Collected data about matches from {} {}", tier, player.get('puuid'))

            except Exception as e:
                print(f"Error while downloading data ... : {e}")

        return matches_ids





    """
    Collecting all match data from each tier - used in DataUploader class
    """
    def collect_data_from_tier(self, players_per_division, matches_per_player, tier):
        all_match_ids = set()

        players = self.get_players_by_tier(tier, players_per_division)

        tier_match_ids = self.get_unique_matches_id_by_puuid(players, tier, matches_per_player)
        all_match_ids.update(tier_match_ids)

        print(f"Collected {len(tier_match_ids)} unique ID from {tier}")

        # after collecting all ids we just use analyze_matches to retrieve all required information
        analyzed_matches = self.analyze_matches(all_match_ids)
        print(f"Analyzed matches: {len(analyzed_matches)}")

        return analyzed_matches





    """
    Function to get players
    """
    def get_players_info(self, player_puuid):
        if player_puuid == "BOT" or not player_puuid:
            print(f"Skipping bot player with puuid: {player_puuid}")
            return None

        #https://eun1.api.riotgames.com/tft/league/v1/by-puuid/....
        url = "{}/{}/league/v1/by-puuid/{}?api_key={}".format(self.eune_base_url,
                                                              self.game_type[0],
                                                              player_puuid,
                                                              self.api_key)
        try:
            #player_info = self.make_request(url)
            player_info = self.rate_limited_requests(url)
            if isinstance(player_info, list) and player_info:
                return player_info[0]
            print(f"No ranked data for player {player_puuid}")
            return player_info
        except Exception as e:
            print(f"Error while downloading data ... : {e}")
            return None

    """
    Function to download all data about matches needed for analysis (raw data (json)).
    """

    def get_match_details(self, match_id):
        # https://europe.api.riotgames.com/tft/match/v1/matches/EUN1_3769226704?api_key=.....
        url = "{}/{}/match/v1/matches/{}?api_key={}".format(self.europe_base_url,
                                                            self.game_type[0],
                                                            match_id,
                                                            str(self.api_key))
        try:
            # match_data = self.make_request(url)
            match_data = self.rate_limited_requests(url)
            return match_data
        except Exception as e:
            print(f"Error while downloading data ... : {e}")
            return None

    """
    Function to analyze and retrieve all necessary data for analysis. 
    """

    def analyze_matches(self, match_ids):
        matches_data = []
        players_data = []
        traits = []
        units = []
        items = []

        # for testing
        # matches_count = 0

        for match_id in match_ids:
            # for testing purposes
            # if matches_count >= 5:
            #     break

            match_data = self.get_match_details(match_id)
            if not match_data:
                continue

            match_info = match_data['info']

            # adding basic match info (this will be stored in matches table in the database).
            match_entry = {
                "match_id": match_id,
                "game_datetime": match_info['game_datetime'],
                "game_length": match_info['game_length'],
                "mapId": match_info['mapId'],
                "tft_set_number": match_info['tft_set_number'],
            }
            matches_data.append(match_entry)

            # now we will get info about players, traits, units and items (each will be stored separately)
            for player in match_info['participants']:
                try:
                    # checking if player is not a BOT
                    if player['puuid'] == "BOT" or not player['puuid']:
                        print(f"Skipping BOT player in match {match_id}")
                        continue

                    print(f"Processing player {player['puuid']} in match {match_id}")
                    playerInfo = self.get_players_info(player['puuid'])

                    player_entry = {
                        "match_id": match_id,
                        "puuid": player['puuid'],
                        "placement": player['placement'],
                        "level": player['level'],
                        "gold_left": player['gold_left'],
                        "last_round": player['last_round'],
                        "players_eliminated": player['players_eliminated'],
                        "time_eliminated": player['time_eliminated'],
                        "total_damage": player['total_damage_to_players'],
                        "companion_id": player['companion']['content_ID']
                    }

                    # adding ranking info if available, otherwise default values
                    if playerInfo and isinstance(playerInfo, dict):
                        if 'tier' in playerInfo and 'rank' in playerInfo:
                            player_entry.update({
                                "tier": playerInfo['tier'],
                                "division": playerInfo['rank'],
                                "leaguePoints": playerInfo.get('leaguePoints', 0),
                                "wins": playerInfo.get('wins', 0),
                                "losses": playerInfo.get('losses', 0)
                            })
                            # print(
                            #     f"Added ranked data for player {player['puuid']}: {playerInfo['tier']} {playerInfo['rank']}")
                        else:
                            # print(f"Player {player['puuid']} has no tier/rank info")

                            player_entry.update({
                                "tier": "UNRANKED",
                                "division": "NONE",
                                "leaguePoints": 0,
                                "wins": 0,
                                "losses": 0
                            })
                    else:
                        # print(f"No details for player {player['puuid']}")
                        player_entry.update({
                            "tier": "UNRANKED",
                            "division": "NONE",
                            "leaguePoints": 0,
                            "wins": 0,
                            "losses": 0
                        })

                    players_data.append(player_entry)
                    # print(f"Added player data for {player['puuid']}")

                    for trait in player['traits']:
                        try:
                            trait_entry = {
                                "match_id": match_id,
                                "puuid": player['puuid'],
                                "trait_name": trait['name'],
                                "num_units": trait['num_units'],
                                "style": trait['style'],
                                "tier_current": trait['tier_current'],
                                "tier_total": trait['tier_total']
                            }
                            traits.append(trait_entry)
                        except KeyError as e:
                            print(f"Missing key in trait data for player {player['puuid']}: {e}")
                            continue

                    for unit in player['units']:
                        try:
                            unit_entry = {
                                "match_id": match_id,
                                "puuid": player['puuid'],
                                "character_id": unit['character_id'],
                                "rarity": unit['rarity'],
                                "tier": unit['tier']
                            }
                            units.append(unit_entry)

                            for item_name in unit['itemNames']:
                                item_entry = {
                                    "match_id": match_id,
                                    "puuid": player['puuid'],
                                    "character_id": unit['character_id'],
                                    "item_id": item_name
                                }
                                items.append(item_entry)
                        except KeyError as e:
                            print(f"Missing key in unit data for player {player['puuid']}: {e}")
                            continue

                except Exception as e:
                    print(f"Error processing player {player.get('puuid', 'unknown')} in match {match_id}: {e}")
                    continue

            # matches_count += 1

        #return matches_data, players_data, traits, units, items
        return {
            "matches": matches_data,
            "players": players_data,
            "traits": traits,
            "units": units,
            "items": items
        }

#
