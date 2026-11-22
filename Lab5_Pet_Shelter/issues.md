# Lab 5 – Issue Table (pet_shelter.py)

**SRN:** PES1UG24CS321  
Line numbers refer to the original file (see `reports/before/`).

| # | Issue | Type | Tool / Code | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|---------|-------------|--------------|
| 1 | SQL injection | Security (Medium) | Bandit B608 | 10 | `INSERT` built with `%` string formatting, so a name like `x'); DROP TABLE pets;--` is executed as SQL. A name containing `'` also crashes the insert. | Use a parameterised query (`VALUES (?, ?, ?, 0)`) and pass the values as a tuple. |
| 2 | Mutable default argument | Bug | Pylint W0102 | 9 | `tags=[]` is created once and shared by every call, so tags pile up across unrelated pets. | Default to `None` and create a new list inside the function. |
| 3 | Bare `except` hiding errors | Bug | Pylint W0702, Flake8 E722 | 27–30 | `oldestAvailable` catches *everything* (even `KeyboardInterrupt`) just to handle "no rows"; real DB errors are hidden too. | Check `if row is None: return None` explicitly; no try/except needed. |
| 4 | Try / except / pass | Security / Bug (Low) | Bandit B110, Pylint W0718 | 34–37 | `clearUnadopted` catches broad `Exception` and silently ignores it, so a failed delete goes unnoticed. | Catch only `sqlite3.Error` and report the error. |
| 5 | Weak random for codes | Security (Low) | Bandit B311 | 22 | `random.randint` is predictable; adoption codes could be guessed. | Use `secrets.randbelow(9000) + 1000`. |
| 6 | Global mutable state | Bug / Design | Pylint W0603 | 15–18 | `adoption_count` is a global incremented even when the pet id does not exist or the pet was already adopted, so the count can be wrong. | Removed the global; `adoption_count()` now counts adopted rows in the DB, and `adopt()` only updates available pets and returns `True/False`. |
| 7 | Changes never committed | Bug | (manual review) | 10, 17, 35 | Writes were never `commit()`ed, so they would be lost on a file-backed DB. | Call `conn.commit()` after every write. |
| 8 | Code runs on import | Design | (manual review) | 54 | `main()` ran at import time, so importing the module ran the demo. | Wrapped in `if __name__ == "__main__":`. |
| 9 | Non-snake_case names | Style | Pylint C0103 | 9, 21, 25, 33, 40 | `registerPet`, `adoptionCode`, `oldestAvailable`, `clearUnadopted`, `shelterStatus`. | Renamed to `register_pet`, `adoption_code`, `oldest_available`, `clear_unadopted`, `shelter_status`. |
| 10 | Missing docstrings | Style | Pylint C0114 / C0116 | 1, all functions | No module or function docstrings. | Added a docstring to the module and each function. |
| 11 | Lines too long | Style | Flake8 E501, Pylint C0301 | 5, 10, 27 | Lines of 103–116 characters. | Split SQL strings over several lines (≤ 79 chars). |
| 12 | Multiple statements on one line | Style | Flake8 E701, Pylint C0321 | 41 | `if adoption_count > 0: return "active"`. | Put the `return` on its own line. |
| 13 | Old-style `%` formatting | Style | Pylint C0209 | 10 | `%` formatting used to build SQL. | Removed entirely by fix #1. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 3.95 / 10 (23 messages) | **10.00 / 10** |
| Bandit | 3 issues (1 Medium, 2 Low) | **0 issues** |
| Flake8 | 5 issues | **0 issues** |

Program output is unchanged: `Kiwi PET-xxxx active`.
