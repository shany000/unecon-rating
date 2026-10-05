from dotenv import load_dotenv

from analyzer import AnalyzerService
from core import CoreService
from database import Neo4jDatabase
from parser.service import ParserService


load_dotenv()


class FailingParser:
    def get_groups(self, year, direction):
        raise RuntimeError(
            "Parser не должен вызываться"
        )

    def get_student(self, student_id):
        raise RuntimeError(
            "Parser не должен вызываться"
        )


def main():
    parser = ParserService()
    analyzer = AnalyzerService()

    with Neo4jDatabase() as database:
        core = CoreService(
            parser=parser,
            database=database,
            analyzer=analyzer,
        )

        print("1. Поиск тестовой группы...")

        year = 2026
        direction_id = "бизнес-информатика"
        group_id = (
            "2026:бизнес-информатика:би-2601"
        )

        directions = core.get_directions(year)

        direction = next(
            (
                item
                for item in directions
                if item.id == direction_id
            ),
            None,
        )

        assert direction is not None

        groups = core.get_groups(
            year,
            direction_id,
        )

        group = next(
            (
                item
                for item in groups
                if item.id == group_id
            ),
            None,
        )

        assert group is not None

        print(
            f"Найдена группа: {group.name}"
        )

        print()
        print("2. Проверка студентов в Neo4j...")

        students_in_database = database.get_students(
            group_id,
        )

        print(
            f"Студентов в БД: "
            f"{len(students_in_database)}"
        )

        assert students_in_database

        print(
            f"Первый студент: "
            f"{students_in_database[0]}"
        )

        print()
        print("3. Проверка Core.get_students()...")

        students = core.get_students(
            group_id,
        )

        print(
            f"Студентов через Core: "
            f"{len(students)}"
        )

        assert len(students) == len(
            students_in_database
        )

        assert {
            student.id
            for student in students
        } == {
            student.id
            for student in students_in_database
        }

        print()
        print("4. Проверка получения студентов без Parser...")

        core_from_database = CoreService(
            parser=FailingParser(),
            database=database,
            analyzer=analyzer,
        )

        students_without_parser = (
            core_from_database.get_students(
                group_id,
            )
        )

        print(
            f"Студентов без Parser: "
            f"{len(students_without_parser)}"
        )

        assert len(students_without_parser) == len(
            students
        )

        print()
        print("5. Получение полного студента через Parser...")

        student_ref = students[0]

        student = core.get_student(
            student_ref.id,
        )

        print(
            f"ID: {student.id}"
        )

        print(
            f"Имя: {student.name}"
        )

        print(
            f"Группа: {student.group}"
        )

        print(
            f"Оценок: {len(student.grades)}"
        )

        assert student.id == student_ref.id
        assert student.name == student_ref.name

        print()
        print("Все тесты успешно пройдены.")


if __name__ == "__main__":
    main()