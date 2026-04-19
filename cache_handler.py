import time
import os
import json

from logger import Log

class CacheHandler:
    def __init__(self):
        self.filePrefix = "priceCache"
        self.logger = Log()

    def __createFile(self):
        for file in os.listdir():
            if self.filePrefix in file:
                os.remove(file)

        self.fileName = f"{self.filePrefix}_{int(time.time())}.txt"
        try:
            with open(self.fileName, "x"):
                pass
            self.logger.log_info(f"Created Cachefile: {self.fileName,}", True)
            return True
        except FileExistsError:
            self.logger.log_error(f"Failed to create Cachefile: {self.fileName,}", True)
            return False

    def getLastCacheTime(self):
        allFiles = os.listdir()
        for file in allFiles:
            if self.filePrefix in file:
                time = file.split("_")[1].split(".")[0]
                return int(time)
        return 0
    
    def getFileName(self):
        return self.fileName

    def write(self, data):
        if not (self.__createFile()):
            self.logger.log_error("Cannot find file:" + self.fileName,)
            return
        
        with open(self.fileName, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def read(self):
        for file in os.listdir():
            if self.filePrefix in file:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data_string = f.read()
                    return json.loads(data_string)
                except UnicodeDecodeError:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        data_string = f.read()
                    try:
                        return json.loads(data_string)
                    except json.JSONDecodeError:
                        self.logger.log_error(f"Invalid JSON in file {file}")
                        return None
                except json.JSONDecodeError:
                    self.logger.log_error(f"Invalid JSON in file {file}")
                    return None
                except Exception as e:
                    self.logger.log_error(f"Cannot read file {file}: {e}")
                    return None
        return None 