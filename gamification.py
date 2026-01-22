"""Gamification engine for the Python Learning Quest notebook.

Design goals:
- Simple, beginner-friendly API: `game`, `tracker.start(...)`, `tracker.complete(...)`.
- Persistence via JSON so progress survives kernel restarts.
- No required UI dependencies (works in plain Python + Jupyter).

This module is intentionally lightweight and testable.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


_DIFFICULTY_XP: dict[str, int] = {
    "Basic": 10,
    "Intermediate": 25,
    "Advanced": 50,
}


def _today_iso() -> str:
    import datetime

    return datetime.date.today().isoformat()


def _yesterday_iso() -> str:
    import datetime

    return (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


@dataclass
class PlayerProfile:
    name: str
    level: int = 1
    xp: int = 0
    xp_to_next_level: int = 100
    total_xp: int = 0
    rank: str = "Novice"

    streak_current: int = 0
    streak_longest: int = 0
    last_exercise_date: str | None = None

    total_exercises_completed: int = 0
    total_time_spent_minutes: float = 0.0

    # Stores completed exercise IDs (e.g. "2.1", "8.2").
    completed_exercises: list[str] | None = None


class GamificationEngine:
    """Core gamification logic and persistence."""

    def __init__(self, player_name: str = "Python_Learner", data_dir: str | Path = ".game_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.data_file = self.data_dir / f"player_{player_name}.json"
        self.player = PlayerProfile(name=player_name)

        # A small, extensible achievement catalog.
        self.achievements: dict[str, dict[str, Any]] = {
            "first_exercise": {"name": "First Step", "xp": 10, "unlocked": False},
            "5_exercises": {"name": "Getting Started", "xp": 25, "unlocked": False},
            "10_exercises": {"name": "Momentum", "xp": 50, "unlocked": False},
            "25_exercises": {"name": "Dedication", "xp": 100, "unlocked": False},
            "50_exercises": {"name": "Master Learner", "xp": 250, "unlocked": False},
            "100_exercises": {"name": "Python Legend", "xp": 500, "unlocked": False},
            "7_day_streak": {"name": "Week Warrior", "xp": 75, "unlocked": False},
            "30_day_streak": {"name": "Month Master", "xp": 300, "unlocked": False},
        }

        # Daily stats used for simple charts later.
        self.daily_stats: list[dict[str, Any]] = []

        self.load()

    # ----------------------------
    # Persistence
    # ----------------------------

    def save(self) -> None:
        if self.player.completed_exercises is None:
            self.player.completed_exercises = []
        payload = {
            "player": asdict(self.player),
            "achievements": self.achievements,
            "daily_stats": self.daily_stats,
        }
        self.data_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.data_file.exists():
            return

        payload = json.loads(self.data_file.read_text(encoding="utf-8"))
        player_data = payload.get("player", {})
        for k, v in player_data.items():
            if hasattr(self.player, k):
                setattr(self.player, k, v)

        if self.player.completed_exercises is None:
            self.player.completed_exercises = []

        self.achievements.update(payload.get("achievements", {}))
        self.daily_stats = payload.get("daily_stats", [])

    # ----------------------------
    # XP / Leveling
    # ----------------------------

    def get_progress_to_next_level(self) -> float:
        if self.player.xp_to_next_level <= 0:
            return 0.0
        return (self.player.xp / self.player.xp_to_next_level) * 100

    def _update_rank(self) -> None:
        ranks = [
            (1, "Novice"),
            (3, "Apprentice"),
            (5, "Practitioner"),
            (8, "Professional"),
            (10, "Expert"),
            (15, "Master"),
            (20, "Legend"),
        ]
        for level, name in reversed(ranks):
            if self.player.level >= level:
                self.player.rank = name
                return

    def _apply_level_ups(self) -> None:
        while self.player.xp >= self.player.xp_to_next_level:
            self.player.xp -= self.player.xp_to_next_level
            self.player.level += 1
            self.player.xp_to_next_level = int(self.player.xp_to_next_level * 1.15)
            self._update_rank()

    # ----------------------------
    # Streaks / Achievements
    # ----------------------------

    def _update_streak(self) -> None:
        today = _today_iso()
        yesterday = _yesterday_iso()

        if self.player.last_exercise_date is None:
            self.player.streak_current = 1
        elif self.player.last_exercise_date == today:
            # already counted today
            pass
        elif self.player.last_exercise_date == yesterday:
            self.player.streak_current += 1
        else:
            self.player.streak_current = 1

        if self.player.streak_current > self.player.streak_longest:
            self.player.streak_longest = self.player.streak_current

        self.player.last_exercise_date = today

    def _check_achievements(self) -> list[str]:
        unlocked_now: list[str] = []
        total = self.player.total_exercises_completed

        checks = {
            "first_exercise": total >= 1,
            "5_exercises": total >= 5,
            "10_exercises": total >= 10,
            "25_exercises": total >= 25,
            "50_exercises": total >= 50,
            "100_exercises": total >= 100,
            "7_day_streak": self.player.streak_current >= 7,
            "30_day_streak": self.player.streak_current >= 30,
        }

        for ach_id, ok in checks.items():
            if not ok:
                continue
            if self.achievements.get(ach_id, {}).get("unlocked"):
                continue
            self.achievements[ach_id]["unlocked"] = True
            bonus = int(self.achievements[ach_id].get("xp", 0))
            self.player.xp += bonus
            self.player.total_xp += bonus
            unlocked_now.append(f"🏆 {self.achievements[ach_id]['name']} (+{bonus} XP)")

        return unlocked_now

    # ----------------------------
    # Public API
    # ----------------------------

    def add_xp(self, amount: int, *, exercise_id: str, time_minutes: float) -> list[str]:
        """Award XP for an exercise completion.

        Returns:
            A list of achievement messages unlocked in this award.
        """

        self.player.xp += amount
        self.player.total_xp += amount
        self.player.total_exercises_completed += 1
        self.player.total_time_spent_minutes += time_minutes

        if self.player.completed_exercises is None:
            self.player.completed_exercises = []
        if exercise_id not in self.player.completed_exercises:
            self.player.completed_exercises.append(exercise_id)

        today = _today_iso()
        daily = next((d for d in self.daily_stats if d.get("date") == today), None)
        if daily is None:
            daily = {"date": today, "xp": 0, "count": 0}
            self.daily_stats.append(daily)
        daily["xp"] += amount
        daily["count"] += 1

        self._update_streak()
        self._apply_level_ups()
        unlocked = self._check_achievements()

        self.save()
        return unlocked

    def daily_quest(self) -> dict[str, Any]:
        """Return a simple rotating daily quest definition."""

        # Rotates deterministically by date so it feels "daily".
        day_key = int(_today_iso().replace("-", ""))
        quests = [
            {"title": "Warm-up", "goal": 1, "metric": "exercises", "reward_xp": 20},
            {"title": "Consistency", "goal": 2, "metric": "exercises", "reward_xp": 40},
            {"title": "XP Hunter", "goal": 50, "metric": "xp", "reward_xp": 60},
        ]
        return quests[day_key % len(quests)]

    def leaderboard(self, top_n: int = 5) -> list[dict[str, Any]]:
        """Return a simple local leaderboard across saved profiles.

        This scans `.game_data/player_*.json` and ranks by total_xp.
        """

        rows: list[dict[str, Any]] = []
        for path in sorted(self.data_dir.glob("player_*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                player = payload.get("player", {})
                rows.append(
                    {
                        "name": player.get("name", path.stem),
                        "total_xp": int(player.get("total_xp", 0)),
                        "level": int(player.get("level", 1)),
                        "rank": player.get("rank", "Novice"),
                    }
                )
            except Exception:
                continue

        rows.sort(key=lambda r: (r["total_xp"], r["level"]), reverse=True)
        return rows[: max(1, top_n)]

    def render_text_dashboard(self) -> str:
        unlocked = sum(1 for a in self.achievements.values() if a.get("unlocked"))
        progress = self.get_progress_to_next_level()
        bar = ("█" * int(progress // 5)).ljust(20)

        avg_time = (
            self.player.total_time_spent_minutes / self.player.total_exercises_completed
            if self.player.total_exercises_completed
            else 0.0
        )

        return (
            "\n"
            "╔══════════════════════════════════════════════════════╗\n"
            "║           🎮 PYTHON LEARNING QUEST DASHBOARD         ║\n"
            "╠══════════════════════════════════════════════════════╣\n"
            f"║ Player: {self.player.name:<44} ║\n"
            f"║ Rank:   {self.player.rank:<44} ║\n"
            "║                                                      ║\n"
            f"║ Level: {self.player.level:<3}  XP: {self.player.total_xp:<8}  Exercises: {self.player.total_exercises_completed:<6} ║\n"
            f"║ Progress: [{bar}] {progress:>5.1f}%                 ║\n"
            f"║ XP to next: {self.player.xp}/{self.player.xp_to_next_level:<34} ║\n"
            "║                                                      ║\n"
            f"║ Streak: 🔥 {self.player.streak_current:<3} (Best: {self.player.streak_longest:<3})  Achievements: {unlocked}/{len(self.achievements)} ║\n"
            f"║ Avg time/ex: {avg_time:>5.1f} min                               ║\n"
            "╚══════════════════════════════════════════════════════╝\n"
        )


class ExerciseTracker:
    """Tracks per-exercise timing and awards XP on completion."""

    def __init__(self, game: GamificationEngine):
        self.game = game
        self._current: dict[str, Any] | None = None
        self._start_ts: float | None = None

    def start(self, exercise_id: str, topic: str, difficulty: str) -> None:
        self._current = {"id": exercise_id, "topic": topic, "difficulty": difficulty}
        self._start_ts = time.time()
        print(f"🚀 Started {exercise_id} • {topic} • {difficulty}")

    def complete(self, *, tests_passed: bool = True) -> str:
        if self._current is None or self._start_ts is None:
            return "❌ No exercise started. Call tracker.start(...) first."

        elapsed_min = (time.time() - self._start_ts) / 60
        difficulty = str(self._current["difficulty"])
        base_xp = _DIFFICULTY_XP.get(difficulty, 10)

        bonus_msgs: list[str] = []
        xp = base_xp

        if elapsed_min <= 5:
            xp += 10
            bonus_msgs.append("⚡ Speed Bonus +10")
        if tests_passed:
            xp += 5
            bonus_msgs.append("✅ Tests Bonus +5")

        unlocked = self.game.add_xp(xp, exercise_id=str(self._current["id"]), time_minutes=elapsed_min)

        lines = [
            "=" * 60,
            f"✅ Completed {self._current['id']} (+{xp} XP)",
            f"⏱️ Time: {elapsed_min:.1f} min",
        ]
        lines.extend(bonus_msgs)
        lines.extend(unlocked)
        lines.append(self.game.render_text_dashboard())

        self._current = None
        self._start_ts = None
        return "\n".join(lines)
