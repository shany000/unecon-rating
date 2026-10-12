from __future__ import annotations

from collections import Counter
from numbers import Real

from dotenv import load_dotenv

from database import Neo4jDatabase
from parser.service import ParserService


GROUPS = [
    (
        "ПМ-2301",
        "2023:прикладная-математика-и-информатика:пм-2301",
    ),
    (
        "ПМ-2302",
        "2023:прикладная-математика-и-информатика:пм-2302",
    ),
]

TARGET_SUBJECTS = {
    "архитектура компьютеров",
    "иностранный язык",
    "история россии",
    "право",
}
TARGET_SEMESTER = 1


def normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def display_distribution(counter: Counter) -> str:
    if not counter:
        return "нет данных"
    return "; ".join(
        f"{value}: {count}"
        for value, count in sorted(counter.items(), key=lambda item: str(item[0]))
    )


def main() -> None:
    load_dotenv()
    parser = ParserService()

    with Neo4jDatabase() as database:
        database.verify_connectivity()

        for group_name, group_id in GROUPS:
            students = database.get_students(group_id)
            print("\n" + "=" * 100)
            print(f"Группа: {group_name}; студентов в Neo4j: {len(students)}")
            print(f"ID: {group_id}")
            print("=" * 100)

            subject_rows: dict[str, list] = {
                subject: [] for subject in TARGET_SUBJECTS
            }

            for index, student_ref in enumerate(students, start=1):
                print(
                    f"Загрузка карточки {index}/{len(students)}",
                    end="\r",
                    flush=True,
                )
                student = parser.get_student(student_ref.id)
                for grade in student.grades:
                    subject_key = normalize(grade.subject)
                    if (
                        grade.semester == TARGET_SEMESTER
                        and subject_key in TARGET_SUBJECTS
                    ):
                        subject_rows[subject_key].append(grade)

            print(" " * 80, end="\r")
            for subject in sorted(TARGET_SUBJECTS):
                rows = subject_rows[subject]
                print(f"\nПредмет: {subject}; семестр: {TARGET_SEMESTER}")
                print(f"Записей найдено: {len(rows)}")
                if not rows:
                    print("  Записи не найдены. Проверь исходное название предмета/семестр.")
                    continue

                grades = Counter(repr(item.grade) for item in rows)
                control_types = Counter(repr(item.control_type) for item in rows)
                total_types = Counter(type(item.total).__name__ for item in rows)
                totals = [
                    float(item.total)
                    for item in rows
                    if isinstance(item.total, Real) and not isinstance(item.total, bool)
                ]
                nonempty_grades = sum(
                    item.grade is not None and str(item.grade).strip() != ""
                    for item in rows
                )

                print(f"  Сырые значения Grade.grade: {display_distribution(grades)}")
                print(f"  Типы контроля: {display_distribution(control_types)}")
                print(f"  Типы total: {display_distribution(total_types)}")
                print(f"  Незаполненных/пустых grade: {len(rows) - nonempty_grades}")
                print(f"  total: заполнено {len(totals)} из {len(rows)}")
                if totals:
                    print(f"  Диапазон total: {min(totals):.2f} .. {max(totals):.2f}")

                print("  Примеры исходных записей (без имён студентов):")
                for item in rows[:8]:
                    print(
                        "   ",
                        f"subject={item.subject!r}; semester={item.semester!r};",
                        f"control_type={item.control_type!r}; grade={item.grade!r};",
                        f"total={item.total!r};",
                        f"kt1={item.kt1!r}; kt2={item.kt2!r};",
                        f"kt3={item.kt3!r}; kt4={item.kt4!r}; exam={item.exam!r}",
                    )


if __name__ == "__main__":
    main()
