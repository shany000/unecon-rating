# UNEcon Rating

Веб-приложение для анализа успеваемости студентов Санкт-Петербургского государственного экономического университета.

## Запуск проекта

**1. Клонировать репозиторий**

```bash
git clone https://github.com/shany000/unecon-rating.git
cd unecon-rating
```

**2. Настроить окружение**

Создать файл `.env` на основе шаблона `.env.example`:

```powershell
Copy-Item .env.example .env
```

При необходимости изменить настройки подключения к базе данных в `.env`.

**3. Запустить проект**

```bash
docker compose up --build -d
```

## Адреса

- **Веб-приложение:** http://localhost:8501
- **Neo4j Browser:** http://localhost:7474
- **Подключение к базе данных:** `bolt://localhost:7687`

Для входа в Neo4j Browser используйте логин и пароль из `.env`.

## Остановка проекта

```bash
docker compose down
```

Данные базы данных сохраняются в Docker volumes.
