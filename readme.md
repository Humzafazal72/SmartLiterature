# SmartLiterature: Agentic AI based Solution for Literature Review

# Requirements
- python==3.10.3
- MySql

# Set-up:
- Clone the repo and move to the project Directory.
  ``` bash
   git clone 
   cd SmartLiterature

- Install requirements.
  ``` bash
  pip install -r requirements.txt

- Create a MySql Database.

- Create a .env file. It will have the following environment variables.
  - LANGCHAIN_API_KEY
  - GROQ_API_KEY
  - DB_PASSWORD
  - DB_NAME
  - SECRET_KEY (This will be used for creating the JWT token. It can by any string.)  

- initiate Alembic for db migrations.
  ``` bash
  alembic init migrations

- Paste the following code in migrations/env.py.
  ``` bash
  import sys
  import os
  from logging.config import fileConfig

  from sqlalchemy import engine_from_config, pool
  from alembic import context

  # Import your Base and DB URL from app
  sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # so Alembic sees your app
  from app.database import Base, MYSQL_URL

  # Alembic Config object, provides access to alembic.ini
  config = context.config

  # Load logging config
  if config.config_file_name is not None:
    fileConfig(config.config_file_name)

  # Set the sqlalchemy.url dynamically (instead of alembic.ini hardcoding)
  config.set_main_option("sqlalchemy.url", MYSQL_URL)

  # Point Alembic to your models’ metadata
  target_metadata = Base.metadata


  def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


  def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


  if context.is_offline_mode():
    run_migrations_offline()
  else:
    run_migrations_online()

- Make Migrations.
  ``` bash
  alembic revision --autogenerate -m "init schema"
  alembic upgrade head

- Run the Project.
  ``` bash
  uvicorn main:app --reload 
