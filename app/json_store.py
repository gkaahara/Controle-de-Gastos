import json
import os
import shutil
import uuid
from datetime import datetime, timezone
import portalocker


class JsonStore:
    def __init__(self, filepath, lock_timeout=5, backup_count=None, backup_retention_days=365):
        self.filepath = filepath
        self.lock_timeout = lock_timeout
        self.backup_count = backup_count
        self.backup_retention_days = backup_retention_days
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                json.dump([], f)

    @property
    def _backup_dir(self):
        return os.path.join(os.path.dirname(self.filepath), "backups")

    def _backup(self):
        if self.backup_count == 0 or not os.path.exists(self.filepath):
            return
        os.makedirs(self._backup_dir, exist_ok=True)
        base = os.path.basename(self.filepath)
        name, ext = os.path.splitext(base)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_path = os.path.join(self._backup_dir, f"{name}_{ts}{ext}")
        shutil.copy2(self.filepath, backup_path)

        backups = sorted(
            f for f in os.listdir(self._backup_dir) if f.startswith(name) and f.endswith(ext)
        )

        # Remove backups older than retention days
        if self.backup_retention_days:
            cutoff = datetime.now().timestamp() - (self.backup_retention_days * 86400)
            for f in backups:
                try:
                    ts_part = f[len(name) + 1:-len(ext)]
                    file_dt = datetime.strptime(ts_part, "%Y%m%d_%H%M%S_%f")
                    if file_dt.timestamp() < cutoff:
                        os.remove(os.path.join(self._backup_dir, f))
                except (ValueError, IndexError):
                    continue
            backups = sorted(
                f for f in os.listdir(self._backup_dir) if f.startswith(name) and f.endswith(ext)
            )

        # Count-based cap (secondary)
        if self.backup_count:
            while len(backups) > self.backup_count:
                oldest = os.path.join(self._backup_dir, backups.pop(0))
                os.remove(oldest)

    def _read(self):
        with open(self.filepath, "r") as f:
            return json.load(f)

    def _write(self, data):
        self._backup()
        with portalocker.Lock(self.filepath, mode="w", timeout=self.lock_timeout) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all(self):
        return self._read()

    def get_by_id(self, item_id):
        data = self._read()
        for item in data:
            if item["id"] == item_id:
                return item
        return None

    def create(self, item):
        data = self._read()
        item["id"] = str(uuid.uuid4())
        item["createdAt"] = datetime.now(timezone.utc).isoformat()
        item["updatedAt"] = item["createdAt"]
        data.append(item)
        self._write(data)
        return item

    def update(self, item_id, updates):
        data = self._read()
        for i, item in enumerate(data):
            if item["id"] == item_id:
                data[i].update(updates)
                data[i]["updatedAt"] = datetime.now(timezone.utc).isoformat()
                self._write(data)
                return data[i]
        return None

    def delete(self, item_id):
        data = self._read()
        for i, item in enumerate(data):
            if item["id"] == item_id:
                data.pop(i)
                self._write(data)
                return True
        return False
