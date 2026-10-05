from __future__ import annotations

import re
import time
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from curl_cffi import requests

from models import (
    Direction,
    Grade,
    Group,
    Student,
    StudentRef,
    Year,
)


BASE_URL = "https://rating.unecon.ru"

INDEX_URL = f"{BASE_URL}/index.php"
STUDENT_URL = f"{BASE_URL}/stud_cd.php"

REQUEST_DELAY = 1
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3

HEADERS = {
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
}


class ParserService:
    def _request(self, url, params=None):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers=HEADERS,
                    impersonate="chrome",
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()

                print(f"GET {response.url}")

                time.sleep(REQUEST_DELAY)

                return response.content

            except Exception as error:
                print(
                    f"Ошибка запроса "
                    f"(попытка {attempt}/{MAX_RETRIES}): {error}"
                )

                if attempt < MAX_RETRIES:
                    time.sleep(REQUEST_DELAY * 2)

        raise RuntimeError(
            f"Не удалось получить страницу: {url}"
        )

    @staticmethod
    def _parse_query_params(href):
        parsed = urlparse(href)

        return {
            key: values[0]
            for key, values in parse_qs(
                parsed.query
            ).items()
            if values
        }

    @staticmethod
    def _normalize_text(text):
        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

    @classmethod
    def _normalize_direction_name(cls, name):
        name = cls._normalize_text(name)

        name = re.sub(
            r"^(Бакалавриат|Специалитет|Магистратура|Аспирантура)\s*-\s*",
            "",
            name,
            flags=re.IGNORECASE,
        )

        if "(" in name:
            name = name.split("(", 1)[0]

        name = re.sub(
            r"\s+\d{4}\s*$",
            "",
            name,
        )

        return name.strip()

    @classmethod
    def _direction_id(cls, name):
        return re.sub(
            r"[^0-9a-zа-я]+",
            "-",
            cls._normalize_direction_name(name).lower(),
        ).strip("-")

    @staticmethod
    def _group_id(year, direction_id, group_name):
        normalized = re.sub(
            r"[^0-9a-zа-я]+",
            "-",
            group_name.lower(),
        ).strip("-")

        return f"{year}:{direction_id}:{normalized}"

    @classmethod
    def _find_filter_block(cls, soup, title):
        for element in soup.select(
            ".filter > ul > li"
        ):
            label = element.find("b")

            if label is None:
                continue

            text = cls._normalize_text(
                label.get_text(
                    " ",
                    strip=True,
                )
            )

            if text == title:
                return element

        raise RuntimeError(
            f"Не найден блок фильтра: {title}"
        )

    def parse_years(self, html):
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        block = self._find_filter_block(
            soup,
            "Курс",
        )

        years = set()

        for link in block.select("a.option"):
            params = self._parse_query_params(
                link.get("href", "")
            )

            if "y" not in params:
                continue

            year = int(params["y"])

            if 2000 <= year <= 2100:
                years.add(year)

        return sorted(years)

    def parse_directions(self, html):
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        block = self._find_filter_block(
            soup,
            "Направление",
        )

        directions = {}

        for link in block.select("a.option"):
            params = self._parse_query_params(
                link.get("href", "")
            )

            up_id = params.get("up")

            if not up_id:
                continue

            raw_name = self._normalize_text(
                link.get_text(
                    " ",
                    strip=True,
                )
            )

            if raw_name.lower() == "не выбрано":
                continue

            name = self._normalize_direction_name(
                raw_name,
            )

            if not name:
                continue

            direction_id = self._direction_id(
                name,
            )

            if direction_id not in directions:
                directions[direction_id] = Direction(
                    id=direction_id,
                    name=name,
                )

            direction = directions[direction_id]

            if up_id not in direction.up_ids:
                direction.up_ids.append(up_id)

        return list(directions.values())

    def get_catalog(self):
        html = self._request(
            INDEX_URL,
            {
                "y": "2023",
                "k": "1",
                "f": "1",
                "up": "none",
            },
        )

        years = self.parse_years(html)

        catalog = []

        for year in years:
            html = self._request(
                INDEX_URL,
                {
                    "y": str(year),
                    "k": "1",
                    "f": "1",
                    "up": "none",
                },
            )

            directions = self.parse_directions(
                html,
            )

            catalog.append(
                Year(
                    year=year,
                    directions=directions,
                )
            )

        return catalog

    @staticmethod
    def _extract_student_ref(link):
        params = ParserService._parse_query_params(
            link.get("href", "")
        )

        student_id = params.get("stud")

        if not student_id:
            return None

        name = ParserService._normalize_text(
            link.get_text(
                " ",
                strip=True,
            )
        )

        if not name:
            return None

        return StudentRef(
            id=int(student_id),
            name=name,
        )

    @classmethod
    def _extract_group_name(cls, element):
        group_pattern = re.compile(
            r"\b[A-ZА-ЯЁ]{1,10}[-–]\d{4}\b"
        )

        text = cls._normalize_text(
            element.get_text(
                " ",
                strip=True,
            )
        )

        match = group_pattern.search(text)

        if match:
            return match.group(0)

        previous = element.find_previous(
            [
                "h2",
                "h3",
                "h4",
                "h5",
                "caption",
                "div",
            ]
        )

        if previous is not None:
            text = cls._normalize_text(
                previous.get_text(
                    " ",
                    strip=True,
                )
            )

            match = group_pattern.search(text)

            if match:
                return match.group(0)

        return None

    def parse_groups(
        self,
        html,
        year,
        direction,
    ):
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        groups = {}

        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                links = row.select(
                    'a[href*="stud_cd.php?stud="]'
                )

                if not links:
                    continue

                group_name = self._extract_group_name(
                    row,
                )

                if not group_name:
                    continue

                group_id = self._group_id(
                    year,
                    direction.id,
                    group_name,
                )

                if group_id not in groups:
                    groups[group_id] = Group(
                        id=group_id,
                        name=group_name,
                    )

                group = groups[group_id]

                for link in links:
                    student = self._extract_student_ref(
                        link,
                    )

                    if student is None:
                        continue

                    if not any(
                        existing.id == student.id
                        for existing in group.students
                    ):
                        group.students.append(
                            student,
                        )

        return list(groups.values())

    def get_groups(
        self,
        year,
        direction,
    ):
        groups = {}

        for up_id in direction.up_ids:
            html = self._request(
                INDEX_URL,
                {
                    "y": str(year),
                    "k": "1",
                    "f": "1",
                    "up": up_id,
                },
            )

            parsed_groups = self.parse_groups(
                html,
                year,
                direction,
            )

            for group in parsed_groups:
                if group.id not in groups:
                    groups[group.id] = group
                    continue

                existing = groups[group.id]

                for student in group.students:
                    if not any(
                        item.id == student.id
                        for item in existing.students
                    ):
                        existing.students.append(
                            student,
                        )

        return list(groups.values())

    @staticmethod
    def _parse_student_title(title):
        title = re.sub(
            r"\s+",
            " ",
            title,
        ).strip()

        match = re.match(
            r"(.+?)\s*\(([^)]+)\)",
            title,
        )

        if not match:
            return title, ""

        return (
            match.group(1).strip(),
            match.group(2).strip(),
        )

    @staticmethod
    def _parse_semester(row):
        cell = row.find(
            "td",
            class_="new_semestr",
        )

        if cell is None:
            return None

        match = re.search(
            r"(\d+)\s*семестр",
            cell.get_text(
                " ",
                strip=True,
            ),
            re.IGNORECASE,
        )

        if not match:
            return None

        return int(match.group(1))

    @classmethod
    def _parse_subject(cls, row):
        cell = row.find(
            "td",
            class_="align_left",
        )

        if cell is None:
            return None, None

        desktop = cell.find(
            "span",
            class_="no_mobile",
        )

        if desktop is None:
            return None, None

        text = cls._normalize_text(
            desktop.get_text(
                " ",
                strip=True,
            )
        )

        match = re.match(
            r"^(.*?)\s*"
            r"\(\s*"
            r"(Экзамен|Зачет|Дифференцированный зачет|Диф\.?\s*зачет)"
            r"\s*\)",
            text,
            re.IGNORECASE,
        )

        if not match:
            return None, None

        return (
            match.group(1).strip(),
            match.group(2).strip(),
        )

    @staticmethod
    def _parse_number(value):
        value = value.strip()

        if not value or value in {"-", "–"}:
            return None

        value = value.replace(
            ",",
            ".",
        )

        match = re.fullmatch(
            r"\s*(-?\d+(?:\.\d+)?)"
            r"(?:\s*\(\s*-?\d+(?:\.\d+)?\s*\))?\s*",
            value,
        )

        if match is None:
            return None

        number = float(
            match.group(1)
        )

        if number.is_integer():
            return int(number)

        return number

    def parse_student(
        self,
        html,
        student_id,
    ):
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        title = soup.find("h1")

        if title is None:
            raise RuntimeError(
                f"Не найден заголовок студента {student_id}"
            )

        name, group = self._parse_student_title(
            title.get_text(
                " ",
                strip=True,
            )
        )

        grades = []

        for table in soup.find_all(
            "table",
            class_="stud_cds",
        ):
            current_semester = None

            for row in table.find_all("tr"):
                semester = self._parse_semester(
                    row,
                )

                if semester is not None:
                    current_semester = semester
                    continue

                columns = row.find_all("td")

                if len(columns) < 7:
                    continue

                subject, control_type = self._parse_subject(
                    row,
                )

                if subject is None:
                    continue

                if len(columns) == 7:
                    kt4 = None
                    exam_index = 4
                    total_index = 5
                    grade_index = 6
                else:
                    kt4 = self._parse_number(
                        columns[4].get_text(
                            strip=True,
                        )
                    )
                    exam_index = 5
                    total_index = 6
                    grade_index = 7

                grades.append(
                    Grade(
                        semester=current_semester,
                        subject=subject,
                        control_type=control_type,
                        kt1=self._parse_number(
                            columns[1].get_text(
                                strip=True,
                            )
                        ),
                        kt2=self._parse_number(
                            columns[2].get_text(
                                strip=True,
                            )
                        ),
                        kt3=self._parse_number(
                            columns[3].get_text(
                                strip=True,
                            )
                        ),
                        kt4=kt4,
                        exam=self._parse_number(
                            columns[exam_index].get_text(
                                strip=True,
                            )
                        ),
                        total=self._parse_number(
                            columns[total_index].get_text(
                                strip=True,
                            )
                        ),
                        grade=columns[grade_index].get_text(
                            " ",
                            strip=True,
                        ),
                    )
                )

        return Student(
            id=student_id,
            name=name,
            group=group,
            grades=grades,
        )

    def get_student(
        self,
        student_id,
    ):
        html = self._request(
            STUDENT_URL,
            {
                "stud": str(student_id),
            },
        )

        return self.parse_student(
            html,
            student_id,
        )