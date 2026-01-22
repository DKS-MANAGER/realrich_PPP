"""UI/UX helpers for the Python Learning Quest notebook.

Provides:
- Design tokens (colors)
- HTML dashboard renderer
- Exercise card renderer
- Simple analytics plotting

Works best in Jupyter, but degrades gracefully.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


COLORS: dict[str, str] = {
    "primary_blue": "#00D9FF",
    "accent_pink": "#FF006E",
    "success_green": "#00FF88",
    "warning_gold": "#FFB82C",
    "dark_bg": "#1a1a2e",
    "light_bg": "#0f3460",
    "card_bg": "#16213e",
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "border": "#00D9FF",
    "locked": "#666666",
    "in_progress": "#FFB82C",
    "completed": "#00FF88",
}


def _try_html(html: str):
    try:
        from IPython.display import HTML

        return HTML(html)
    except Exception:
        return html


class BeautifulDashboard:
    """Professional-looking HTML dashboard for the gamification engine."""

    def __init__(self, game_engine):
        self.game = game_engine
        self.colors = COLORS

    def render(self):
        player = self.game.player
        progress = self.game.get_progress_to_next_level()
        unlocked = sum(1 for a in self.game.achievements.values() if a.get("unlocked"))

        avg_time = (
            player.total_time_spent_minutes / player.total_exercises_completed
            if player.total_exercises_completed
            else 0.0
        )

        html = f"""
<style>
  .pq-container {{
    background: linear-gradient(135deg, {self.colors['dark_bg']} 0%, {self.colors['light_bg']} 100%);
    padding: 24px;
    border-radius: 16px;
    border: 2px solid {self.colors['primary_blue']};
    font-family: 'Courier New', monospace;
    color: {self.colors['text_primary']};
    max-width: 980px;
    margin: 0 auto;
    box-shadow: 0 0 24px rgba(0, 217, 255, 0.25);
  }}
  .pq-header {{
    text-align: center;
    border-bottom: 2px solid {self.colors['primary_blue']};
    padding-bottom: 12px;
    margin-bottom: 18px;
  }}
  .pq-title {{
    font-size: 26px;
    margin: 0;
    color: {self.colors['primary_blue']};
    text-shadow: 0 0 12px rgba(0, 217, 255, 0.6);
  }}
  .pq-subtitle {{
    margin-top: 6px;
    font-size: 13px;
    color: {self.colors['warning_gold']};
  }}
  .pq-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }}
  .pq-card {{
    background: rgba(22, 33, 62, 0.82);
    border: 1px solid {self.colors['primary_blue']};
    border-radius: 12px;
    padding: 16px;
    backdrop-filter: blur(8px);
  }}
  .pq-card-title {{
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: {self.colors['primary_blue']};
    margin-bottom: 8px;
    font-weight: 700;
  }}
  .pq-big {{
    font-size: 32px;
    font-weight: 800;
    color: {self.colors['accent_pink']};
  }}
  .pq-small {{
    font-size: 11px;
    color: {self.colors['text_secondary']};
    margin-top: 6px;
  }}
  .pq-progress {{
    background: rgba(0,0,0,0.45);
    border: 1px solid {self.colors['primary_blue']};
    height: 26px;
    border-radius: 8px;
    overflow: hidden;
    margin-top: 10px;
  }}
  .pq-progress-fill {{
    height: 100%;
    width: {progress:.2f}%;
    background: linear-gradient(90deg, {self.colors['primary_blue']}, {self.colors['accent_pink']});
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    transition: width 0.3s ease;
  }}
  .pq-badge {{
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    border: 1px solid {self.colors['warning_gold']};
    color: {self.colors['warning_gold']};
    font-weight: 700;
    font-size: 12px;
    margin-top: 8px;
  }}
  @media (max-width: 820px) {{
    .pq-grid {{ grid-template-columns: 1fr; }}
    .pq-title {{ font-size: 20px; }}
  }}
</style>

<div class="pq-container">
  <div class="pq-header">
    <h1 class="pq-title">PYTHON LEARNING QUEST</h1>
    <div class="pq-subtitle">{player.rank} • Level {player.level} • {player.name}</div>
  </div>

  <div class="pq-grid">
    <div class="pq-card">
      <div class="pq-card-title">Total XP</div>
      <div class="pq-big">{player.total_xp}</div>
      <div class="pq-small">Experience earned so far</div>
    </div>

    <div class="pq-card">
      <div class="pq-card-title">Exercises</div>
      <div class="pq-big">{player.total_exercises_completed}</div>
      <div class="pq-small">Completed successfully</div>
    </div>
  </div>

  <div class="pq-card" style="margin-top: 14px;">
    <div class="pq-card-title">Level Progress</div>
    <div class="pq-progress">
      <div class="pq-progress-fill">{progress:.0f}%</div>
    </div>
    <div class="pq-small">XP: {player.xp}/{player.xp_to_next_level} → Level {player.level + 1}</div>
  </div>

  <div class="pq-grid" style="margin-top: 14px;">
    <div class="pq-card">
      <div class="pq-card-title">Streak</div>
      <div class="pq-badge">Current 🔥 {player.streak_current}</div>
      <div class="pq-small">Best: {player.streak_longest}</div>
    </div>

    <div class="pq-card">
      <div class="pq-card-title">Achievements</div>
      <div class="pq-big" style="font-size: 26px;">{unlocked}/{len(self.game.achievements)}</div>
      <div class="pq-small">Unlocked badges</div>
    </div>
  </div>

  <div class="pq-card" style="margin-top: 14px;">
    <div class="pq-card-title">Time</div>
    <div class="pq-small">Total: {player.total_time_spent_minutes:.0f} min • Avg/exercise: {avg_time:.1f} min</div>
  </div>
