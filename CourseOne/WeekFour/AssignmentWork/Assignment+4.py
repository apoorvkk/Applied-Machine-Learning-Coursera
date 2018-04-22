
# coding: utf-8

# ### ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[2]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[3]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[8]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''

        
    df = pd.read_table('university_towns.txt', header=None, names=['T'])
    
    df['State'] = df['T'].apply(lambda x: np.NaN if '[edit]' not in x else x.split('[')[0].strip())
    df['State'] = df['State'].ffill()
    df['RegionName'] = df['T'].apply(lambda x: np.NaN if '[edit]' in x else x.split('(')[0].strip())
    df = df.dropna()
    
    return df[['State', 'RegionName']]

get_list_of_university_towns()


# In[7]:

def get_gdp_figures():
    df = pd.read_excel('gdplev.xls', skiprows=7, usecols=[4,6], names=['Quarters', 'GDP in billions of chained 2009 dollars'])
    quarters = df['Quarters'].astype('category', categories=df['Quarters'], ordered=True)
    return df[quarters >= '2000q1']


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    df = get_gdp_figures()
    def is_start_of_recession(x):
        curr_val = x['GDP in billions of chained 2009 dollars']
        try:
            prev_val = df.loc[x.name - 1]['GDP in billions of chained 2009 dollars']  
        except KeyError:
            prev_val = None
        try:
            next_val = df.loc[x.name + 1]['GDP in billions of chained 2009 dollars']
        except KeyError:
            next_val = None
        
        if (not prev_val or (prev_val and prev_val > curr_val)) and (not next_val or (next_val and next_val < curr_val)):
            return True
        return False
        
    df['is_start_recession'] = df.apply(is_start_of_recession, axis=1)
    
    return df[df['is_start_recession']].iloc[0]['Quarters']
get_recession_start()


# In[6]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    df = get_gdp_figures()
    quarters = df['Quarters'].astype('category', categories=df['Quarters'], ordered=True)
    df = df[quarters >= '2008q3']
 
    def is_end_of_recession(x):
        curr_val = x['GDP in billions of chained 2009 dollars']
        try:
            prev_val = df.loc[x.name - 1]['GDP in billions of chained 2009 dollars']  
        except KeyError:
            prev_val = None
        try:
            before_prev_val = df.loc[x.name - 2]['GDP in billions of chained 2009 dollars']
        except KeyError:
            before_prev_val = None
        
        if not prev_val or not before_prev_val:
            return False
        
        if before_prev_val < prev_val < curr_val:
            return True
        return False
    df['is_end_recession'] = df.apply(is_end_of_recession, axis=1)
    
    return df[df['is_end_recession'] == True].iloc[0]['Quarters']
get_recession_end()


# In[10]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    df = get_gdp_figures()
    quarters = df['Quarters'].astype('category', categories=df['Quarters'], ordered=True)
    df = df['2008q3' <= quarters]
    df = df[quarters <= '2009q4']
    return df.loc[df['GDP in billions of chained 2009 dollars'].idxmin()]['Quarters']
get_recession_bottom()


# In[11]:

import math
def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    df = pd.read_csv('City_Zhvi_AllHomes.csv')
    df = df.set_index(['State', 'RegionName'])
    df = df[df.filter(regex='^2').columns]
    columns = df.columns
    
    df = df.T
    df = df.reset_index()
    df = df.groupby(df.index // 3).mean().T
    
    def to_quarters(month):
        return "{year}q{quarter}".format(year=month[:4],quarter=int(month[-2:]) // 4 + 1)
    df.columns = np.unique(columns.map(to_quarters))
    
    df = df.reset_index()
    
    df['State'] = df['State'].apply(lambda x: states[x])
    return df.set_index(['State', 'RegionName'])

convert_housing_data_to_quarters()


# In[14]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    recession_start = get_recession_start()
    recession_bottom = get_recession_bottom()
    
    gdp_df = get_gdp_figures()
    
    hd_df = convert_housing_data_to_quarters()
    hd_df = hd_df.reset_index()
    hd_df = hd_df.T
    states = hd_df.loc['State']
    region_names = hd_df.loc['RegionName']
    hd_df = hd_df[2:]
    hd_df.index = pd.CategoricalIndex(hd_df.index, ordered=True)
    hd_df = hd_df[recession_start: recession_bottom].T
    hd_df.columns = hd_df.columns.astype(np.str)
    hd_df['State'] = states
    hd_df['RegionName'] = region_names
    hd_df = hd_df.set_index(['State', 'RegionName'])
    
    unit_df = get_list_of_university_towns().set_index(['State', 'RegionName'])
    
    uni_town_hp = unit_df.join(hd_df, how='left')
    non_uni_town_hp = hd_df[hd_df.index.map(lambda x: x not in unit_df.index)]
    
    uni_town_hp_med = uni_town_hp.mean()
    non_uni_town_hp_med = non_uni_town_hp.mean()
    
    t_val = ttest_ind(uni_town_hp_med, non_uni_town_hp_med)
    return (t_val.pvalue < 0.01, t_val.pvalue, "university town" if uni_town_hp_med.mean() < non_uni_town_hp_med.mean() else "non-university town")
run_ttest()


# In[ ]:



