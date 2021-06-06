import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import sys

nodeServerUrl = "http://ec2-15-207-240-66.ap-south-1.compute.amazonaws.com/api/safety/getAllRecords"

# define a function to take in recipe title and return the top recommended recipes
def recommender(title, indices, df, cosine_sim, top_n):
    # initialize an empty list of recommended recipes
    top_recipes = []
    
    # get the index of the recipe that matches the title
    idx = indices[indices == title].index[0]

    # creating a Series with the similarity scores in descending order
    score_series = pd.Series(cosine_sim[idx]).sort_values(ascending=False)

    # getting the indexes of the n most similar recipes
    top_idx = score_series.iloc[1:top_n+1].index.tolist()
    
    # get the title of the top n matching recipes
    for i in top_idx:
        top_recipes.append(df.index[i])
   
    return top_recipes

# define a function to print recommended meals
def print_rec(df, i):
    recipe = df['recipe'][i]
    serving = df['serving'][i]    
    calorie = df['calorie'][i]
    link = df['link'][i]
    st.subheader(f'Day {i+1}: {recipe}')
    st.write(f'Your portion: {serving}')
    st.write(f'Calorie: {calorie}')
    st.write(link)

def print_rec_lunch(df, i):
    recipe_lunch = df['recipe_lunch'][i]
    serving_lunch = df['serving_lunch'][i]    
    calorie_lunch = df['calorie_lunch'][i]
    link_lunch = df['link_lunch'][i]
    st.subheader(f'Day {i+1}: {recipe_lunch}')
    st.write(f'Your portion: {serving_lunch}')
    st.write(f'Calorie: {calorie_lunch}')
    st.write(link_lunch)

def print_rec_dinner(df, i):
    recipe_dinner = df['recipe_dinner'][i]
    serving_dinner = df['serving_dinner'][i]    
    calorie_dinner = df['calorie_dinner'][i]
    link_dinner = df['link_dinner'][i]
    st.subheader(f'Day {i+1}: {recipe_dinner}')
    st.write(f'Your portion: {serving_dinner}')
    st.write(f'Calorie: {calorie_dinner}')
    st.write(link_dinner)

# def print_summary(df, i):
#     recipe = df['recipe'][i]
#     link = df['link'][i]
#     st.subheader(f'Day {i+1}: {recipe}')
#     st.write(link)
#     recipe_lunch = df['recipe_lunch'][i]
#     link_lunch = df['link_lunch'][i]
#     st.subheader(f'Day {i+1}: {recipe_lunch}')
#     st.write(link_lunch)
#     recipe_dinner = df['recipe_dinner'][i]
#     link_dinner = df['link_dinner'][i]
#     st.subheader(f'Day {i+1}: {recipe_dinner}')
#     st.write(link_dinner)
    
# define a function to plot macronutrient ratio
def plot_nutrient(df, i):
    labels = ['Carbohydrate', 'Protein', 'Fat']
    sizes = [df['carb ratio'][i], df['protein ratio'][i], df['fat ratio'][i]]
    colors = ['#45b69c', '#CFC0BD', '#433E3F']

    # plot
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
            startangle=90, counterclock=False, radius=0.5)
    plt.axis('square')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot();
    

    
