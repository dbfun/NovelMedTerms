#!/usr/bin/bash

set -euo pipefail

##########################################################################################################
#
# Восстановление эксперимента из бекапа.
#
# Использование:
#   ./restore-backup.sh "workflows/Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0"
#
##########################################################################################################

BACKUP_DIR="$1"
BACKUP_FILE="${BACKUP_DIR}/novel-medterms.sql"

if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo "❌ Ошибка: файл бекапа не найден:"
  echo "  ${BACKUP_FILE}"
  exit 1
fi

docker compose exec -T -e PGPASSWORD=secret postgres psql \
  -U default \
  -d novel-medterms \
  < "${BACKUP_FILE}"

echo "♻️  База данных восстановлена"