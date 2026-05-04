.PHONY: help up down restart build logs db-logs ps backup db-shell

help:
	@echo "Garmin MCP Server — Docker Compose Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  up           Start DB + scraper (detached)"
	@echo "  down         Stop all services"
	@echo "  restart      Restart scraper only"
	@echo "  build        Rebuild scraper image (no cache)"
	@echo "  logs         Tail scraper logs"
	@echo "  db-logs      Tail TimescaleDB logs"
	@echo "  ps           Show service status"
	@echo "  backup       Trigger backup to Google Drive now"
	@echo "  db-shell     Open psql shell (timescaledb)"
	@echo "  help         Show this message"

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart scraper

build:
	docker compose build --no-cache scraper

logs:
	docker compose logs -f scraper

db-logs:
	docker compose logs -f timescaledb

ps:
	docker compose ps

backup:
	docker compose exec scraper bash -c "pg_dump $$TIMESCALE_URL | gzip > /tmp/manual_backup.sql.gz && rclone copy /tmp/manual_backup.sql.gz gdrive-garmin:garmin-health-backup/ && rm /tmp/manual_backup.sql.gz"

db-shell:
	docker compose exec timescaledb psql -U garmin -d garmin
