import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def noCluster():
    # creating the dataset
    data = {'remedy':2, 'npaths':2, 'rsta':27}
    algorithms = list(data.keys())
    values = list(data.values())

    fig = plt.figure(figsize = (10, 5))

    # creating the bar plot
    plt.bar(algorithms, values, color ='maroon', width = 0.4)

    plt.xlabel("Algorithms")
    plt.ylabel("Steps")
    plt.title("Steps for 3-regular, 6 nodes")
    plt.show()

def cluster():  
    # create data
    x = np.arange(3)
    remedy = [120, 156, 254]
    npaths = [114, 148, 198]
    rsta =   [194, 295, 462]
    da     = [72, 88, 104]
    width = 0.2

    # plot data in grouped manner of bar type
    plt.bar(x-0.2, remedy, width, color='cyan')
    plt.bar(x, npaths, width, color='orange')
    plt.bar(x+0.2, rsta, width, color='green')
    plt.bar(x+0.4, da, width, color='red')

    plt.xticks(x, ['remedy', 'npaths', 'rsta', 'da'])
    plt.xlabel("Algorithms")
    plt.ylabel("Steps")
    plt.legend(["Validation 5", "Validation 6", "Validation 7"])
    plt.show()



def clusterPandas():
    # create data
    df = pd.DataFrame([['remedy',  1, 1, 1, 1, 1, 2], 
                       ['npaths',  1, 1, 1, 1, 1, 2], 
                       ['rsta', 42, 43, 44, 44, 112, 44]],
                       columns=['Algorithms', '7 vertices', '8 vertices', '9 vertices', '10 vertices', '11 vertices', '12 vertices'])
    # view data
    print(df)

    # plot grouped bar chart
    result = df.plot(x='Algorithms',
            kind='bar',
            stacked=False,
            title='6-Regular, Increasing Vertex Count - Edge (0,4) Failure')
    result.set_ylabel("Steps")
    result.set_xlabel("Algorithms")

    #ax = df.plot.bar()
    #for container in ax.containers:
    #    ax.bar_label(container)

    plt.show()

def clusterPandass():
    # create data
    df = pd.DataFrame([['remedy', 20, 5], 
                       ['npaths', 31, 5], 
                       ['rsta', 134, 103]],
                       columns=['Algorithms', '(0,1) failure', '(0,2) failure',])
    # view data
    print(df)

    # plot grouped bar chart
    result = df.plot(x='Algorithms',
            kind='bar',
            stacked=False,
            title='17 Node Topology - Edge Failures')
    result.set_ylabel("Steps")
    result.set_xlabel("Algorithms")

    plt.show()

# run
clusterPandass()