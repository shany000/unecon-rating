from __future__ import annotations

from collections import defaultdict

from models import (
    Grade,
    GroupComparison,
    GroupSemesterComparison,
    GroupSubjectComparison,
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
    def _grade_to_value(cls, grade: str) -> float | None:
        return cls.GRADE_VALUES.get(grade.strip().lower())

    @staticmethod
    def _normalize_subject(subject: str) -> str:
        return " ".join(subject.lower().split())

    @classmethod
    def _group_by_semester(cls, student: Student) -> dict[int, list[Grade]]:
        result = defaultdict(list)
        for grade in student.grades:
            if grade.semester is not None:
                result[grade.semester].append(grade)
        return dict(result)

    @classmethod
    def _compare_semester(
        cls,
        semester: int,
        first_grades: list[Grade],
        second_grades: list[Grade],
    ) -> SemesterComparison:
        first_by_subject = {
            cls._normalize_subject(grade.subject): grade
            for grade in first_grades
        }
        second_by_subject = {
            cls._normalize_subject(grade.subject): grade
            for grade in second_grades
        }
        common_keys = sorted(first_by_subject.keys() & second_by_subject.keys())
        common_subjects = [first_by_subject[key].subject for key in common_keys]
        student_1_points_by_subject = {}
        student_2_points_by_subject = {}
        grade_pairs = []
        point_pairs = []

        for key in common_keys:
            first_grade = first_by_subject[key]
            second_grade = second_by_subject[key]
            subject = first_grade.subject
            student_1_points_by_subject[subject] = first_grade.total
            student_2_points_by_subject[subject] = second_grade.total

            first_grade_value = cls._grade_to_value(first_grade.grade)
            second_grade_value = cls._grade_to_value(second_grade.grade)
            if first_grade_value is not None and second_grade_value is not None:
                grade_pairs.append((first_grade_value, second_grade_value))
            if first_grade.total is not None and second_grade.total is not None:
                point_pairs.append((first_grade.total, second_grade.total))

        first_grade_average = None
        second_grade_average = None
        if grade_pairs:
            first_grade_average = sum(pair[0] for pair in grade_pairs) / len(grade_pairs)
            second_grade_average = sum(pair[1] for pair in grade_pairs) / len(grade_pairs)

        first_points_average = None
        second_points_average = None
        if point_pairs:
            first_points_average = sum(pair[0] for pair in point_pairs) / len(point_pairs)
            second_points_average = sum(pair[1] for pair in point_pairs) / len(point_pairs)

        return SemesterComparison(
            semester=semester,
            common_subjects=common_subjects,
            common_subjects_count=len(common_subjects),
            student_1_average_grade=first_grade_average,
            student_2_average_grade=second_grade_average,
            student_1_average_points=first_points_average,
            student_2_average_points=second_points_average,
            grade_subjects_count=len(grade_pairs),
            points_subjects_count=len(point_pairs),
            student_1_points_by_subject=student_1_points_by_subject,
            student_2_points_by_subject=student_2_points_by_subject,
        )

    @classmethod
    def compare_students(
        cls,
        first_student: Student,
        second_student: Student,
    ) -> StudentComparison:
        first_by_semester = cls._group_by_semester(first_student)
        second_by_semester = cls._group_by_semester(second_student)
        semesters = sorted(first_by_semester.keys() & second_by_semester.keys())
        semester_results = [
            cls._compare_semester(
                semester,
                first_by_semester[semester],
                second_by_semester[semester],
            )
            for semester in semesters
        ]

        first_grade_values = [
            cls._grade_to_value(grade.grade)
            for grade in first_student.grades
        ]
        first_grade_values = [value for value in first_grade_values if value is not None]
        second_grade_values = [
            cls._grade_to_value(grade.grade)
            for grade in second_student.grades
        ]
        second_grade_values = [value for value in second_grade_values if value is not None]
        first_points = [grade.total for grade in first_student.grades if grade.total is not None]
        second_points = [grade.total for grade in second_student.grades if grade.total is not None]

        return StudentComparison(
            student_1_id=first_student.id,
            student_2_id=second_student.id,
            student_1_overall_average_grade=(
                sum(first_grade_values) / len(first_grade_values)
                if first_grade_values else None
            ),
            student_2_overall_average_grade=(
                sum(second_grade_values) / len(second_grade_values)
                if second_grade_values else None
            ),
            student_1_overall_average_points=(
                sum(first_points) / len(first_points) if first_points else None
            ),
            student_2_overall_average_points=(
                sum(second_points) / len(second_points) if second_points else None
            ),
            overall_grade_subjects_count_1=len(first_grade_values),
            overall_grade_subjects_count_2=len(second_grade_values),
            overall_points_subjects_count_1=len(first_points),
            overall_points_subjects_count_2=len(second_points),
            semesters=semester_results,
        )

    @classmethod
    def _group_grade_data(
        cls,
        students: list[Student],
    ) -> tuple[dict[int, dict[str, list[Grade]]], list[float], list[float]]:
        by_semester: dict[int, dict[str, list[Grade]]] = defaultdict(
            lambda: defaultdict(list)
        )
        all_grade_values: list[float] = []
        all_points: list[float] = []

        for student in students:
            for grade in student.grades:
                if grade.semester is not None:
                    by_semester[grade.semester][cls._normalize_subject(grade.subject)].append(grade)
                grade_value = cls._grade_to_value(grade.grade)
                if grade_value is not None:
                    all_grade_values.append(grade_value)
                if grade.total is not None:
                    all_points.append(float(grade.total))

        return (
            {semester: dict(subjects) for semester, subjects in by_semester.items()},
            all_grade_values,
            all_points,
        )

    @classmethod
    def _average(cls, values: list[float]) -> float | None:
        return sum(values) / len(values) if values else None

    @staticmethod
    def _weighted_average(values: list[tuple[float, int]]) -> float | None:
        total_weight = sum(weight for _, weight in values)
        if not total_weight:
            return None
        return sum(value * weight for value, weight in values) / total_weight

    @classmethod
    def _compare_group_semester(
        cls,
        semester: int,
        first_subjects: dict[str, list[Grade]],
        second_subjects: dict[str, list[Grade]],
    ) -> GroupSemesterComparison:
        common_keys = sorted(first_subjects.keys() & second_subjects.keys())
        subject_results = []

        for key in common_keys:
            first_grades = first_subjects[key]
            second_grades = second_subjects[key]
            first_grade_values = [
                value for value in (cls._grade_to_value(grade.grade) for grade in first_grades)
                if value is not None
            ]
            second_grade_values = [
                value for value in (cls._grade_to_value(grade.grade) for grade in second_grades)
                if value is not None
            ]
            first_points = [float(grade.total) for grade in first_grades if grade.total is not None]
            second_points = [float(grade.total) for grade in second_grades if grade.total is not None]

            subject_results.append(
                GroupSubjectComparison(
                    subject=first_grades[0].subject,
                    group_1_average_grade=cls._average(first_grade_values),
                    group_2_average_grade=cls._average(second_grade_values),
                    group_1_average_points=cls._average(first_points),
                    group_2_average_points=cls._average(second_points),
                    group_1_grade_count=len(first_grade_values),
                    group_2_grade_count=len(second_grade_values),
                    group_1_points_count=len(first_points),
                    group_2_points_count=len(second_points),
                )
            )

        grades_1 = [
            (item.group_1_average_grade, item.group_1_grade_count)
            for item in subject_results
            if item.group_1_average_grade is not None and item.group_1_grade_count
        ]
        grades_2 = [
            (item.group_2_average_grade, item.group_2_grade_count)
            for item in subject_results
            if item.group_2_average_grade is not None and item.group_2_grade_count
        ]
        points_1 = [
            (item.group_1_average_points, item.group_1_points_count)
            for item in subject_results
            if item.group_1_average_points is not None and item.group_1_points_count
        ]
        points_2 = [
            (item.group_2_average_points, item.group_2_points_count)
            for item in subject_results
            if item.group_2_average_points is not None and item.group_2_points_count
        ]

        return GroupSemesterComparison(
            semester=semester,
            common_subjects=[item.subject for item in subject_results],
            group_1_average_grade=cls._weighted_average(grades_1),
            group_2_average_grade=cls._weighted_average(grades_2),
            group_1_average_points=cls._weighted_average(points_1),
            group_2_average_points=cls._weighted_average(points_2),
            grade_subjects_count=sum(
                item.group_1_average_grade is not None and item.group_2_average_grade is not None
                for item in subject_results
            ),
            points_subjects_count=sum(
                item.group_1_average_points is not None and item.group_2_average_points is not None
                for item in subject_results
            ),
            subjects=subject_results,
        )

    @classmethod
    def compare_groups(
        cls,
        first_group_id: str,
        second_group_id: str,
        first_group_name: str,
        second_group_name: str,
        first_students: list[Student],
        second_students: list[Student],
    ) -> GroupComparison:
        first_by_semester, first_grade_values, first_points = cls._group_grade_data(first_students)
        second_by_semester, second_grade_values, second_points = cls._group_grade_data(second_students)

        common_semesters = sorted(first_by_semester.keys() & second_by_semester.keys())
        semester_results = [
            cls._compare_group_semester(
                semester,
                first_by_semester[semester],
                second_by_semester[semester],
            )
            for semester in common_semesters
        ]

        return GroupComparison(
            group_1_id=first_group_id,
            group_2_id=second_group_id,
            group_1_name=first_group_name,
            group_2_name=second_group_name,
            group_1_student_count=len(first_students),
            group_2_student_count=len(second_students),
            group_1_overall_average_grade=cls._average(first_grade_values),
            group_2_overall_average_grade=cls._average(second_grade_values),
            group_1_overall_average_points=cls._average(first_points),
            group_2_overall_average_points=cls._average(second_points),
            group_1_grade_count=len(first_grade_values),
            group_2_grade_count=len(second_grade_values),
            group_1_points_count=len(first_points),
            group_2_points_count=len(second_points),
            semesters=semester_results,
        )