</div>
"""
        return _try_html(html)


@dataclass
class ExerciseCard:
    exercise_id: str
    topic: str
    difficulty: str
    description: str
    xp_reward: int
    status: str = "available"  # locked, available, in_progress, completed

    def render(self):
        diff_colors = {
            "Basic": (COLORS["success_green"], "rgba(0, 255, 136, 0.10)"),
            "Intermediate": (COLORS["warning_gold"], "rgba(255, 184, 44, 0.10)"),
            "Advanced": (COLORS["accent_pink"], "rgba(255, 0, 110, 0.10)"),
        }
        border, bg = diff_colors.get(self.difficulty, (COLORS["primary_blue"], "rgba(0, 217, 255, 0.08)"))

        icons = {"locked": "🔒", "available": "⭕", "in_progress": "🔄", "completed": "✅"}
        icon = icons.get(self.status, "⭕")

        html = f"""
<style>
  .pq-ex-card {{
    background: rgba(22, 33, 62, 0.90);
    border: 2px solid {border};
    border-radius: 14px;
    padding: 16px;
    margin: 10px 0;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
    box-shadow: 0 0 16px rgba(0,0,0,0.25);
  }}
  .pq-ex-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 12px 28px rgba(0, 217, 255, 0.22);
  }}
  .pq-ex-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }}
  .pq-ex-id {{
    font-weight: 800;
    color: {COLORS['primary_blue']};
    font-family: 'Courier New', monospace;
  }}
  .pq-ex-badge {{
    background: {bg};
    color: {border};
    border: 1px solid {border};
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
  }}
  .pq-ex-topic {{
    margin-top: 10px;
    color: {COLORS['text_secondary']};
    font-size: 12px;
  }}
  .pq-ex-desc {{
    margin-top: 6px;
    color: {COLORS['text_primary']};
    font-size: 13px;
    line-height: 1.5;
  }}
  .pq-ex-foot {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;
    border-top: 1px solid rgba(0, 217, 255, 0.18);
    padding-top: 10px;
  }}
  .pq-ex-xp {{
    font-weight: 800;
    color: {COLORS['warning_gold']};
  }}
  .pq-ex-status {{
    font-size: 22px;
  }}
</style>

<div class="pq-ex-card">
  <div class="pq-ex-head">
    <div class="pq-ex-id">Exercise {self.exercise_id}</div>
    <div class="pq-ex-badge">{self.difficulty}</div>
  </div>
  <div class="pq-ex-topic">{self.topic}</div>
  <div class="pq-ex-desc">{self.description}</div>
  <div class="pq-ex-foot">
    <div class="pq-ex-xp">+{self.xp_reward} XP</div>
    <div class="pq-ex-status">{icon}</div>
  </div>
</div>
"""
        return _try_html(html)


def plot_beautiful_stats(game_engine) -> None:
    """Render a small dark-themed stats dashboard using matplotlib."""

  try:
    import matplotlib.pyplot as plt
  except Exception as exc:  # pragma: no cover
    msg = (
      "matplotlib is required for plot_beautiful_stats(). "
      "Install it with: pip install matplotlib\n"
      f"Details: {exc}"
    )
    print(msg)
    return

    primary = COLORS["primary_blue"]
    accent = COLORS["accent_pink"]
    success = COLORS["success_green"]
    warning = COLORS["warning_gold"]

    fig = plt.figure(figsize=(14, 8), facecolor=COLORS["dark_bg"])

    # XP per day
    ax1 = plt.subplot(2, 2, 1)
    ax1.set_facecolor(COLORS["light_bg"])
    days = list(range(len(game_engine.daily_stats)))
    xp = [d.get("xp", 0) for d in game_engine.daily_stats]
    ax1.plot(days, xp, color=primary, linewidth=3, marker="o")
    ax1.fill_between(days, xp, color=primary, alpha=0.15)
    ax1.set_title("XP Earned Per Day", color=primary, fontweight="bold")
    ax1.tick_params(colors=primary)
    ax1.grid(True, alpha=0.25)

    # Achievements
    ax2 = plt.subplot(2, 2, 2)
    ax2.set_facecolor(COLORS["light_bg"])
    unlocked = sum(1 for a in game_engine.achievements.values() if a.get("unlocked"))
    locked = len(game_engine.achievements) - unlocked
    ax2.pie([unlocked, locked], labels=["Unlocked", "Locked"], colors=[success, "#444"], autopct="%1.0f%%")
    ax2.set_title("Achievements", color=success, fontweight="bold")

    # Leaderboard
    ax3 = plt.subplot(2, 2, 3)
    ax3.set_facecolor(COLORS["light_bg"])
    board = game_engine.leaderboard(top_n=5)
    names = [r["name"] for r in board]
    xp_vals = [r["total_xp"] for r in board]
    ax3.barh(names, xp_vals, color=warning, alpha=0.85)
    ax3.set_title("Local Leaderboard (Top XP)", color=warning, fontweight="bold")
    ax3.tick_params(colors=warning)

    # Progress summary
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis("off")
    p = game_engine.player
    txt = (
        f"Player: {p.name}\n"
        f"Rank: {p.rank}\n"
        f"Level: {p.level}\n"
        f"Total XP: {p.total_xp}\n"
        f"Exercises: {p.total_exercises_completed}\n"
        f"Streak: {p.streak_current} (Best {p.streak_longest})\n"
    )
    ax4.text(
        0.05,
        0.95,
        txt,
        va="top",
        fontfamily="monospace",
        fontsize=12,
        color=accent,
        bbox=dict(boxstyle="round", facecolor=COLORS["light_bg"], edgecolor=accent, linewidth=2, alpha=0.8),
    )

    plt.suptitle("PYTHON QUEST • ANALYTICS", color=primary, fontsize=16, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
