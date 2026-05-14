import numpy as np
import datetime as dt

class Task():

    def __init__(self, name:str, description:str, due_date:dt.datetime, timeslot, duration:dt.timedelta,\
                  priority:str, flexibility:bool, difficulty:str):
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
        """
        self.name = name
        self.description = description
        self.due_date = due_date
        self.timeslot = timeslot
        self.duration = duration
        self.priority = priority
        self.flexibility = flexibility
        self.difficulty = difficulty


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

        #if self.due_date >= today:
        self._time_till_due = (self.due_date - today)

        #else:
        #    self._time_till_due = -( (self.due_date - today).total_seconds() )

        return self._time_till_due
    

    @property
    def work_required(self):
        """The amount of "work" required to complete a task. "Work" is calculated by multiplying the duration by the difficulty modifier"""
        if self.flexibility == False:
            self._work_required = None # This could also be 0 but that could result in accidental divide by zero errors.
        else:
            self._work_required = self.duration*self.difficulty # This formula probably needs adjustment.

        return self._work_required
    

    @property
    def urgency(self):
        """How soon something is due and how important it is."""
        # This was originally going to be the ultimate number that would determine order of tasks, however I think splitting that off
        # into it's own thing and using this as just a measure of timeliness is best. It will be much easier to adjust timeliness separately
        # from work/time required to do something when structured this way.

        # I am unsure whether difficulty should be accounted for in urgency as it's already in work_required. It probably shouldn't be here
        # since difficulty is part of how long you think something will take rather than how long you have left/how much you want to prioritize
        # something.
        
        if self.flexibility == False:
            self._urgency = None # Putting None here for now, but I should probably do something else in the future
        
        else:
            days_to_complete = self.duration/dt.timedelta(minutes=30)
            self._urgency = self.time_till_due.days/days_to_complete            # This is wrong, but what I want to do is to check how many days are left till 
                                                                # the thing is due (not counting today). Then I want to check how many days it would
                                                                # take to complete the task if you spent 30 minutes on it everyday. You take both of
                                                                # those and divide the amount of days to complete the task at 30 minutes a day by
                                                                # the amount of days left till the thing is due. Given this is the case it seems
                                                                # like my current implementation of self.time_till_due is not good. I probably need
                                                                # to return the dt.datetime object instead of the raw total seconds like I am doing
                                                                # currently.

        return self._urgency

    

    """def calculate_urgency(self):
        urgency = float()
        if self.flexibility == False:
            urgency = 0
            return urgency
        today = dt.datetime.now()
        time_till = self.due_date - today

        urgency = (self.duration.total_seconds()/np.log(time_till.total_seconds()))#*self.priority*self.difficulty
        return urgency"""


test = Task(name="testname", description="test", due_date=dt.datetime(year= 2026, month= 6, day= 28), timeslot=None,\
             duration=dt.timedelta(hours= 5), priority="5", flexibility=True, difficulty="10")

print(test.difficulty, test.priority, test.time_till_due, test.work_required, test.urgency)