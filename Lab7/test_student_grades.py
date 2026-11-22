"""
Lab 7 - Fuzz testing student_grades.py with Hypothesis
Name : Pendyala Dhoni Satwik
SRN  : PES1UG24CS321

Run:  pytest test_student_grades.py      (or: python -m pytest test_student_grades.py)

Contract tested (what a robust implementation must do):
  * never raise, whatever it is given (any string, None, other types)
  * return None for invalid input
  * return the correct answer for valid input
"""
import re
from hypothesis import given, settings, strategies as st
from student_grades import average_marks, parse_srn, short_name

ANY_INPUT = st.text() | st.none() | st.integers() | st.floats() | st.lists(st.text())


# ----------------------------------------------------------------------------------
# 1. The three "no crash" fuzz tests from the starter file
# ----------------------------------------------------------------------------------
@given(st.text() | st.none())
def test_average_marks_no_crash(s):
    try:
        average_marks(s)
    except Exception as e:
        assert False, f"average_marks crashed on {s!r} with {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_parse_srn_no_crash(s):
    try:
        parse_srn(s)
    except Exception as e:
        assert False, f"parse_srn crashed on {s!r} with {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_short_name_no_crash(s):
    try:
        short_name(s)
    except Exception as e:
        assert False, f"short_name crashed on {s!r} with {type(e).__name__}: {e}"


# ----------------------------------------------------------------------------------
# 2. Wider fuzzing: non-string inputs must not crash either
# ----------------------------------------------------------------------------------
@given(ANY_INPUT)
def test_all_functions_survive_any_type(x):
    for fn in (average_marks, parse_srn, short_name):
        try:
            fn(x)
        except Exception as e:
            assert False, f"{fn.__name__} crashed on {x!r} with {type(e).__name__}: {e}"


# ----------------------------------------------------------------------------------
# 3. average_marks: correct on valid CSV, None on anything malformed
# ----------------------------------------------------------------------------------
valid_marks = st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=20)


@given(valid_marks, st.sampled_from([",", ", ", " , "]))
def test_average_marks_valid_csv(marks, sep):
    csv = sep.join(str(m) for m in marks)
    assert average_marks(csv) == round(sum(marks) / len(marks), 2)


@given(valid_marks, st.integers(min_value=0, max_value=20))
def test_average_marks_empty_element_rejected(marks, pos):
    parts = [str(m) for m in marks]
    parts.insert(pos % (len(parts) + 1), "")          # e.g. "78,,92" or ",78" or "78,"
    assert average_marks(",".join(parts)) is None


@given(st.integers().filter(lambda m: m < 0 or m > 100))
def test_average_marks_out_of_range_rejected(m):
    assert average_marks(f"50,{m}") is None


@given(st.text())
def test_average_marks_result_is_none_or_valid_number(s):
    r = average_marks(s)
    assert r is None or (isinstance(r, float) and 0 <= r <= 100)


# ----------------------------------------------------------------------------------
# 4. parse_srn: correct fields for well-formed SRNs, None otherwise
# ----------------------------------------------------------------------------------
valid_srn = st.builds(
    lambda campus, year, dept, num: f"PES{campus}UG{year:02d}{dept}{num:03d}",
    st.sampled_from([1, 2]),
    st.integers(min_value=0, max_value=99),
    st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=2, max_size=2),
    st.integers(min_value=0, max_value=999),
)


@given(valid_srn)
def test_parse_srn_valid(srn):
    assert parse_srn(srn) == (srn[:4], int(srn[6:8]), srn[8:10])


@given(valid_srn)
def test_parse_srn_accepts_lowercase_and_spaces(srn):
    assert parse_srn("  " + srn.lower() + " ") == (srn[:4], int(srn[6:8]), srn[8:10])


@given(st.text())
def test_parse_srn_never_returns_garbage(s):
    r = parse_srn(s)
    if r is not None:      # anything accepted must really look like an SRN
        campus, year, dept = r
        assert re.fullmatch(r"PES[12]", campus)
        assert isinstance(year, int) and 0 <= year <= 99
        assert re.fullmatch(r"[A-Z]{2}", dept)


@given(valid_srn, st.integers(min_value=1, max_value=12))
def test_parse_srn_truncated_rejected(srn, cut):
    assert parse_srn(srn[:-cut]) is None


# ----------------------------------------------------------------------------------
# 5. short_name: "F. Last" for two-word names, None otherwise
# ----------------------------------------------------------------------------------
word = st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=12)


@given(word, word)
def test_short_name_valid(first, last):
    assert short_name(f"{first} {last}") == first[0].upper() + ". " + last.capitalize()


@given(word, word, st.sampled_from(["  ", "\t", "   "]))
def test_short_name_extra_whitespace(first, last, gap):
    assert short_name(f" {first}{gap}{last} ") == first[0].upper() + ". " + last.capitalize()


@given(st.lists(word, min_size=0, max_size=6).filter(lambda w: len(w) != 2))
def test_short_name_wrong_word_count_rejected(words):
    assert short_name(" ".join(words)) is None


@settings(max_examples=300)
@given(st.text())
def test_short_name_output_format(s):
    r = short_name(s)
    assert r is None or re.fullmatch(r"\S+\. \S+", r)
