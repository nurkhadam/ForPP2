-- ============================================================
-- procedures.sql — New DB-side logic for TSIS 1
-- Contains two stored procedures and one stored function.
-- All use CREATE OR REPLACE so they can be re-applied safely on every startup.
-- (Procedures from Practice 8 are NOT repeated here)
-- ============================================================


-- ──────────────────────────────────────────────────────────────
-- PROCEDURE 1: add_phone
-- Adds a new phone number to an existing contact.
-- Validates that the contact exists and that the phone type is valid.
-- Usage: CALL add_phone('Alice', '87001234567', 'mobile');
-- ──────────────────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,   -- the name of the contact to add the phone to
    p_phone        VARCHAR,   -- the phone number string to insert
    p_type         VARCHAR    -- phone type: must be 'home', 'work', or 'mobile'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id INTEGER;   -- will hold the contact's ID once found
BEGIN
    -- Look up the contact by name; LIMIT 1 in case of duplicate names
    SELECT id INTO v_id
    FROM contacts
    WHERE name = p_contact_name
    LIMIT 1;

    -- If no contact was found, v_id is NULL — raise an error to stop execution
    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    -- Validate the phone type against the allowed set
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Phone type must be home, work, or mobile (got "%")', p_type;
    END IF;

    -- Insert the new phone number linked to the found contact
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type);

    -- Log a success message visible in the DB console / psycopg2 notices
    RAISE NOTICE 'Phone % (%) added to contact "%"', p_phone, p_type, p_contact_name;
END;
$$;


-- ──────────────────────────────────────────────────────────────
-- PROCEDURE 2: move_to_group
-- Moves a contact to a group, creating the group first if it doesn't exist.
-- Usage: CALL move_to_group('Alice', 'VIP');
-- ──────────────────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,   -- the name of the contact to move
    p_group_name   VARCHAR    -- the target group name (new or existing)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;   -- will hold the contact's ID
    v_group_id   INTEGER;   -- will hold the group's ID
BEGIN
    -- Insert the group if it doesn't exist; ON CONFLICT DO NOTHING is safe to call always
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    -- Retrieve the group ID (whether it was just created or already existed)
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- Look up the contact by name
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name
    LIMIT 1;

    -- Stop with an error if the contact doesn't exist
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    -- Update the contact's group_id to point to the target group
    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%"', p_contact_name, p_group_name;
END;
$$;


-- ──────────────────────────────────────────────────────────────
-- FUNCTION 3: search_contacts
-- Full-text search across contact name, email, and ALL phone numbers.
-- Returns a result set (table), not a single value.
-- ILIKE = case-insensitive LIKE; % wildcards added around p_query in the WHERE clause.
-- STRING_AGG joins multiple phone numbers into one comma-separated string per contact.
-- Usage: SELECT * FROM search_contacts('gmail');
-- ──────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(                   -- defines the columns of the returned result set
    id       INT,
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR,            -- group name (aliased from groups.name)
    phones   TEXT                -- comma-separated list of all phone numbers for the contact
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name   AS grp,
        -- Concatenate all phones into one string: "87001234567 (mobile), 87009998877 (work)"
        STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ') AS phones
    FROM contacts c
    LEFT JOIN groups g  ON g.id = c.group_id      -- attach group name (NULL if no group)
    LEFT JOIN phones p  ON p.contact_id = c.id    -- attach all phones (NULL if no phones)
    WHERE
        c.name  ILIKE '%' || p_query || '%'        -- match anywhere in the name
        OR c.email ILIKE '%' || p_query || '%'     -- match anywhere in the email
        OR p.phone LIKE '%' || p_query || '%'      -- match anywhere in any phone number
    GROUP BY c.id, c.name, c.email, c.birthday, g.name   -- one row per contact
    ORDER BY c.name;             -- results sorted alphabetically by name
END;
$$;