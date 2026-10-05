from dotenv import load_dotenv

from analyzer import AnalyzerService
from core import CoreService
from database import Neo4jDatabase
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

        catalog = core.initialize_catalog()

        print(
            f"Получено годов: {len(catalog)}"
        )

        directions = database.get_directions(
            2023,
        )

        for direction in directions:
            if (
                direction.name
                == "Прикладная математика и информатика"
            ):
                print(
                    "Направление:",
                    direction.name,
                )
                print(
                    "up_ids:",
                    direction.up_ids,
                )


if __name__ == "__main__":
    main()