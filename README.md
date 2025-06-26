
# AutoRiaScraper

Async web scraper for collecting used car listings from [AutoRia.com](https://auto.ria.com/)  
Built with **Python 3.12**, **Playwright**, **PostgreSQL**, and **Docker Compose**.


### Project Structure

<img width="512" alt="Project Structure" src="https://github.com/user-attachments/assets/a45e6bc8-a046-48f8-9c04-d2e8bf5fa0c6" />


# Quickstart

### 1. Clone the project

```bash
git clone https://github.com/kanunnikova23/AutoRiaScraper.git
cd AutoRiaScraper
````

### 2. Set up environment variables

Create a `.env` file in the root:

```env
START_URL=https://auto.ria.com/search/?indexName=used&  # Base URL for scraping
DATABASE_URL=postgresql+asyncpg://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>  # Full DB URL
SCRAPING_TIME=16:22  # Daily scraping time (HH:MM)

# PostgreSQL config
POSTGRES_DB=autoriadb
POSTGRES_USER=postgresuser
POSTGRES_PASSWORD=your_password_here
POSTGRES_PORT=5432

# Docker container
CONTAINER_NAME=auto-ria-db

# Optional
DUMP_FORMAT=sql  # Format for DB backups (e.g. sql or custom)
```
---

### Important Notes

Before running the scraper, make sure to adjust `main.py`:

-  **Comment out** `run_scraper()` if you're relying on scheduled jobs instead of running the scraper directly:

```python
# await run_scraper()  # disable this if you're using scheduled scraping
```

### 3. Start the application

```bash
docker compose up --build
```

This will:

*  start PostgreSQL
*  build and run the scraper container
*  initialize the database tables
*  launch the scheduler (daily jobs like DB dumps)

### 4. Access the PostgreSQL database

You can connect using **DBeaver** or any Postgres client:

> Use the credentials defined in your `.env` file:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_PORT`


---

##  Features

*  Fully async web scraping (Playwright)
*  Structured parser logic with BeautifulSoup
*  Stores car data in PostgreSQL
*  Daily DB dumps via scheduler
*  Easy setup with Docker Compose


