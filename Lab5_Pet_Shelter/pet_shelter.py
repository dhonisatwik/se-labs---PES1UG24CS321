"""Animal shelter adoption register backed by an in-memory SQLite DB."""
import secrets
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE pets (id INTEGER PRIMARY KEY, name TEXT, species TEXT, "
    "age INTEGER, adopted INTEGER)"
)


def register_pet(name, species, age, tags=None):
    """Add a pet to the register and return the list of species tags."""
    if tags is None:
        tags = []
    conn.execute(
        "INSERT INTO pets (name, species, age, adopted) "
        "VALUES (?, ?, ?, 0)",
        (name, species, age),
    )
    conn.commit()
    tags.append(species)
    return tags


def adopt(pet_id):
    """Mark a pet as adopted. Return True if an available pet was updated."""
    cursor = conn.execute(
        "UPDATE pets SET adopted = 1 WHERE id = ? AND adopted = 0",
        (pet_id,),
    )
    conn.commit()
    return cursor.rowcount == 1


def adoption_count():
    """Return how many pets have been adopted."""
    row = conn.execute(
        "SELECT COUNT(*) FROM pets WHERE adopted = 1").fetchone()
    return row[0]


def adoption_code():
    """Return a random, hard-to-guess adoption code such as PET-4821."""
    return "PET-" + str(secrets.randbelow(9000) + 1000)


def oldest_available():
    """Return the name of the oldest unadopted pet, or None if none left."""
    row = conn.execute(
        "SELECT name, age FROM pets WHERE adopted = 0 ORDER BY age DESC"
    ).fetchone()
    if row is None:
        return None
    return row[0]


def clear_unadopted():
    """Delete every pet that has not been adopted."""
    try:
        conn.execute("DELETE FROM pets WHERE adopted = 0")
        conn.commit()
    except sqlite3.Error as err:
        print("Could not clear unadopted pets:", err)


def shelter_status():
    """Return 'active' if any pet has been adopted, otherwise 'quiet'."""
    if adoption_count() > 0:
        return "active"
    return "quiet"


def main():
    """Run a short demonstration of the register."""
    register_pet("Bruno", "dog", 7)
    register_pet("Mitzi", "cat", 3)
    register_pet("Kiwi", "parrot", 12)
    adopt(1)
    print(oldest_available(), adoption_code(), shelter_status())
    clear_unadopted()


if __name__ == "__main__":
    main()
