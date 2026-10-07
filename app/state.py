"""MarketPilot AI - Thread-Safe In-Memory State Manager

Provides JobStore singleton with dual interface:
1. Method-based API: create_job, get_job, update_job, add_agent_execution
2. Dict-like API: job_store[job_id], job_id in job_store, job_store.get()
"""
import threading
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class JobDict(dict):
    """Dictionary subclass supporting attribute access and dict access."""
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

class JobStore:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JobStore, cls).__new__(cls)
                cls._instance.jobs: Dict[str, JobDict] = {}
                cls._instance._id_counter = 1
                cls._instance.audit_log: List[str] = []
            return cls._instance

    def _generate_job_id(self) -> str:
        with self._lock:
            current_id = self._id_counter
            self._id_counter += 1
            return f"MP-2026-{current_id:06d}"

    def create_job(self, campaign_input: Union[Dict[str, Any], Any]) -> str:
        """Create a new job and return its job_id."""
        job_id = self._generate_job_id()
        now = datetime.now().isoformat()
        campaign_data = campaign_input if isinstance(campaign_input, dict) else (
            campaign_input.model_dump() if hasattr(campaign_input, 'model_dump') else dict(campaign_input)
        )
        
        job = JobDict({
            "job_id": job_id,
            "status": "created",
            "campaign": campaign_data,
            "datasets": {},
            "corrections": [],
            "results": {},
            "execution_log": [],
            "agents": [],
            "progress": 0,
            "quality_checks": [],
            "rag_retrievals": [],
            "approval_status": "pending",
            "created_at": now,
            "updated_at": now
        })
        with self._lock:
            self.jobs[job_id] = job
            self.audit_log.append(f"{now} - Created job {job_id}")
        return job_id

    def get_job(self, job_id: str) -> Optional[JobDict]:
        """Get job by ID."""
        with self._lock:
            return self.jobs.get(job_id)

    def update_job(self, job_id: str, job_data: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[JobDict]:
        """Update job fields."""
        with self._lock:
            if job_id not in self.jobs:
                return None
            job = self.jobs[job_id]
            if job_data and isinstance(job_data, dict):
                job.update(job_data)
            if kwargs:
                job.update(kwargs)
            now = datetime.now().isoformat()
            job["updated_at"] = now
            self.audit_log.append(f"{now} - Updated job {job_id}")
            return job

    def update_status(self, job_id: str, status: str, progress: Optional[int] = None) -> Optional[JobDict]:
        """Update job status and optional progress percentage."""
        kwargs = {"status": status}
        if progress is not None:
            kwargs["progress"] = progress
        return self.update_job(job_id, **kwargs)

    def add_agent_execution(self, job_id: str, execution: Dict[str, Any]) -> bool:
        """Append an agent execution log entry."""
        with self._lock:
            if job_id not in self.jobs:
                return False
            if "execution_log" not in self.jobs[job_id]:
                self.jobs[job_id]["execution_log"] = []
            if "agents" not in self.jobs[job_id]:
                self.jobs[job_id]["agents"] = []
            self.jobs[job_id]["execution_log"].append(execution)
            self.jobs[job_id]["agents"].append(execution)
            now = datetime.now().isoformat()
            self.jobs[job_id]["updated_at"] = now
            self.audit_log.append(f"{now} - Agent execution logged for {job_id}: {execution.get('agent', 'unknown')}")
            return True

    def get_all_jobs(self) -> List[JobDict]:
        """Get all stored jobs."""
        with self._lock:
            return list(self.jobs.values())

    # Dict-like interface support
    def __getitem__(self, job_id: str) -> JobDict:
        with self._lock:
            if job_id not in self.jobs:
                raise KeyError(job_id)
            return self.jobs[job_id]

    def __setitem__(self, job_id: str, value: Any):
        with self._lock:
            if not isinstance(value, JobDict):
                value = JobDict(value if isinstance(value, dict) else {"data": value})
            value["job_id"] = job_id
            if "updated_at" not in value:
                value["updated_at"] = datetime.now().isoformat()
            self.jobs[job_id] = value

    def __contains__(self, job_id: str) -> bool:
        with self._lock:
            return job_id in self.jobs

    def __len__(self) -> int:
        with self._lock:
            return len(self.jobs)

    def get(self, job_id: str, default: Any = None) -> Any:
        with self._lock:
            return self.jobs.get(job_id, default)

    def items(self):
        with self._lock:
            return list(self.jobs.items())

    def values(self):
        with self._lock:
            return list(self.jobs.values())

    def keys(self):
        with self._lock:
            return list(self.jobs.keys())

# Global singleton instance
job_store = JobStore()
