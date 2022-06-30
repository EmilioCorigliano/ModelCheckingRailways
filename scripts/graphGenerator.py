import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Global parameters
strategy = 1
trains = 4
file = f"dataModels{trains}"


def color(status):
    if status == -1:  # timeout
        return ["Timeout", "grey"]
    elif status == 0:  # failed both
        return ["Failed both", "#FF0000"]
    elif status == 1:  # passed enoughSOC
        return ["Passed only enoughSOC", "orange"]
    elif status == 2:  # passed trainsInTime
        return ["Passed only trainsInTime", "#00FFFF"]
    elif status == 3:  # passed both
        return ["Passed both", "#00FF00"]
    else:
        print("Something's wrong with status {}".format(status))
        return ["Invalid", "#000000"]


fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

ax.set_title(f"Strategy {strategy} with {trains} trains")
ax.set_xlabel("Rate of discharge")
ax.set_ylabel("Speed of the trains")
ax.set_zlabel("Rate of charge")

# generating legend
legend_elements = []
labels = []
for i in range(5):
    label, c = color(i - 1)
    legend_elements.append(Line2D([0], [0], color=c, marker='o', label=label))
    labels.append(label)

with open(file + ".csv", "r") as csv:
    line = csv.readline()

    for line in csv.readlines():
        [strat, minTimeInStation, Crec, Cdis, V, status] = line.split(',')

        size = (int(V) - 60) / 10

        if int(strat) == strategy:
            # if int(V) in [120, 180, 240]:
            label, c = color(int(status))
            ax.scatter(int(Cdis), int(V), int(Crec), c=c)  # , s=size)  # plot the point (2,3,4) on the figure

ax.view_init(elev=3, azim=10)
ax.set_proj_type('ortho')
ax.invert_xaxis()
fig.tight_layout()
ax.legend(handles=legend_elements, labels=labels)
plt.show()
