# import numpy as np
import datetime as dt
from timeslot import TimeSlot

time_0900 = dt.time(hour=9)
time_1700 = dt.time(hour=17)
example_time_window = TimeSlot(time_0900, time_1700)
minutes_30 = dt.timedelta(minutes=30)


class Task:
    def __init__(
        self,
        name: str,
        description: str,
        due_date: dt.datetime,
        duration: dt.timedelta,
        priority: int,
        flexibility: bool,
        difficulty: int,
        work_length: dt.timedelta = minutes_30,
        work_window: TimeSlot = example_time_window,
    ):
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

        self.name: str = name
        self.description: str = description
        self.due_date: dt.datetime = due_date
        self.work_window: TimeSlot = work_window
        self.duration: dt.timedelta = duration
        self.priority = priority
        self.flexibility: bool = flexibility
        self.difficulty = difficulty
        self.work_length: dt.timedelta = work_length

        self.date_created: dt.datetime = dt.datetime.now()

        self._priority: float
        self._difficulty: float
        self._time_scheduled: dt.datetime

    @property
    def priority(self):
        """Make doc string"""
        return self._priority

    @priority.setter
    def priority(self, value: int):
        if value not in range(0, 6, 1):
            raise ValueError(
                "priority outside of expected range, must be an integer from 0 to 5 in the form of a string"
            )
        else:
            self._priority = 1.0 + value / 10.0

    @property
    def difficulty(self):
        """Make doc string"""
        return self._difficulty

    @difficulty.setter
    def difficulty(self, value: int):
        if value not in range(0, 11, 1):
            raise ValueError(
                "difficulty outside of expected range, must be an integer from 0 to 10."
            )
        else:
            self._difficulty = 1.0 + value / 10.0

    @property
    def time_till_due(self):
        """The time left to complete a task in seconds. Otherwise, the amount of seconds between now and the due date"""
        today = dt.datetime.now()

        if self.due_date >= today:
            _time_till_due = self.due_date - today

        else:
            _time_till_due = dt.timedelta(days=0)

        return _time_till_due

    @property
    def urgency(self):
        """How soon something is due and how important it is. Maxes out at whatever priority is. Max if there are more days required to complete the task than days till it is due"""

        if not self.flexibility:
            _urgency = None  # Putting None here for now, but I should probably do something else in the future

        elif self.time_till_due.days == dt.timedelta(days=0).days:
            _urgency = self.priority

        else:
            days_to_complete = self.duration / self.work_length
            _urgency = (
                min(days_to_complete / self.time_till_due.days, 1) * self.priority
            )

        return _urgency

    @property
    def ultimate_prio(self):
        """Make doc string"""
        if self.urgency is None:
            _ultimate_prio = None
        else:
            _ultimate_prio = self.urgency * self.difficulty
        return _ultimate_prio

    @property
    def time_scheduled(self):
        return self._time_scheduled

    @time_scheduled.setter
    def time_scheduled(self, value: dt.datetime):
        self._time_scheduled = value
