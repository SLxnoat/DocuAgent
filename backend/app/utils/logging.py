import logging

from app.config import settings


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter to redact sensitive data such as secret keys, API tokens, and other credentials.
    """

    def __init__(self):
        super().__init__()
        # Collect sensitive values from settings
        self.sensitive_values = set()
        for attr in ["secret_key", "api_token", "ollama_api_key"]:
            value = getattr(settings, attr, None)
            if value:
                self.sensitive_values.add(value)

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Redact sensitive information from the log record.

        Args:
            record: The log record to filter.

        Returns:
            True to allow the record to be logged (always True for this filter).
        """
        # Redact in the message
        if record.msg:
            record.msg = self._redact(str(record.msg))

        # Redact in args if they are strings
        if record.args:
            record.args = tuple(
                self._redact(str(arg)) if isinstance(arg, str) else arg for arg in record.args
            )

        return True

    def _redact(self, message: str) -> str:
        """
        Replace sensitive values with '[REDACTED]' in the given message.

        Args:
            message: The log message string.

        Returns:
            The message with sensitive values redacted.
        """
        for value in self.sensitive_values:
            if value:
                message = message.replace(value, "[REDACTED]")
        return message
