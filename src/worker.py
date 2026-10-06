import time

from src.pipeline import process_pending_files


def main():
    print("DataPulse worker started. Watching for CSV files.")
    while True:
        results = process_pending_files()
        for result in results:
            print(
                f"run={result['run_id']} rows={result['total_rows']} "
                f"clean={result['clean_rows']} quarantine={result['quarantined_rows']} "
                f"score={result['quality_score']}"
            )
        time.sleep(10)


if __name__ == "__main__":
    main()
