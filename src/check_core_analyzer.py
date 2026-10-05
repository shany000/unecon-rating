from __future__ import annotations

from dotenv import load_dotenv

from analyzer import AnalyzerService
from core import CoreService
from database import Neo4jDatabase
from models import StudentComparison
from parser.service import ParserService


load_dotenv()


def main():
    parser = ParserService()
    analyzer = AnalyzerService()

    with Neo4jDatabase() as database:
        core = CoreService(
            parser=parser,
            database=database,
            analyzer=analyzer,
        )

        print("1. Поиск направления...")

        year = 2023
        direction_name = (
            "Прикладная математика и информатика"
        )

        directions = core.get_directions(
            year,
        )

        direction = next(
            (
                item
                for item in directions
                if item.name == direction_name
            ),
            None,
        )

        assert direction is not None

        print(
            f"Направление: {direction.name}"
        )

        print()
        print("2. Получение групп через Core...")

        groups = core.get_groups(
            year,
            direction.id,
        )

        print(
            f"Получено групп: {len(groups)}"
        )

        for group in groups:
            print(
                f"{group.id} | "
                f"{group.name} | "
                f"студентов: {len(group.students)}"
            )

        group = next(
            (
                item
                for item in groups
                if item.name.strip().upper()
                == "ПМ-2301"
            ),
            None,
        )

        if group is None:
            print()
            print(
                "Группа ПМ-2301 не найдена."
            )
            print(
                "Требуемое имя: 'ПМ-2301'"
            )
            print(
                "Фактические имена групп:"
            )

            for item in groups:
                print(
                    repr(item.name)
                )

            raise RuntimeError(
                "Не удалось найти группу ПМ-2301"
            )

        print()
        print(
            f"Найдена группа: {group.name}"
        )

        print()
        print("3. Получение студентов через Core...")

        students = core.get_students(
            group.id,
        )

        print(
            f"Студентов в группе: "
            f"{len(students)}"
        )

        assert len(students) >= 2

        selected_students = []

        print()
        print("4. Поиск студентов с оценками...")

        for student_ref in students:
            student = core.get_student(
                student_ref.id,
            )

            print(
                f"{student.id}: "
                f"{student.name} | "
                f"дисциплин: "
                f"{len(student.grades)}"
            )

            has_scores = any(
                grade.total is not None
                or grade.grade.strip()
                for grade in student.grades
            )

            if has_scores:
                selected_students.append(
                    student_ref
                )

            if len(selected_students) == 2:
                break

        assert len(selected_students) == 2

        first_student_ref = selected_students[0]
        second_student_ref = selected_students[1]

        print()
        print("Выбраны студенты:")

        print(
            f"1. {first_student_ref.id} "
            f"{first_student_ref.name}"
        )

        print(
            f"2. {second_student_ref.id} "
            f"{second_student_ref.name}"
        )

        print()
        print("5. Сравнение через Core...")

        result = core.compare_students(
            first_student_ref.id,
            second_student_ref.id,
        )

        assert isinstance(
            result,
            StudentComparison,
        )

        print()
        print("6. Общая успеваемость")

        print(
            f"Студент 1: "
            f"{result.student_1_overall_average_grade}"
        )

        print(
            f"Студент 2: "
            f"{result.student_2_overall_average_grade}"
        )

        print(
            f"Студент 1, средние баллы: "
            f"{result.student_1_overall_average_points}"
        )

        print(
            f"Студент 2, средние баллы: "
            f"{result.student_2_overall_average_points}"
        )

        assert (
            result.student_1_overall_average_grade
            is not None
        )

        assert (
            result.student_2_overall_average_grade
            is not None
        )

        assert (
            result.student_1_overall_average_points
            is not None
        )

        assert (
            result.student_2_overall_average_points
            is not None
        )

        print()
        print("7. Сравнение по семестрам")

        assert result.semesters

        for semester in result.semesters:
            print()
            print(
                f"Семестр {semester.semester}"
            )

            print(
                "Общие предметы:",
                semester.common_subjects,
            )

            print(
                "Количество общих предметов:",
                semester.common_subjects_count,
            )

            print(
                "Средняя оценка студента 1:",
                semester.student_1_average_grade,
            )

            print(
                "Средняя оценка студента 2:",
                semester.student_2_average_grade,
            )

            print(
                "Средние баллы студента 1:",
                semester.student_1_average_points,
            )

            print(
                "Средние баллы студента 2:",
                semester.student_2_average_points,
            )

        print()
        print(
            "Интеграционный тест "
            "Core + Parser + Analyzer "
            "успешно пройден."
        )


if __name__ == "__main__":
    main()