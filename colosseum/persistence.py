import json
from pathlib import Path


def init_match_dir(base_dir: Path, match_id: str, meta: dict) -> Path:
    """Create match directory structure and write meta.json."""
    match_dir = base_dir / match_id
    snapshots_dir = match_dir / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    (match_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return match_dir


def save_step(match_dir: Path, step: int, player: int, move: dict, state: dict) -> None:
    """Append move to moves.jsonl and save full state snapshot."""
    # Append to moves.jsonl
    record = {"step": step, "player": player, "move": move}
    with open(match_dir / "moves.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Save full snapshot
    snapshot_path = match_dir / "snapshots" / f"step_{step:04d}.json"
    snapshot_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def save_result(match_dir: Path, result: dict) -> None:
    """Write result.json."""
    (match_dir / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
