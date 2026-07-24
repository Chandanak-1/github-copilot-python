import json
from typing import Any, Dict, List


def normalize_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'name': str(entry.get('name', 'Anonymous')).strip() or 'Anonymous',
        'time': int(entry.get('time') or 0),
        'difficulty': str(entry.get('difficulty', 'medium')),
        'hints': int(entry.get('hints') or 0),
    }


def sort_leaderboard(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = [normalize_entry(entry) for entry in entries]
    return sorted(normalized, key=lambda item: item['time'])


def top_entries(entries: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    return sort_leaderboard(entries)[:limit]


def add_entry(entries: List[Dict[str, Any]], entry: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
    return top_entries(entries + [entry], limit)


def parse_storage(raw: str) -> List[Dict[str, Any]]:
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return []
    if not isinstance(data, list):
        return []
    return sort_leaderboard(data)
