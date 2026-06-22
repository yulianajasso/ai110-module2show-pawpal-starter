from dataclasses import dataclass
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int

    def get_profile(self) -> str:
        pass

    def update_info(self, name: Optional[str] = None, breed: Optional[str] = None, age: Optional[int] = None) -> None:
        pass


@dataclass
class Task:
    name: str
    duration: int                        # minutes
    priority: str                        # "high", "medium", or "low"
    recurrence: str                      # "daily", "weekly", or "as-needed"
    notes: str = ""
    last_completed: Optional[str] = None # ISO date string, e.g. "2026-06-21"

    def is_due_today(self) -> bool:
        pass

    def to_dict(self) -> dict:
        pass


class Owner:
    def __init__(self, name: str, available_time: int, pet: "Pet" = None,
                 start_time: int = 480, preferences: Optional[dict] = None):
        self.name = name
        self.available_time = available_time          # total minutes free today
        self.pet = pet                                # the pet this owner cares for
        self.start_time = start_time                  # day start in minutes since midnight (480 = 8:00 AM)
        self.preferences = preferences or {}

    def set_availability(self, minutes: int) -> None:
        pass

    def get_constraints(self) -> dict:
        pass


class Scheduler:
    def __init__(self, pet: Pet, owner: Owner):
        self.pet = pet
        self.owner = owner
        self.tasks: list[Task] = []
        self.schedule: list[dict] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_name: str) -> None:
        pass

    def generate_plan(self) -> list:
        pass

    def explain_plan(self) -> str:
        pass
