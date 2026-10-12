from __future__ import annotations

from dotenv import load_dotenv

from analyzer import AnalyzerService
from core import CoreService
from database import Neo4jDatabase
from parser.service import ParserService


def main() -> None:
    load_dotenv()

    parser = ParserService()
    analyzer = AnalyzerService()

    with Neo4jDatabase() as database:
        database.verify_connectivity()

        core = CoreService(
            parser=parser,
            database=database,
            analyzer=analyzer,
        )

        catalog = core.ensure_catalog()

        total_directions = sum(
            len(year.directions)
            for year in catalog
        )

        print("Каталог готов.")
        print(f"Годов: {len(catalog)}")
        print(f"Направлений: {total_directions}")

        for year in catalog:
            print(
                f"{year.year}: "
                f"{len(year.directions)} направлений"
            )


if __name__ == "__main__":
    main()