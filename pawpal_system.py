from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    name: str
    duration: int                         # minutes
    priority: str                         # "high", "medium", or "low"
    recurrence: str                       # "daily", "weekly", or "as-needed"
    notes: str = ""
    last_completed: Optional[str] = None  # ISO date string e.g. "2026-06-21"
    next_due: Optional[str] = None        # ISO date string for next scheduled occurrence
    completed_today: bool = False

    # How many days until this recurrence repeats
    _RECURRENCE_DAYS = {"daily": 1, "weekly": 7}

    def is_due_today(self) -> bool:
        """Return True if today is on or after next_due, or if the task has never been completed."""
        today = date.today()
        if self.next_due is not None:
            return today >= date.fromisoformat(self.next_due)
        # Fallback for tasks that have never been completed
        if self.completed_today:
            return False
        if self.recurrence == "weekly" and self.last_completed is not None:
            last = date.fromisoformat(self.last_completed)
            return (today - last) >= timedelta(days=7)
        # daily and as-needed with no history are always due
        return True

    def mark_complete(self) -> None:
        """Mark done today and calculate next_due via timedelta based on recurrence."""
        today = date.today()
        self.completed_today = True
        self.last_completed = today.isoformat()
        interval = self._RECURRENCE_DAYS.get(self.recurrence)
        if interval:
            self.next_due = (today + timedelta(days=interval)).isoformat()
        else:
            # as-needed: no automatic next occurrence
            self.next_due = None

    def to_dict(self) -> dict:
        """Serialize this task to a plain dictionary for storage or display."""
        return {
            "name": self.name,
            "duration": self.duration,
            "priority": self.priority,
            "recurrence": self.recurrence,
            "notes": self.notes,
            "last_completed": self.last_completed,
            "next_due": self.next_due,
            "completed_today": self.completed_today,
        }


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list = field(default_factory=list)  # list[Task]

    def get_profile(self) -> str:
        """Return a one-line summary of the pet's name, breed, species, and age."""
        return f"{self.name} ({self.breed} {self.species}, age {self.age})"

    def update_info(self, name: Optional[str] = None, breed: Optional[str] = None,
                    age: Optional[int] = None) -> None:
        """Update any combination of name, breed, or age; unchanged fields are left as-is."""
        if name is not None:
            self.name = name
        if breed is not None:
            self.breed = breed
        if age is not None:
            self.age = age

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove all tasks whose name matches task_name."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def get_due_tasks(self) -> list:
        """Return only the tasks that are due today."""
        return [t for t in self.tasks if t.is_due_today()]


class Owner:
    def __init__(self, name: str, available_time: int,
                 start_time: int = 480, preferences: Optional[dict] = None):
        self.name = name
        self.available_time = available_time  # total minutes free today
        self.start_time = start_time          # minutes since midnight (480 = 8:00 AM)
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name from the owner's list."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def set_availability(self, minutes: int) -> None:
        """Update the total minutes the owner has free today."""
        self.available_time = minutes

    def get_constraints(self) -> dict:
        """Return available time, day start time, and preferences as a dict."""
        return {
            "available_time": self.available_time,
            "start_time": self.start_time,
            "preferences": self.preferences,
        }

    def get_all_tasks(self) -> list:
        """Return all due tasks across every pet, tagged with the pet's name."""
        result = []
        for pet in self.pets:
            for task in pet.get_due_tasks():
                result.append((pet, task))
        return result

    def get_tasks_for_pet(self, pet_name: str) -> list:
        """Return all tasks (due or not) belonging to the named pet."""
        for pet in self.pets:
            if pet.name == pet_name:
                return list(pet.tasks)
        return []

    def get_incomplete_tasks(self) -> list:
        """Return all tasks across every pet that have not been completed today."""
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                if not task.completed_today:
                    result.append((pet, task))
        return result


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.schedule: list[dict] = []   # slots that made the cut
        self.skipped: list[dict] = []    # tasks that didn't fit or aren't due

    def generate_plan(self) -> list[dict]:
        """Sort due tasks by priority then greedily fill available time."""
        self.schedule = []
        self.skipped = []

        constraints = self.owner.get_constraints()
        time_remaining = constraints["available_time"]
        cursor = constraints["start_time"]  # current clock position (minutes since midnight)

        candidates = self.owner.get_all_tasks()
        # Sort by priority first, then shortest duration (fits more tasks in), then name
        candidates.sort(key=lambda pair: (
            PRIORITY_ORDER.get(pair[1].priority, 99),
            pair[1].duration,
            pair[1].name,
        ))

        for pet, task in candidates:
            if task.duration <= time_remaining:
                end = cursor + task.duration
                self.schedule.append({
                    "pet": pet.name,
                    "task": task.name,
                    "duration": task.duration,
                    "priority": task.priority,
                    "start": _minutes_to_time(cursor),
                    "end": _minutes_to_time(end),
                    "notes": task.notes,
                })
                cursor = end
                time_remaining -= task.duration
            else:
                self.skipped.append({
                    "pet": pet.name,
                    "task": task.name,
                    "duration": task.duration,
                    "priority": task.priority,
                    "reason": "not enough time remaining",
                })

        return self.schedule

    def explain_plan(self) -> str:
        if not self.schedule and not self.skipped:
            return "No plan generated yet. Call generate_plan() first."

        lines = []
        if self.schedule:
            lines.append(f"Daily plan for {self.owner.name}:\n")
            for slot in self.schedule:
                lines.append(
                    f"  {slot['start']} — {slot['end']}  {slot['task']} "
                    f"({slot['pet']}, {slot['duration']} min, priority: {slot['priority']})"
                )
                if slot["notes"]:
                    lines.append(f"    Note: {slot['notes']}")
        else:
            lines.append("No tasks were scheduled.")

        if self.skipped:
            lines.append("\nSkipped tasks:")
            for item in self.skipped:
                lines.append(
                    f"  - {item['task']} ({item['pet']}): {item['reason']}"
                )

        return "\n".join(lines)

    def sort_by_time(self) -> list[dict]:
        """Return the schedule sorted by start time (HH:MM strings sort correctly lexicographically)."""
        return sorted(self.schedule, key=lambda slot: slot["start"])

    def filter_by_pet(self, pet_name: str) -> list[dict]:
        """Return only the scheduled slots that belong to the given pet."""
        return [slot for slot in self.schedule if slot["pet"] == pet_name]

    def add_task(self, task: Task, pet_name: str) -> None:
        """Add a Task to the pet identified by pet_name; raises ValueError if not found."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                pet.add_task(task)
                return
        raise ValueError(f"No pet named '{pet_name}' found.")

    def remove_task(self, task_name: str, pet_name: str) -> None:
        """Remove a task by name from the pet identified by pet_name; raises ValueError if not found."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                pet.remove_task(task_name)
                return
        raise ValueError(f"No pet named '{pet_name}' found.")


def _minutes_to_time(minutes: int) -> str:
    """Convert minutes-since-midnight to a HH:MM string."""
    h, m = divmod(minutes, 60)
    return f"{h:02d}:{m:02d}"
