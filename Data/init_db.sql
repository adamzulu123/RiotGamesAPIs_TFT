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














