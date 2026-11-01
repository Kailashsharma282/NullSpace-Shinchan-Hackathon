import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("10.0.0.0/8"),        # RFC 1918 Private
    ipaddress.ip_network("172.16.0.0/12"),     # RFC 1918 Private
    ipaddress.ip_network("192.168.0.0/16"),    # RFC 1918 Private
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / Cloud Metadata
    ipaddress.ip_network("0.0.0.0/8"),         # Current network
    ipaddress.ip_network("100.64.0.0/10"),     # Shared Address Space
    ipaddress.ip_network("192.0.0.0/24"),      # IETF Protocol Assignments
    ipaddress.ip_network("198.18.0.0/15"),     # Benchmarking
    ipaddress.ip_network("224.0.0.0/4"),       # Multicast
    ipaddress.ip_network("240.0.0.0/4"),       # Reserved
    # IPv6
    ipaddress.ip_network("::1/128"),           # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),         # IPv6 Link-Local
]

def is_ip_allowed(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            return False
        for net in BLOCKED_IP_NETWORKS:
            if ip in net:
                return False
        return True
    except ValueError:
        return False

def validate_url_for_ssrf(url: str) -> Tuple[bool, str]:
    """
    Validates URL scheme, resolves hostname to IP, checks against private/link-local ranges.
    Returns (is_valid, reason).
    """
    try:
        parsed = urlparse(url.strip())
    except Exception as e:
        return False, f"Malformed URL: {str(e)}"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported scheme: {parsed.scheme}. Only HTTP/HTTPS permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL contains no valid host name."

    # Block common internal names
    blocked_hostnames = {"localhost", "metadata", "metadata.google.internal", "instance-data"}
    if hostname.lower() in blocked_hostnames or hostname.lower().endswith(".local") or hostname.lower().endswith(".internal"):
        return False, f"Access to internal host '{hostname}' is forbidden (SSRF protection)."

    # Resolve IP address
    try:
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
        addr_info = socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        if not addr_info:
            return False, f"Unable to resolve hostname '{hostname}'."
        
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            if not is_ip_allowed(ip_str):
                return False, f"Access to IP address {ip_str} for host '{hostname}' is blocked (SSRF protection)."
    except socket.gaierror as e:
        return False, f"DNS resolution failed for '{hostname}': {str(e)}"
    except Exception as e:
        return False, f"URL validation check failed: {str(e)}"

    return True, "URL passed security checks."

