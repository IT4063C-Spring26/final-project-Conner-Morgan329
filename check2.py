#!/usr/bin/env python
# coding: utf-8

# Loading Data, Cleaning, and Basic Visualizations

# In[5]:


#Import Modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# <h1>HRSA Mental Health Dataset Availability</h1>

# In[14]:


hrsa_df = pd.read_csv("BCD_HPSA_FCT_DET_MH.csv")

hrsa_df.head()


# In[ ]:


# remove empty columns
hrsa_df = hrsa_df.loc[:, ~hrsa_df.columns.str.contains('^Unnamed')]

# filter for Ohio
hrsa_ohio = hrsa_df[hrsa_df['state'] == 'OH'].copy()

# check data
hrsa_ohio.head()


# In[32]:


hrsa_county_ohio = hrsa_ohio.groupby(['fips', 'county', 'state']).agg({
    'hpsa_score': 'mean',
    'population_in_shortage': 'sum',
    'provider_shortage': 'sum'
}).reset_index()

hrsa_county_ohio.head(10)


# First Visualization:
# This bar chart shows the top 10 counties in Ohio with the highest mental health provider shortages. The visualization highlights significant variation in access to mental health services across counties. Some counties experience substantially higher shortages, indicating potential gaps in service availability and unequal distribution of mental health resources.

# In[33]:


# Sort and take top 10 counties
top_shortage = hrsa_county_ohio.sort_values(
    by='provider_shortage', ascending=False
).head(10)

# Create bar chart
plt.figure(figsize=(10,6))
plt.bar(top_shortage['county'], top_shortage['provider_shortage'])

plt.title('Top 10 Ohio Counties by Mental Health Provider Shortage')
plt.xlabel('County')
plt.ylabel('Provider Shortage')

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# <h1>CDC</h1>

# In[ ]:


#read data 
places_df = pd.read_csv("PLACES__County_Data_(GIS_Friendly_Format),_2025_release_20260419.csv")


# In[35]:


#filter to ohio
places_ohio = places_df[places_df['StateAbbr'] == 'OH'].copy()


# In[ ]:


#Cleaing the columns I need for the analysis
places_clean = places_ohio[[
    'CountyFIPS',
    'CountyName',
    'StateAbbr',
    'MHLTH_CrudePrev'
]].copy()

#Rename to match previous data set
places_clean = places_clean.rename(columns={
    'CountyFIPS': 'fips',
    'CountyName': 'county',
    'StateAbbr': 'state',
    'MHLTH_CrudePrev': 'mental_health_rate'
})

#make mips match previous data set for merging  
places_clean['fips'] = places_clean['fips'].astype(str).str.zfill(5)

places_clean.head()


# In[42]:


#merge data sets
merged_df = hrsa_county_ohio.merge(
    places_clean,
    on='fips',
    how='inner'
)

merged_df.head()


# In[43]:


plt.figure(figsize=(8,6))

plt.scatter(
    merged_df['mental_health_rate'],
    merged_df['provider_shortage']
)

plt.xlabel('Mental Health Rate (%)')
plt.ylabel('Provider Shortage')
plt.title('Mental Health Need vs Provider Shortage (Ohio)')

plt.show()


# Visual 2: 
# This scatter plot shows the relationship between mental health need and provider shortage across Ohio counties. The data does not show a strong relationship, as counties with similar mental health rates often have very different levels of provider shortage. This suggests that access to mental health services is not evenly distributed. Some counties experience both high mental health need and high provider shortages, indicating potential gaps in care.

# <h1>ACS</h1>

# In[ ]:


# Pull ACS 5-year data for Ohio counties using the Census API
url = (
    "https://api.census.gov/data/2024/acs/acs5"
    "?get=NAME,B01003_001E"
    "&for=county:*"
    "&in=state:39"
)
#The state 39 = Ohio
#Name B01003_001E = Total Population

acs_df = pd.read_json(url)

acs_df.columns = acs_df.iloc[0]
acs_df = acs_df[1:].copy()

acs_df = acs_df.rename(columns={
    "NAME": "county_name",
    "B01003_001E": "population",
    "state": "state_fips",
    "county": "county_fips"
})

acs_df["population"] = pd.to_numeric(acs_df["population"])
acs_df["fips"] = acs_df["state_fips"] + acs_df["county_fips"]

acs_df.head()

