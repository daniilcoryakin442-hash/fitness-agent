# db/client.py — подключение к Supabase

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

_client: Client = None

def get_client() -> Client:
    global _client
    if _client is None:
        print(f"[supabase] connecting to {SUPABASE_URL}")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[supabase] connected!")
    return _client
