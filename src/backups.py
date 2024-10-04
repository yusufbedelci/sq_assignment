from datetime import datetime
import zipfile
from config import Config
from pathlib import Path


class Backups:
    def __init__(self, config: Config):
        self.config = config
        self.dir_path = Path(__file__).resolve().parent
        self.backup_dir = self.dir_path / "backups"

    def create(self):
        try:
            # Ensure the backup directory exists
            self.backup_dir.mkdir(exist_ok=True)

            # Create a file name based on the current datetime
            timestamp = datetime.now().strftime("%d %B %Y at %H-%M-%S")
            sql_file_name = self.backup_dir / "data.sql"
            log_backup_file_name = self.backup_dir / "log_backup.log"
            log_file_name = self.dir_path / "app.log"
            zip_file_name = self.backup_dir / f"{timestamp}.zip"

            # Open the backup file in write mode
            with sql_file_name.open("w") as f:
                # Iterate through the SQL dump of the database and write to the file
                for line in self.config.con.iterdump():
                    f.write(f"{line}\n")

            # copy the log file to the backup directory
            with log_file_name.open("r") as f:
                with log_backup_file_name.open("w") as backup_file:
                    backup_file.write(f.read())

            # Create a zip file containing the SQL backup
            with zipfile.ZipFile(zip_file_name, "w") as zipf:
                zipf.write(sql_file_name, arcname=sql_file_name.name)
                zipf.write(log_backup_file_name, arcname=log_backup_file_name.name)

            # Remove the temporary SQL file
            sql_file_name.unlink()
            log_backup_file_name.unlink()

            print(f"Backup created successfully: {zip_file_name.name}")
            return zip_file_name.name
        except Exception as e:
            print(f"Error creating backup: {e}")
            ...

    def restore(self, zip_file_name: str):
        try:
            # Extract the zip file
            zip_file_path = self.backup_dir / zip_file_name
            with zipfile.ZipFile(zip_file_path, "r") as zipf:
                zipf.extractall(path=self.backup_dir)

            sql_file_name = self.backup_dir / "data.sql"
            log_backup_file_name = self.backup_dir / "log_backup.log"

            # Ensure the data.sql file exists
            if not sql_file_name.exists():
                raise FileNotFoundError("{sql_file_name} not found in the zip file")

            if not log_backup_file_name.exists():
                raise FileNotFoundError("{log_backup_file_name} not found in the zip file")

            # Disable foreign key checks to avoid conflicts
            cursor = self.config.con.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.close()

            # Get the list of all tables
            cursor = self.config.con.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # Drop all tables
            for table in tables:
                drop_table_sql = f"DROP TABLE IF EXISTS {table[0]}"
                cursor.execute(drop_table_sql)
                print(drop_table_sql)  # Debug print to see the drop statements

            # Commit changes to ensure all tables are dropped
            self.config.con.commit()

            # Open the SQL file in read mode
            with sql_file_name.open("r") as f:
                # Execute the script to restore the database
                self.config.con.executescript(f.read())

            # Remove the temporary SQL file
            sql_file_name.unlink()

            # Restore log file
            with log_backup_file_name.open("r") as f:
                log_file_name = self.dir_path / "app.log"
                with log_file_name.open("w") as log_file:
                    log_file.write(f.read())

            # Remove the temporary log file
            log_backup_file_name.unlink()

            print(f"Database restored successfully from {zip_file_name}")
        except Exception as e:
            print(f"Error restoring backup: {e}")
            ...
        finally:
            # Re-enable foreign key checks
            cursor = self.config.con.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.close()

    def list(self):
        return sorted(
            (backup.name for backup in self.backup_dir.glob("*.zip")),
            key=lambda name: (self.backup_dir / name).stat().st_ctime,
            reverse=True,
        )
