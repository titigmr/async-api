"""Test for individual config components URL construction."""

import os
from unittest.mock import patch

from api.core.config import Settings


class TestConfigComponents:
    """Test the construction of URLs from individual components."""

    def test_database_url_from_components_default(self):
        """Test database URL construction with default values."""
        settings = Settings()
        url = settings.database_url_from_components
        assert "postgresql+asyncpg://" in url
        assert "db:5432" in url
        assert "tasks" in url

    def test_database_url_from_components_custom(self):
        """Test database URL construction with custom environment variables."""
        with patch.dict(
            os.environ,
            {
                "DB_HOST": "custom-db",
                "DB_PORT": "9999",
                "DB_NAME": "custom-tasks",
                "DB_USERNAME": "custom-user",
                "DB_PASSWORD": "custom-pass",
                "DB_SCHEME": "postgresql+asyncpg",
            },
        ):
            settings = Settings()
            url = settings.database_url_from_components
            assert "postgresql+asyncpg://custom-user:" in url
            assert "@custom-db:9999/custom-tasks" in url

    def test_broker_url_from_components_default(self):
        """Test broker URL construction with default values."""
        settings = Settings()
        url = settings.broker_url_from_components
        assert url == "amqp://guest:guest@rabbitmq:5672"

    def test_broker_url_from_components_custom(self):
        """Test broker URL construction with custom environment variables."""
        with patch.dict(
            os.environ,
            {
                "BROKER_HOST": "custom-broker",
                "BROKER_PORT": "5673",
                "BROKER_USERNAME": "custom-user",
                "BROKER_PASSWORD": "custom-pass",
                "BROKER_VHOST": "/custom",
            },
        ):
            settings = Settings()
            url = settings.broker_url_from_components
            assert url == "amqp://custom-user:custom-pass@custom-broker:5673/custom"

    def test_broker_url_vhost_root(self):
        """Test broker URL construction with root vhost."""
        with patch.dict(
            os.environ,
            {
                "BROKER_VHOST": "/",
            },
        ):
            settings = Settings()
            url = settings.broker_url_from_components
            # Root vhost should result in no path
            assert not url.endswith("/")

    def test_broker_url_vhost_custom(self):
        """Test broker URL construction with custom vhost."""
        with patch.dict(
            os.environ,
            {
                "BROKER_VHOST": "myvhost",
            },
        ):
            settings = Settings()
            url = settings.broker_url_from_components
            assert url.endswith("/myvhost")

    def test_backward_compatibility(self):
        """Test that legacy URL properties still work."""
        settings = Settings()
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "BROKER_URL")
        assert isinstance(settings.DATABASE_URL, str)
        assert isinstance(settings.BROKER_URL, str)
