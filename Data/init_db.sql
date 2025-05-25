CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR(100) PRIMARY KEY,
    game_datetime BIGINT,
    game_length DOUBLE PRECISION,
    map_id INT,
    tft_set_number INT
);

CREATE TABLE IF NOT EXISTS players (
    puuid VARCHAR(100) NOT NULL,
    match_id VARCHAR(100) NOT NULL,
    placement INT,
    level INT,
    gold_left INT,
    last_round INT,
    players_eliminated INT,
    time_eliminated DOUBLE PRECISION,
    total_damage INT,
    companion_id VARCHAR(100),
    PRIMARY KEY (puuid, match_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS traits (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL,
    puuid VARCHAR(100) NOT NULL,
    trait_name VARCHAR(100) NOT NULL,
    num_units INT,
    style INT,
    tier_current INT,
    tier_total INT,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (puuid, match_id) REFERENCES players(puuid, match_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS units (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL,
    puuid VARCHAR(100) NOT NULL,
    character_id VARCHAR(100) NOT NULL,
    rarity INT,
    tier INT,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (puuid, match_id) REFERENCES players(puuid, match_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(100) NOT NULL,
    puuid VARCHAR(100) NOT NULL,
    character_id VARCHAR(100) NOT NULL,
    item_id VARCHAR(100) NOT NULL,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (puuid, match_id) REFERENCES players(puuid, match_id) ON DELETE CASCADE
);

ALTER TABLE players
ADD COLUMN tier VARCHAR(50),
ADD COLUMN division VARCHAR(10);

ALTER TABLE players
ADD COLUMN leaguePoints INT,
ADD COLUMN wins INT,
ADD COLUMN losses INT;

-- adding constraint because we need to have unique values in those columns too - this is necessary for data accuracy
-- if we are constantly retrieving data from the api, but in our case where we want to just store data,
-- that we once get and then use it for the analysis it's not crucial.
-- we have only 1gb storage and those indexes contains a lot of memory
ALTER TABLE traits ADD CONSTRAINT unique_trait UNIQUE (match_id, puuid, trait_name);
ALTER TABLE units ADD CONSTRAINT unique_unit UNIQUE (match_id, puuid, character_id);
ALTER TABLE items ADD CONSTRAINT unique_item UNIQUE (match_id, puuid, character_id, item_id);














