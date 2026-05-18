#!/bin/bash

# Database backup script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
DB_NAME="adrite_db"
DB_USER="postgres"

# Create backups folder if not exists
mkdir -p $BACKUP_DIR

# Create backup
echo "Starting backup..."
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_DIR/backup_$DATE.sql"
else
    echo "Backup failed!"
    exit 1
fi

# Delete backups older than 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
echo "Old backups cleaned up"