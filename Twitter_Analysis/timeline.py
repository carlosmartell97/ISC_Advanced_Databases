"""
Creates a simple Gantt chart
Adapted from http://www.clowersresearch.com/main/gantt-charts-in-matplotlib/
"""

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates
import Global
from matplotlib.dates import MONTHLY, DateFormatter, rrulewrapper, RRuleLocator

from pylab import *

def create_date(month, year):
    """Creates the date"""

    date = dt.datetime(int(year), int(month), 1)
    mdate = matplotlib.dates.date2num(date)

    return mdate

# Data

def create():
    pos = arange(0.5,2.5,0.5)
    print "pos:\n  "+str(pos)

    ylabels = []
    # ylabels.append('Hardware Design & Review')
    # ylabels.append('Hardware Construction')
    # ylabels.append('Integrate and Test Laser Source')
    # ylabels.append('Objective #1')
    # ylabels.append('Objective #2')
    # ylabels.append('Present at ASMS')
    ylabels.append('')
    ylabels.append('Activity')

    effort = []
    # effort.append([0.2, 1.0])
    # effort.append([0.2, 1.0])
    # effort.append([0.2, 1.0])
    # effort.append([0.3, 0.75])
    # effort.append([0.25, 0.75])
    # effort.append([0.3, 0.75])
    effort.append([0.5, 0.9])
    effort.append([0.7, 0.4])

    customDates = []
    print "first_tweet_month: "+str(Global.first_tweet_month)
    print "first_tweet_year: "+str(Global.first_tweet_year)
    first_tweet_month_end = (Global.first_tweet_month+2)%13 if (Global.first_tweet_month != 12 and Global.first_tweet_month != 11) else 2
    first_tweet_year_end = Global.first_tweet_year if first_tweet_month_end != 2 else Global.first_tweet_year+1
    print "first_tweet_month_end: "+str(first_tweet_month_end)
    print "first_tweet_year_end: "+str(first_tweet_year_end)
    customDates.append([create_date(Global.first_tweet_month, Global.first_tweet_year), create_date(first_tweet_month_end, first_tweet_year_end)])
    # customDates.append([create_date(6,2014),create_date(8,2014),create_date(8,2014)])
    # customDates.append([create_date(7,2014),create_date(9,2014),create_date(9,2014)])
    # customDates.append([create_date(10,2014),create_date(3,2015),create_date(3,2015)])
    # customDates.append([create_date(2,2015),create_date(6,2015),create_date(6,2015)])
    # customDates.append([create_date(5,2015),create_date(6,2015),create_date(6,2015)])
    print "created_at_month: "+str(Global.created_at_month)
    print "created_at_year: "+str(Global.created_at_year)
    created_at_month_end = (Global.created_at_month+2)%13 if (Global.created_at_month != 12 and Global.created_at_month != 11) else 2
    created_at_year_end = Global.created_at_year if created_at_month_end != 2 else Global.created_at_year+1
    print "created_at_month_end: "+str(created_at_month_end)
    print "created_at_year_end: "+str(created_at_year_end)
    #
    print "cien_tweet_month: "+str(Global.cien_tweet_month)
    print "cien_tweet_year: "+str(Global.cien_tweet_year)
    cien_tweet_month_end = (Global.cien_tweet_month+2)%13 if (Global.cien_tweet_month != 12 and Global.cien_tweet_month != 11) else 2
    cien_tweet_year_end = Global.cien_tweet_year if cien_tweet_month_end != 2 else Global.cien_tweet_year+1
    print "cien_tweet_month_end: "+str(cien_tweet_month_end)
    print "cien_tweet_year_end: "+str(cien_tweet_year_end)
    if(Global.cien_tweet_year != 0):
        customDates.append([create_date(Global.created_at_month, Global.created_at_year), create_date(created_at_month_end, created_at_year_end), create_date(created_at_month_end, created_at_year_end),
                            create_date(Global.first_tweet_month, Global.first_tweet_year), create_date(first_tweet_month_end, first_tweet_year_end), create_date(first_tweet_month_end, first_tweet_year_end),
                            create_date(Global.cien_tweet_month, Global.cien_tweet_year), create_date(cien_tweet_month_end, cien_tweet_year_end), create_date(cien_tweet_month_end, cien_tweet_year_end)
                            ])
    else:
        customDates.append([create_date(Global.created_at_month, Global.created_at_year), create_date(created_at_month_end, created_at_year_end), create_date(created_at_month_end, created_at_year_end),
                            create_date(Global.first_tweet_month, Global.first_tweet_year), create_date(first_tweet_month_end, first_tweet_year_end), create_date(first_tweet_month_end, first_tweet_year_end)
                            ])
    # customDates.append([create_date(4,2015),create_date(8,2015),create_date(8,2015)])

    task_dates = {}
    for i, task in enumerate(ylabels):
        print "i: "+str(i)
        print "  task: "+task
        print "  customDates[i]: "+str(customDates[i])
        task_dates[task] = customDates[i]
    # task_dates['Climatology'] = [create_date(5,2014),create_date(6,2014),create_date(10,2013)]
    # task_dates['Structure'] = [create_date(10,2013),create_date(3,2014),create_date(5,2014)]
    # task_dates['Impacts'] = [create_date(5,2014),create_date(12,2014),create_date(2,2015)]
    # task_dates['Thesis'] = [create_date(2,2015),create_date(5,2015)]

    # Initialise plot

    fig = plt.figure()
    # ax = fig.add_axes([0.15,0.2,0.75,0.3]) #[left,bottom,width,height]
    ax = fig.add_subplot(111)

    # Plot the data

    # start_date,end_date = task_dates[ylabels[0]]
    # ax.barh(0.5, end_date - start_date, left=start_date, height=0.3, align='center', color='blue', alpha = 0.75)
    # ax.barh(0.45, (end_date - start_date)*effort[0][0], left=start_date, height=0.1, align='center', color='blue', alpha = 0.75, label = "account created")
    # ax.barh(0.45, (end_date - start_date)*effort[0][0], left=start_date, height=0.1, align='center', color='green', alpha = 0.75, label = "time taken for 1st tweet: "+str(Global.time_taken_1st_tweet))
    # ax.barh(0.55, (end_date - start_date)*effort[0][1], left=start_date, height=0.1, align='center', color='red', alpha = 0.75, label = "after that, time taken for 100 tweets: "+str(Global.time_taken_100_tweets))
    for i in range(0,len(ylabels)-1):
        labels = ['Analysis','Reporting'] if i == 1 else [None,None]
        print "i date: "+str(i)
        piEffort, studentEffort = effort[i+1]

        print "NOW....."
        print "task_dates: "+str(task_dates)
        if(Global.cien_tweet_year != 0):
            start_date,mid_date,end_date, start_date_new,mid_date_new,end_date_new, cien_start,cien_mid,cien_end = task_dates[ylabels[i+1]]
        else:
            start_date,mid_date,end_date, start_date_new,mid_date_new,end_date_new = task_dates[ylabels[i+1]]
        ax.barh((i*0.5)+1.0+0.3, mid_date - start_date, left=start_date, height=0.3, align='center', color='blue', alpha = 0.75, label = "account created")
        # ax.barh((i*0.5)+1.0-0.05, (mid_date - start_date)*piEffort, left=start_date, height=0.1, align='center', color='yellow', alpha = 0.75)
        # ax.barh((i*0.5)+1.0+0.05, (mid_date - start_date)*studentEffort, left=start_date, height=0.1, align='center', color='orange', alpha = 0.75)
        # ax.barh((i*0.5)+1.0, end_date - mid_date, left=mid_date, height=0.3, align='center',label=labels[1], color='yellow')

        ax.barh((i*0.5)+1.0, mid_date_new - start_date_new, left=start_date_new, height=0.3, align='center', color='green', alpha = 0.75, label = "time taken for 1st tweet: "+str(Global.time_taken_1st_tweet))
        # ax.barh((i*0.5)+1.0-0.05, (mid_date_new - start_date_new)*piEffort, left=start_date_new, height=0.1, align='center', color='red', alpha = 0.75)
        # ax.barh((i*0.5)+1.0+0.05, (mid_date_new - start_date_new)*studentEffort, left=start_date_new, height=0.1, align='center', color='yellow', alpha = 0.75)

        if(Global.cien_tweet_year != 0):
            ax.barh((i*0.5)+1.0-0.3, cien_mid - cien_start, left=cien_start, height=0.3, align='center', color='red', alpha = 0.75, label = "after that, time taken for 100 tweets: "+str(Global.time_taken_100_tweets))
            # ax.barh((i*0.5)+1.0-0.05, (cien_mid - cien_start)*piEffort, left=cien_start, height=0.1, align='center', color='red', alpha = 0.75)
            # ax.barh((i*0.5)+1.0+0.05, (cien_mid - cien_start)*studentEffort, left=cien_start, height=0.1, align='center', color='orange', alpha = 0.75)
    # Format the y-axis

    locsy, labelsy = yticks(pos,ylabels)
    plt.setp(labelsy, fontsize = 12)

    # Format the x-axis

    ax.axis('tight')
    ax.set_ylim(ymin = -0.1, ymax = 1.5)
    ax.grid(color = 'g', linestyle = ':')

    ax.xaxis_date() #Tell matplotlib that these are dates...

    created_at_date = dt.datetime(Global.created_at_year, Global.created_at_month, 1)
    first_tweet_date = dt.datetime(Global.first_tweet_year, Global.first_tweet_month, 1)
    if(Global.cien_tweet_year != 0):
        final_tweet_date = dt.datetime(Global.cien_tweet_year, Global.cien_tweet_month, 1)
    else:
        final_tweet_date = dt.datetime(Global.first_tweet_year, Global.first_tweet_month, 1)
    date_delta = final_tweet_date - created_at_date
    # max_timespan = dt.datetime(2, 1, 1)  # 2 years
    print "created date: "+str(created_at_date)
    print "first tweet date: "+str(first_tweet_date)
    print "final tweet date: "+str(final_tweet_date)
    print "difference: "+str(date_delta.days)
    if(date_delta.days > (365 * 11)-1):  # 11 years
        rule = rrulewrapper(MONTHLY, interval=15)
    elif(date_delta.days > (365 * 8)-1):  # 8 years
        rule = rrulewrapper(MONTHLY, interval=9)
    elif(date_delta.days > (365 * 4)-1):  # 4 years
        rule = rrulewrapper(MONTHLY, interval=6)
    elif(date_delta.days > (365 +(365/2))-1):  # 1 and 1/2 years
        rule = rrulewrapper(MONTHLY, interval=3)
    else:
        rule = rrulewrapper(MONTHLY, interval=1)
    loc = RRuleLocator(rule)
    formatter = DateFormatter("%b '%y")

    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    labelsx = ax.get_xticklabels()
    plt.setp(labelsx, rotation=30, fontsize=12)

    # Format the legend

    font = font_manager.FontProperties(size='small')
    ax.legend(loc=1,prop=font)

    # Finish up
    ax.invert_yaxis()
    fig.autofmt_xdate()
    plt.savefig('png/'+Global.screen_name+'_gantt.png')

if __name__ == '__main__':
    create()
    plt.show()
