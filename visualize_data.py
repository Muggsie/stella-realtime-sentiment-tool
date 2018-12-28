from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# init the interface to our db
connect = MongoClient('localhost', 27017)
db = connect.stella.sentiment
data = pd.DataFrame(list(db.find())) # getting our entire mongodb into a dataframe

# other commands
# data = pd.DataFrame(list(db.find().limit( 100 ))) # getting only the earliest N records
# db.remove({ 'volume':0 }) # removing records

# storing data temporarily in pandas dataframes
time = data['time']
volume = data['volume']
very_positive = data['very_positve']
positive =  data['positive']
neutral =  data['neutral']
negative =  data['negative']
very_negative = data['very_negative']
sentiment =  data['sentiment']
 
# There are 4 types of baseline we can use:
baseline = ["sym"]
 
# Let's make 4 plots, 1 for each baseline
for n, v in enumerate(baseline):
    if n<3 :
        plt.tick_params(labelbottom=False)
    plt.stackplot(time, very_negative, negative, neutral, positive, very_positive, baseline=v)

    #plt.stackplot(x, yB, color = 'grey', baseline=v)
    plt.title(v)
    plt.legend(['+neg','neg','neut','pos','+pos'], loc='upper left')
    plt.plot(time, neutral, color = 'orange')
    plt.axis('tight', size=0.2)

#plt.plot(x, yA)
#plt.plot(x, yB, color='grey', marker='x')
#plt.plot(x, yC, color='green', marker='x')
#plt.plot(x, yD, color='red', marker='x')
#plt.plot(x, yE, color='orange')
    plt.show()