# define a function to take in recommended recipe list and return optimized recipes
def optimizer(rec_recipes, df, protein_lower, calorie, time='off'):
    protein_lower = protein_lower # set protein min
    fat_limit = 0.40 # set fat_ratio limit
    calorie_limit = calorie # set calorie limit 

    # create a new rec dict
    new_rec = {'recipe': [], 'link': [], 'serving': [], 'calorie': [], 'protein': [], 
               'fat ratio': [], 'protein ratio': [], 'carb ratio': []}

    while len(rec_recipes) > 0:
        if len(new_rec['recipe']) == 7:
            # df = pd.DataFrame(new_rec, index=[['Day 1 B','Day 1 L','Day 1 D','Day 2 B','Day 2 L','Day 3 B','Day 3 L','Day 3 D','Day 4 B','Day 4 L','Day 4 D','Day 5 B','Day 5 L','Day 5 D']])
            df = pd.DataFrame(new_rec, index=[['Day 1','Day 2','Day 3', 'Day 4', 'Day 5','Day 6', 'Day 7']])
            
            st.title('Weekly BREAKFAST plan is ready.')
            for i in range(7):
                print_rec(df, i)
                plot_nutrient(df, i)
            return


        recipe = np.random.choice(rec_recipes)
        rec_recipes.remove(recipe) 
        
        # check time
        if time == 'on':
            if df.loc[recipe].cook_time > 30 or df.loc[recipe].cook_time == 0:
                continue
            
        # check fat
        if df.loc[recipe].fat_ratio > fat_limit:
            continue
            
        # check calorie
        if df.loc[recipe].calorie > calorie_limit:
            portion = np.round(calorie_limit/df.loc[recipe].calorie, 2) 
            protein = np.round(df.loc[recipe].protein_g * portion)
            
            # check protein
            if protein < protein_lower:
                continue
            calorie = np.round(df.loc[recipe].calorie * portion) 
            serving = np.round(portion/df.loc[recipe].servings, 1)
            fat_ratio = df.loc[recipe].fat_ratio
            protein_ratio = df.loc[recipe].protein_ratio            
            carb_ratio = df.loc[recipe].carb_ratio            
            link = df.loc[recipe].link            
            new_rec['recipe'].append(recipe)
            new_rec['link'].append(link)
            new_rec['serving'].append(serving)
            new_rec['calorie'].append(calorie)
            new_rec['protein'].append(protein)
            new_rec['fat ratio'].append(fat_ratio)
            new_rec['protein ratio'].append(protein_ratio)
            new_rec['carb ratio'].append(carb_ratio)
            
        else:
            portion = np.round(calorie_limit/df.loc[recipe].calorie, 2) 
            protein = np.round(df.loc[recipe].protein_g * portion)
            
            # check protein
            if protein < protein_lower:
                continue
            calorie = np.round(df.loc[recipe].calorie * portion) 
            serving = np.round(portion/df.loc[recipe].servings, 1)
            fat_ratio = df.loc[recipe].fat_ratio
            protein_ratio = df.loc[recipe].protein_ratio            
            carb_ratio = df.loc[recipe].carb_ratio            
            link = df.loc[recipe].link
            new_rec['recipe'].append(recipe)
            new_rec['link'].append(link)
            new_rec['serving'].append(serving)
            new_rec['calorie'].append(calorie)
            new_rec['protein'].append(protein)
            new_rec['fat ratio'].append(fat_ratio)
            new_rec['protein ratio'].append(protein_ratio)
            new_rec['carb ratio'].append(carb_ratio)

    st.warning('Running out of recipes. Please start over and choose more preferred meals.')
    return

    # define a function to take in recommended recipe list and return optimized recipes
