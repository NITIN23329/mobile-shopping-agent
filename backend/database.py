import logging
import os
import random
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, ClientOptions, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Supabase credentials are not configured. Set SUPABASE_URL and one of SUPABASE_SERVICE_ROLE_KEY, SUPABASE_KEY, or SUPABASE_ANON_KEY."
    )

TABLE_NAME =  "phones"

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options=ClientOptions(postgrest_client_timeout=30),
)

logger = logging.getLogger(__name__)

MAX_SUPABASE_RETRIES = int(os.getenv("SUPABASE_MAX_RETRIES", "3"))
RETRY_BACKOFF_BASE = float(os.getenv("SUPABASE_RETRY_BASE_SECONDS", "0.5"))
RETRY_BACKOFF_CAP = float(os.getenv("SUPABASE_RETRY_CAP_SECONDS", "4"))


@dataclass
class PhoneRecord:
    """Data transfer object mirroring the `phones` table."""

    id: str
    brand_name: str
    phone_name: str
    image_url: Optional[str] = None
    price: Optional[str] = None
    spotlight: Dict[str, Any] = field(default_factory=dict)
    all_specs: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "PhoneRecord":
        return cls(
            id=row.get("id"),
            brand_name=row.get("brand_name"),
            phone_name=row.get("phone_name"),
            image_url=row.get("image_url"),
            price=row.get("price"),
            spotlight=row.get("spotlight") or {},
            all_specs=row.get("all_specs") or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _execute(query) -> List[PhoneRecord]:
    last_error: Optional[Exception] = None
    for attempt in range(1, MAX_SUPABASE_RETRIES + 1):
        try:
            response = query.execute()
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning(
                "Supabase query failed (attempt %s/%s): %s",
                attempt,
                MAX_SUPABASE_RETRIES,
                exc,
            )
            if attempt >= MAX_SUPABASE_RETRIES:
                raise RuntimeError(f"Supabase query failed after {MAX_SUPABASE_RETRIES} attempts: {exc}") from exc

            backoff = min(RETRY_BACKOFF_BASE * (2 ** (attempt - 1)), RETRY_BACKOFF_CAP)
            jitter = random.uniform(0, 0.3)
            time.sleep(backoff + jitter)
    else:
        if last_error:
            raise RuntimeError(f"Supabase query failed: {last_error}") from last_error
        raise RuntimeError("Supabase query failed: unknown error")

    data = getattr(response, "data", None)
    if not isinstance(data, list):
        return []
    return [PhoneRecord.from_row(row) for row in data]


def get_all_phones() -> List[PhoneRecord]:
    """Return every phone row from Supabase as DTOs."""

    return _execute(supabase.table(TABLE_NAME).select("*"))


def search_phones(filters: Dict[str, Any]) -> List[PhoneRecord]:
    """Fetch phones with light filtering (brand/phone name)."""

    query = supabase.table(TABLE_NAME).select("*")

    brand = filters.get("brand")
    if brand:
        query = query.eq("brand_name", brand)

    name = filters.get("phone_name") or filters.get("model")
    if name:
        query = query.ilike("phone_name", f"%{name}%")

    return _execute(query)


def get_phone_by_id(phone_id: str) -> Optional[PhoneRecord]:
    """Return a single phone row by its ID."""

    data = _execute(
        supabase.table(TABLE_NAME)
        .select("*")
        .eq("id", phone_id)
        .limit(1)
    )
    return data[0] if data else None


def get_phone_by_model(model_name: str) -> Optional[PhoneRecord]:
    """Return the first phone whose name matches the provided text."""

    data = _execute(
        supabase.table(TABLE_NAME)
        .select("*")
        .ilike("phone_name", f"%{model_name}%")
        .limit(1)
    )
    return data[0] if data else None


def refresh_phone_cache() -> List[PhoneRecord]:
    """No-op placeholder to maintain previous API; returns current rows."""

    return get_all_phones()

