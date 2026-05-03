"""
phonebook.py — TSIS 1  Extended Contact Management
===================================================
Builds on top of Practice 7 & 8 (CRUD, CSV import, pattern-search function,
upsert / bulk-insert procedures, pagination function).
Nothing from Practice 7/8 is re-implemented here.

New features
------------
3.1  Extended schema  — phones table, groups table, email, birthday
3.2  Console search   — filter by group, search by email, sort, paged navigation
3.3  Import / Export  — JSON export, JSON import with duplicate handling,
                        extended CSV import (email, birthday, group, phone type)
3.4  New procedures   — add_phone, move_to_group, search_contacts (via SQL files)
"""

# --- Standard library imports ---
import csv                          # for reading CSV files row by row
import json                         # for reading and writing JSON files
import os                           # for file path operations
from datetime import date, datetime # date — stores dates, datetime — parses strings into dates
from connect import get_connection  # our custom DB connection helper from connect.py


# ─────────────────────────────────────────────────────────────
# HELPERS  — small utility functions used by many other functions
# ─────────────────────────────────────────────────────────────

def _run_sql_file(path: str):
    """
    Opens a .sql file and executes its entire content as one statement.
    Used to apply schema.sql and procedures.sql on startup.
    """
    with open(path, "r") as f:
        sql = f.read()          # read the whole SQL text into a string
    conn = get_connection()     # open a new DB connection
    cur = conn.cursor()         # create a cursor to send SQL commands
    cur.execute(sql)            # execute the full SQL script
    conn.commit()               # save changes to the database
    cur.close()                 # close the cursor
    conn.close()                # close the connection


def _print_contacts(rows, headers=("ID", "Name", "Email", "Birthday", "Group", "Phones")):
    """
    Pretty-prints a list of contact tuples as an aligned table.
    Automatically adjusts column widths based on the longest value in each column.
    """
    if not rows:
        print("  (no contacts found)")
        return

    # Calculate the max width needed for each column
    col_w = [max(len(str(h)), max(len(str(r[i])) if r[i] else 0 for r in rows))
             for i, h in enumerate(headers)]

    sep = "─" * (sum(col_w) + 3 * len(headers) + 1)  # horizontal separator line
    fmt = " | ".join(f"{{:<{w}}}" for w in col_w)     # format string with left-aligned columns

    print(sep)
    print(fmt.format(*headers))   # print the header row
    print(sep)
    for row in rows:
        # Replace None values with empty string so the table prints cleanly
        display = tuple(str(v) if v is not None else "" for v in row)
        print(fmt.format(*display))
    print(sep)
    print(f"  {len(rows)} contact(s)")


def _date_input(prompt: str):
    """
    Asks the user to enter a date in YYYY-MM-DD format.
    Keeps asking until a valid date is entered, or Enter is pressed to skip.
    Returns a date object or None.
    """
    while True:
        raw = input(prompt + " (YYYY-MM-DD, or Enter to skip): ").strip()
        if not raw:
            return None         # user pressed Enter — no date provided
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()   # parse string → date
        except ValueError:
            print("  Invalid date. Try again.")


def _choose_group(cur) -> int | None:
    """
    Fetches all groups from DB, displays them, and returns the chosen group ID.
    Returns None if the user skips or the input is unrecognized.
    """
    cur.execute("SELECT id, name FROM groups ORDER BY id")  # get all groups sorted by ID
    groups = cur.fetchall()
    if not groups:
        return None             # no groups exist yet
    print("  Groups:")
    for g in groups:
        print(f"    {g[0]}. {g[1]}")   # show group ID and name
    choice = input("  Enter group number (or Enter to skip): ").strip()
    if not choice:
        return None             # user skipped
    for g in groups:
        if str(g[0]) == choice:
            return g[0]         # return the matching group ID
    print("  Unknown group — skipping")
    return None


