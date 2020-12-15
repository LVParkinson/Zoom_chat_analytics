#!/usr/bin/python3

"""
Script to convert raw text file from Zoom chat into usable dataframe
Exports csv with three columns: time, author, and comment
Runs a few functions for basic analysis

Author: Lindsey Viann Parkinson
Last Updated: December 15, 2020

"""
# Import modules and packages
import fire
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import networkx as nx





def convert_to_csv(filepath, csv_name):
    file = open(filepath, mode='r',encoding="utf8")

    time = []
    author =[]
    comment =[]

    regex_time = r'\d{2}:\d{2}:\d{2}'
    regex_author = r'\bFrom \s(.*?:)' #this could be improved to avoid the space and colon at the end
    regex_comment = r'(?:\: )(.*$)'

    for line in file:
    # Empty lines will be ignored
        if line.strip(): 
        #seperate line to get a view of comments
            #print(line)
        # use .extend() instead of .append() to avoid making a list of single-item lists
            time.extend(re.findall(regex_time, line))
            author.extend(re.findall(regex_author, line))
            comment.extend(re.findall(regex_comment, line))
        print(line)
    
    s1=pd.Series(time,name='time')
    s2=pd.Series(author,name='author')
    s3=pd.Series(comment ,name='comment')
    
    df = pd.concat([s1,s2,s3], axis=1)
    
    df['author'] = df['author'].str[:-2]
    df = df[~df['author'].str.contains("Privately")].reset_index(drop=True)
    
    df.to_csv(csv_name, index = False) 
    
    print(df)
    print("check source folder for csv")
    
    
    
def find_urls(pathtocsv):
    """
    Extract urls from comments. 
    Only works with full urls containing "http"
    """
    df = pd.read_csv(pathtocsv)
    
    links=[]
    for comment in df['comment']:
        links.extend(re.findall(r'(https?://[^\s]+)', comment))
    return links
    

def comments_by_author(pathtocsv):
    """
    Count the number of comments made by each author
    """
    df = pd.read_csv(pathtocsv)
    return df.groupby(df['author'])['author'].count().sort_values(ascending=False)



def comments_over_time(pathtocsv):
    """
    Count the number of comments over time. Return histogram.
    tinterval: Optional. the time interval, in minutes, to count comments
    yticks: Optional. Y-axis tick mark interval
    """
    tinterval = 10 
    yticks = 2
    
    df = pd.read_csv(pathtocsv)
    
    #convert string to time
    df['time'] = pd.to_datetime(df['time'],format= '%H:%M:%S' ).dt.time

    # get a list of the times
    times = [t.hour + t.minute/60. for t in df['time']]

    # set the time interval required (in minutes)
    tinterval = tinterval

    # find the lower and upper bin edges (on an integer number of 10 mins past the hour)
    lowbin = np.min(times) - np.fmod(np.min(times)-np.floor(np.min(times)), tinterval/60.)
    highbin = np.max(times) - np.fmod(np.max(times)-np.ceil(np.max(times)), tinterval/60.)
    bins = np.arange(lowbin, highbin, tinterval/60.)  # set the bin edges
    
    
    # create the histogram
    plt.hist(times, bins=bins)
    ax = plt.gca()  # get the current plot axes
    ax.set_xticks(bins)  # set the position of the ticks to the histogram bin edges

    # create new labels in hh:mm format (in twelve hour clock)
    newlabels = []
    for edge in bins:
        h, m = divmod(edge%12, 1)  # get hours and minutes (in 12 hour clock)
        newlabels.append('{0:01d}:{1:02d}'.format(int(h), int(m*60)))  # create the new label

    ax.set_xticklabels(newlabels, rotation = 60)  # set the new labels
    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(start, end, yticks))
    ax.set_ylabel("Number of messages")
    ax.set_title("number of messages in 10-min intervals")
    plt.savefig("Zoom_histogram.png")
    
    print("check working directory for Zoom_histogram.png")

    
    
def comment_network(pathtocsv):
    """
    Create a network graph of who responds to comments
    Lines are drawn between the author of a comment and the next person to comment
    
    """
    df = pd.read_csv(pathtocsv)
    
    dfchatters = df[['author']]
    dfchatters['responder'] = df['author'].shift(periods=-1)
    dfchatters = dfchatters.dropna()
    
    G = nx.DiGraph()

    G = nx.from_pandas_edgelist(dfchatters, 'author', 'responder')
    
    figure(figsize=(23, 15))
    nx.draw_shell(G, with_labels=True,font_weight='bold')

    plt.savefig("Zoom_network.png", bbox_inches="tight")
    
    print("check working directory for Zoom_network.png")

    
    
if __name__ == '__main__':
  fire.Fire({
      'convert_to_csv': convert_to_csv,
      'find_urls': find_urls,
      'comments_by_author': comments_by_author,
      'comments_over_time': comments_over_time,
      'comment_network': comment_network
  })
