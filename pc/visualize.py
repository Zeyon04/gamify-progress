import json
import matplotlib.pyplot as plt

DATA_PATH = "../data/data.json"

def level_from_xp(xp):
    lvl, threshold = 1, 50
    while xp >= threshold:
        xp -= threshold
        threshold = int(threshold * 1.05)
        lvl += 1
    return lvl, xp, threshold

with open(DATA_PATH, "r") as f:
    data = json.load(f)

areas = data["areas"]
names, levels, xps = [], [], []

for area, info in areas.items():
    lvl, rem, nxt = level_from_xp(info.get("xp", 0))
    names.append(area)
    levels.append(lvl)
    xps.append(info.get("xp", 0))

plt.bar(names, xps)
for i, lvl in enumerate(levels):
    plt.text(i, xps[i] + 10, f"Lvl {lvl}", ha="center")
plt.title("Progreso por área")
plt.ylabel("XP total")
plt.show()
