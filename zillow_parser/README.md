# Zillow Agents Parser (Django starter)

A Django project with application (`zillow_agents_parser_app`) and Postgress
application-owned database table (`agents`). It supports a two-stage workflow:

1. Search/listing stage: read locations from `sources/search_locations.txt`,
   retrieve paginated agent cards, and extract profile URLs.
2. Profile stage: visit each profile through an authorized data source and
   extract extended agent information plus sales history.
3. Save each successful profile immediately to PostgreSQL. Sales history is
   stored as JSON in the same `agents` row, so no additional business tables
   are created.
