"""
URL validation utilities for DocuAgent AI.
Provides protection against SSRF (Server-Side Request Forgery) attacks.
"""

import ipaddress
import socket
from urllib.parse import urlparse


def validate_target_url(url: str) -> None:
    """
    Validate a target URL to prevent SSRF attacks.
    Blocks loopback addresses and RFC 1918 private subnets.

    Args:
        url: The URL to validate

    Raises:
        ValueError: If the URL is invalid or points to a prohibited address
        socket.gaierror: If DNS resolution fails
    """
    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {e}") from e

    # Check if we have a hostname
    if not parsed.hostname:
        raise ValueError("URL must contain a hostname")

    # Get the hostname
    hostname = parsed.hostname

    # Check for obvious localhost patterns first (before DNS resolution)
    localhost_indicators = [
        "localhost",
        "localhost.localdomain",
        "localhost",
        "localhost",
    ]

    if hostname.lower() in localhost_indicators:
        raise ValueError("Loopback addresses are not allowed")

    # Resolve the hostname to IP addresses
    try:
        # Get all address info for the hostname
        addr_info = socket.getaddrinfo(
            hostname,
            None,  # Port doesn't matter for our check
            family=socket.AF_UNSPEC,  # Both IPv4 and IPv6
            type=socket.SOCK_STREAM,
            flags=socket.AI_CANONNAME,
        )
    except socket.gaierror as e:
        raise socket.gaierror(f"Could not resolve hostname '{hostname}': {e}") from e

    # Check each resolved IP address
    for _family, _, _, _, sockaddr in addr_info:
        ip_addr = sockaddr[0]

        try:
            ip = ipaddress.ip_address(ip_addr)
        except ValueError:
            # Skip invalid IP addresses (shouldn't happen from socket.getaddrinfo)
            continue

        # Check if IP is in prohibited ranges
        if _is_prohibited_ip(ip):
            raise ValueError(
                f"Access to {hostname} ({ip_addr}) is not allowed: "
                "loopback and private network addresses are prohibited"
            )


def _is_prohibited_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """
    Check if an IP address is in prohibited ranges (loopback or private).

    Args:
        ip: IP address to check

    Returns:
        True if the IP is prohibited, False otherwise
    """
    # Loopback addresses
    if ip.is_loopback:
        return True

    # Private addresses (RFC 1918 for IPv4, RFC 4193 for IPv6 unique local, RFC 4291 for IPv6 link-local)
    if ip.is_private:
        return True

    # Additional checks for specific ranges that might not be caught by is_private
    if ip.version == 4:
        # RFC 1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
        # Also block link-local (169.254.0.0/16) and reserved ranges
        if ip in ipaddress.IPv4Network("10.0.0.0/8"):
            return True
        if ip in ipaddress.IPv4Network("172.16.0.0/12"):
            return True
        if ip in ipaddress.IPv4Network("192.168.0.0/16"):
            return True
        # Link-local
        if ip in ipaddress.IPv4Network("169.254.0.0/16"):
            return True
        # Reserved/IETF protocol assignments
        if ip in ipaddress.IPv4Network("0.0.0.0/8"):  # "This" network
            return True
        if ip in ipaddress.IPv4Network(
            "127.0.0.0/8"
        ):  # Loopback (already covered by is_loopback but being explicit)
            return True
        if ip in ipaddress.IPv4Network("192.0.0.0/24"):  # IETF protocol assignments
            return True
        if ip in ipaddress.IPv4Network("192.0.2.0/24"):  # TEST-NET-1
            return True
        if ip in ipaddress.IPv4Network("198.18.0.0/15"):  # Network benchmark testing
            return True
        if ip in ipaddress.IPv4Network("198.51.100.0/24"):  # TEST-NET-2
            return True
        if ip in ipaddress.IPv4Network("203.0.113.0/24"):  # TEST-NET-3
            return True
        if ip in ipaddress.IPv4Network("224.0.0.0/4"):  # Multicast
            return True
        if ip in ipaddress.IPv4Network("240.0.0.0/4"):  # Reserved
            return True
        if ip in ipaddress.IPv4Network("255.255.255.255/32"):  # Limited broadcast
            return True

    elif ip.version == 6:
        # IPv6 unique local (fc00::/7)
        if ip in ipaddress.IPv6Network("fc00::/7"):
            return True
        # IPv6 link-local (fe80::/10)
        if ip in ipaddress.IPv6Network("fe80::/10"):
            return True
        # IPv6 loopback (::1/128) - already covered by is_loopback
        # IPv6 unspecified (::/128)
        if ip == ipaddress.IPv6Address("::"):
            return True
        # IPv6 multicast (ff00::/8)
        if ip in ipaddress.IPv6Network("ff00::/8"):
            return True
        # IPv6 reserved (2001:db8::/32 for documentation)
        if ip in ipaddress.IPv6Network("2001:db8::/32"):
            return True
        # IPv6 6to4 relay anycast (2002:a00::/24)
        if ip in ipaddress.IPv6Network("2002:a00::/24"):
            return True

    return False