# ─────────────────────────────────────────────────────────────
# 3.1  SCHEMA INITIALISATION
# ─────────────────────────────────────────────────────────────

def init_schema():
    """
    Runs schema.sql to create the groups, contacts, and phones tables.
    Uses IF NOT EXISTS and ON CONFLICT, so it is safe to call multiple times
    without duplicating data or causing errors.
    """
    # Get the folder where this Python file lives
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(script_dir, "schema.sql")   # full path to schema.sql

    if not os.path.exists(schema_path):
        print(f"  schema.sql not found at {schema_path}")
        return

    _run_sql_file(schema_path)  # execute the SQL file
    print("  Schema ready.")


def init_procedures():
    """
    Runs procedures.sql to create or replace stored procedures and functions:
    add_phone, move_to_group, search_contacts.
    CREATE OR REPLACE makes this safe to call on every startup.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    proc_path = os.path.join(script_dir, "procedures.sql")  # full path to procedures.sql

    if not os.path.exists(proc_path):
        print(f"  procedures.sql not found at {proc_path}")
        return

    _run_sql_file(proc_path)    # execute the SQL file
    print("  Procedures ready.")


# ─────────────────────────────────────────────────────────────
# 3.2  ADVANCED CONSOLE SEARCH & FILTER
# ─────────────────────────────────────────────────────────────

def _fetch_contacts(conn, order_by="name"):
    """
    Fetches all contacts from the DB with their group name and phone numbers.
    Uses LEFT JOIN so contacts without a group or phone still appear.
    STRING_AGG concatenates multiple phone numbers into one comma-separated string.
    order_by: 'name' | 'birthday' | 'created_at'
    """
    # Whitelist allowed columns to prevent SQL injection via f-string
    allowed = {"name", "birthday", "created_at"}
    if order_by not in allowed:
        order_by = "name"       # fall back to name if invalid input

    cur = conn.cursor()
    cur.execute(f"""
        SELECT c.id, c.name, c.email, c.birthday,
               g.name AS grp,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id   -- attach group name to each contact
        LEFT JOIN phones p ON p.contact_id = c.id  -- attach all phones to each contact
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
        ORDER BY c.{order_by} NULLS LAST           -- chosen sort column, NULLs go last
    """)
    rows = cur.fetchall()   # retrieve all result rows
    cur.close()
    return rows


def filter_by_group():
    """
    Displays contacts that belong to a specific group chosen by the user.
    Fetches available groups first, then filters contacts by the chosen group_id.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM groups ORDER BY id")  # load all groups
    groups = cur.fetchall()
    cur.close()

    if not groups:
        print("  No groups found.")
        conn.close()
        return

    print("\n  Available groups:")
    for g in groups:
        print(f"    {g[0]}. {g[1]}")
    choice = input("  Select group number: ").strip()

    # Match the user's input to a group ID
    group_id = None
    for g in groups:
        if str(g[0]) == choice:
            group_id = g[0]
            break

    if group_id is None:
        print("  Invalid choice.")
        conn.close()
        return

    # Query contacts that belong to the selected group
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday,
               g.name AS grp,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE c.group_id = %s          -- filter by the chosen group
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY c.name
    """, (group_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    _print_contacts(rows)   # display results in a formatted table


def search_by_email():
    """
    Searches contacts by a partial email match using ILIKE (case-insensitive LIKE).
    The % wildcards allow matching any characters before and after the fragment.
    """
    pattern = input("  Enter email fragment: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday,
               g.name AS grp,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE c.email ILIKE %s          -- case-insensitive partial match on email
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY c.name
    """, (f"%{pattern}%",))             # wrap pattern with wildcards
    rows = cur.fetchall()
    cur.close()
    conn.close()
    _print_contacts(rows)


