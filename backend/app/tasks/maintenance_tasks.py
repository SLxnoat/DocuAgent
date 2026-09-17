"""
Maintenance tasks for DocuAgent AI Celery workers.
"""

from pathlib import Path

from celery.utils.log import get_task_logger

from app.celery import celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.maintenance_tasks.cleanup_old_assets")
def cleanup_old_assets(self, max_age_hours: int = 24):
    """
    Celery task to clean up old asset files.

    Args:
        max_age_hours: Maximum age of files to keep in hours

    Returns:
        dict: Result containing cleanup statistics
    """
    try:
        logger.info(f"Starting cleanup of assets older than {max_age_hours} hours")

        from app.config import settings

        assets_dir = Path(settings.assets_dir)

        if not assets_dir.exists():
            return {
                "success": True,
                "message": "Assets directory does not exist",
                "files_removed": 0,
                "space_freed_mb": 0,
            }

        # Import time for age calculation
        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        files_removed = 0
        space_freed = 0

        # Walk through assets directory
        for file_path in assets_dir.rglob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        files_removed += 1
                        space_freed += file_size
                        logger.debug(f"Removed old asset: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove {file_path}: {e}")

        space_freed_mb = space_freed / (1024 * 1024)

        logger.info(
            f"Cleanup completed: {files_removed} files removed, " f"{space_freed_mb:.2f} MB freed"
        )

        return {
            "success": True,
            "files_removed": files_removed,
            "space_freed_mb": round(space_freed_mb, 2),
            "message": f"Cleaned up {files_removed} old asset files",
        }

    except Exception as exc:
        logger.error(f"Asset cleanup failed: {exc}")
        raise self.retry(exc=exc) from exc


@celery_app.task(name="app.tasks.maintenance_tasks.health_check")
def health_check():
    """
    Celery task to perform a health check on the worker.

    Returns:
        dict: Health check results
    """
    try:
        # Check Redis connection
        import redis

        from app.config import settings

        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        redis_status = "healthy"

        # Check disk space
        import shutil

        disk_usage = shutil.disk_usage("/")
        disk_free_gb = disk_usage.free / (1024**3)
        disk_status = "healthy" if disk_free_gb > 1.0 else "warning"  # Warn if less than 1GB free

        return {
            "success": True,
            "redis_status": redis_status,
            "disk_free_gb": round(disk_free_gb, 2),
            "disk_status": disk_status,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return {
            "success": False,
            "error": str(exc),
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }


@celery_app.task(bind=True, name="app.tasks.maintenance_tasks.rotate_logs")
def rotate_logs(self, max_size_mb: int = 100):
    """
    Celery task to rotate log files if they exceed maximum size.

    Args:
        max_size_mb: Maximum log file size in MB before rotation

    Returns:
        dict: Result containing rotation statistics
    """
    try:
        logger.info(f"Starting log rotation for files over {max_size_mb} MB")
        logs_rotated = 0

        # This would integrate with the actual logging system
        # For now, we'll just return a placeholder
        logger.info("Log rotation completed (placeholder implementation)")

        return {
            "success": True,
            "logs_rotated": logs_rotated,
            "message": f"Log rotation checked for files over {max_size_mb} MB",
        }

    except Exception as exc:
        logger.error(f"Log rotation failed: {exc}")
        raise self.retry(exc=exc) from exc
