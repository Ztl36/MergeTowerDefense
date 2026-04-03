import json
import os
import sqlite3
import time
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "game.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                coins INTEGER NOT NULL,
                highest_wave INTEGER NOT NULL,
                grid_data TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            )
            """
        )
        conn.commit()


def build_config() -> dict[str, Any]:
    max_tower_level = 5
    towers: dict[str, Any] = {}
    for level in range(1, max_tower_level + 1):
        splash_radius = 0
        if level >= 3:
            splash_radius = 10 + level * 15
        towers[str(level)] = {
            "level": level,
            "damage": 1 + level * 1,
            "fire_rate": 0.75 + level * 0.35,
            "bullet_speed": 520 + level * 35,
            "splash_radius": splash_radius,
            "crit_rate": 0.04 + level * 0.03,
            "crit_multiplier": 1.35 + level * 0.15,
        }

    waves: list[dict[str, Any]] = []
    for wave in range(1, 51):
        spawn_interval_ms = max(180, int(900 - (wave - 1) * 14))
        base_enemy_hp = 3 + (wave - 1) * 1
        base_enemy_speed = 55 + (wave - 1) * 2.4
        kill_reward = 1
        base_xp_drop = 8 + wave * 3
        enemy_count = min(8 + wave * 2, 60)

        is_boss = wave % 5 == 0
        if is_boss:
            enemy_count = 1
            enemy_hp = int(base_enemy_hp * 22)
            enemy_speed = base_enemy_speed * 0.5
            kill_reward = int(kill_reward * 50)
            xp_drop = int(base_xp_drop * 25)
        else:
            enemy_hp = base_enemy_hp
            enemy_speed = base_enemy_speed
            xp_drop = base_xp_drop

        waves.append(
            {
                "wave": wave,
                "spawn_interval_ms": spawn_interval_ms,
                "enemy_hp": enemy_hp,
                "enemy_speed": enemy_speed,
                "kill_reward": kill_reward,
                "enemy_count": enemy_count,
                "is_boss": is_boss,
                "xp_drop": xp_drop,
            }
        )

    return {
        "meta": {
            "grid_size": 5,
            "start_gold": 100,
            "buy_cost": 10,
            "max_tower_level": max_tower_level,
            "default_user_id": "test_user",
            "wave_duration_sec": 12,
        },
        "player": {
            "xp_to_next_level": [100, 250, 500, 1000, 2000],
        },
        "towers": towers,
        "waves": waves,
    }


class SaveRequest(BaseModel):
    user_id: str = Field(default="test_user", min_length=1)
    coins: int = Field(ge=0)
    highest_wave: int = Field(ge=1)
    grid_data: list[list[int]]


init_db()

app = FastAPI(title="Merge Tower Defense API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)


@app.get("/api/config")
def api_config() -> dict[str, Any]:
    return build_config()


@app.post("/api/save")
def api_save(payload: SaveRequest) -> dict[str, Any]:
    now = int(time.time())
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO users(user_id, coins, highest_wave, grid_data, updated_at)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                coins=excluded.coins,
                highest_wave=excluded.highest_wave,
                grid_data=excluded.grid_data,
                updated_at=excluded.updated_at
            """,
            (
                payload.user_id,
                int(payload.coins),
                int(payload.highest_wave),
                json.dumps(payload.grid_data, ensure_ascii=False),
                now,
            ),
        )
        conn.commit()

    return {"ok": True, "user_id": payload.user_id, "updated_at": now}


@app.get("/api/load/{user_id}")
def api_load(user_id: str) -> dict[str, Any]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT user_id, coins, highest_wave, grid_data, updated_at FROM users WHERE user_id=?",
            (user_id,),
        ).fetchone()

    if not row:
        cfg = build_config()
        return {
            "exists": False,
            "user_id": user_id,
            "coins": int(cfg["meta"]["start_gold"]),
            "highest_wave": 1,
            "grid_data": None,
            "updated_at": None,
        }

    grid_data = json.loads(row["grid_data"]) if row["grid_data"] else None
    return {
        "exists": True,
        "user_id": row["user_id"],
        "coins": int(row["coins"]),
        "highest_wave": int(row["highest_wave"]),
        "grid_data": grid_data,
        "updated_at": int(row["updated_at"]),
    }


@app.get("/api/health")
def api_health() -> dict[str, Any]:
    return {"ok": True}

