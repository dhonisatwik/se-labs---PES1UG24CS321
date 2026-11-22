"""
Lab 6 - Branch coverage tests for student_grades.py
Name : Pendyala Dhoni Satwik
SRN  : PES1UG24CS321

Goal: make every decision (if / elif / or / and) take BOTH its True and its False
outcome, and test the boundary value of every comparison.
Run:
    coverage run --branch -m pytest BranchCoverageTest_student_grades.py
    coverage report -m
"""
import pytest
from student_grades import letter_grade, final_marks, exam_eligibility


# ============================================================ letter_grade
# Decision 1: marks < 0 or marks > 100  -> True via either side, False when valid
@pytest.mark.parametrize("marks", [-1, -0.5, 101, 150])
def test_letter_grade_invalid_marks_raise(marks):
    with pytest.raises(ValueError, match="invalid marks"):
        letter_grade(marks)


# Decisions 2-7: each grade band's lower boundary (True branch) and the value
# just below it (False branch, falls to the next elif)
@pytest.mark.parametrize("marks, expected", [
    (100, "S"), (90, "S"),       # top of range and S boundary
    (89, "A"), (80, "A"),        # just below 90 -> elif >= 80
    (79, "B"), (70, "B"),
    (69, "C"), (60, "C"),
    (59, "D"), (50, "D"),
    (49, "E"), (40, "E"),
    (39, "F"), (0, "F"),         # every elif False -> final return "F"
])
def test_letter_grade_all_bands_and_boundaries(marks, expected):
    assert letter_grade(marks) == expected


# ============================================================ final_marks
# Decision 1: internal > 40 or external > 60
def test_final_marks_internal_too_high():
    with pytest.raises(ValueError, match="marks out of range"):
        final_marks(41, 50, False)          # left side True


def test_final_marks_external_too_high():
    with pytest.raises(ValueError, match="marks out of range"):
        final_marks(30, 61, False)          # left False, right True


def test_final_marks_upper_limits_are_valid():
    assert final_marks(40, 60, False) == 100  # both sides False at the boundary


# Decision 2: has_project False -> no bonus (branch 23 -> 27)
def test_final_marks_without_project():
    assert final_marks(30, 45, False) == 75


# Decision 3: has_project True and total <= 100 -> bonus kept, no cap (branch 25 -> 27)
def test_final_marks_project_bonus_no_cap():
    assert final_marks(30, 45, True) == 80


def test_final_marks_project_bonus_reaches_exactly_100():
    assert final_marks(35, 60, True) == 100   # 95 + 5 = 100, not > 100


# Decision 3: has_project True and total > 100 -> capped at 100
def test_final_marks_project_bonus_capped():
    assert final_marks(40, 60, True) == 100   # 105 -> 100
    assert final_marks(38, 60, True) == 100   # 103 -> 100


# ============================================================ exam_eligibility
# Decision 1: not fees_paid
def test_exam_blocked_even_with_full_attendance():
    assert exam_eligibility(100, False, True) == "blocked"


# Decision 2: attendance >= 75
@pytest.mark.parametrize("attendance", [75, 90, 100])
def test_exam_eligible_by_attendance(attendance):
    assert exam_eligibility(attendance, True, False) == "eligible"


# Decision 3: attendance >= 65 and has_medical -> all combinations
def test_exam_eligible_medical_at_lower_boundary():
    assert exam_eligibility(65, True, True) == "eligible"     # True and True


def test_exam_detained_medical_but_attendance_too_low():
    assert exam_eligibility(64, True, True) == "detained"     # False and (not evaluated)


def test_exam_detained_attendance_ok_but_no_medical():
    assert exam_eligibility(74, True, False) == "detained"    # True and False


def test_exam_detained_very_low_attendance():
    assert exam_eligibility(10, True, False) == "detained"
