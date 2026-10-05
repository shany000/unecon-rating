from __future__ import annotations

from collections import defaultdict

from models import (
    Grade,
    SemesterComparison,
    Student,
    StudentComparison,
)


class AnalyzerService:
    GRADE_VALUES = {
        "отл.": 5.0,
        "хор.": 4.0,
        "удовл.": 3.0,
        "н/я": 2.0,
    }

    @classmethod
    def _grade_to_value(
        cls,
        grade: str,
    ) -> float | None:
        normalized = grade.strip().lower()

        return cls.GRADE_VALUES.get(
            normalized
        )

    @staticmethod
    def _normalize_subject(
        subject: str,
    ) -> str:
        return " ".join(
            subject.lower().split()
        )

    @classmethod
    def _group_by_semester(
        cls,
        student: Student,
    ) -> dict[int, list[Grade]]:
        result = defaultdict(list)

        for grade in student.grades:
            if grade.semester is None:
                continue

            result[grade.semester].append(
                grade
            )

        return dict(result)

    @classmethod
    def _compare_semester(
        cls,
        semester: int,
        first_grades: list[Grade],
        second_grades: list[Grade],
    ) -> SemesterComparison:
        first_by_subject = {
            cls._normalize_subject(
                grade.subject
            ): grade
            for grade in first_grades
        }

        second_by_subject = {
            cls._normalize_subject(
                grade.subject
            ): grade
            for grade in second_grades
        }

        common_keys = sorted(
            first_by_subject.keys()
            & second_by_subject.keys()
        )

        common_subjects = [
            first_by_subject[key].subject
            for key in common_keys
        ]

        student_1_points_by_subject = {}
        student_2_points_by_subject = {}

        grade_pairs = []
        point_pairs = []

        for key in common_keys:
            first_grade = first_by_subject[key]
            second_grade = second_by_subject[key]

            subject = first_grade.subject

            student_1_points_by_subject[
                subject
            ] = first_grade.total

            student_2_points_by_subject[
                subject
            ] = second_grade.total

            first_grade_value = (
                cls._grade_to_value(
                    first_grade.grade
                )
            )

            second_grade_value = (
                cls._grade_to_value(
                    second_grade.grade
                )
            )

            if (
                first_grade_value is not None
                and second_grade_value is not None
            ):
                grade_pairs.append(
                    (
                        first_grade_value,
                        second_grade_value,
                    )
                )

            if (
                first_grade.total is not None
                and second_grade.total is not None
            ):
                point_pairs.append(
                    (
                        first_grade.total,
                        second_grade.total,
                    )
                )

        first_grade_average = None
        second_grade_average = None

        if grade_pairs:
            first_grade_average = (
                sum(
                    pair[0]
                    for pair in grade_pairs
                )
                / len(grade_pairs)
            )

            second_grade_average = (
                sum(
                    pair[1]
                    for pair in grade_pairs
                )
                / len(grade_pairs)
            )

        first_points_average = None
        second_points_average = None

        if point_pairs:
            first_points_average = (
                sum(
                    pair[0]
                    for pair in point_pairs
                )
                / len(point_pairs)
            )

            second_points_average = (
                sum(
                    pair[1]
                    for pair in point_pairs
                )
                / len(point_pairs)
            )

        return SemesterComparison(
            semester=semester,
            common_subjects=common_subjects,
            common_subjects_count=len(
                common_subjects
            ),
            student_1_average_grade=(
                first_grade_average
            ),
            student_2_average_grade=(
                second_grade_average
            ),
            student_1_average_points=(
                first_points_average
            ),
            student_2_average_points=(
                second_points_average
            ),
            grade_subjects_count=len(
                grade_pairs
            ),
            points_subjects_count=len(
                point_pairs
            ),
            student_1_points_by_subject=(
                student_1_points_by_subject
            ),
            student_2_points_by_subject=(
                student_2_points_by_subject
            ),
        )

    @classmethod
    def compare_students(
        cls,
        first_student: Student,
        second_student: Student,
    ) -> StudentComparison:
        first_by_semester = (
            cls._group_by_semester(
                first_student
            )
        )

        second_by_semester = (
            cls._group_by_semester(
                second_student
            )
        )

        semesters = sorted(
            first_by_semester.keys()
            & second_by_semester.keys()
        )

        semester_results = [
            cls._compare_semester(
                semester,
                first_by_semester[semester],
                second_by_semester[semester],
            )
            for semester in semesters
        ]

        first_overall_grade_values = []
        second_overall_grade_values = []

        for grade in first_student.grades:
            value = cls._grade_to_value(
                grade.grade
            )

            if value is not None:
                first_overall_grade_values.append(
                    value
                )

        for grade in second_student.grades:
            value = cls._grade_to_value(
                grade.grade
            )

            if value is not None:
                second_overall_grade_values.append(
                    value
                )

        first_points = [
            grade.total
            for grade in first_student.grades
            if grade.total is not None
        ]

        second_points = [
            grade.total
            for grade in second_student.grades
            if grade.total is not None
        ]

        first_overall_grade = None
        second_overall_grade = None

        if first_overall_grade_values:
            first_overall_grade = (
                sum(first_overall_grade_values)
                / len(first_overall_grade_values)
            )

        if second_overall_grade_values:
            second_overall_grade = (
                sum(second_overall_grade_values)
                / len(second_overall_grade_values)
            )

        first_overall_points = None
        second_overall_points = None

        if first_points:
            first_overall_points = (
                sum(first_points)
                / len(first_points)
            )

        if second_points:
            second_overall_points = (
                sum(second_points)
                / len(second_points)
            )

        return StudentComparison(
            student_1_id=first_student.id,
            student_2_id=second_student.id,
            student_1_overall_average_grade=(
                first_overall_grade
            ),
            student_2_overall_average_grade=(
                second_overall_grade
            ),
            student_1_overall_average_points=(
                first_overall_points
            ),
            student_2_overall_average_points=(
                second_overall_points
            ),
            overall_grade_subjects_count_1=len(
                first_overall_grade_values
            ),
            overall_grade_subjects_count_2=len(
                second_overall_grade_values
            ),
            overall_points_subjects_count_1=len(
                first_points
            ),
            overall_points_subjects_count_2=len(
                second_points
            ),
            semesters=semester_results,
        )