def sort_and_show():
    """
    Fetches all contacts and displays them sorted by the user's chosen column.
    Delegates actual DB query to _fetch_contacts() which handles the ORDER BY clause.
    """
    print("  Sort by: 1-name  2-birthday  3-date added")
    choice = input("  Choose: ").strip()
    # Map menu numbers to actual DB column names
    order_map = {"1": "name", "2": "birthday", "3": "created_at"}
    order_by = order_map.get(choice, "name")    # default to name if invalid
    conn = get_connection()
    rows = _fetch_contacts(conn, order_by)
    conn.close()
    _print_contacts(rows)


def paginated_navigation():
    """
    Displays contacts page by page using LIMIT and OFFSET.
    LIMIT controls how many rows per page; OFFSET skips rows already shown.
    User navigates with [n]ext, [p]rev, [q]uit.
    """
    limit = 5   # default number of contacts per page
    try:
        limit = int(input("  Contacts per page [5]: ").strip() or "5")
    except ValueError:
        pass    # keep default if user enters non-numeric input

    # Count total contacts to calculate how many pages exist
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM contacts")
    total = cur.fetchone()[0]   # single integer: total number of contacts
    cur.close()
    conn.close()

    if total == 0:
        print("  Phonebook is empty.")
        return

    # Ceiling division: rounds up to include the last partial page
    total_pages = (total + limit - 1) // limit
    page = 0    # current page index (0-based)

    while True:
        offset = page * limit   # calculate how many rows to skip
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday,
                   g.name AS grp,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
            ORDER BY c.name
            LIMIT %s OFFSET %s          -- LIMIT = page size, OFFSET = rows to skip
        """, (limit, offset))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        print(f"\n  Page {page + 1} / {total_pages}")
        _print_contacts(rows)
        print("  [n]ext  [p]rev  [q]uit")
        cmd = input("  > ").strip().lower()

        if cmd == "n":
            if page < total_pages - 1:
                page += 1           # move to next page
            else:
                print("  Already on last page.")
        elif cmd == "p":
            if page > 0:
                page -= 1           # move to previous page
            else:
                print("  Already on first page.")
        elif cmd == "q":
            break                   # exit paged navigation


# ─────────────────────────────────────────────────────────────
# 3.3  IMPORT / EXPORT
# ─────────────────────────────────────────────────────────────

def _json_default(obj):
    """
    Custom JSON serializer for types that json.dump() cannot handle by default.
    Converts date and datetime objects to ISO 8601 strings (e.g. '1990-05-14').
    Raises TypeError for any other unsupported type.
    """
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()  # convert date → string like "1990-05-14"
    raise TypeError(f"Type {type(obj)} not JSON-serialisable")


def export_to_json():
    """
    Exports all contacts (with their phones and group) to contacts_export.json.
    For each contact, a separate query fetches its phone list to build a nested structure.
    The output file is saved in the current working directory.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Fetch all contacts with their group name
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name AS grp
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY c.id
    """)
    contacts_raw = cur.fetchall()

    result = []     # will hold the final list of contact dictionaries
    for cid, name, email, birthday, grp in contacts_raw:
        # For each contact, fetch all its phone numbers
        cur.execute("""
            SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id
        """, (cid,))
        # Build a list of {phone, type} dicts for this contact
        phones = [{"phone": r[0], "type": r[1]} for r in cur.fetchall()]

        # Append a full contact record to the result list
        result.append({
            "id": cid,
            "name": name,
            "email": email,
            "birthday": birthday,   # _json_default will convert this to a string
            "group": grp,
            "phones": phones,
        })

    cur.close()
    conn.close()

    out_path = "contacts_export.json"
    with open(out_path, "w", encoding="utf-8") as f:
        # indent=2 makes the JSON human-readable; default= handles date conversion
        json.dump(result, f, ensure_ascii=False, indent=2, default=_json_default)

    print(f"  Exported {len(result)} contacts to '{out_path}'")


def import_from_json():
    """
    Reads contacts from a JSON file and inserts them into the database.
    If a contact with the same name already exists, the user is asked
    whether to overwrite (update fields + replace phones) or skip.
    """
    path = input("  Path to JSON file: ").strip()
    if not os.path.exists(path):
        print(f"  File not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)     # parse JSON file into a Python list of dicts

    conn = get_connection()
    cur = conn.cursor()
    added = skipped = overwritten = 0   # counters for the summary message

    for item in data:
        # Extract fields from each JSON object (use .get() to avoid KeyError)
        name     = item.get("name", "").strip()
        email    = item.get("email")
        birthday = item.get("birthday")     # comes in as a string or None
        grp_name = item.get("group")
        phones   = item.get("phones", [])   # list of {phone, type} dicts

        if not name:
            continue    # skip records with no name

        # Convert birthday string to a Python date object
        if birthday:
            try:
                birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
            except ValueError:
                birthday = None     # ignore invalid date formats

        # Resolve group: insert if missing, then fetch its ID
        group_id = None
        if grp_name:
            # ON CONFLICT DO NOTHING prevents error if group already exists
            cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (grp_name,))
            cur.execute("SELECT id FROM groups WHERE name = %s", (grp_name,))
            row = cur.fetchone()
            if row:
                group_id = row[0]

        # Check if a contact with this name already exists in the DB
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            # Duplicate found — ask user what to do
            answer = input(f"  Contact '{name}' already exists. Overwrite? [y/N]: ").strip().lower()
            if answer != "y":
                skipped += 1
                continue    # keep the existing record unchanged

            # Overwrite: update contact fields and replace all phones
            cur.execute("""
                UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s
            """, (email, birthday, group_id, existing[0]))
            cur.execute("DELETE FROM phones WHERE contact_id = %s", (existing[0],))  # remove old phones
            contact_id = existing[0]
            overwritten += 1
        else:
            # New contact — insert and retrieve the generated ID
            cur.execute("""
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (name, email, birthday, group_id))
            contact_id = cur.fetchone()[0]
            added += 1

        # Insert all phone numbers for this contact
        for ph in phones:
            phone_val  = ph.get("phone", "").strip()
            phone_type = ph.get("type", "mobile")   # default type if missing
            if phone_val:
                cur.execute("""
                    INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)
                """, (contact_id, phone_val, phone_type))

    conn.commit()   # save all changes at once
    cur.close()
    conn.close()
    print(f"  Import done: {added} added, {overwritten} overwritten, {skipped} skipped.")


