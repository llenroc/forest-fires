import numpy as np
import pandas as pd
from datetime import timedelta, datetime

class BaseTimeFold(object):
    ''' 
    Base class for a cross-validation iterator. 

    Setup and prep for the class.
    '''

<<<<<<< HEAD
    def __init__(self, df, step_size, max_folds, test_set_date, 
            resample_train_fire_pct, resample_method):
        ''' Inputs: Pandas DataFrame, Datetime timedelta, Integer''' 
        
        self.n_folds = 0
        self.max_folds = max_folds
        self.df = df
        self.all_dates = df['date_fire'] 
        self.step_size = step_size
        self.test_date = test_set_date - timedelta(days=1)
        self.resample_method = resample_method
        self.resample_train_fire_pct = resample_train_fire_pct

    def __len__(self): 
        return self.n_folds

    def _check_resample(self, train_indices): 
        '''Input: Numpy Array

        Check the percent of the obs. in the training set that will be
        actual fires. If it is smaller than the resample_train_fire_pct, 
        then resample as noted by the resample_method attribute. 
        '''
        training_perc_fire = self.df.ix[train_indices, 'fire_bool'].mean()
        
        if training_perc_fire > self.resample_train_fire_pct: 
            return train_indices
        else: 
            train_indices = self._resample(train_indices)
            return train_indices

    def _resample(self, train_indices): 
        '''Input: Numpy Array 

        Conduct resampling as noted by the resample_method attribute. 
        "simple upsample" will just be duplicating a # of random positive 
        cases; "downsample"  will be taking all positive cases and a random 
        number of equal negative cases. 
        '''

        if self.resample_method == 'simple upsample': 
            fire_indices = np.where(self.df['fire_bool'] == True)[0]
            positive_indices = np.intersect1d(fire_indices, train_indices)
            # Get a random sample from the positive indices, equal in size. 
            resampled_indices = np.random.choice(positive_indices, 
                    positive_indices.shape[0])
            train_indices = np.concatenate((train_indices, resampled_indices), 
                    axis=0)
            return train_indices
        if self.resample_method == 'downsample': 
            fire_indices = np.where(self.df['fire_bool'] == True)[0]
            positive_indices = np.intersect1d(fire_indices, train_indices)
            negative_indices = np.setdiff1d(train_indices, fire_indices)
            resampled_indices = np.random.choice(negative_indices, 
                    positive_indices.shape[0], replace=False)
            train_indices = np.concatenate((positive_indices, resampled_indices),
                    axis=0)
            return train_indices
=======
    def __init__(self, dates, step_size, init_split_point=None): 
        ''' Inputs: NumpyArray, Datetime timedelta, Datetime datetime ''' 
        
        self.n_folds = 0
        self.dates = pd.Series(dates)
        self.step_size = step_size
        self.test_indices = np.array((3, 4))
        if not init_split_point:
            self._set_init_split_point()
            self.split_point = self.init_split_point
        else: 
            self.init_split_point = init_split_point
            self.split_point = self.init_split_point

    def _set_init_split_point(self): 
        ''' 
        Assign an initial time-based split point 
        for the first train/test split. 
        '''
        
        exact_init_split_point = self.dates.min() + self.step_size
        # We need to round this to midnight so that we don't get 
        # obs. on the same day in the train and test sets. 
        self.init_split_point = datetime(exact_init_split_point.year, 
                        exact_init_split_point.month, exact_init_split_point.day, 
                        0, 0, 0)
    def __len__(self): 
        return self.n_folds
>>>>>>> master

class SequentialTimeFold(BaseTimeFold):
    ''' 
    Sequential time fold cross-validation iterator. 

    Provides train/test indices to split the data based 
    off a date or datetime column. The user inputs 
    a numpy array of dates, and a step size by which to 
    generate the folds. 

    Folds are created in a sequential manner, where 
<<<<<<< HEAD
    all obs. on days before the test_date - step_size 
    are in the training set, and all obs. on the test_date 
    are in the test set. 
    '''

    def __init__(self, df, step_size, max_folds, test_set_date): 
        super(SequentialTimeFold, self).__init__(df, step_size, max_folds, 
                test_set_date)
