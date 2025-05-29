import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor, execute_values
from contextlib import contextmanager
import pandas as pd


class DatabaseConnection:
    def __init__(self, dotenv_path):
        load_dotenv(dotenv_path)
        envs = ['PG_DB_PASSWORD', 'PG_DB_USER', 'PG_DB_DATABASE', 'PG_DB_HOST', 'PG_DB_PORT']
        for env in envs:
            if not os.environ.get(env):
                raise Exception(f'Environment variable {env} is not set')

        self.conn = psycopg2.connect(
            database=os.getenv('PG_DB_DATABASE'),
            user=os.getenv('PG_DB_USER'),
            password=os.getenv('PG_DB_PASSWORD'),
            host=os.getenv('PG_DB_HOST'),
            port=os.getenv('PG_DB_PORT'),
            sslmode="require"
        )
        # otwieramy przy każdym połaczeniu bo tych danych jest bardzo duzo
        # self.cursor = self.conn.cursor()  # to obiekt pozwalajacy na odbieranie i wysyłanie zapytan do bazy
        # taki tunel do komunikacji z baza

    def __del__(self):
        """Closing connection"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def query(self, query, args=None, fetch_one=False):
        # self.ensure_connection()
        with self.conn.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchone() if fetch_one else cursor.fetchall()

    def execute_query(self, query, params=None):
        # self.ensure_connection()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()
        except Exception as e:
            print(f'Error while executing query: {e}')
            self.conn.rollback()
            raise e

    # todo: tutaj trzeba bedzie optymalnie jakoś co jakiś czas sprawdzac stan połaczenia

    def ensure_connection(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        except (psycopg2.InterfaceError, psycopg2.OperationalError):
            print("Reconnecting to database...")
            self.reconnect()

    def reconnect(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass
        self.conn = psycopg2.connect(
            database=os.getenv('PG_DB_DATABASE'),
            user=os.getenv('PG_DB_USER'),
            password=os.getenv('PG_DB_PASSWORD'),
            host=os.getenv('PG_DB_HOST'),
            port=os.getenv('PG_DB_PORT'),
            sslmode="require"
        )
    # matches table operations
    def add_match(self, match_data):
        """Adding a new match to the database - ignoring duplicate matches"""
        sql = """
        INSERT INTO matches (match_id, game_datetime, game_length, map_id, tft_set_number) 
        VALUES (%s, %s, %s, %s, %s) ON CONFLICT (match_id) DO NOTHING
        RETURNING match_id """

        params = (
            match_data["match_id"],
            match_data["game_datetime"],
            match_data["game_length"],
            match_data["mapId"],
            match_data["tft_set_number"],
        )
        try:
            self.execute_query(sql, params)
            print("Match added successfully")
        except Exception as e:
            print(f'Error while adding match: {e}')

    def get_match(self, match_id):
        return self.query("SELECT * FROM matches WHERE match_id = %s", (match_id,), fetch_one=True)

    def get_all_matches(self):
        return self.query("SELECT * FROM matches")

    def delete_match(self, match_id):
        self.execute_query("DELETE FROM matches WHERE match_id = %s", (match_id,))
        print("Match deleted successfully")

    # players table - operations
    def add_player(self, player):
        sql = """
        INSERT INTO players(puuid, match_id, placement, level, gold_left, last_round,
            players_eliminated, time_eliminated, total_damage, companion_id, tier, division, leaguePoints, wins, losses) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT (puuid, match_id) DO NOTHING"""

        params = (
            player['puuid'],
            player['match_id'],
            player['placement'],
            player['level'],
            player['gold_left'],
            player['last_round'],
            player['players_eliminated'],
            player['time_eliminated'],
            player['total_damage'],
            player['companion_id'],
            player['tier'],
            player['division'],
            player['leaguePoints'],
            player['wins'],
            player['losses']
        )

        try:
            self.execute_query(sql, params)
            print("Player added successfully")
        except Exception as e:
            print(f'Error while adding player info: {e}')

    def get_player(self, puuid):
        return self.query("SELECT * FROM players WHERE puuid = %s", (puuid,), fetch_one=True)

    def get_all_players(self):
        return self.query("SELECT * FROM players")

    def delete_player(self, puuid):
        self.execute_query("DELETE FROM players WHERE puuid = %s", (puuid,))

    # traits table operations
    def add_traits(self, traits):
        sql = """
            INSERT INTO traits (match_id, puuid, trait_name, num_units, style, tier_current, tier_total) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT unique_trait DO NOTHING
            """

        params = (
            traits['match_id'],
            traits['puuid'],
            traits['trait_name'],
            traits['num_units'],
            traits['style'],
            traits['tier_current'],
            traits['tier_total']
        )

        try:
            self.execute_query(sql, params)
            print("Trait added successfully")
        except Exception as e:
            print(f'Error while adding trait info: {e}')

    def get_traits(self, puuid):
        return self.query("SELECT * FROM traits WHERE puuid = %s", (puuid,))

    def get_all_traits(self):
        return self.query("SELECT * FROM traits")

    def delete_traits(self, puuid):
        self.execute_query("DELETE FROM traits WHERE puuid = %s", (puuid,))

    # units table operations
    def add_unit(self, unit):
        sql = """
        INSERT INTO units (match_id, puuid, character_id, rarity, tier)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT unique_unit DO NOTHING
        """
        params = (
            unit["match_id"],
            unit["puuid"],
            unit["character_id"],
            unit["rarity"],
            unit["tier"],
        )
        try:
            self.execute_query(sql, params)
            print("Unit added successfully")
        except Exception as e:
            print(f'Error while adding unit: {e}')

    def get_units(self, puuid):
        return self.query("SELECT * FROM units WHERE puuid = %s", (puuid,))

    def get_all_units(self):
        return self.query("SELECT * FROM units")

    def delete_units(self, puuid):
        self.execute_query("DELETE FROM units WHERE puuid = %s", (puuid,))

    # items table operations
    def add_item(self, item):
        sql = """
        INSERT INTO items (match_id, puuid, character_id, item_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT unique_item DO NOTHING
        """
        params = (
            item["match_id"],
            item["puuid"],
            item["character_id"],
            item["item_id"],
        )
        try:
            self.execute_query(sql, params)
            print("Item added successfully")
        except Exception as e:
            print(f'Error while adding item: {e}')

    def get_items(self, puuid):
        return self.query("SELECT * FROM items WHERE puuid = %s", (puuid,))

    def get_all_items(self):
        return self.query("SELECT * FROM items")

    def delete_items(self, puuid):
        self.execute_query("DELETE FROM items WHERE puuid = %s", (puuid,))

    # bulk insert - czyli to co używamy podczas pobierania danych z api bo jest dużo szybciej
    def execute_bulk(self, sql, values):
        self.ensure_connection()
        with self.conn.cursor() as cursor:
            cursor.executemany(sql, values)
        self.conn.commit()

    def add_matches_bulk(self, matches_list):
        """Bulk insert matches"""
        if not matches_list:
            return

        sql = """
        INSERT INTO matches (match_id, game_datetime, game_length, map_id, tft_set_number) 
        VALUES (%s, %s, %s, %s, %s) ON CONFLICT (match_id) DO NOTHING
        """

        values = [
            (
                match['match_id'],
                match['game_datetime'],
                match['game_length'],
                match['mapId'],
                match['tft_set_number']
            )
            for match in matches_list
        ]

        try:
            self.execute_bulk(sql, values)
            print(f"Successfully inserted {len(values)} matches in bulk.")
        except Exception as e:
            print(f'Error during bulk insert of matches: {e}')
            self.conn.rollback()
            raise e

    def add_players_bulk(self, players_list):
        """Bulk insert players"""
        if not players_list:
            return

        sql = """
        INSERT INTO players(puuid, match_id, placement, level, gold_left, last_round,
            players_eliminated, time_eliminated, total_damage, companion_id, tier, division, leaguePoints, wins, losses) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT (puuid, match_id) DO NOTHING
        """

        values = [
            (
                player['puuid'],
                player['match_id'],
                player['placement'],
                player['level'],
                player['gold_left'],
                player['last_round'],
                player['players_eliminated'],
                player['time_eliminated'],
                player['total_damage'],
                player['companion_id'],
                player['tier'],
                player['division'],
                player['leaguePoints'],
                player['wins'],
                player['losses']
            )
            for player in players_list
        ]

        try:
            self.execute_bulk(sql, values)
            print(f"Successfully inserted {len(values)} players in bulk.")
        except Exception as e:
            print(f'Error during bulk insert of players: {e}')
            self.conn.rollback()
            raise e

    def add_traits_bulk(self, traits_list):
        sql = """
        INSERT INTO traits (match_id, puuid, trait_name, num_units, style, tier_current, tier_total)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (match_id, puuid, trait_name) DO NOTHING
        """

        values = [
            (
                trait['match_id'],
                trait['puuid'],
                trait['trait_name'],
                trait['num_units'],
                trait['style'],
                trait['tier_current'],
                trait['tier_total']
            )
            for trait in traits_list
        ]

        try:
            self.execute_bulk(sql, values)
            print(f"Successfully inserted {len(values)} traits in bulk.")
        except Exception as e:
            print(f'Error during bulk insert of traits: {e}')
            self.conn.rollback()

    def add_units_bulk(self, units_list):
        """Bulk insert units"""
        if not units_list:
            return

        sql = """
        INSERT INTO units (match_id, puuid, character_id, rarity, tier)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT unique_unit DO NOTHING
        """

        values = [
            (
                unit['match_id'],
                unit['puuid'],
                unit['character_id'],
                unit['rarity'],
                unit['tier']
            )
            for unit in units_list
        ]

        try:
            self.execute_bulk(sql, values)
            print(f"Successfully inserted {len(values)} units in bulk.")
        except Exception as e:
            print(f'Error during bulk insert of units: {e}')
            self.conn.rollback()
            raise e

    def add_items_bulk(self, items_list):
        """Bulk insert items"""
        if not items_list:
            return

        sql = """
        INSERT INTO items (match_id, puuid, character_id, item_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT unique_item DO NOTHING
        """

        values = [
            (
                item['match_id'],
                item['puuid'],
                item['character_id'],
                item['item_id']
            )
            for item in items_list
        ]

        try:
            self.execute_bulk(sql, values)
            print(f"Successfully inserted {len(values)} items in bulk.")
        except Exception as e:
            print(f'Error during bulk insert of items: {e}')
            self.conn.rollback()
            raise e

    #