def _import_csv_from_path(path: str):
    """
    Internal CSV importer — handles extended fields: email, birthday, group, phone type.
    Called both automatically on startup (contacts.csv) and from the menu (option 2).

    Expected CSV columns (header row required):
        name, phone, type, email, birthday, group
    Missing columns default to empty / None.
    Duplicate (name + phone) combinations are silently skipped.
    """
    if not os.path.exists(path):
        print(f"  File not found: {path}")
        return

    conn = get_connection()
    cur = conn.cursor()
    added = skipped = 0    # counters for the summary

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)  # reads each row as a dict keyed by column headers
        for row in reader:
            # Extract each field; use defaults if the column is missing
            name     = row.get("name", "").strip()
            phone    = row.get("phone", "").strip()
            ptype    = row.get("type", "mobile").strip() or "mobile"
            email    = row.get("email", "").strip() or None     # empty string → None
            birthday_str = row.get("birthday", "").strip()
            grp_name = row.get("group", "").strip() or None

            if not name or not phone:
                continue    # skip rows that are missing required fields

            # Convert birthday string to a Python date object
            birthday = None
            if birthday_str:
                try:
                    birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
                except ValueError:
                    pass    # leave birthday as None if format is invalid

            # Resolve group: create it if it doesn't exist, then get its ID
            group_id = None
            if grp_name:
                # ON CONFLICT DO NOTHING safely handles existing groups
                cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (grp_name,))
                cur.execute("SELECT id FROM groups WHERE name = %s", (grp_name,))
                r = cur.fetchone()
                if r:
                    group_id = r[0]

            # Upsert contact: update if name exists, insert if new
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()
            if existing:
                contact_id = existing[0]
                # Update optional fields only if a new value is provided
                # COALESCE keeps the old DB value when the new value is NULL
                cur.execute("""
                    UPDATE contacts
                    SET email    = COALESCE(%s, email),
                        birthday = COALESCE(%s, birthday),
                        group_id = COALESCE(%s, group_id)
                    WHERE id = %s
                """, (email, birthday, group_id, contact_id))
            else:
                # Insert brand-new contact and get its auto-generated ID
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """, (name, email, birthday, group_id))
                contact_id = cur.fetchone()[0]

            # Skip if this exact phone number already exists for this contact
            cur.execute("""
                SELECT 1 FROM phones WHERE contact_id = %s AND phone = %s
            """, (contact_id, phone))
            if cur.fetchone():
                skipped += 1
                continue    # duplicate phone — do not insert again

            # Validate phone type; fall back to 'mobile' if value is unexpected
            if ptype not in ("home", "work", "mobile"):
                ptype = "mobile"

            # Insert the phone number linked to the contact
            cur.execute("""
                INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)
            """, (contact_id, phone, ptype))
            added += 1

    conn.commit()   # commit all inserts/updates in one transaction
    cur.close()
    conn.close()
    print(f"  CSV import done: {added} phones added, {skipped} duplicates skipped.")


def import_csv_extended():
    """Menu option 2 — asks the user for a CSV file path, then delegates to _import_csv_from_path."""
    path = input("  CSV file path: ").strip()
    _import_csv_from_path(path)


# ─────────────────────────────────────────────────────────────
# 3.4  WRAPPERS FOR NEW STORED PROCEDURES / FUNCTION
# ─────────────────────────────────────────────────────────────

def add_phone_to_contact():
    """
    Calls the add_phone stored procedure defined in procedures.sql.
    The procedure validates the contact name and phone type on the DB side,
    and raises an exception if the contact is not found or the type is invalid.
    """
    name  = input("  Contact name: ").strip()
    phone = input("  Phone number: ").strip()
    print("  Type: 1-mobile  2-home  3-work")
    t = input("  Choose: ").strip()
    ptype = {"1": "mobile", "2": "home", "3": "work"}.get(t, "mobile")  # map number → type string

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))  # call DB procedure
        conn.commit()
        print(f"  Phone added.")
    except Exception as e:
        conn.rollback()         # undo changes if the procedure raised an error
        print(f"  Error: {e}")
    finally:
        cur.close()
        conn.close()


def move_contact_to_group():
    """
    Calls the move_to_group stored procedure defined in procedures.sql.
    The procedure creates the group if it doesn't exist, then updates the contact's group_id.
    Raises an exception if the contact name is not found.
    """
    name  = input("  Contact name: ").strip()
    group = input("  Group name (new or existing): ").strip()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))    # call DB procedure
        conn.commit()
        print(f"  Contact '{name}' moved to group '{group}'.")
    except Exception as e:
        conn.rollback()         # undo changes on error
        print(f"  Error: {e}")
    finally:
        cur.close()
        conn.close()


def full_search():
    """
    Calls the search_contacts() SQL function defined in procedures.sql.
    Searches across name, email, AND all phone numbers using ILIKE (case-insensitive).
    Returns matching contacts with their concatenated phone list.
    """
    query = input("  Enter search query: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))  # call DB function
    rows = cur.fetchall()
    cur.close()
    conn.close()
    _print_contacts(rows)


# ─────────────────────────────────────────────────────────────
# ADD CONTACT  (full extended form)
# ─────────────────────────────────────────────────────────────

def add_contact_full():
    """
    Interactively collects all contact fields from the user and saves them.
    Inserts the contact record first (to get the ID), then inserts each phone.
    The loop continues until the user submits an empty phone to stop.
    """
    name     = input("  Name: ").strip()
    email    = input("  Email (Enter to skip): ").strip() or None   # empty → None
    birthday = _date_input("  Birthday")    # uses helper that validates date format

    conn = get_connection()
    cur = conn.cursor()
    group_id = _choose_group(cur)   # show group list and get chosen group ID

    # Insert the contact and retrieve its auto-generated ID
    cur.execute("""
        INSERT INTO contacts (name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s) RETURNING id
    """, (name, email, birthday, group_id))
    contact_id = cur.fetchone()[0]

    # Allow adding multiple phone numbers in a loop
    print("  Add phone numbers (enter blank phone to stop):")
    while True:
        phone = input("    Phone: ").strip()
        if not phone:
            break       # empty input ends the phone entry loop
        print("    Type: 1-mobile  2-home  3-work")
        t = input("    Choose: ").strip()
        ptype = {"1": "mobile", "2": "home", "3": "work"}.get(t, "mobile")
        cur.execute("""
            INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)
        """, (contact_id, phone, ptype))

    conn.commit()   # save contact + all phones together
    cur.close()
    conn.close()
    print(f"  Contact '{name}' added (ID {contact_id}).")


# ─────────────────────────────────────────────────────────────
# MENU
# ─────────────────────────────────────────────────────────────

def menu():
    """
    Main entry point of the application.
    Initialises the DB schema and procedures, auto-imports contacts.csv,
    then enters an infinite loop showing the menu until the user exits.
    """
    # Run schema and procedure setup on every startup (safe due to IF NOT EXISTS / CREATE OR REPLACE)
    init_schema()
    init_procedures()

    # ── AUTO-IMPORT contacts.csv ─────────────────────────────────
    # Build the path to contacts.csv sitting next to this script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    auto_csv = os.path.join(script_dir, "contacts.csv")
    if os.path.exists(auto_csv):
        print(f"  Auto-importing contacts.csv ...")
        _import_csv_from_path(auto_csv)     # duplicates are automatically skipped
    # ────────────────────────────────────────────────────────────

    while True:
        print("""
