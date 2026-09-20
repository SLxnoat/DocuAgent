"""
Unit tests for app/utils/logging.py SensitiveDataFilter.
Verifies redaction of API tokens, secret keys, and passwords from logs.
"""

import logging

from app.utils.logging import SensitiveDataFilter


def test_sensitive_data_filter_redacts_tokens():
    filt = SensitiveDataFilter()
    filt.sensitive_values.add("super-secret-token")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Connecting with token super-secret-token to API",
        args=(),
        exc_info=None,
    )

    filt.filter(record)
    assert "super-secret-token" not in record.msg
    assert "[REDACTED]" in record.msg


def test_sensitive_data_filter_redacts_args():
    filt = SensitiveDataFilter()
    filt.sensitive_values.add("my-secret-password")

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="User login with %s",
        args=("my-secret-password", 123),
        exc_info=None,
    )

    filt.filter(record)
    assert record.args[0] == "[REDACTED]"
    assert record.args[1] == 123
