"""
Skills Loader — Reads markdown playbooks from the skills/ directory.

Skills are plain markdown files that describe workflows Claudius should follow.
They're loaded into memory and injected as context when triggered.
"""

import logging
from pathlib import Path

logger = logging.getLogger("claudius.skills")


class SkillLoader:
    """Loads and manages markdown skill playbooks."""

    def __init__(self, config: dict):
        self.path = Path(config.get("path", "skills/"))
        self.auto_reload = config.get("auto_reload", True)
        self.skills: dict[str, str] = {}

    def load_all(self):
        """Load all .md files from the skills directory."""
        self.skills.clear()
        if not self.path.exists():
            logger.warning(f"Skills directory not found: {self.path}")
            return

        for md_file in sorted(self.path.glob("*.md")):
            if md_file.name == "README.md":
                continue
            skill_name = md_file.stem
            self.skills[skill_name] = md_file.read_text()
            logger.debug(f"  Loaded skill: {skill_name}")

    def get(self, name: str) -> str | None:
        """Get a skill's content by name."""
        if self.auto_reload:
            self.load_all()
        return self.skills.get(name)

    def list_skills(self) -> list[str]:
        """List all available skill names."""
        if self.auto_reload:
            self.load_all()
        return list(self.skills.keys())
