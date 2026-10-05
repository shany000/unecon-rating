from __future__ import annotations

from dataclasses import dataclass, field


Score = int | float | None


@dataclass
class Grade:
    semester: int | None
    subject: str
    control_type: str
    kt1: Score
    kt2: Score
    kt3: Score
    kt4: Score
    exam: Score
    total: Score
    grade: str


@dataclass
class StudentRef:
    id: int
    name: str


@dataclass
class Student:
    id: int
    name: str
    group: str
    grades: list[Grade] = field(default_factory=list)


@dataclass
class Group:
    id: str
    name: str
    students: list[StudentRef] = field(default_factory=list)


@dataclass
class Direction:
    id: str
    name: str
    up_ids: list[str] = field(default_factory=list)


@dataclass
class Year:
    year: int
    directions: list[Direction] = field(default_factory=list)


@dataclass
class SemesterComparison:
    semester: int
    common_subjects: list[str] = field(
        default_factory=list
    )
    common_subjects_count: int = 0

    student_1_average_grade: float | None = None
    student_2_average_grade: float | None = None

    student_1_average_points: float | None = None
    student_2_average_points: float | None = None

    grade_subjects_count: int = 0
    points_subjects_count: int = 0

    student_1_points_by_subject: dict[
        str,
        Score,
    ] = field(
        default_factory=dict
    )

    student_2_points_by_subject: dict[
        str,
        Score,
    ] = field(
        default_factory=dict
    )


@dataclass
class StudentComparison:
    student_1_id: int
    student_2_id: int

    student_1_overall_average_grade: float | None = None
    student_2_overall_average_grade: float | None = None

    student_1_overall_average_points: float | None = None
    student_2_overall_average_points: float | None = None

    overall_grade_subjects_count_1: int = 0
    overall_grade_subjects_count_2: int = 0

    overall_points_subjects_count_1: int = 0
    overall_points_subjects_count_2: int = 0

    semesters: list[SemesterComparison] = field(
        default_factory=list
    )