# import numpy as np
import datetime as dt
from timeslot import TimeSlot
from dataclasses import dataclass

time_0900 = dt.time(hour=9)
time_1700 = dt.time(hour=17)
example_time_window = TimeSlot(time_0900, time_1700)
minutes_30 = dt.timedelta(minutes=30)


@dataclass(slots=True)
class Task:
        name: str
        description: str
        due_date: dt.datetime
        duration: dt.timedelta
        priority: int
        flexibility: bool
        difficulty: int
        work_length: dt.timedelta = minutes_30
        work_window: TimeSlot = example_time_window

        """
        **description** is self-explanatory.

        **due_date** is when something is due.

        **work_window** is the time of day in which you can work on this thing (say from 08:00 to 20:00).

        **duration** is how long you expect it to take to complete the task

        **priority** is going to be a number 0-5 (could be more or less) with 5 being the highest and 0 the lowest.
            Each number is going to correspond to a phrase which the user will select.

        **flexibility** is a bool where a 0 is not flexible and 1 is flexible. Flexible tasks can be moved about and
            dynamically scheduled. Inflexible tasks must always take place on the due date.

        **difficulty** is a number 1-10 of how difficult a task is expected to be by the user. More difficult tasks
            have higher urgency.

        **work_length** is how long the user wants to work on the task daily, default is 30 minutes
        """
test = Task(name='test', description='desctiption test', due_date=dt.datetime(year=2026, month=6, day=13, hour=12, minute=15), duration=dt.timedelta(hours=5), priority=5, flexibility=True, difficulty=10)
print(test)


def urgency(task:Task):
    """How soon something is due and how important it is. Maxes out at whatever priority is. Max if there are more days required to complete the task than days till it is due"""

    if not task.flexibility:
        _urgency = None  # Putting None here for now, but I should probably do something else in the future

    elif task.time_till_due.days == dt.timedelta(days=0).days:
        _urgency = task.priority

    else:
        days_to_complete = task.duration / task.work_length
        _urgency = (
            min(days_to_complete / task.time_till_due.days, 1) * task.priority
        )

    return _urgency


def ultimate_prio(task):
    """Make doc string"""
    if task.urgency is None:
        _ultimate_prio = None
    else:
        _ultimate_prio = task.urgency * task.difficulty
    return _ultimate_prio
