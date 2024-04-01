import sys
import ray
from collections import deque
from typing import Dict, List, Any

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from extensions.ray_objectives import CooperativeObjectivesListStorage

try:
    ray.init(address="auto", namespace="babyagi", logging_level=logging.FATAL, ignore_reinit_error=True)
except:
    ray.init(namespace="babyagi", logging_level=logging.FATAL, ignore_reinit_error=True)

@ray.remote(name="CooperativeTaskListStorageActor")
class CooperativeTaskListStorageActor:
    def __init__(self):
        self.tasks: deque[Dict[str, Any]] = deque([])
        self.task_id_counter: int = 0

    def append(self, task: Dict[str, Any]) -> None:
        self.tasks.append(task)
        del task  # remove the object from the object store after it's no longer needed

    def replace(self, tasks: List[Dict[str, Any]]) -> None:
        self.tasks = deque(tasks)

    def popleft(self) -> Dict[str, Any]:
        return self.tasks.popleft()

    def is_empty(self) -> bool:
        return not bool(self.tasks)

    def next_task_id(self) -> int:
        self.task_id_counter += 1
        return self.task_id_counter

    def get_task_names(self) -> List[str]:
        return [t["task_name"] for t in self.tasks]

