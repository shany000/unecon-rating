from models import Grade, Student
from analyzer import AnalyzerService


def grade(
    semester,
    subject,
    total,
    result,
):
    return Grade(
        semester=semester,
        subject=subject,
        control_type="Экзамен",
        kt1=None,
        kt2=None,
        kt3=None,
        kt4=None,
        exam=None,
        total=total,
        grade=result,
    )


def main():
    student_1 = Student(
        id=1,
        name="Студент 1",
        group="TEST-1",
        grades=[
            grade(
                1,
                "Математика",
                90,
                "отл.",
            ),
            grade(
                1,
                "Программирование",
                80,
                "хор.",
            ),
            grade(
                1,
                "История",
                70,
                "удовл.",
            ),
            grade(
                2,
                "Математика",
                85,
                "отл.",
            ),
            grade(
                2,
                "Базы данных",
                75,
                "хор.",
            ),
        ],
    )

    student_2 = Student(
        id=2,
        name="Студент 2",
        group="TEST-2",
        grades=[
            grade(
                1,
                "Математика",
                80,
                "хор.",
            ),
            grade(
                1,
                "Программирование",
                90,
                "отл.",
            ),
            grade(
                1,
                "Философия",
                60,
                "удовл.",
            ),
            grade(
                2,
                "Математика",
                70,
                "удовл.",
            ),
            grade(
                2,
                "Базы данных",
                95,
                "отл.",
            ),
        ],
    )

    analyzer = AnalyzerService()

    result = analyzer.compare_students(
        student_1,
        student_2,
    )

    print(
        "Студент 1:",
        result.student_1_id,
    )

    print(
        "Студент 2:",
        result.student_2_id,
    )

    print()
    print("Общая успеваемость")

    print(
        "Студент 1:",
        result.student_1_overall_average_grade,
    )

    print(
        "Студент 2:",
        result.student_2_overall_average_grade,
    )

    print(
        "Студент 1, средние баллы:",
        result.student_1_overall_average_points,
    )

    print(
        "Студент 2, средние баллы:",
        result.student_2_overall_average_points,
    )

    print()
    print("Сравнение по семестрам")

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
            "Средняя оценка 1:",
            semester.student_1_average_grade,
        )

        print(
            "Средняя оценка 2:",
            semester.student_2_average_grade,
        )

        print(
            "Средние баллы 1:",
            semester.student_1_average_points,
        )

        print(
            "Средние баллы 2:",
            semester.student_2_average_points,
        )

    assert (
        result.student_1_overall_average_grade
        == 4.2
    )

    assert (
        result.student_2_overall_average_grade
        == 4.0
    )

    assert (
        result.student_1_overall_average_points
        == 80.0
    )

    assert (
        result.student_2_overall_average_points
        == 79.0
    )

    assert len(result.semesters) == 2

    semester_1 = result.semesters[0]

    assert semester_1.semester == 1

    assert semester_1.common_subjects_count == 2

    assert semester_1.common_subjects == [
        "Математика",
        "Программирование",
    ]

    assert (
        semester_1.student_1_average_grade
        == 4.5
    )

    assert (
        semester_1.student_2_average_grade
        == 4.5
    )

    assert (
        semester_1.student_1_average_points
        == 85.0
    )

    assert (
        semester_1.student_2_average_points
        == 85.0
    )

    semester_2 = result.semesters[1]

    assert semester_2.semester == 2

    assert semester_2.common_subjects_count == 2

    assert semester_2.common_subjects == [
        "Базы данных",
        "Математика",
    ]

    assert (
        semester_2.student_1_average_grade
        == 4.5
    )

    assert (
        semester_2.student_2_average_grade
        == 4.0
    )

    assert (
        semester_2.student_1_average_points
        == 80.0
    )

    assert (
        semester_2.student_2_average_points
        == 82.5
    )

    print()
    print("Все тесты Analyzer успешно пройдены.")


if __name__ == "__main__":
    main()