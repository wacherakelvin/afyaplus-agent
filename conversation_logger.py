import json
from datetime import datetime

class ConversationLogger:
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.start_time = datetime.utcnow().isoformat()
        self.messages = []
        self.total_tokens = 0
        self.turns = 0

    def add_exchange(self, user_text, assistant_text, tokens_used):
        timestamp = datetime.utcnow().isoformat()
        self.messages.append({"role": "user", "content": user_text, "timestamp": timestamp})
        self.messages.append({"role": "assistant", "content": assistant_text, "timestamp": timestamp})
        self.turns += 1
        self.total_tokens += tokens_used

    def save_log(self, path):
        end_time = datetime.utcnow().isoformat()
        log = {
            "patient_id": self.patient_id,
            "start_time": self.start_time,
            "end_time": end_time,
            "turns": self.turns,
            "total_tokens": self.total_tokens,
            "messages": self.messages,
        }
        with open(path, "w") as f:
            json.dump(log, f, indent=2)