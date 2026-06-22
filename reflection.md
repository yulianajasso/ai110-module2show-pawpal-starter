# PawPal+ Project Reflection

## 1. System Design

**a. Core user actions**

The three core actions a user should be able to perform in PawPal+:

1. **Add and manage a pet profile** — The user enters their pet's basic information (name, species, breed, age). This profile is the foundation for all scheduling; the app needs to know *whose* care is being planned before any tasks make sense.

2. **Add and edit care tasks** — The user creates tasks such as walks, feedings, medication, grooming, or enrichment. Each task has at minimum a duration and a priority level. The user can also edit or remove tasks as the pet's needs change over time.

3. **Generate and view today's schedule** — The user triggers the scheduler, which takes the available time window and the list of tasks, then produces a prioritized daily plan with assigned time slots. The plan also explains the reasoning — which tasks were included, which were skipped, and why — so the owner understands and trusts the output.

**b. Initial design**

The system is built around four main objects:

---

**`Pet`**
Represents the animal being cared for.

- *Attributes:* `name`, `species`, `breed`, `age`
- *Methods:*
  - `get_profile()` — returns a summary of the pet's info for display
  - `update_info(...)` — allows editing name, breed, or age after creation

---

**`Task`**
Represents a single care activity.

- *Attributes:* `name`, `duration` (minutes), `priority` (`high` / `medium` / `low`), `recurrence` (`daily` / `weekly` / `as-needed`), `notes`
- *Methods:*
  - `is_due_today()` — checks whether the task should appear in today's plan based on recurrence
  - `to_dict()` — serializes the task for storage or display

---

**`Owner`**
Represents the person using the app and their daily constraints.

- *Attributes:* `name`, `available_time` (total minutes free today), `preferences` (e.g., preferred start time, tasks to always include)
- *Methods:*
  - `set_availability(minutes)` — updates how much time is free today
  - `get_constraints()` — returns the time and preference constraints the scheduler will use

---

**`Scheduler`**
Contains the planning logic — the brain of the app.

- *Attributes:* `pet`, `owner`, `tasks` (list of Task objects), `schedule` (ordered list of scheduled slots)
- *Methods:*
  - `add_task(task)` — adds a Task to the task list
  - `remove_task(task_name)` — removes a task by name
  - `generate_plan()` — sorts tasks by priority, fits them into the available time window, and returns an ordered schedule
  - `explain_plan()` — returns a human-readable explanation of why each task was included or skipped

---

**Relationships:**
- `Owner` has one `Pet`
- `Scheduler` belongs to an `Owner` and holds a list of `Task` objects
- `Scheduler.generate_plan()` uses both `Owner.get_constraints()` and `Task.is_due_today()` to decide what makes the final schedule

**b. Design changes**

After reviewing the skeleton with an AI assistant, three gaps were identified and corrected:

1. **Added `pet` attribute to `Owner`** — The UML showed `Owner --> Pet`, but the initial skeleton had no `pet` field on `Owner`. Without it, there was no way to navigate from an owner to their pet. Fixed by adding `self.pet` to `Owner.__init__`.

2. **Added `last_completed` to `Task`** — `is_due_today()` is supposed to handle recurrence (daily vs. weekly), but the original `Task` had no date tracking. A weekly task has no way to know if it was already done this week without storing when it was last completed. Added `last_completed: Optional[str]` (ISO date string).

3. **Added `start_time` to `Owner`** — `generate_plan()` needs to assign actual clock times (e.g., "8:00 AM — Morning walk"). Without a day-start time, the scheduler can only produce a relative order, not a real schedule. Added `start_time: int` (minutes since midnight, defaulting to 480 = 8:00 AM).

These were structural gaps — not logic errors — that would have required revisiting the data model mid-implementation if left unfixed.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
