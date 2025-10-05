import math, json, os

BASE_XP = {
  "estudiar": 1.0,
  "lectura": 0.25,
  "entrenar": 1.0,
  "andar": 0.25,
  "meditar": 1.0,
  "organizar": 1.0
}

PENALTY_XP = 100
RECOVERY_DAYS = 10
MAX_EXTRA_BUFF = 2.0  # 200%

def buff_time(m):
    return 0.30 * (1 - math.exp(-m/80))

def buff_day(streak_days):
    return min(0.10 * streak_days, 2.0)

BUFF_FOOD = 0.02
BUFF_SLEEP = 0.02

def compute_day_xp(area_state, minutes_by_task, streak_days, days_missed, food_ok, sleep_ok, penalty_applied):
    total_area_xp = 0
    for task, mins in minutes_by_task.items():
        base_rate = BASE_XP.get(task, 0.0)
        bt = buff_time(mins)
        bd = buff_day(streak_days)
        extra = bt + bd + (BUFF_FOOD if food_ok else 0) + (BUFF_SLEEP if sleep_ok else 0)
        extra = min(extra, MAX_EXTRA_BUFF)
        debuff = min(0.10 * days_missed, 1.0)
        multiplier = max(0.0, 1.0 + extra - debuff)
        xp = int(round(base_rate * mins * multiplier))
        total_area_xp += xp
    return total_area_xp

def process_day(state, day_payload):
    date = day_payload['date']
    sessions = day_payload['sessions']
    food_ok = day_payload.get('food_ok', False)
    sleep_ok = day_payload.get('sleep_ok', False)

    minutes_by_area_task = {}
    for s in sessions:
        key = (s['area'], s['task'])
        minutes_by_area_task.setdefault(key, 0)
        minutes_by_area_task[key] += s['minutes']

    per_area = {}
    for (area, task), mins in minutes_by_area_task.items():
        per_area.setdefault(area, {})[task] = mins

    for area, tasks in per_area.items():
        area_state = state['areas'].setdefault(area, {"xp": 0, "streak": 0, "days_missed": 0, "recovery_streak": 0, "penalty_applied": False})
        streak_days = area_state['streak']
        days_missed = area_state['days_missed']
        penalty_applied = area_state['penalty_applied']

        xp_gained = compute_day_xp(area_state, tasks, streak_days, days_missed, food_ok, sleep_ok, penalty_applied)

        if area_state['days_missed'] >= 10 and not penalty_applied:
            area_state['xp'] = max(0, area_state['xp'] - PENALTY_XP)
            area_state['penalty_applied'] = True
            penalty_applied = True

        if sum(tasks.values()) > 0:
            area_state['xp'] += xp_gained
            area_state['days_missed'] = 0
            area_state['recovery_streak'] = min(area_state['recovery_streak'] + 1, RECOVERY_DAYS)
            area_state['streak'] += 1
            if area_state['recovery_streak'] >= RECOVERY_DAYS:
                area_state['penalty_applied'] = False
                area_state['recovery_streak'] = 0
        else:
            area_state['days_missed'] += 1
            area_state['streak'] = 0
            area_state['recovery_streak'] = 0

    return state
