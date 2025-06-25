import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CURRENT_FILE = os.path.abspath(__file__)  # /app/services/db_backup.py
APP_DIR = os.path.dirname(os.path.dirname(CURRENT_FILE))  # /app
ROOT_DIR = os.path.dirname(APP_DIR)  # project root (/dumps)
DUMP_DIR = os.path.join(ROOT_DIR, "dumps")  # dump folder created in the root of the project


def dump_database():
    format_ = os.getenv("DUMP_FORMAT", "sql")
    db_name = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    container_name = os.getenv("CONTAINER_NAME")

    now = datetime.now().strftime("%Y-%m-%d")

    os.makedirs(DUMP_DIR, exist_ok=True)

    # Create /dumps inside the container too
    subprocess.run(["docker", "exec", container_name, "mkdir", "-p", "/dumps"])

    # Choose file extension and pg_dump format arguments based on selected format
    extension = "sql" if format_ == "sql" else "dump"
    pg_args = [] if format_ == "sql" else ["-Fc"]

    # Host-side path where the backup will be saved
    path = os.path.join(DUMP_DIR, f"backup_{now}.{extension}")

    # Container-side path where pg_dump will write the file
    container_path = f"/dumps/backup_{now}.{extension}"

    # Full pg_dump command executed inside the Docker container
    cmd = [
        "docker", "exec", container_name, "pg_dump",  # run pg_dump inside container
        "-U", user,  # DB user
        "-d", db_name,  # DB name
        *pg_args,  # optional format args
        "-f", container_path  # output file inside container
    ]

    # Execute the backup command
    subprocess.run(cmd)
    print(f"[DUMP] Saved to {path}")
