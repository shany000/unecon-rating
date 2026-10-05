from __future__ import annotations

from dotenv import load_dotenv

from parser.service import ParserService


load_dotenv()


def print_student(student):
    print(f"ID: {student.id}")
    print(f"Имя: {student.name}")
    print(f"Группа: {student.group}")
    print(f"Дисциплин: {len(student.grades)}")

    print()

    for grade in student.grades:
        print(
            f"Семестр: {grade.semester}"
        )
        print(
            f"Предмет: {grade.subject}"
        )
        print(
            f"Форма контроля: {grade.control_type}"
        )
        print(
            f"КТ1: {grade.kt1}"
        )
        print(
            f"КТ2: {grade.kt2}"
        )
        print(
            f"КТ3: {grade.kt3}"
        )
        print(
            f"КТ4: {grade.kt4}"
        )
        print(
            f"Экзамен: {grade.exam}"
        )
        print(
            f"Сумма: {grade.total}"
        )
        print(
            f"Оценка: {grade.grade}"
        )
        print("-" * 60)


def main():
    parser = ParserService()

    current_student_id = 687385
    senior_student_id = 640211

    print("=" * 60)
    print(
        f"1. Проверка текущего студента "
        f"{current_student_id}"
    )
    print("=" * 60)

    current_student = parser.get_student(
        current_student_id,
    )

    print_student(current_student)

    assert current_student.id == current_student_id
    assert current_student.name
    assert current_student.group
    assert current_student.grades

    print()
    print("Текущий студент успешно распознан.")

    print()
    print("=" * 60)
    print(
        f"2. Проверка студента старшего курса "
        f"{senior_student_id}"
    )
    print("=" * 60)

    senior_student = parser.get_student(
        senior_student_id,
    )

    print_student(senior_student)

    assert senior_student.id == senior_student_id
    assert senior_student.name
    assert senior_student.group
    assert senior_student.grades

    has_scores = False

    for grade in senior_student.grades:
        if any(
            value is not None
            for value in (
                grade.kt1,
                grade.kt2,
                grade.kt3,
                grade.kt4,
                grade.exam,
                grade.total,
            )
        ):
            has_scores = True
            break

        if grade.grade:
            has_scores = True
            break

    assert has_scores

    print()
    print(
        "У старшего студента найдены "
        "заполненные оценки."
    )

    print()
    print("=" * 60)
    print("3. Проверка структуры оценок")
    print("=" * 60)

    for grade in senior_student.grades:
        assert grade.subject
        assert grade.control_type

        print(
            f"{grade.subject} | "
            f"КТ1={grade.kt1} | "
            f"КТ2={grade.kt2} | "
            f"КТ3={grade.kt3} | "
            f"КТ4={grade.kt4} | "
            f"Экзамен={grade.exam} | "
            f"Сумма={grade.total} | "
            f"Оценка={grade.grade!r}"
        )

    print()
    print("Все проверки успешно пройдены.")


if __name__ == "__main__":
    main()