=======
    all dates before the split_point + step_size are 
    in the training folds, and all dates after are in 
    the test folds. 
    '''

    def __init__(self, dates, step_size, init_split_point=None): 
        super(SequentialTimeFold, self).__init__(dates, step_size, 
                init_split_point)
>>>>>>> master

    def __iter__(self): 
        return self

    def next(self):
        ''' Generates integer indices corresponding to train/test sets. '''
<<<<<<< HEAD
        # Initialize a array with shape 0 so that we can issue the check 
        # every time to make sure that we don't return back a test_indices
        # array with no actual indices. 
        test_indices = np.zeros((0))

        while test_indices.shape[0] == 0: 
            test_date = self.test_date
            test_date_plus = test_date + timedelta(days=1)
            test_indices = np.where(np.logical_and(self.all_dates >= test_date, 
                self.all_dates < test_date_plus))[0]
            train_indices = np.where(self.all_dates < test_date)[0]
            self.test_date -= self.step_size
        
        if self.n_folds <= self.max_folds: 
=======
        split_point = self.split_point
        test_indices = np.where(self.dates >= self.split_point)[0]
        train_indices = np.where(self.dates < self.split_point)[0]
        self.test_indices = test_indices 
        self.split_point += self.step_size
        
        if self.test_indices.shape[0] != 0: 
>>>>>>> master
            self.n_folds += 1
            return train_indices, test_indices
        else: 
            raise StopIteration()

class StratifiedTimeFold(BaseTimeFold):
    ''' 
    Stratified time fold cross-validation iterator. 

    Provides train/test indices to split the data based 
    off a date or datetime column. The user inputs 
    a numpy array of dates, and a step size by which to 
    generate the folds. 

    Folds are created in a stratified manner.  
    '''

<<<<<<< HEAD
    def __init__(self, df, step_size, max_folds, test_set_date, days_back, 
            cutoff_train_fire_pct=0.05, resample_train_fire_pct=0.20,
            resample_method='downsample'):
        super(StratifiedTimeFold, self).__init__(df, step_size, max_folds, 
                test_set_date, resample_train_fire_pct, resample_method)
        self.years_list = self._set_years_list() 
        self.days_back = days_back
        self.cutoff_train_fire_pct = cutoff_train_fire_pct
=======
    def __init__(self, dates, step_size, init_split_point=None): 
        super(StratifiedTimeFold, self).__init__(dates, step_size, 
                init_split_point)
        self.years_list = self._set_years_list() 
>>>>>>> master

    def _set_years_list(self): 
        ''' 
        Create a list of years to cycle 
        through for the iteration process. 
        '''
<<<<<<< HEAD
        year_max = self.all_dates.max().year
        year_min = self.all_dates.min().year
=======
        year_max = self.dates.max().year
        year_min = self.dates.min().year
>>>>>>> master
        year_list = xrange(year_min, year_max + 1)
        return year_list

    def __iter__(self): 
        return self

    def next(self):

        ''' Generates integer indices corresponding to train/test sets. '''
<<<<<<< HEAD
        test_indices, train_indices = np.zeros((0)), np.array([])
        
        while test_indices.shape[0] == 0: 
            test_date = self.test_date
            test_date_plus = test_date + self.step_size 
            test_indices = np.where(np.logical_and(self.all_dates >= test_date, 
                self.all_dates < test_date_plus))[0]
          
            # Now grab all the fires that will be used for training. We'll 
            # have to cycle back through the years to grab these. 
            for year in self.years_list:
                train_idx_temp = self._grab_indices(year)
                train_indices = np.concatenate((train_idx_temp, train_indices))
            training_perc_fire = self.df.ix[train_indices, 'fire_bool'].mean()
            if training_perc_fire < self.cutoff_train_fire_pct:  
                train_indices = np.where(self.all_dates < self.test_date)[0]
            self.test_date -= self.step_size
        
        training_perc_fire = self.df.ix[train_indices, 'fire_bool'].mean()
        print training_perc_fire
        train_indices = self._check_resample(train_indices)
        training_perc_fire = self.df.ix[train_indices, 'fire_bool'].mean()
        print training_perc_fire
        if self.n_folds <= self.max_folds: 
            self.n_folds += 1
=======
        idx = np.arange(self.dates.shape[0])
        test_indices, train_indices = np.array([]), np.array([])
        
        if self.test_indices.shape[0] != 0: 
            self.n_folds += 1
            for year in self.years_list:
                train_idx_temp, test_idx_temp = self._grab_indices(year)
                train_indices = np.concatenate((train_idx_temp, train_indices))
                test_indices = np.concatenate((test_idx_temp, test_indices))
            self.split_point += self.step_size
            self.test_indices = test_indices 
            
>>>>>>> master
            return train_indices, test_indices
        else: 
            raise StopIteration()

    def _grab_indices(self, year): 
        '''
        Input: Integer
        Output: Numpy Array, Numpy Array 

        Grab the train and test indices. 
        '''

<<<<<<< HEAD
        date_range = self._get_date_range(year)

        train_indices = np.where((self.all_dates >= date_range.min()) 
                & (self.all_dates < date_range.max()))[0]

        return train_indices
=======
        split_point = self.split_point
        date_range = self._get_date_range(year)

        test_indices = np.where((self.dates >= date_range.min()) 
                & (self.dates < date_range.max()) 
                & (self.dates >= split_point))[0]
        train_indices = np.where((self.dates >= date_range.min()) 
                & (self.dates < date_range.max()) 
                & (self.dates < split_point))[0]

        return train_indices, test_indices
>>>>>>> master


    def _get_date_range(self, year): 
        '''
        Input: Integer
        Output: Pandas DateRange

<<<<<<< HEAD
        Output a date range based off of the current test_date 
        but for the inputted year. The output will be a date range 
        that starts at the test_date (with the year replaced by the 
        inputted year), and goes back by the days_back argument. 
        '''
    
        if year == self.test_date.year: 
            start_date_range = self.test_date
        else: 
            start_date_range = datetime(year, self.test_date.month, 
                    self.test_date.day + 1, 0, 0, 0) 
        end_date_range = start_date_range - timedelta(days=self.days_back)
        date_range = pd.date_range(end_date_range, start_date_range)
=======
        Output a date range based off of the current split
        point plus step size, but for the inputted year. The 
        output will be a date range that starts at the current 
        split point (with the year replaced by the inputted year), 
        and extends by the step size. 
        '''

        start_date_range = datetime(year, 
                self.split_point.month, self.split_point.day, 
                self.split_point.hour, self.split_point.minute, 
                self.split_point.second)
        end_date_range = start_date_range + self.step_size
        date_range = pd.date_range(start_date_range, end_date_range)
>>>>>>> master

        return date_range

