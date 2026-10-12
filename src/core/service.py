from __future__ import annotations

from collections.abc import Callable

from analyzer import AnalyzerService
from database.neo4j import Neo4jDatabase
from models import Direction, Group, GroupComparison, Student, StudentComparison, StudentRef, Year
from parser.service import ParserService


class CoreService:
    def __init__(
        self,
        parser: ParserService,
        database: Neo4jDatabase,
        analyzer: AnalyzerService,
    ):
        self.parser = parser
        self.database = database
        self.analyzer = analyzer

    def _download_and_save_catalog(self) -> list[Year]:
        catalog = self.parser.get_catalog()
        if not catalog:
            raise RuntimeError("Parser не получил каталог с сайта.")

        empty_years = [item.year for item in catalog if not item.directions]
        if empty_years:
            raise RuntimeError("Не найдены направления для годов: " + f"{empty_years}")

        self.database.save_catalog(catalog)
        return catalog

    def initialize_catalog(self) -> list[Year]:
        self.database.create_constraints()
        return self._download_and_save_catalog()

    def ensure_catalog(self) -> list[Year]:
        self.database.create_constraints()
        years = self.database.get_years()
        if years:
            catalog = []
            catalog_is_complete = True
            for year in years:
                directions = self.database.get_directions(year)
                if not directions:
                    catalog_is_complete = False
                    break
                catalog.append(Year(year=year, directions=directions))

            if catalog_is_complete:
                print("Каталог уже находится в Neo4j. Повторная загрузка не требуется.")
                return catalog

        print("Каталог отсутствует или заполнен не полностью. Загружаем данные с сайта.")
        return self._download_and_save_catalog()

    def get_years(self) -> list[int]:
        return self.database.get_years()

    def get_directions(self, year: int) -> list[Direction]:
        return self.database.get_directions(year)

    def get_groups(self, year: int, direction_id: str) -> list[Group]:
        groups = self.database.get_groups(year, direction_id)
        if groups:
            return groups

        directions = self.database.get_directions(year)
        direction = next((item for item in directions if item.id == direction_id), None)
        if direction is None:
            raise ValueError(f"Направление не найдено: {direction_id} (год {year})")

        groups = self.parser.get_groups(year, direction)
        self.database.save_groups(year, direction_id, groups)
        return groups

    def get_students(self, group_id: str) -> list[StudentRef]:
        return self.database.get_students(group_id)

    def get_student(self, student_id: int) -> Student:
        return self.parser.get_student(student_id)

    def compare_students(
        self,
        first_student_id: int,
        second_student_id: int,
    ) -> StudentComparison:
        first_student = self.get_student(first_student_id)
        second_student = self.get_student(second_student_id)
        return self.analyzer.compare_students(first_student, second_student)

    def compare_groups(
        self,
        first_group_id: str,
        second_group_id: str,
        first_group_name: str,
        second_group_name: str,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> GroupComparison:
        first_refs = self.get_students(first_group_id)
        second_refs = self.get_students(second_group_id)
        if not first_refs:
            raise ValueError(f"В группе «{first_group_name}» не найдены студенты.")
        if not second_refs:
            raise ValueError(f"В группе «{second_group_name}» не найдены студенты.")

        total = len(first_refs) + len(second_refs)
        processed = 0
        loaded_students: dict[int, Student] = {}

        def load_students(refs: list[StudentRef]) -> list[Student]:
            nonlocal processed
            students = []
            for ref in refs:
                student = loaded_students.get(ref.id)
                if student is None:
                    student = self.get_student(ref.id)
                    loaded_students[ref.id] = student
                students.append(student)
                processed += 1
                if progress_callback is not None:
                    progress_callback(processed, total)
            return students

        first_students = load_students(first_refs)
        second_students = load_students(second_refs)

        return self.analyzer.compare_groups(
            first_group_id=first_group_id,
            second_group_id=second_group_id,
            first_group_name=first_group_name,
            second_group_name=second_group_name,
            first_students=first_students,
            second_students=second_students,
        )
