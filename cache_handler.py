import time
import os
import json

from logger import Log

class CacheHandler:
    def __init__(self):
        self.logger = Log()

    def __createFile(self, fileName):
        for file in os.listdir():
            if fileName in file:
                os.remove(file)
        
        constructFileName = f"{fileName}_{int(time.time())}.txt"

        try:
            with open(constructFileName, "x"):
                pass
            return constructFileName
        except FileExistsError:
            self.logger.log_error(f"Failed to create Cachefile: {constructFileName}", True)
            return None
    
    def getFileCacheTime(self, fileName):
        for file in os.listdir():
            if fileName in file:
                time = file.split("_")[1].split(".")[0]
                return int(time)
        return 0
    
    def write(self, fileName, data):
        file = self.__createFile(fileName)

        if file == None:
            self.logger.log_error(f"Cannot find file: {fileName}", True)
            return
    
        with open(file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        
    def read(self, fileName):
        for file in os.listdir():
            if fileName in file:
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        data = f.read()
                    return json.loads(data)
                
                except UnicodeDecodeError:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        data = f.read()
                    try:
                        return json.loads(data)
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