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

The scheduler considers three constraints:

1. **Available time** — the owner sets how many minutes they have free today. No task can be scheduled if the remaining time is smaller than its duration. This is the hardest constraint: the scheduler stops accepting tasks the moment time runs out.

2. **Task priority** — each task is labeled high, medium, or low. The scheduler always places high-priority tasks first, so feeding and medication are never bumped by enrichment activities regardless of order. Within the same priority, shorter tasks come first as a tiebreaker, which maximizes how many tasks fit in the window.

3. **Recurrence and due date** — tasks are only eligible if `is_due_today()` returns True. Daily tasks are always eligible; weekly tasks check whether 7 days have passed since they were last completed using `next_due` and `timedelta`.

Available time was treated as the most important constraint because it is a hard physical limit — there is no way to schedule more minutes than exist. Priority was ranked second because the whole value of a scheduler is ensuring critical care (medication, feeding) always happens. Recurrence was a natural filter applied before the scheduler even sees the task list.

**b. Tradeoffs**

**Tradeoff: greedy priority fill vs. optimal packing**

The scheduler uses a greedy algorithm: it sorts tasks by priority (then shortest duration as a tiebreaker) and assigns them one by one until time runs out. Once a task is placed, the decision is final — the scheduler never backtracks to try a different combination that might fit more tasks overall.

This means a long high-priority task (e.g., a 45-minute vet visit) can consume most of the available time and cause several short medium-priority tasks to be skipped, even though skipping the vet visit would have allowed five other tasks to fit instead.

A more optimal approach — such as a knapsack algorithm — could find the combination of tasks that maximizes total value (weighted by priority) within the time budget. However, that would be significantly more complex to implement and explain, and for a daily pet care app the greedy approach is reasonable: pet owners generally *do* want high-priority tasks like feeding and medication to run first, even if it crowds out lower-priority ones. The greedy result matches the intuition of the user.

**Tradeoff noted during algorithm review: readability vs. conciseness in `detect_conflicts()`**

The AI suggested replacing the explicit `enumerate`/nested-loop pattern with `itertools.combinations`. The combinations version is more Pythonic but calls the `_time_to_minutes()` helper up to 4 times per pair (no caching) and hides the "compare each pair exactly once" intent behind a stdlib function name. The current explicit version was kept because it is easier to read and marginally more efficient.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used in four distinct roles across the project:

- **Design brainstorming** — in the early phases, asking "what classes does a pet care scheduler need and what should each one own?" produced the initial four-class structure (Pet, Task, Owner, Scheduler) quickly. Describing the system in plain English and letting AI suggest the structure was faster and more thorough than working from a blank page.

- **Skeleton generation** — once the design was agreed on, asking AI to generate Python dataclass stubs from the UML description saved the repetitive boilerplate work. The stubs were correct in structure even before any logic was filled in.

- **Gap detection** — attaching the skeleton and asking "does this match my UML, and are there any missing relationships?" caught three structural problems before implementation began: the missing `pet` reference on `Owner`, the missing `last_completed` on `Task`, and the missing `start_time` on `Owner`. Finding these in the design phase was much cheaper than discovering them mid-implementation.

- **Algorithm review** — sharing a completed method and asking "how could this be simplified?" produced a concrete alternative (`itertools.combinations`) that was worth evaluating even if it was ultimately not adopted.

The most effective prompt pattern was attaching the actual file and asking a specific, scoped question rather than a broad one. "Based on my skeleton, what structural gaps do you see?" produced five actionable findings. "How should I design a scheduler?" would have produced a generic answer.

**b. Judgment and verification**

During the algorithm review phase, the AI suggested replacing the explicit `enumerate`/nested-loop in `detect_conflicts()` with `itertools.combinations`. The suggestion was technically correct — `combinations(schedule, 2)` produces exactly the same pairs — and it is the more Pythonic pattern.

It was not accepted for two reasons. First, `combinations` calls `_time_to_minutes()` up to four times per pair because the converted start/end values aren't cached in variables, while the explicit version assigns them once per slot. Second, and more importantly, the explicit loop makes the intent visible: `for b in self.schedule[i+1:]` communicates "compare each pair exactly once and don't compare a slot against itself" in a way a reader can verify by inspection. `combinations` hides that guarantee behind a name that not every reader knows.

