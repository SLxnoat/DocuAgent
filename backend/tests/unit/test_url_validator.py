"""
Unit tests for SSRF URL validation utilities.
"""

from __future__ import annotations

import ipaddress

import pytest

from app.utils.url_validator import _is_prohibited_ip, validate_target_url


def test_valid_public_urls():
    """Verify that legitimate public HTTPS/HTTP URLs pass validation."""
    public_urls = [
        "https://example.com",
        "https://www.google.com/search?q=test",
        "http://github.com",
        "https://api.stripe.com/v1/charges",
    ]
    for url in public_urls:
        # Should not raise
        validate_target_url(url)


def test_block_loopback_addresses():
    """Verify that localhost and loopback IPv4/IPv6 are strictly blocked."""
    loopback_urls = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost.localdomain",
        "http://127.0.0.1",
        "http://127.0.0.1:8080",
        "http://127.0.1.1",
        "http://[::1]",
    ]
    for url in loopback_urls:
        with pytest.raises(ValueError) as exc_info:
            validate_target_url(url)
        assert any(
            phrase in str(exc_info.value).lower()
            for phrase in ["loopback", "prohibited", "not allowed"]
        )


def test_block_rfc1918_private_networks():
    """Verify that RFC 1918 private subnets are blocked."""
    private_urls = [
        # 10.0.0.0/8
        "http://10.0.0.1",
        "http://10.254.254.254:3000",
        # 172.16.0.0/12
        "http://172.16.0.1",
        "http://172.31.255.255",
        # 192.168.0.0/16
        "http://192.168.1.1",
        "http://192.168.100.50:8080",
    ]
    for url in private_urls:
        with pytest.raises(ValueError) as exc_info:
            validate_target_url(url)
        assert "not allowed" in str(exc_info.value).lower()


def test_block_cloud_metadata_endpoints():
    """Verify that AWS/GCP/Azure link-local metadata (169.254.169.254) is blocked."""
    metadata_urls = [
        "http://169.254.169.254/latest/meta-data/",
        "http://169.254.169.254/computeMetadata/v1/",
    ]
    for url in metadata_urls:
        with pytest.raises(ValueError):
            validate_target_url(url)


def test_invalid_url_format():
    """Verify that malformed URLs raise ValueError."""
    invalid_urls = [
        "not-a-url",
        "://missing-scheme",
        "http://",
    ]
    for url in invalid_urls:
        with pytest.raises(ValueError):
            validate_target_url(url)


def test_is_prohibited_ip_direct():
    """Verify the internal _is_prohibited_ip function directly."""
    assert _is_prohibited_ip(ipaddress.ip_address("127.0.0.1")) is True
    assert _is_prohibited_ip(ipaddress.ip_address("10.0.0.1")) is True
    assert _is_prohibited_ip(ipaddress.ip_address("172.16.0.1")) is True
    assert _is_prohibited_ip(ipaddress.ip_address("192.168.1.1")) is True
    assert _is_prohibited_ip(ipaddress.ip_address("169.254.169.254")) is True
    assert _is_prohibited_ip(ipaddress.ip_address("8.8.8.8")) is False
    assert _is_prohibited_ip(ipaddress.ip_address("1.1.1.1")) is False
