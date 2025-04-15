import psycopg2
import os
from dotenv import load_dotenv


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

        self.cursor = self.conn.cursor()  # to obiekt pozwalajacy na odbieranie i wysyłanie zapytan do bazy
        # taki tunel do komunikacji z baza

    def fetch_all(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()














    #