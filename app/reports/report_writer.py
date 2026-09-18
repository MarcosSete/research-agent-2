from datetime import datetime
import json
from pathlib import Path


REPORTS_DIR = Path("reports")


def save_research_report(content: str) -> tuple[Path, Path]:
    """Save the final research synthesis as Markdown and JSON."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_name = f"research_{timestamp}"

    markdown_path = REPORTS_DIR / f"{base_name}.md"
    json_path = REPORTS_DIR / f"{base_name}.json"

    markdown_path.write_text(content, encoding="utf-8")

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "content": content,
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return markdown_path, json_path