def optimizer_lunch(rec_recipes, df, protein_lower, calorie, time='off'):
    protein_lower = protein_lower # set protein min
    fat_limit = 0.40 # set fat_ratio limit
    calorie_limit = calorie # set calorie limit 

    # create a new rec dict
    new_rec_lunch = {'recipe_lunch': [], 'link_lunch': [], 'serving_lunch': [], 'calorie_lunch': [], 'protein': [], 
               'fat ratio': [], 'protein ratio': [], 'carb ratio': []}
     

    while len(rec_recipes) > 0:
        if len(new_rec_lunch['recipe_lunch']) == 7:
            # df = pd.DataFrame(new_rec, index=[['Day 1 B','Day 1 L','Day 1 D','Day 2 B','Day 2 L','Day 3 B','Day 3 L','Day 3 D','Day 4 B','Day 4 L','Day 4 D','Day 5 B','Day 5 L','Day 5 D']])
            df = pd.DataFrame(new_rec_lunch, index=[['Day 1','Day 2','Day 3', 'Day 4', 'Day 5','Day 6', 'Day 7']])
            
            st.title('Weekly LUNCH plan is ready.')
            for i in range(7):
                print_rec_lunch(df, i)
                plot_nutrient(df, i)
            return


        recipe_lunch = np.random.choice(rec_recipes)
        rec_recipes.remove(recipe_lunch) 
        
        # check time
        if time == 'on':
            if df.loc[recipe_lunch].cook_time > 30 or df.loc[recipe_lunch].cook_time == 0:
                continue
            
        # check fat
        if df.loc[recipe_lunch].fat_ratio > fat_limit:
            continue
            
        # check calorie
        if df.loc[recipe_lunch].calorie > calorie_limit:
            portion = np.round(calorie_limit/df.loc[recipe_lunch].calorie, 2) 
            protein = np.round(df.loc[recipe_lunch].protein_g * portion)
            
            # check protein
            if protein < protein_lower:
                continue
            calorie_lunch = np.round(df.loc[recipe_lunch].calorie * portion) 
            serving_lunch = np.round(portion/df.loc[recipe_lunch].servings, 1)
            fat_ratio = df.loc[recipe_lunch].fat_ratio
            protein_ratio = df.loc[recipe_lunch].protein_ratio            
            carb_ratio = df.loc[recipe_lunch].carb_ratio            
            link_lunch = df.loc[recipe_lunch].link            
            new_rec_lunch['recipe_lunch'].append(recipe_lunch)
            new_rec_lunch['link_lunch'].append(link_lunch)
            new_rec_lunch['serving_lunch'].append(serving_lunch)
            new_rec_lunch['calorie_lunch'].append(calorie_lunch)
            new_rec_lunch['protein'].append(protein)
            new_rec_lunch['fat ratio'].append(fat_ratio)
            new_rec_lunch['protein ratio'].append(protein_ratio)
            new_rec_lunch['carb ratio'].append(carb_ratio)
            
        else:
            portion = np.round(calorie_limit/df.loc[recipe_lunch].calorie, 2) 
            protein = np.round(df.loc[recipe_lunch].protein_g * portion)
            
            # check protein
            if protein < protein_lower:
                continue
            calorie_lunch = np.round(df.loc[recipe_lunch].calorie * portion) 
            serving_lunch = np.round(portion/df.loc[recipe_lunch].servings, 1)
            fat_ratio = df.loc[recipe_lunch].fat_ratio
            protein_ratio = df.loc[recipe_lunch].protein_ratio            
            carb_ratio = df.loc[recipe_lunch].carb_ratio            
            link_lunch = df.loc[recipe_lunch].link
            new_rec_lunch['recipe_lunch'].append(recipe_lunch)
            new_rec_lunch['link_lunch'].append(link_lunch)
            new_rec_lunch['serving_lunch'].append(serving_lunch)
            new_rec_lunch['calorie_lunch'].append(calorie_lunch)
            new_rec_lunch['protein'].append(protein)
            new_rec_lunch['fat ratio'].append(fat_ratio)
            new_rec_lunch['protein ratio'].append(protein_ratio)
            new_rec_lunch['carb ratio'].append(carb_ratio)

    st.warning('Running out of recipes. Please start over and choose more preferred meals.')
    return

        # define a function to take in recommended recipe list and return optimized recipes
