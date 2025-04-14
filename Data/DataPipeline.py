import requests
from dotenv import load_dotenv
import os


class DataPipeline:
    def __init__(self, dotenv_path):
        load_dotenv(dotenv_path)
        self.api_key = os.getenv('RIOT_GAMES_KEY')

        self.eune_base_url = "https://eun1.api.riotgames.com"
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

    def get_matches_by_tier(self, tier):
        #retrieving data from every division in each tier
        #https://eun1.api.riotgames.com/tft/league/v1/entries/EMERALD/II?queue=RANKED_TFT&page=2&api_key=.....
        data = []
        for division in self.divisions:
            #division_players = []
            for page in range(1, 5):
                url = "{}/{}/league/v1/entries/{}/{}?queue={}&page={}&api_key={}".format(self.eune_base_url,
                                                                                        self.game_type[0],
                                                                                        tier,
                                                                                        division,
                                                                                        self.queue_tft,
                                                                                        page,
                                                                                        str(self.api_key))

            print("Uploading data from z... {}", division)
            response = self.make_request(url)
            data.append(response)
        return data
