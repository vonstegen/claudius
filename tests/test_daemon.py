"""Basic tests for Claudius components."""

import pytest
from pathlib import Path

from src.config import load_config, _expand_env_vars
from src.skills import SkillLoader
from src.memory import MemoryStore


class TestConfig:
    def test_expand_env_vars_string(self):
        import os
        os.environ["TEST_VAR"] = "hello"
        assert _expand_env_vars("${TEST_VAR}") == "hello"
        del os.environ["TEST_VAR"]

    def test_expand_env_vars_missing(self):
        result = _expand_env_vars("${NONEXISTENT_VAR_XYZ}")
        assert result == "${NONEXISTENT_VAR_XYZ}"

    def test_expand_env_vars_nested(self):
        import os
        os.environ["TEST_NEST"] = "world"
        result = _expand_env_vars({"key": "${TEST_NEST}", "list": ["${TEST_NEST}"]})
        assert result == {"key": "world", "list": ["world"]}
        del os.environ["TEST_NEST"]


class TestSkills:
    def test_load_skills(self, tmp_path):
        # Create a test skill
        skill_file = tmp_path / "test-skill.md"
        skill_file.write_text("# Test Skill\n\nDo something.")

        loader = SkillLoader({"path": str(tmp_path)})
        loader.load_all()

        assert "test-skill" in loader.skills
        assert "Do something" in loader.get("test-skill")

    def test_list_skills(self, tmp_path):
        (tmp_path / "alpha.md").write_text("# Alpha")
        (tmp_path / "beta.md").write_text("# Beta")
        (tmp_path / "README.md").write_text("# Ignored")

        loader = SkillLoader({"path": str(tmp_path)})
        loader.load_all()

        names = loader.list_skills()
        assert "alpha" in names
        assert "beta" in names
        assert "README" not in names

    def test_missing_skill(self, tmp_path):
        loader = SkillLoader({"path": str(tmp_path)})
        loader.load_all()
        assert loader.get("nonexistent") is None


class TestMemory:
    @pytest.mark.asyncio
    async def test_initialize(self, tmp_path):
        store = MemoryStore({
            "db_path": str(tmp_path / "test.db"),
            "markdown_path": str(tmp_path / "MEMORY.md"),
            "conversation_path": str(tmp_path / "conversations"),
        })
        await store.initialize()
        assert (tmp_path / "test.db").exists()
        await store.stop()

    @pytest.mark.asyncio
    async def test_state_roundtrip(self, tmp_path):
        store = MemoryStore({
            "db_path": str(tmp_path / "test.db"),
            "markdown_path": str(tmp_path / "MEMORY.md"),
            "conversation_path": str(tmp_path / "conversations"),
        })
        await store.initialize()

        await store.set_state("test_key", "test_value")
        result = await store.get_state("test_key")
        assert result == "test_value"

        await store.stop()

    @pytest.mark.asyncio
    async def test_conversation_logging(self, tmp_path):
        store = MemoryStore({
            "db_path": str(tmp_path / "test.db"),
            "markdown_path": str(tmp_path / "MEMORY.md"),
            "conversation_path": str(tmp_path / "conversations"),
        })
        await store.initialize()

        await store.log_conversation("telegram", "user", "hello")
        await store.log_conversation("telegram", "assistant", "hi there")

        context = await store.get_recent_context(limit=10)
        assert "hello" in context
        assert "hi there" in context

        await store.stop()