╔══════════════════════════════════════╗
║       PHONEBOOK  —  TSIS 1           ║
╠══════════════════════════════════════╣
║  ADD / IMPORT                        ║
║  1  Add contact (full form)          ║
║  2  Import from CSV (extended)       ║
║  3  Import from JSON                 ║
╠══════════════════════════════════════╣
║  SEARCH / FILTER                     ║
║  4  Filter by group                  ║
║  5  Search by email                  ║
║  6  Full search (name/email/phone)   ║
║  7  Sort & show all                  ║
║  8  Paginated navigation             ║
╠══════════════════════════════════════╣
║  PHONE / GROUP MANAGEMENT            ║
║  9  Add phone to existing contact    ║
║  10 Move contact to group            ║
╠══════════════════════════════════════╣
║  EXPORT                              ║
║  11 Export all contacts to JSON      ║
╠══════════════════════════════════════╣
║  0  Exit                             ║
╚══════════════════════════════════════╝""")

        choice = input("Choose: ").strip()

        # Map each menu number to the corresponding function
        actions = {
            "1":  add_contact_full,
            "2":  import_csv_extended,
            "3":  import_from_json,
            "4":  filter_by_group,
            "5":  search_by_email,
            "6":  full_search,
            "7":  sort_and_show,
            "8":  paginated_navigation,
            "9":  add_phone_to_contact,
            "10": move_contact_to_group,
            "11": export_to_json,
        }

        if choice == "0":
            print("Bye!")
            break                       # exit the menu loop
        elif choice in actions:
            try:
                actions[choice]()       # call the matching function
            except Exception as e:
                print(f"  Unexpected error: {e}")
        else:
            print("  Wrong choice.")    # input did not match any option


# Entry point — only runs when this file is executed directly (not imported)
if __name__ == "__main__":
    menu()