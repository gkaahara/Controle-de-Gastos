import pytest
import tempfile
import os
import json
from app.json_store import JsonStore


@pytest.fixture
def store():
    tmp = tempfile.mkdtemp()
    filepath = os.path.join(tmp, "test.json")
    s = JsonStore(filepath, backup_count=0)
    yield s
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


class TestJsonStore:
    def test_creates_file_on_init(self, store):
        assert os.path.exists(store.filepath)
        with open(store.filepath, "r") as f:
            assert json.load(f) == []

    def test_create_adds_item(self, store):
        item = store.create({"nome": "Teste", "valor": 100})
        assert item["id"] is not None
        assert item["nome"] == "Teste"
        assert item["valor"] == 100
        assert "createdAt" in item

    def test_get_all_returns_all(self, store):
        store.create({"nome": "A"})
        store.create({"nome": "B"})
        items = store.get_all()
        assert len(items) == 2

    def test_get_by_id_returns_item(self, store):
        created = store.create({"nome": "Teste"})
        fetched = store.get_by_id(created["id"])
        assert fetched["nome"] == "Teste"

    def test_get_by_id_returns_none_if_not_found(self, store):
        assert store.get_by_id("nonexistent") is None

    def test_update_modifies_item(self, store):
        created = store.create({"nome": "Antigo"})
        updated = store.update(created["id"], {"nome": "Novo"})
        assert updated["nome"] == "Novo"
        assert updated["id"] == created["id"]

    def test_update_returns_none_if_not_found(self, store):
        assert store.update("nonexistent", {"nome": "X"}) is None

    def test_delete_removes_item(self, store):
        created = store.create({"nome": "Remover"})
        result = store.delete(created["id"])
        assert result is True
        assert store.get_by_id(created["id"]) is None

    def test_delete_returns_false_if_not_found(self, store):
        assert store.delete("nonexistent") is False

    def test_lock_acquired_during_write(self, store):
        store.create({"nome": "Lock test"})
        items = store.get_all()
        assert len(items) == 1


class TestJsonStoreBackup:
    def test_backup_created_on_first_write(self):
        tmp = tempfile.mkdtemp()
        filepath = os.path.join(tmp, "data.json")
        store = JsonStore(filepath, backup_count=3)
        store.create({"nome": "Teste"})
        backup_dir = os.path.join(os.path.dirname(filepath), "backups")
        assert os.path.isdir(backup_dir)
        files = os.listdir(backup_dir)
        assert len(files) == 1
        assert files[0].startswith("data_")
        assert files[0].endswith(".json")

    def test_backup_contains_previous_state(self):
        tmp = tempfile.mkdtemp()
        filepath = os.path.join(tmp, "data.json")
        store = JsonStore(filepath, backup_count=3)
        store.create({"nome": "Primeiro"})
        store.create({"nome": "Segundo"})
        backup_dir = os.path.join(os.path.dirname(filepath), "backups")
        backup_files = sorted(os.listdir(backup_dir))
        first_backup = json.load(open(os.path.join(backup_dir, backup_files[0])))
        assert len(first_backup) == 0
        second_backup = json.load(open(os.path.join(backup_dir, backup_files[1])))
        assert len(second_backup) == 1
        assert second_backup[0]["nome"] == "Primeiro"

    def test_backup_rotation_removes_oldest(self):
        tmp = tempfile.mkdtemp()
        filepath = os.path.join(tmp, "data.json")
        store = JsonStore(filepath, backup_count=2)
        for i in range(4):
            store.create({"nome": f"Item {i}"})
        backup_dir = os.path.join(os.path.dirname(filepath), "backups")
        files = os.listdir(backup_dir)
        assert len(files) == 2

    def test_backup_disabled_when_count_zero(self):
        tmp = tempfile.mkdtemp()
        filepath = os.path.join(tmp, "data.json")
        store = JsonStore(filepath, backup_count=0)
        store.create({"nome": "Teste"})
        backup_dir = os.path.join(os.path.dirname(filepath), "backups")
        assert not os.path.isdir(backup_dir)
