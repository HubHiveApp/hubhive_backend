from __future__ import with_statement
import logging
from logging.config import fileConfig
from flask import current_app
from alembic import context
import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

from app import create_app
from app.extensions import db
from app.models import *

app = create_app()
app.app_context().push()
config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])

target_metadata = db.metadata

def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = db.engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