def optimizer_dinner(rec_recipes, df, protein_lower, calorie, time='off'):
    protein_lower = protein_lower # set protein min
    fat_limit = 0.40 # set fat_ratio limit
    calorie_limit = calorie # set calorie limit 

    # create a new rec dict
    new_rec_dinner = {'recipe_dinner': [], 'link_dinner': [], 'serving_dinner': [], 'calorie_dinner': [], 'protein': [], 
               'fat ratio': [], 'protein ratio': [], 'carb ratio': []}
    

    while len(rec_recipes) > 0:
        if len(new_rec_dinner['recipe_dinner']) == 7:
            # df = pd.DataFrame(new_rec, index=[['Day 1 B','Day 1 L','Day 1 D','Day 2 B','Day 2 L','Day 3 B','Day 3 L','Day 3 D','Day 4 B','Day 4 L','Day 4 D','Day 5 B','Day 5 L','Day 5 D']])
            df = pd.DataFrame(new_rec_dinner, index=[['Day 1','Day 2','Day 3', 'Day 4', 'Day 5','Day 6', 'Day 7']])
            
            st.title('Weekly DINNER plan is ready.')
            for i in range(7):
                print_rec_dinner(df, i)
                plot_nutrient(df, i)
            return


        recipe_dinner = np.random.choice(rec_recipes)
        rec_recipes.remove(recipe_dinner) 
        
        # check time
        if time == 'on':
            if df.loc[recipe_dinner].cook_time > 30 or df.loc[recipe_dinner].cook_time == 0:
                continue
            
        # check fat
        if df.loc[recipe_dinner].fat_ratio > fat_limit:
            continue
            
        # check calorie
        if df.loc[recipe_dinner].calorie > calorie_limit:
            portion = np.round(calorie_limit/df.loc[recipe_dinner].calorie, 2) 
            protein = np.round(df.loc[recipe_dinner].protein_g * portion)
            
            # check protein
            if protein < protein_lower:
                continue
            calorie_dinner = np.round(df.loc[recipe_dinner].calorie * portion) 
            serving_dinner = np.round(portion/df.loc[recipe_dinner].servings, 1)
            fat_ratio = df.loc[recipe_dinner].fat_ratio
            protein_ratio = df.loc[recipe_dinner].protein_ratio            
            carb_ratio = df.loc[recipe_dinner].carb_ratio            
            link_dinner = df.loc[recipe_dinner].link            
            new_rec_dinner['recipe_dinner'].append(recipe_dinner)
            new_rec_dinner['link_dinner'].append(link_dinner)
            new_rec_dinner['serving_dinner'].append(serving_dinner)
            new_rec_dinner['calorie_dinner'].append(calorie_dinner)
            new_rec_dinner['protein'].append(protein)
            new_rec_dinner['fat ratio'].append(fat_ratio)
            new_rec_dinner['protein ratio'].append(protein_ratio)
            new_rec_dinner['carb ratio'].append(carb_ratio)
            
        else:
            portion = np.round(calorie_limit/df.loc[recipe_dinner].calorie, 2) 
            protein = np.round(df.loc[recipe_dinner].protein_g * portion)
            
            # check protein
            if protein < protein_lower:
                continue
            calorie_dinner = np.round(df.loc[recipe_dinner].calorie * portion) 
            serving_dinner = np.round(portion/df.loc[recipe_dinner].servings, 1)
            fat_ratio = df.loc[recipe_dinner].fat_ratio
            protein_ratio = df.loc[recipe_dinner].protein_ratio            
            carb_ratio = df.loc[recipe_dinner].carb_ratio            
            link_dinner = df.loc[recipe_dinner].link
            new_rec_dinner['recipe_dinner'].append(recipe_dinner)
            new_rec_dinner['link_dinner'].append(link_dinner)
            new_rec_dinner['serving_dinner'].append(serving_dinner)
            new_rec_dinner['calorie_dinner'].append(calorie_dinner)
            new_rec_dinner['protein'].append(protein)
            new_rec_dinner['fat ratio'].append(fat_ratio)
            new_rec_dinner['protein ratio'].append(protein_ratio)
            new_rec_dinner['carb ratio'].append(carb_ratio)


    st.warning('Running out of recipes. Please start over and choose more preferred meals.')

    return


def getWeeklyAverageExerciseTimeAndHeartRate():
    try:
        response = requests.get(nodeServerUrl).json()
        df = pd.DataFrame(response.get('payload'))
        df.drop(columns=["_id", "__v", "gender","exerciseType"], axis=1, inplace=True)
        df = df[df.heartRate != 0]
        sessionIDs = df.sessionId.unique()
        groupedSessions = df.groupby(df.sessionId)
        sessionIDs.sort()
        weeklySessions = 3
        exerciseDuration = 0
        avgHR = 0
        for i in range(weeklySessions):
            session = groupedSessions.get_group(sessionIDs[i])
            avgHR += session['heartRate'].sum() / session.shape[0]
            exerciseDuration += session.shape[0]
    
        avgHR = avgHR / weeklySessions
        # convert seconds to hrs
        exerciseDuration = exerciseDuration / (60 * 60)
        print(avgHR, exerciseDuration)
        return avgHR, exerciseDuration

    except:
        print("Unexpected error:", sys.exc_info()[0])


if __name__ == '__main__':
    getWeeklyAverageExerciseTimeAndHeartRate()