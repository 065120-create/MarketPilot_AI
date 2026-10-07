import logging
import threading
from datetime import datetime
from typing import List, Dict, Any

COLORS = {
    "RESET": "\033[0m",
    "INFO": "\033[94m",
    "SUCCESS": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "AGENT": "\033[96m",
    "SYSTEM": "\033[95m",
}

class MarketPilotLogger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MarketPilotLogger, cls).__new__(cls)
                cls._instance.logs = []
            return cls._instance

    def _format_message(self, level: str, agent: str, message: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        color = COLORS.get(level, COLORS["RESET"])
        reset = COLORS["RESET"]
        return f"{color}[{timestamp}] [{agent}] {message}{reset}"

    def _store_log(self, level: str, agent: str, message: str, metadata: Dict[str, Any] = None):
        with self._lock:
            self.logs.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "agent": agent,
                "message": message,
                "metadata": metadata or {}
            })
            if len(self.logs) > 1000:
                self.logs.pop(0)

    def log(self, level: str, agent: str, message: str, metadata: Dict[str, Any] = None):
        formatted_msg = self._format_message(level, agent, message)
        print(formatted_msg)
        self._store_log(level, agent, message, metadata)

    def agent_start(self, agent_name: str, task: str):
        self.log("AGENT", agent_name, f"Started task: {task}")

    def agent_complete(self, agent_name: str, task: str, result: str = ""):
        msg = f"Completed task: {task}" + (f" | {result}" if result else "")
        self.log("SUCCESS", agent_name, msg)

    def agent_error(self, agent_name: str, error: str):
        self.log("ERROR", agent_name, f"Error: {error}")

    def agent_retry(self, agent_name: str, attempt: int, error: str):
        self.log("WARNING", agent_name, f"Retry attempt {attempt} after error: {error}")

    def rag_query(self, query: str, results_count: int):
        self.log("SYSTEM", "RAG", f"Query: '{query}' returned {results_count} results")

    def tool_call(self, agent_name: str, tool_name: str, args: str):
        self.log("AGENT", agent_name, f"Called tool: {tool_name} with args: {args}")

    def quality_check(self, agent_name: str, check_name: str, passed: bool):
        level = "SUCCESS" if passed else "WARNING"
        self.log(level, agent_name, f"Quality check '{check_name}' passed: {passed}")

    def validation(self, component: str, message: str, is_valid: bool):
        level = "SUCCESS" if is_valid else "ERROR"
        self.log(level, "SYSTEM", f"Validation for {component}: {message}")

    def get_logs(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.logs)

logger = MarketPilotLogger()
