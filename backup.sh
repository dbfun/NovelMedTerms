#!/usr/bin/bash

set -euo pipefail

##########################################################################################################
#
# Снятие бекапа для быстрого восстановления эксперимента.
#
# Использование:
#   ./backup.sh "workflows/Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0"
#
##########################################################################################################

BACKUP_DIR="$1"
BACKUP_FILE="${BACKUP_DIR}/novel-medterms.sql"

if [[ -z "${BACKUP_DIR}" ]]; then
  echo "❌ Ошибка: не указан каталог для сохранения бекапа"
  exit 1
fi

# Создаём каталог, если его нет
mkdir -p "${BACKUP_DIR}"

docker compose exec -T postgres pg_dump \
  -U default \
  -d novel-medterms \
  --clean \
  --if-exists \
  > "${BACKUP_FILE}"

echo "📦 Бекап сохранен: ${BACKUP_FILE}"