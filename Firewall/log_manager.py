# log_manager.py
import os
import time
from datetime import datetime

class LogManager:
    def __init__(self, base_dir="logs", filename="devilfirewall.log"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.path = os.path.join(self.base_dir, filename)

    def _line(self, level, message):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{ts} | {level:<7} | {message}\n"

    def log(self, level, message):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(self._line(level, message))

    def info(self, message):  self.log("INFO", message)
    def warn(self, message):  self.log("WARN", message)
    def error(self, message): self.log("ERROR", message)

    def read_last(self, n=200):
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[-n:]

    def search(self, keyword, n=200):
        keyword = (keyword or "").lower()
        if not keyword:
            return self.read_last(n)
        matches = []
        for line in self.read_last(5000):
            if keyword in line.lower():
                matches.append(line)
                if len(matches) >= n:
                    break
        return matches
