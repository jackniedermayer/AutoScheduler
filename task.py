import datetime as dt

# from dataclasses import dataclass
from pydantic.dataclasses import dataclass


time_0900 = dt.time(hour=9)
time_1700 = dt.time(hour=17)
example_time_window = (time_0900, time_1700)
minutes_30 = dt.timedelta(minutes=30)


@dataclass(slots=True)
class StaticTask:
    """
    This is for things like doctor appointments where it just happens over a certain time period. StaticTasks are also created when a Task is scheduled
    so there will be many StaticTask objects per Task.
        **description** is task-explanatory.

        **start_time** is when the task starts.

        **end_time** is when the task ends
    """

    name: str
    interval: tuple[dt.datetime, dt.datetime]
    description: str = ""
    parent_task: Task | None = None


@dataclass(slots=True)
class Task:
    """
    **description** is task-explanatory.

    **due_date** is when something is due.

    **work_window** is the time of day in which you can work on this thing (say from 08:00 to 20:00).

    **duration** is how long you expect it to take to complete the task

    **priority** is going to be a number 0-10 (could be more or less) with 10 being the highest and 0 the lowest.
        Each number is going to correspond to a phrase which the user will select.

    **flexibility** is a bool where a 0 is not flexible and 1 is flexible. Flexible tasks can be moved about and
        dynamically scheduled. Inflexible tasks must always take place on the due date.

    **difficulty** is a number 1-10 of how difficult a task is expected to be by the user. More difficult tasks
        have higher urgency.

    **work_length** is how long the user wants to work on the task daily, default is 30 minutes
    """

    name: str
    description: str
    due_date: dt.datetime
    duration: dt.timedelta
    priority: int
    difficulty: int
    work_length: dt.timedelta = minutes_30
    work_window: tuple[dt.time, dt.time] = example_time_window


def ultimate_prio(task: Task) -> float:
    """Make doc string"""
    today = dt.datetime.now()

    if task.due_date > today:
        time_till_due = task.due_date - today
    else:
        time_till_due = dt.timedelta(days=0)

    if time_till_due.days == 0:
        return task.priority * task.difficulty
    else:
        return (
            min((task.duration / task.work_length) / time_till_due.days, 1)
            * task.priority
            * task.difficulty
        )
