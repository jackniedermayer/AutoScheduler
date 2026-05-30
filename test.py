import datetime as dt

from task import Task

test = Task(
    name="testname",
    description="test",
    due_date=dt.datetime(year=2026, month=5, day=19),
    work_window=None,
    duration=dt.timedelta(hours=5),
    priority="5",
    flexibility=True,
    difficulty="10",
)


print(
    test.difficulty, test.priority, test.time_till_due, test.urgency, test.ultimate_prio
)
