-- ============================================================
-- schema.sql — Extended PhoneBook Schema (TSIS 1)
-- Creates three tables: groups, contacts, phones.
-- All statements use IF NOT EXISTS / ON CONFLICT so this file
-- can be re-run safely without losing existing data.
-- ============================================================


-- TABLE 1: groups / categories
-- Each contact can belong to one group (Family, Work, Friend, Other).
-- SERIAL = auto-incrementing integer primary key.
-- UNIQUE on name prevents duplicate group names.
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,        -- auto-generated unique ID for each group
    name VARCHAR(50) UNIQUE NOT NULL -- group name; must be unique and non-empty
);

-- Seed four default groups so the app works without manual setup.
-- ON CONFLICT (name) DO NOTHING = skip silently if the group already exists.
INSERT INTO groups (name) VALUES
    ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;


-- TABLE 2: contacts — the main entity of the phonebook.
-- Replaces the old single-table "phonebook" from Practice 7/8.
-- group_id is a foreign key: links each contact to one row in the groups table.
-- ON DELETE SET NULL = if the group is deleted, the contact keeps its data but loses its group.
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,                              -- auto-generated contact ID
    name       VARCHAR(100) NOT NULL,                           -- full name, required
    email      VARCHAR(100),                                    -- optional email address
    birthday   DATE,                                            -- optional date of birth (YYYY-MM-DD)
    group_id   INTEGER REFERENCES groups(id) ON DELETE SET NULL, -- FK → groups; nullable
    created_at TIMESTAMP DEFAULT NOW()                          -- automatically set to current time on insert
);


-- TABLE 3: phones — one-to-many relationship with contacts.
-- One contact can have multiple phone numbers (home, work, mobile).
-- contact_id is a foreign key: links each phone to exactly one contact.
-- ON DELETE CASCADE = if the contact is deleted, all its phones are deleted too.
-- CHECK constraint enforces only valid phone types.
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,                              -- auto-generated phone record ID
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE, -- FK → contacts; required
    phone      VARCHAR(20)  NOT NULL,                           -- the phone number string
    type       VARCHAR(10)  CHECK (type IN ('home', 'work', 'mobile')) -- allowed values only
);