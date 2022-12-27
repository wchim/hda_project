import streamlit as st
import numpy as np
import pandas as pd
import time

def convert_weight(unit, body_wt):
    if unit == 'Pounds':
        wt_lb = round(body_wt, 2)
        wt_kg = round(body_wt/2.2, 2)
    elif unit == 'Kilograms':
        wt_lb = round(body_wt*2.2, 2)
        wt_kg = round(body_wt, 2)
    return wt_lb, wt_kg

def find_n_day_trend(n, body_wts):
    n_day_trend = body_wts.rolling(n).apply(lambda x: np.polyfit(range(n), x, 1)[0], raw=True).values[-1]
    n_day_trend = round(n_day_trend, 3)
    return n_day_trend

'''
Backend functions for fitness portion of the app
'''
'''Round down to multiple of 5'''
def round_to_five(wt):
    return int(5 * (np.floor(wt/5)))

'''Input total weight and output amount of each type of plate to load onto bar'''
def generate_plates(wt):
    output_str = ''
    rnd_wt = round_to_five(wt)
    wo_bar = rnd_wt - 45
    side_wt = wo_bar/2
    #print(f'Actual Weight (lbs): {wt}\nRounded Weight (lbs): {rnd_wt}\nWithout Bar (lbs): {wo_bar}\nWeight per Side(lbs): {side_wt}')
    output_str += f'Weight per Side(lbs): {side_wt}\n'
    gym_wts = [45,35,25,10,5,2.5]
    for g in gym_wts:
        plate_ct = int(np.floor(side_wt/g))
        if side_wt%g == side_wt:
            pass
        elif side_wt%g > 0:
            output_str += f'{plate_ct} {g} pound weights\n'
            side_wt = side_wt%g
            #print(side_wt)|
        elif side_wt%g == 0:
            output_str += f'{plate_ct} {g} pound weights'
            break
    #print(output_str)
    return output_str

'''Calculate one rep max using Brzycki formula based on weight and rep'''
def find_orm(wt, reps):
    to_kg = wt/2.2
    if reps >= 1:
        return to_kg * (36/(37-reps)) * 2.2
    else:
        return 0

def reverse_orm(orm, reps):
    orm_kg = orm/2.2
    return (orm_kg*(37-reps))/36 * 2.2

'''Generate a breakdown table of general sets based on a PERFORMED SET'''
def get_breakdown(wt_input, reps):
    orm = find_orm(wt_input, reps)
    rnd_orm = round_to_five(orm)
    print(f'Set Weight (lbs): {wt_input}\nSet Reps: {reps}\nORM (lbs): {orm}\nRounded ORM (lbs): {rnd_orm}')

    perc = ['95%','90%','85%','80%','75%','70%','65%','60%','55%','50%']
    set_reps = [3,5,7,9,10,12,14,16,18,20]
    set_wts = [round(reverse_orm(orm, r),2) for r in set_reps]
    rnd_set_wts = [round_to_five(r) for r in set_wts]

    wt_breakdown = pd.DataFrame({'Approximate Percentage': perc,
                                 'Actual Weight (lbs)': set_wts,
                                 'Rounded Weight (lbs)': rnd_set_wts,
                                 'Reps': set_reps})
    #print(tabulate(wt_breakdown,headers='keys',showindex=False,tablefmt='heavy_outline'))
    st.dataframe(wt_breakdown)

'''Generate monthly workout plan referencing 5/3/1 powerlifting program based on ONE WEIGHT'''
def generate_exercise(orm):
    
    plan = {
        'Week One':{
        'set_multiplier': [0.65,0.75,0.85],
        'reps': ['5','5','5+']},
        'Week Two':{
        'set_multiplier': [0.7,0.8,0.9],
        'reps': ['3','3','3+']},
        'Week Three':{
        'set_multiplier': [0.75,0.85,0.95],
        'reps': ['5','3','1+']},
        'Week Four':{
        'set_multiplier': [0.4,0.5,0.6],
        'reps': ['5','5','5']}
    }
    base_wt = orm*0.9
    week_dct = {}
    for week in plan:
        idx = 0
        wkout_ls = []
        set_ls = []
        while idx < 3:

            set_multiplier = plan[week]['set_multiplier'][idx]
            reps = plan[week]['reps'][idx]

            set_wt = set_multiplier*base_wt
            rnd_wt = round_to_five(set_wt)
            set_num = idx + 1

            plates = generate_plates(set_wt)
            wkout_ls.append(f'{rnd_wt} lbs for {reps} reps\n{plates}')
            set_ls.append(f'Set {set_num}')

            idx += 1
        week_dct[week] = wkout_ls

        df = pd.DataFrame(data=week_dct,
                          index=set_ls)
    #print(tabulate(df,headers='keys',tablefmt='fancy_grid'))
    return df

'''Generate monthly workout plan referencing 5/3/1 powerlifting program based on USER PROFILE'''
def generate_plan():
    
    profiles = {
        'Wayne Chim': {'Bench Press': 200,
                       'Squat': 295,
                       'Deadlift': 335,
                       'Shoulder Press':125},
        'Sideman Wu': {'Bench Press': 195,
                       'Squat': 275,
                       'Deadlift': 315,
                       'Shoulder Press': 135}
    }
    
    for user in profiles:
        name = user.lower()
        name = name.replace(' ','_')
        filename = f'{name}_workout.txt'
        with open(filename,'w',encoding='utf-8') as f:
            for exercise in profiles[user]:
                #print(exercise)
                #generate_plan(profiles[user][exercise])
                entry = generate_exercise(profiles[user][exercise])
                f.write(exercise+'\n')
                f.write(tabulate(entry,headers='keys',tablefmt='fancy_grid'))
                f.write('\n')
            print(f'Workout generated for {user}!')