"""
Lab 7 - Fixed (hardened) version of student_grades.py
Name : Pendyala Dhoni Satwik
SRN  : PES1UG24CS321

Every function validates its input and returns None instead of crashing or
returning a wrong value. Bugs found by fuzzing (Hypothesis) and fixed:

average_marks
  - None / non-string input          -> AttributeError on .split          (fixed: type check)
  - ""  ,  "78,,92"  ,  "78,"         -> ValueError: int('')               (fixed: reject empty elements)
  - "abc", "7.5", "²"                 -> ValueError from int()             (fixed: try/except)
  - "-5,200"                          -> silently averaged impossible marks (fixed: 0..100 range check)
parse_srn
  - None / non-string input          -> TypeError on slicing              (fixed: type check)
  - short or empty strings ("", "PES1") -> ValueError: int('')            (fixed: full-format regex)
  - "xxxxxx12yy"                      -> returned garbage ('xxxx', 12, 'yy') without error (fixed: regex)
  - "PES1UG2３CS123" (Unicode digit)  -> int() accepted non-ASCII digits   (fixed: ASCII-only [0-9])
short_name
  - None / non-string input          -> AttributeError on .split          (fixed: type check)
  - "", "ravi", "a b c"               -> ValueError: wrong number of values to unpack (fixed: exactly 2 words)
  - "1 2", "@ #"                      -> produced "1. 2"                   (fixed: words must contain letters only)
"""
import re

_SRN_PATTERN = re.compile(r"(PES[12])UG([0-9]{2})([A-Z]{2})[0-9]{3}")
_NAME_WORD = re.compile(r"[^\W\d_]+(?:['-][^\W\d_]+)*")   # letters, optionally joined by ' or -


def average_marks(marks_csv):
    """Average of comma-separated integer marks (each 0-100), rounded to 2 dp; None if invalid."""
    if not isinstance(marks_csv, str):
        return None
    parts = [p.strip() for p in marks_csv.split(",")]
    if not parts or any(p == "" for p in parts):
        return None
    marks = []
    for p in parts:
        if not p.isascii():                 # reject Unicode digits / symbols that int() might accept
            return None
        try:
            m = int(p)
        except ValueError:
            return None
        if m < 0 or m > 100:
            return None
        marks.append(m)
    return round(sum(marks) / len(marks), 2)


def parse_srn(srn):
    """('PES1', year, 'CS') for an SRN like PES1UG23CS123; None if the SRN is malformed."""
    if not isinstance(srn, str):
        return None
    srn = srn.strip()
    if not srn.isascii():                   # e.g. full-width digits or ligatures that .upper() would expand
        return None
    match = _SRN_PATTERN.fullmatch(srn.upper())
    if match is None:
        return None
    campus, year, dept = match.groups()
    return campus, int(year), dept


def short_name(full_name):
    """'R. Kumar' for 'ravi kumar'; None unless the input is exactly two alphabetic words."""
    if not isinstance(full_name, str):
        return None
    parts = full_name.split()
    if len(parts) != 2:
        return None
    first, last = parts
    if not (_NAME_WORD.fullmatch(first) and _NAME_WORD.fullmatch(last)):
        return None
    return first[0].upper() + ". " + last.capitalize()


def _ask(prompt):
    try:
        return input(prompt)
    except EOFError:
        return None


def main():
    print("==== Running average_marks ====")
    user_input = _ask("Enter marks as CSV (e.g. 78,85,92): ")
    result = average_marks(user_input)
    if result is None:
        print("Invalid input: enter whole-number marks between 0 and 100, separated by commas.")
    else:
        print("Average Marks:", result)

    print("\n==== Running parse_srn ====")
    user_input = _ask("Enter an SRN (e.g. PES1UG23CS123): ")
    result = parse_srn(user_input)
    if result is None:
        print("Invalid SRN: expected the format PES1UG23CS123.")
    else:
        print("Campus, Year and Dept:", result)

    print("\n==== Running short_name ====")
    user_input = _ask("Enter first and last name (e.g. ravi kumar): ")
    result = short_name(user_input)
    if result is None:
        print("Invalid name: enter exactly a first name and a last name.")
    else:
        print("Short Name:", result)


if __name__ == "__main__":
    main()
