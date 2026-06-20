"""
Thread-safe singleton Supabase admin client.

Avoids creating a new HTTP client on every request, which adds latency
and wastes connections. All routes share a single cached client instance.
"""

import os
import threading

_client = None
_lock = threading.Lock()


def get_supabase_admin():
    """Return the cached Supabase service-role client (initialised on first call)."""
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                from supabase import create_client
                url = os.environ.get('SUPABASE_URL', '')
                key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
                if not url or not key:
                    raise RuntimeError(
                        'SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set'
                    )
                _client = create_client(url, key)
    return _client