The evaluation process was: read the suggested code, ask "is this clearer or just shorter?", and run the existing tests against both versions to confirm they produced identical results. Both passed. The decision was made on readability grounds, not correctness.

How separate chat sessions helped: keeping the algorithmic work in a separate session from the core implementation prevented the context from becoming polluted with "are these classes right?" questions while writing "how should this algorithm work?" questions. Each session had a single focus, which made the AI's responses more targeted and made it easier to evaluate suggestions against the specific goal of that phase rather than the overall project.

---

## 4. Testing and Verification

**a. What you tested**

23 automated tests across seven areas:

- **Recurrence logic** — whether `is_due_today()` correctly gates tasks by their `next_due` date, including the boundary conditions (not due the day before, due on the exact day).
- **Task completion** — whether `mark_complete()` sets all three fields (`completed_today`, `last_completed`, `next_due`) correctly for each recurrence type.
- **Pet management** — adding and removing tasks, and confirming a pet with no tasks returns an empty due list.
- **Priority ordering** — that the scheduler places high-priority tasks before low, and shorter tasks before longer ones when priority is equal.
- **Time budget** — exact-fit scheduling, one-minute-over skipping, zero-minute edge case, and no-pets edge case.
- **Sorting and filtering** — `sort_by_time()` produces chronological output; `filter_by_pet()` isolates one pet; an unknown pet name returns an empty list.
- **Conflict detection** — a clean sequential schedule produces no warnings; a force-scheduled overlap triggers a warning; adjacent slots that merely touch do not count as conflicts.

These tests mattered because the scheduler's value depends entirely on it being correct. If `is_due_today()` has an off-by-one error, weekly tasks would be scheduled too early. If priority sorting is wrong, medication could be skipped in favour of enrichment. Automated tests make those guarantees verifiable in milliseconds on every future change.

**b. Confidence**

⭐⭐⭐⭐ (4/5). The core scheduling logic is well covered and all 23 tests pass. One star is withheld for two reasons: the tests run against in-memory objects only, so there are no integration tests for the Streamlit UI layer or for session persistence across page refreshes. A user interaction like refreshing the page mid-session, or adding the same pet name twice, could expose untested edge cases.

Edge cases to test next:
- Two pets with the same name (currently no guard against this)
- A task with `duration = 0`
- A user who sets available time to exactly the sum of all task durations
- Tasks whose `next_due` is in the past by more than one interval (e.g., a weekly task last completed 3 weeks ago)

---

## 5. Reflection

**a. What went well**

The part of this project I'm most satisfied with is the separation between the logic layer (`pawpal_system.py`) and the interface layer (`app.py`). Every scheduling decision — priority ordering, time budget enforcement, recurrence, conflict detection — lives in Python classes that can be tested independently of Streamlit. This made it possible to write 23 automated tests that run in under a second and verify the scheduler's behavior without ever opening a browser. It also made the UI code clean: `app.py` imports the classes and calls their methods; it does not contain any scheduling logic itself.

**b. What you would improve**

If I had another iteration, I would add persistence — right now the entire Owner, Pet, and Task state lives in `st.session_state` and disappears when the browser tab closes. A simple JSON save/load on the Owner object would let the app remember pets and tasks between sessions, which is the most obvious gap between a demo and a real tool a pet owner would actually use day to day.

I would also redesign the conflict detection to work proactively during `generate_plan()` rather than as a separate post-hoc check. Right now, `detect_conflicts()` can only find conflicts introduced by `force_schedule()` (since the greedy algorithm is inherently sequential and self-conflict-free). Making conflict detection part of the planning loop would make it meaningful for real scheduling scenarios where a user might manually assign time windows to tasks.

**c. Key takeaway**

The most important thing I learned is that being the "lead architect" in an AI-assisted workflow means owning the *why*, not just the *what*. AI can generate correct code quickly, but it doesn't know which tradeoffs matter for this specific app and this specific user. The decision to keep the explicit `enumerate` loop instead of `itertools.combinations`, to use a greedy algorithm instead of a knapsack solver, to store tasks on `Pet` rather than on `Scheduler` — none of those are objectively right or wrong. They are right *for this system* because of specific constraints: readability for a student codebase, simplicity matching a pet owner's mental model, and separation of concerns for testability.

AI made the implementation faster and surfaced options I might not have considered. But every choice about what to build, what to simplify, and what to reject had to come from a human who understood the problem. That is the role the lead architect plays and the one that cannot be delegated.
