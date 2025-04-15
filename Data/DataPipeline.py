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
        self.tiers = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND"]
        self.divisions = ['I', 'II', 'III', 'IV']

    def make_request(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"{url} returned {response.status_code} : {response.text}")

        return response.json()

    """
    This function retrieves basic player data for each rank, including: puuid, tier, division, wins, and losses.
    Important note: according to Riot's API, a 'win' only refers to a 1st place finish, 
    while 'losses' include placements from 2nd to 8th.

    However, in practice, players can still gain LP by finishing in the top 4 (1st–4th place). 
    To evaluate performance more accurately, we should make additional API calls to fetch the exact placement for each match.
    This will allow us to redefine what we consider a 'win' based on actual in-game results rather than Riot's strict definition.
    """

    def get_players_by_tier(self, tier):
        # retrieving data from every division in each tier
        # https://eun1.api.riotgames.com/tft/league/v1/entries/EMERALD/II?queue=RANKED_TFT&page=2&api_key=.....
        division_players_data = []
        for division in self.divisions:
            for page in range(1, 5):
                url = "{}/{}/league/v1/entries/{}/{}?queue={}&page={}&api_key={}".format(self.eune_base_url,
                                                                                         self.game_type[0],
                                                                                         tier,
                                                                                         division,
                                                                                         self.queue_tft,
                                                                                         page,
                                                                                         str(self.api_key))

                try:
                    response = self.make_request(url)
                    for player in response:
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
    def get_unique_matches_id_by_puuid(self, players_data, tier):
        matches_ids = set()  # only unique match ids
        players_count = 0
        # there is a limit for 20 request per second and 100 request every 2 min, so later we will need a mechanism
        # which will be downloading data partially.

        for player in players_data:

            #for now for tests
            if players_count >= 20:
                print(f"Processed {players_count} players")
                break

            if not player.get('puuid'):
                continue

            # https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/....
            url = "{}/{}/match/v1/matches/by-puuid/{}/ids?start=0&count={}&api_key={}".format(self.europe_base_url,
                                                                                              self.game_type[0],
                                                                                              player.get('puuid'),
                                                                                              20,
                                                                                              str(self.api_key))
            try:
                response = self.make_request(url)
                for match_id in response:
                    matches_ids.add(match_id)

                print("Collected data about matches from {} {}", tier, player.get('puuid'))
                players_count += 1  # this will be deleted in the future

            except Exception as e:
                print(f"Error while downloading data ... : {e}")

        return matches_ids


    """
    Function to download all data needed for analysis (raw data (json)).
    """
    def get_match_details(self, match_id):
        # https://europe.api.riotgames.com/tft/match/v1/matches/EUN1_3769226704?api_key=.....
        url = "{}/{}/match/v1/matches/{}?api_key={}".format(self.europe_base_url,
                                                            self.game_type[0],
                                                            match_id,
                                                            str(self.api_key))
        try:
            match_data = self.make_request(url)
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
        matches_count = 0

        for match_id in match_ids:
            # for testing purposes
            if matches_count >= 1:
                break

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
            #print(match_entry)

            # now we will get info about players, traits, units and items (each will be stored separately)

            for player in match_info['participants']:
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
                players_data.append(player_entry)
                #print(player_entry)

                for trait in player['traits']:
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
                    #print(trait_entry)

                for unit in player['units']:
                    unit_entry = {
                        "match_id": match_id,
                        "puuid": player['puuid'],
                        "character_id": unit['character_id'],
                        "rarity": unit['rarity'],
                        "tier": unit['tier']
                    }
                    units.append(unit_entry)
                    #print(unit_entry)
                    for item_name in unit['itemNames']:
                        item_entry = {
                            "match_id": match_id,
                            "puuid": player['puuid'],
                            "character_id": unit['character_id'],
                            "item_name": item_name
                        }
                        items.append(item_entry)
                        #print(item_entry)

            matches_count += 1

        #return matches_data, players_data, traits, units, items
        return {
            "matches": matches_data,
            "players": players_data,
            "traits": traits,
            "units": units,
            "items": items
        }



















#