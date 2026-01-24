import os
import unittest
import uuid

import pytest
from crewai.utilities.file_handler import PickleHandler


class TestPickleHandler(unittest.TestCase):
    def setUp(self):
        # Use a unique file name for each test to avoid race conditions in parallel test execution
        unique_id = str(uuid.uuid4())
        self.file_name = f"test_data_{unique_id}.json"
        self.file_path = os.path.join(os.getcwd(), self.file_name)
        self.handler = PickleHandler(self.file_name)

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_initialize_file(self):
        assert os.path.exists(self.file_path) is False

        self.handler.initialize_file()

        assert os.path.exists(self.file_path) is True
        assert os.path.getsize(self.file_path) >= 0

    def test_save_and_load(self):
        data = {"key": "value"}
        self.handler.save(data)
        loaded_data = self.handler.load()
        assert loaded_data == data

    def test_load_empty_file(self):
        loaded_data = self.handler.load()
        assert loaded_data == {}

    def test_load_corrupted_file(self):
        # Write invalid JSON to simulate corruption
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write("corrupted data {not valid json")
            file.flush()
            os.fsync(file.fileno())  # Ensure data is written to disk

        # Corrupted JSON files should return empty dict (graceful handling)
        loaded_data = self.handler.load()
        assert loaded_data == {}

    def test_pkl_extension_converted_to_json(self):
        # Test that .pkl extensions are converted to .json
        handler = PickleHandler("test_file.pkl")
        assert handler.file_path.endswith(".json")
