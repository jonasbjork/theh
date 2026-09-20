import csv
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_FILE = Path("scan-data.csv")
ALLOWLIST_FILE = Path("allowed-hosts.txt")
OUTPUT_FILE = Path("inventory.json")


def load_allowed_hosts(path):
    """Returnera en mängd med tillåtna värdadresser."""
    with path.open(encoding="utf-8") as handle:
        return {
            line.strip()
            for line in handle
            if line.strip() and not line.startswith("#")
        }


def load_observations(path, allowed_hosts):
    """Läs CSV och separera godkända rader från scope-avvikelser."""
    accepted = []
    rejected = []

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"host", "port", "protocol", "state", "service"}

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV-filen saknar obligatoriska kolumner")

        for row_number, row in enumerate(reader, start=2):
            try:
                port = int(row["port"])
            except ValueError as error:
                raise ValueError(
                    f"Ogiltigt portnummer på rad {row_number}"
                ) from error

            if not 0 < port <= 65535:
                raise ValueError(f"Port utanför giltigt intervall på rad {row_number}")

            observation = {
                "host": row["host"].strip(),
                "port": port,
                "protocol": row["protocol"].strip().lower(),
                "state": row["state"].strip().lower(),
                "service": row["service"].strip().lower(),
                "source_row": row_number,
            }

            if observation["host"] in allowed_hosts:
                accepted.append(observation)
            else:
                observation["reason"] = "host_not_in_allowlist"
                rejected.append(observation)

    return accepted, rejected


def main():
    allowed_hosts = load_allowed_hosts(ALLOWLIST_FILE)
    accepted, rejected = load_observations(DATA_FILE, allowed_hosts)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": str(DATA_FILE),
        "allowed_hosts": sorted(allowed_hosts),
        "observations": accepted,
        "scope_exceptions": rejected,
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print(f"Godkända observationer: {len(accepted)}")
    print(f"Scope-avvikelser: {len(rejected)}")
    print(f"Rapport sparad i {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
