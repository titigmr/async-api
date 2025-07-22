#!/usr/bin/env python3
"""
Script pour exécuter les migrations Alembic automatiquement
"""

import sys
import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from api.core.config import settings
from api.core.logger import logger


def wait_for_database(max_retries: int = 30, delay: int = 2) -> bool:
    """Attend que la base de données soit disponible"""
    logger.info("🔄 Attente de la disponibilité de la base de données...")

    for attempt in range(max_retries):
        try:
            engine = create_engine(settings.DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Base de données disponible !")
            return True
        except OperationalError as e:
            logger.warning(f"⏳ Tentative {attempt + 1}/{max_retries} - Base de données non disponible: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)

    logger.error("❌ Impossible de se connecter à la base de données après toutes les tentatives")
    return False


def run_migrations() -> bool:
    """Exécute les migrations Alembic"""
    try:
        logger.info("🚀 Exécution des migrations Alembic...")

        # Configuration d'Alembic
        alembic_cfg = Config(str(Path("migrations", "alembic.ini")))
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

        # Vérifier si des migrations sont nécessaires
        command.check(alembic_cfg)
        logger.info("✅ Base de données à jour !")

        # Exécuter les migrations (upgrade to head)
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Migrations appliquées avec succès !")

        return True

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution des migrations: {e}")
        return False


def main() -> None:
    """Point d'entrée principal"""
    logger.info("=== MIGRATIONS ALEMBIC ===")
    logger.info(f"DATABASE_URL: {settings.DATABASE_URL}")

    # Attendre que la base de données soit disponible
    if not wait_for_database():
        sys.exit(1)

    # Exécuter les migrations
    if not run_migrations():
        sys.exit(1)

    logger.info("✅ Migrations terminées avec succès !")


if __name__ == "__main__":
    main()
