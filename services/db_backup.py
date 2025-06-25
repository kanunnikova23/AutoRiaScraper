import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def dump_database():
    format_ = os.getenv("DUMP_FORMAT", "sql")
    db_name = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    container_name = os.getenv("CONTAINER_NAME")

    now = datetime.now().strftime("%Y-%m-%d")

    os.makedirs("dumps", exist_ok=True)

    # створення папки всередині контейнера
    subprocess.run(["docker", "exec", container_name, "mkdir", "-p", "/dumps"])

    dump_dir = "dumps"
    extension = "sql" if format_ == "sql" else "dump"
    pg_args = [] if format_ == "sql" else ["-Fc"]

    path = f"{dump_dir}/backup_{now}.{extension}"
    container_path = f"/dumps/backup_{now}.{extension}"

    cmd = [
        "docker", "exec", container_name, "pg_dump",
        "-U", user, "-d", db_name,
        *pg_args,
        "-f", container_path
    ]

    subprocess.run(cmd)
    print(f"[DUMP] Saved to {path}")
