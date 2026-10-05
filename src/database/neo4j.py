from __future__ import annotations

import os

from neo4j import GraphDatabase

from models import Direction, Group, StudentRef, Year


class Neo4jDatabase:
    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ):
        self._uri = uri or os.getenv(
            "NEO4J_URI",
            "bolt://localhost:7687",
        )
        self._user = user or os.getenv(
            "NEO4J_USER",
            "neo4j",
        )
        self._password = password or os.getenv(
            "NEO4J_PASSWORD",
        )
        self._database = database or os.getenv(
            "NEO4J_DATABASE",
            "neo4j",
        )

        self._driver = GraphDatabase.driver(
            self._uri,
            auth=(self._user, self._password),
        )

    def verify_connectivity(self):
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def create_constraints(self):
        queries = [
            """
            CREATE CONSTRAINT year_year_unique IF NOT EXISTS
            FOR (y:Year)
            REQUIRE y.year IS UNIQUE
            """,
            """
            CREATE CONSTRAINT direction_id_unique IF NOT EXISTS
            FOR (d:Direction)
            REQUIRE d.id IS UNIQUE
            """,
            """
            CREATE CONSTRAINT group_id_unique IF NOT EXISTS
            FOR (g:Group)
            REQUIRE g.id IS UNIQUE
            """,
            """
            CREATE CONSTRAINT student_id_unique IF NOT EXISTS
            FOR (s:Student)
            REQUIRE s.id IS UNIQUE
            """,
        ]

        for query in queries:
            self._driver.execute_query(
                query,
                database_=self._database,
            )

    def get_years(self) -> list[int]:
        records, _, _ = self._driver.execute_query(
            """
            MATCH (y:Year)
            RETURN y.year AS year
            ORDER BY y.year
            """,
            database_=self._database,
        )

        return [
            record["year"]
            for record in records
        ]

    def get_directions(
        self,
        year: int,
    ) -> list[Direction]:
        records, _, _ = self._driver.execute_query(
            """
            MATCH (y:Year {year: $year})
                  -[r:HAS_DIRECTION]->
                  (d:Direction)

            RETURN d.id AS id,
                   d.name AS name,
                   r.up_ids AS up_ids

            ORDER BY d.name
            """,
            year=year,
            database_=self._database,
        )

        return [
            Direction(
                id=record["id"],
                name=record["name"],
                up_ids=record["up_ids"] or [],
            )
            for record in records
        ]

    def get_groups(
        self,
        year: int,
        direction_id: str,
    ) -> list[Group]:
        records, _, _ = self._driver.execute_query(
            """
            MATCH (y:Year {year: $year})
                  -[:HAS_DIRECTION]->
                  (d:Direction {id: $direction_id})
                  -[:HAS_GROUP]->
                  (g:Group)

            RETURN g.id AS id,
                   g.name AS name

            ORDER BY g.name
            """,
            year=year,
            direction_id=direction_id,
            database_=self._database,
        )

        return [
            Group(
                id=record["id"],
                name=record["name"],
            )
            for record in records
        ]

    def get_students(
        self,
        group_id: str,
    ) -> list[StudentRef]:
        records, _, _ = self._driver.execute_query(
            """
            MATCH (g:Group {id: $group_id})
                  -[:HAS_STUDENT]->
                  (s:Student)

            RETURN s.id AS id,
                   s.name AS name

            ORDER BY s.name
            """,
            group_id=group_id,
            database_=self._database,
        )

        return [
            StudentRef(
                id=record["id"],
                name=record["name"],
            )
            for record in records
        ]

    def save_catalog(
        self,
        catalog: list[Year],
    ):
        data = [
            {
                "year": item.year,
                "directions": [
                    {
                        "id": direction.id,
                        "name": direction.name,
                        "up_ids": direction.up_ids,
                    }
                    for direction in item.directions
                ],
            }
            for item in catalog
        ]

        self._driver.execute_query(
            """
            UNWIND $catalog AS year_data

            MERGE (y:Year {year: year_data.year})

            WITH y, year_data

            UNWIND year_data.directions AS direction_data

            MERGE (d:Direction {id: direction_data.id})

            SET d.name = direction_data.name

            REMOVE d.up_ids

            MERGE (y)-[r:HAS_DIRECTION]->(d)

            SET r.up_ids = direction_data.up_ids
            """,
            catalog=data,
            database_=self._database,
        )

    def save_groups(
        self,
        year: int,
        direction_id: str,
        groups: list[Group],
    ):
        data = [
            {
                "id": group.id,
                "name": group.name,
                "students": [
                    {
                        "id": student.id,
                        "name": student.name,
                    }
                    for student in group.students
                ],
            }
            for group in groups
        ]

        self._driver.execute_query(
            """
            MATCH (y:Year {year: $year})
                  -[:HAS_DIRECTION]->
                  (d:Direction {id: $direction_id})

            UNWIND $groups AS group_data

            MERGE (g:Group {id: group_data.id})

            SET g.name = group_data.name

            MERGE (d)-[:HAS_GROUP]->(g)

            WITH g, group_data

            UNWIND group_data.students AS student_data

            MERGE (s:Student {id: student_data.id})

            SET s.name = student_data.name

            MERGE (g)-[:HAS_STUDENT]->(s)
            """,
            year=year,
            direction_id=direction_id,
            groups=data,
            database_=self._database,
        )