# Zillow Agents Parser (Django)

A Django project with application (`zillow_agents_parser_app`) and Postgress
application-owned database table (`agents`). It supports a two-stage workflow:

1. Search/listing stage: read locations from `sources/search_locations.txt`,
   retrieve paginated agent cards, and extract profile URLs.
2. Profile stage: visit each profile through an authorized data source and
   extract extended agent information plus sales history.
3. Save each successful profile immediately to PostgreSQL. Sales history is
   stored as JSON in the same `agents` row, so no additional business tables
   are created.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in Django/PostgreSQL settings.
4. Create the PostgreSQL database named in `DB_NAME`.
5. Set `AUTHORIZED_DATA_SOURCE=true` only after confirming authorization.
6. Configure `ZILLOW_SEARCH_URL_TEMPLATE`.
7. Add one search location per line in `zillow_agents_parser_app/sources/search_locations.txt`.
8. Run migrations: `python manage.py makemigrations zillow_agents_parser_app`
9. Apply migrations: `python manage.py migrate`
10. Create an admin user if needed: `python manage.py createsuperuser`

## One-table data model

`Agent` stores general-card fields, extended profile fields, and
`sales_history` (PostgreSQL JSONField) in one row. `profile_url` is unique.
A stable Zillow/provider ID is stored when available.

## Notes

- The supplied parser's original JSON-file intermediate output is replaced by
  immediate PostgreSQL upserts.
- The search-location list drives Stage 1. Each extracted card's `url` drives
  Stage 2. This matches the two-stage parser logic you supplied.
- The parser is sequential and intentionally conservative. Delays are
  configurable; they are not intended to evade access controls.
