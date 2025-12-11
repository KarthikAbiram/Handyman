import sys
import subprocess
from pathlib import Path
import shutil
import logging
import pandas as pd
from fire import Fire

class Handyman():
    def choice(self, input_directory=r"Choices"):
        """
        Given a directory, list all subfolders as 1,2,3... as options to user
        and request user to make a choice amomg 1,2,3..
        After user makes the selection, execute the run.bat file present inside the 
        selected subfolder
        
        :param choice_directory: Input directory where each subfolder is a choice for user to choose from
        """
        print("--------------------------------------------------------------")
        print("Welcome to Handyman - An Open Source tool with handy scripts")
        print("Source: https://github.com/KarthikAbiram/Handyman")
        print("--------------------------------------------------------------")

        base_path = Path(input_directory)

        if not base_path.exists() or not base_path.is_dir():
            raise ValueError(f"Invalid directory: {input_directory}")

        # List immediate subdirectories
        subfolders = [p for p in base_path.iterdir() if p.is_dir()]

        if not subfolders:
            print("No subfolders found. Nothing to choose from.")
            return

        print("\nAvailable options:")
        for idx, folder in enumerate(subfolders, 1):
            print(f"{idx}. {folder.name}")

        # Get user choice
        while True:
            try:
                choice = int(input("\nChoice: "))
                if 1 <= choice <= len(subfolders):
                    break
                else:
                    print("Invalid option. Try again.")
            except ValueError:
                print("Please enter a valid number.")

        selected_folder = subfolders[choice - 1]
        run_bat = selected_folder / "run.bat"

        if not run_bat.exists():
            raise FileNotFoundError(f"No run.bat found in folder: {selected_folder}")

        print(f"\nExecuting: {run_bat}")

        # Execute the .bat file
        subprocess.run([str(run_bat)], shell=True)

        # Wait for user input before exiting
        input("\nPress any key to exit...")

    def rename(self, input_file, log_file=None):
        """
        Takes an input CSV file with two columns - Source, Destination - and
        renames/moves files accordingly.

        Adds logging and automatically deletes destination files if they
        already exist.

        :param input_file: CSV with columns: Source, Destination
        :param log_file: Optional log file path
        """

        # -----------------------------
        # Setup logging
        # -----------------------------
        log_handlers = [logging.StreamHandler()]
        if log_file:
            log_handlers.append(logging.FileHandler(log_file))

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=log_handlers
        )

        input_path = Path(input_file).resolve()
        csv_dir = input_path.parent  # <-- base directory for relative paths

        df = pd.read_csv(input_file)

        # Validate CSV structure
        required = {"Source", "Destination"}
        if not required.issubset(df.columns):
            logging.error(f"CSV missing required columns: {required}")
            raise ValueError(f"CSV must have columns: {required}")

        # Convert to Path and resolve relative paths
        df["Source"] = df["Source"].apply(lambda p: (csv_dir / p).resolve() if not Path(p).is_absolute() else Path(p))
        df["Destination"] = df["Destination"].apply(lambda p: (csv_dir / p).resolve() if not Path(p).is_absolute() else Path(p))

        # Check all source files exist
        missing = [str(src) for src in df["Source"] if not src.exists()]
        if missing:
            logging.error("Missing source files:\n" + "\n".join(missing))
            raise FileNotFoundError(
                "The following source files do not exist:\n" + "\n".join(missing)
            )

        # Process each move
        for src, dst in zip(df["Source"], df["Destination"]):

            # Ensure destination directory exists
            if not dst.parent.exists():
                logging.info(f"Creating destination directory: {dst.parent}")
                dst.parent.mkdir(parents=True, exist_ok=True)

            # If destination file already exists, delete it
            if dst.exists():
                dst.unlink()

            # Move/rename file
            logging.info(f"Moving: {src} -> {dst}")
            shutil.move(str(src), str(dst))

        logging.info("All files successfully moved/renamed.")

if __name__ == "__main__":
    # If no arguments are given, run a custom default function
    if len(sys.argv) == 1:
        choices_folder = Path("Choices")
        if choices_folder.exists() and choices_folder.is_dir():
            print('No arguments provided. Launching choice menu using "Choices" folder...')
            Handyman().choice(choices_folder)
        else:
            print('No arguments provided, and "Choices" folder not found.')
            Fire(Handyman)
    else:
        Fire(Handyman)

