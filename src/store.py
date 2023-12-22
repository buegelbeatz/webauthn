"""
Simple local persistent singletone key/value-store to save and load all required informations for authentication in small Json files.
The main idea of this store is to just create, delete, load or search data, modification of existing data will not happen. 
"""

import os
import json
import glob
import re
from typing import List, Dict, Any
import datetime


class Store:
    """Encapsulation of the key/value store"""
    _instance = None

    def __new__(cls, path):
        """Implementing the singletone pattern here"""
        if cls._instance is None:
            cls._instance = super(Store, cls).__new__(cls)
            cls._instance.path = path
            if not os.path.exists(path):
                os.makedirs(path)
        return cls._instance
    
    def __init__(self, path):
        self.path = path

    def _filepath(self,key) -> str:
        return os.path.join(self.path, f"store_{key}.json")

    def load(self, key) -> Any:
        """load a json object from file system"""
        if os.path.exists(self._filepath(key)):
            with open(self._filepath(key), 'r', encoding="utf-8") as file:
                return json.load(file)
        return None

    def save(self, key, data):
        """save a json payload to the file system"""
        with open(self._filepath(key), 'w', encoding="utf-8") as file:
            data['timestamp'] = datetime.datetime.now().isoformat()
            json.dump(data, file)

    def remove(self, key):
        """deleting a specific file via key"""
        try:
            os.remove(self._filepath(key))
        except Exception: # # pylint: disable=W0718
            pass

    def count(self) -> int:
        """
            getting the numbers of files in the store. 
            If the count is 0 there should be some 
            kind of admin initialization
        """
        return len(glob.glob(self._filepath('*')))

    def search(self, search_string: str = '') -> List[Dict]:
        """picking a list of all store objects or filter for a specific object type"""
        _result = []
        files = glob.glob(self._filepath(f"{search_string}_*" if search_string else "*"))
        for _file in files:
            with open(_file, 'r', encoding="utf-8") as file:
                payload = json.load(file)
                pattern = re.compile(r"^.*/store_([^_]+)_([^\.]+)\.json$")
                if pattern.match(_file):
                    _type, _id = pattern.match(_file).groups()
                    file_infos = {'type': _type, 'id': _id}
                    _result.append({**payload , **file_infos})
        return _result

__all__ = ['Store']