import json

import leaderboard


def test_normalize_entry_defaults_anonymous_and_safe_values():
    entry = leaderboard.normalize_entry({'time': '120', 'difficulty': 'hard'})

    assert entry['name'] == 'Anonymous'
    assert entry['time'] == 120
    assert entry['difficulty'] == 'hard'
    assert entry['hints'] == 0


def test_sort_leaderboard_sorts_by_numeric_time():
    entries = [
        {'name': 'B', 'time': 150, 'difficulty': 'easy', 'hints': 1},
        {'name': 'A', 'time': 90, 'difficulty': 'hard', 'hints': 2},
        {'name': 'C', 'time': 120, 'difficulty': 'medium', 'hints': 0},
    ]

    sorted_entries = leaderboard.sort_leaderboard(entries)

    assert [e['name'] for e in sorted_entries] == ['A', 'C', 'B']


def test_top_entries_keeps_only_ten_fastest_times():
    entries = [
        {'name': str(i), 'time': i * 10, 'difficulty': 'easy', 'hints': 0}
        for i in range(12)
    ]

    top = leaderboard.top_entries(entries)

    assert len(top) == 10
    assert top[0]['time'] == 0
    assert top[-1]['time'] == 90


def test_add_entry_inserts_entry_and_limits_to_ten():
    entries = [
        {'name': str(i), 'time': i * 10, 'difficulty': 'medium', 'hints': 0}
        for i in range(9)
    ]
    new_entry = {'name': 'Winner', 'time': 5, 'difficulty': 'hard', 'hints': 1}

    updated = leaderboard.add_entry(entries, new_entry)

    assert len(updated) == 10
    assert updated[1]['name'] == 'Winner'
    assert updated[-1]['time'] == 80


def test_parse_storage_returns_empty_on_invalid_json():
    assert leaderboard.parse_storage('not json') == []


def test_parse_storage_returns_sorted_list_for_valid_json():
    raw = json.dumps([
        {'name': 'A', 'time': 200, 'difficulty': 'easy', 'hints': 2},
        {'name': 'B', 'time': 100, 'difficulty': 'hard', 'hints': 0},
    ])

    parsed = leaderboard.parse_storage(raw)

    assert parsed[0]['name'] == 'B'
    assert parsed[1]['name'] == 'A'
