# Database Setup

Project Starter Pro 2 supports both SQLite (for development) and PostgreSQL (for production).

---

## SQLite (Development)

**No setup required!**

- A file `data/dev.db` is automatically created on first run.
- Perfect for local development and testing.
- No external database server needed.

### Usage

Simply run the application:

```bash
cd backend
uvicorn main:app --reload
```

The SQLite database will be created automatically at `data/dev.db`.

---

## PostgreSQL (Production)

For production deployments, use PostgreSQL for better performance and scalability.

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Docker:**
```bash
docker run -d \
  --name psp-postgres \
  -e POSTGRES_USER=psp_user \
  -e POSTGRES_PASSWORD=psp_pass \
  -e POSTGRES_DB=psp \
  -p 5432:5432 \
  postgres:15
```

### 2. Create User and Database

Connect to PostgreSQL as the postgres user:

```bash
sudo -u postgres psql
```

Then, at the `psql=#` prompt, run:

```sql
CREATE DATABASE psp;
CREATE USER psp_user WITH PASSWORD 'psp_pass';
GRANT ALL PRIVILEGES ON DATABASE psp TO psp_user;
\q
```

### 3. Verify Connection

Test the connection:

```bash
psql -U psp_user -d psp -h localhost -W
```

Enter the password (`psp_pass`) when prompted. If it connects successfully, your setup is correct.

### 4. Configure Environment Variables

Create or update your `.env` file:

```bash
# Database Configuration
DB_TYPE=postgres
DB_USER=psp_user
DB_PASS=psp_pass
DB_HOST=localhost
DB_PORT=5432
DB_NAME=psp
```

Or export them directly:

```bash
export DB_TYPE=postgres
export DB_USER=psp_user
export DB_PASS=psp_pass
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=psp
```

### 5. Install Required Python Packages

Make sure you have the PostgreSQL async driver:

```bash
pip install asyncpg aiosqlite
```

### 6. Run Database Migrations

Initialize the database schema with Alembic:

```bash
cd backend

# Create initial migration
alembic revision --autogenerate -m "init"

# Apply migrations
alembic upgrade head
```

---

## Switching Between SQLite and PostgreSQL

### Switch to SQLite (Development)

```bash
export DB_TYPE=sqlite
# or in .env:
# DB_TYPE=sqlite
```

### Switch to PostgreSQL (Production)

```bash
export DB_TYPE=postgres
export DB_USER=psp_user
export DB_PASS=psp_pass
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=psp
```

---

## Database URL Format

The application automatically constructs the database URL based on `DB_TYPE`:

### SQLite
```
sqlite+aiosqlite:///./data/dev.db
```

### PostgreSQL
```
postgresql+asyncpg://psp_user:psp_pass@localhost:5432/psp
```

---

## Troubleshooting

### SQLite Issues

**Problem:** `data/dev.db` not created

**Solution:** Ensure the `data/` directory exists and is writable:
```bash
mkdir -p data
chmod 755 data
```

### PostgreSQL Issues

**Problem:** `psql: command not found`

**Solution:** PostgreSQL is not installed. Follow installation steps above.

---

**Problem:** `FATAL: Peer authentication failed for user "psp_user"`

**Solution:** Edit `/etc/postgresql/*/main/pg_hba.conf` and change:
```
local   all   all   peer
```
to:
```
local   all   all   md5
```

Then restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

**Problem:** `FATAL: password authentication failed for user "psp_user"`

**Solution:** Reset the password:
```bash
sudo -u postgres psql
ALTER USER psp_user WITH PASSWORD 'psp_pass';
\q
```

---

**Problem:** Connection refused on port 5432

**Solution:** PostgreSQL is not running. Start it:
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql
```

---

## Migration Commands Reference

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history
```

---

## Best Practices

1. **Development:** Use SQLite for quick local development
2. **Testing:** Use SQLite or a separate PostgreSQL test database
3. **Production:** Always use PostgreSQL with proper backups
4. **Migrations:** Always review auto-generated migrations before applying
5. **Backups:** Set up regular PostgreSQL backups in production

---

## Production Deployment Checklist

- [ ] PostgreSQL installed and running
- [ ] Database and user created
- [ ] Strong password set (not default `psp_pass`)
- [ ] Environment variables configured
- [ ] Migrations applied (`alembic upgrade head`)
- [ ] Database backups configured
- [ ] Connection pooling configured (if needed)
- [ ] SSL/TLS enabled for database connections
- [ ] Firewall rules configured
- [ ] Monitoring and alerting set up

---

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)

