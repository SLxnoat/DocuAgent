#!/usr/bin/env bash
# ==============================================================================
# DocuAgent AI — Redis RDB Automated Backup Script
# Creates timestamped snapshot backups of Redis database and rotates old archives
# Usage in cron: 0 2 * * * /path/to/DocuAgent/scripts/backup_redis.sh >> /var/log/docuagent-backup.log 2>&1
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${REDIS_BACKUP_DIR:-/var/backups/docuagent/redis}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
BACKUP_FILE="${BACKUP_DIR}/dump_${TIMESTAMP}.rdb"
REDIS_CONTAINER="${REDIS_CONTAINER:-docuagent-redis}"

mkdir -p "${BACKUP_DIR}"

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Starting Redis backup for container: ${REDIS_CONTAINER}..."

# Trigger asynchronous BGSAVE in Redis
docker exec "${REDIS_CONTAINER}" redis-cli bgsave || true

# Wait for background save to finish
while [ "$(docker exec "${REDIS_CONTAINER}" redis-cli lastsave)" = "" ]; do
    sleep 1
done

# Copy dump.rdb from container to backup directory
docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${BACKUP_FILE}"

# Compress archive
gzip -f "${BACKUP_FILE}"
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Backup created successfully: ${BACKUP_FILE}.gz"

# Rotate backups older than retention window
echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Rotating backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -type f -name "dump_*.rdb.gz" -mtime +"${RETENTION_DAYS}" -exec rm -f {} +

echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Redis backup and retention cycle complete."
