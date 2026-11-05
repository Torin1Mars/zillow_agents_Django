# Zillow Agents Parser (Django starter)

A Django project with one application (`zillow_agents_parser_app`) and one
application-owned database table (`agents`). It supports a two-stage workflow:

1. Search/listing stage: read locations from `sources/search_locations.txt`,
   retrieve paginated agent cards, and extract profile URLs.
2. Profile stage: visit each profile through an authorized data source and
   extract extended agent information plus sales history.
3. Save each successful profile immediately to PostgreSQL. Sales history is
   stored as JSON in the same `agents` row, so no additional business tables
   are created.

## Important source-access requirement

The supplied parser logic was designed around Zillow's `__NEXT_DATA__` page
payload. Zillow's terms may restrict automated scraping. This starter defaults
`AUTHORIZED_DATA_SOURCE=false` and will not make HTTP requests until you have
confirmed that your API/provider/license permits this access and explicitly
set it to `true`. Configure `ZILLOW_SEARCH_URL_TEMPLATE` for that authorized
source. It must contain `{location}` and return compatible page data, or adapt
`services/page_fetcher.py` and the parsing paths to the provider's response.

Do not use this project to bypass CAPTCHAs, access controls, rate limits, or
other restrictions.

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

## Run both Django and parser from one IDE launch

Configure the IDE to run `launch_dev.py` from the project root. It starts:
- Django development server at http://127.0.0.1:8000/
- parser worker as a separate process

Both processes write INFO-level logs to the IDE console. The parser also writes
to `logs/parser.log`.

Alternatively, run them separately in two IDE terminal tabs:

- `python manage.py runserver`
- `python manage.py run_zillow_parser`

The parser command supports `--once` to process the configured locations once.
Without `--once`, it repeats the configured location list after a pause.

## One-table data model

`Agent` stores general-card fields, extended profile fields, and
`sales_history` (PostgreSQL JSONField) in one row. `profile_url` is unique.
A stable Zillow/provider ID is stored when available.

## Notes

- The supplied parser's original JSON-file intermediate output is replaced by
  immediate PostgreSQL upserts.
- The search-location list drives Stage 1. Each extracted card's `url` drives
  Stage 2. This matches the two-stage parser logic you supplied.
- The exact search URL template and response schema were not included in the
  supplied code, so those remain configuration/provider-specific.
- The parser is sequential and intentionally conservative. Delays are
  configurable; they are not intended to evade access controls.
