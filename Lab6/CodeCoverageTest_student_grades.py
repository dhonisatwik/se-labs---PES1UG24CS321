"""
Lab 6 - Code (line) coverage tests for student_grades.py
Name : Pendyala Dhoni Satwik
SRN  : PES1UG24CS321

Goal: execute every statement of student_grades.py at least once.
Run:
    coverage run -m pytest CodeCoverageTest_student_grades.py
    coverage report -m
"""
import pytest
from student_grades import letter_grade, final_marks, exam_eligibility


# ---------------------------------------------------------------- letter_grade
def test_letter_grade_invalid_raises():
    # line 3: raise ValueError for marks outside 0-100
    with pytest.raises(ValueError, match="invalid marks"):
        letter_grade(-5)


def test_letter_grade_s():
    assert letter_grade(95) == "S"


def test_letter_grade_a():
    assert letter_grade(85) == "A"


def test_letter_grade_b():
    assert letter_grade(75) == "B"


def test_letter_grade_c():
    assert letter_grade(65) == "C"


def test_letter_grade_d():
    assert letter_grade(55) == "D"


def test_letter_grade_e():
    assert letter_grade(45) == "E"


def test_letter_grade_f():
    # line 16: falls through every elif
    assert letter_grade(30) == "F"


# ---------------------------------------------------------------- final_marks
def test_final_marks_out_of_range_raises():
    # line 21
    with pytest.raises(ValueError, match="marks out of range"):
        final_marks(45, 50, False)


def test_final_marks_project_bonus_capped_at_100():
    # lines 22-27: bonus added, total goes past 100 and is capped
    assert final_marks(40, 60, True) == 100


# ---------------------------------------------------------------- exam_eligibility
def test_exam_blocked_when_fees_unpaid():
    # line 32
    assert exam_eligibility(90, False, False) == "blocked"


def test_exam_eligible_with_good_attendance():
    # line 34
    assert exam_eligibility(80, True, False) == "eligible"


def test_exam_eligible_with_medical():
    # line 36
    assert exam_eligibility(70, True, True) == "eligible"


def test_exam_detained_low_attendance():
    # line 37
    assert exam_eligibility(50, True, False) == "detained"
