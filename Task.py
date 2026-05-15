import numpy as np
import datetime as dt

class Task():

    def __init__(self, name:str, description:str, due_date:dt.datetime, timeslot, duration:dt.timedelta,\
                  priority:str, flexibility:bool, difficulty:str, work_length:dt.timedelta= dt.timedelta(minutes=30)):
        """
        description is self explanatory.

        due_date is when something is due.

        timeslot is the time of day in which you can work on this thing (say from 08:00 to 20:00).

        duration is how long you expect it to take to complete the task

        priority is going to be a number 0-5 (could be more or less) with 5 being the highest and 0 the lowest. 
            Each number is going to correspond to a phrase which the user will select.

        flexibility is a bool where a 0 is not flexible and 1 is flexible. Flexible tasks can be moved about and
            dynamically scheduled. Inflexible tasks must always take place on the due date.

        difficulty is a number 1-10 of how difficult a task is expected to be by the user. More difficult tasks
            have higher urgency.
        
        work_length is how long the user wants to work on the task daily, default is 30 minutes
        """
        self.name = name
        self.description = description
        self.due_date = due_date
        self.timeslot = timeslot
        self.duration = duration
        self.priority = priority
        self.flexibility = flexibility
        self.difficulty = difficulty
        self.work_length = work_length
        
        self.date_created = dt.datetime.now() #This gets reset everytime that the class is initiallized (which happens everytime I run this file)


    @property
    def priority(self):
        """Make doc string"""
        return self._priority
    
    @priority.setter
    def priority(self, value:str):
        priority_dic = {"0":0.2, "1":0.8, "2":1.0, "3":1.3, "4":1.6, "5":2.0}
        keys = list(priority_dic.keys())
        if value not in keys:
            raise ValueError(f"priority outside of expected range, must be an integer from {keys[0]} to {keys[-1]} in the form of a string")
        else:
            self._priority = priority_dic[value]


    @property
    def difficulty(self):
        """Make doc string"""
        return self._difficulty
    
    @difficulty.setter
    def difficulty(self, value:str):
        difficulty_dic = {"0":0.5, "1":0.6, "2":0.7, "3":0.8, "4":0.9, "5":1.0, "6":1.2, "7":1.4, "8":1.6, "9":1.8, "10":2.0}
        keys = list(difficulty_dic.keys())
        if value not in keys:
            raise ValueError(f"difficulty outside of expected range, must be an integer from {keys[0]} to {keys[-1]} in the form of a string.")
        else:
            self._difficulty = difficulty_dic[value]


    @property
    def time_till_due(self):
        """The time left to complete a task in seconds. Otherwise the amount of seconds between now and the due date"""
        today = dt.datetime.now()

        if self.due_date >= today:
            _time_till_due = (self.due_date - today)

        else:
            _time_till_due = dt.timedelta(days=0)

        return _time_till_due
    

    @property
    def work_required(self):
        """The amount of "work" required to complete a task. "Work" is calculated by multiplying the duration by the difficulty modifier"""
        if self.flexibility == False:
            _work_required = None # This could also be 0 but that could result in accidental divide by zero errors.
        else:
            _work_required = self.duration*self.difficulty # This formula probably needs adjustment.

        return _work_required
    

    @property
    def urgency(self):
        """How soon something is due and how important it is. Maxes out at whatever priority is. Max if there are more days required to complete the task than days till it is due"""

        if self.flexibility == False:
            _urgency = None # Putting None here for now, but I should probably do something else in the future

        elif self.time_till_due.days == dt.timedelta(days=0).days:
            _urgency = self.priority
            
        else:
            days_to_complete = self.duration/self.work_length
            _urgency = min(days_to_complete/self.time_till_due.days,1)*self.priority 

        return _urgency
    

    @property
    def ultimate_prio(self):
        """Make doc string"""
        if self.work_required == None or self.urgency == None:
            _ultimate_prio = None
        else:
            work_hours = self.work_required/dt.timedelta(hours=1)
            _ultimate_prio = self.urgency*work_hours
        return _ultimate_prio

