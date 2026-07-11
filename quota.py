from collections import defaultdict
from datetime import datetime, timezone


class QuotaStore:
    def __init__(self):
        self._usage: dict[str, dict[str, int]] = defaultdict(dict)
        self._subscribed_user_ids: set[str] = set()

    def _current_month_key(self) -> str:
        now = datetime.now(timezone.utc)
        return f"{now.year}-{now.month:02d}"

    def get_usage_this_month(self, user_id: str) -> int:
        return self._usage[user_id].get(self._current_month_key(), 0)

    def record_usage(self, user_id: str) -> None:
        key = self._current_month_key()
        self._usage[user_id][key] = self._usage[user_id].get(key, 0) + 1

    def is_subscribed(self, user_id: str) -> bool:
        return user_id in self._subscribed_user_ids

    def set_subscribed(self, user_id: str, subscribed: bool) -> None:
        if subscribed:
            self._subscribed_user_ids.add(user_id)
        else:
            self._subscribed_user_ids.discard(user_id)
