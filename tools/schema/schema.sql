CREATE TABLE IF NOT EXISTS guilds (
    guild_id BIGINT UNIQUE NOT NULL,
    prefix VARCHAR(5)
);

CREATE SCHEMA IF NOT EXISTS voicemaster;

CREATE TABLE IF NOT EXISTS voicemaster.configuration (
    guild_id BIGINT UNIQUE NOT NULL,
    channel_id BIGINT UNIQUE NOT NULL,
    interface_id BIGINT UNIQUE NOT NULL,
    category_id BIGINT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS voicemaster.channels (
    guild_id BIGINT  NOT NULL,
    owner_id BIGINT NOT NULL,
    channel_id BIGINT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS forcenick (
    guild_id BIGINT PRIMARY KEY,
    user_id BIGINT,
    name TEXT
);

CREATE TABLE IF NOT EXISTS welcome (
    guild_id BIGINT,
    channel_id BIGINT,
    message TEXT,
    PRIMARY KEY (guild_id, channel_id)
);
