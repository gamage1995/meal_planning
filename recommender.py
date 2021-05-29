import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import helperfunctions
from sklearn.metrics.pairwise import cosine_similarity

# image = Image.open('logo.jpg')
# st.image(image, use_column_width=True)

st. sidebar.image('image.jpg',use_column_width=True)
st.sidebar.title("Smart Digital Personal Fitness Trainer")
st.sidebar.write("Get your weekly personalized and healthy meal plan!!")

"""
# Personalized Meal Plan Recommendation Module      

"""
st.markdown("***")

# user input demographic info
st.write("Enter your details to get your customized meal plan")
gender = st.radio(label='Gender', options=('Male', 'Female'))
age = st.number_input('Age', value=18, step=1)
ht = st.number_input('Height (in)', value=60, step=1)
wt = st.number_input('Current weight (lb)', value=100, step=1)
#####
# st.write('Daily Calorie Allowance will be calculated based on your input')
# st.write('If you have data about the calories burnt in the workout, choose the label "Input From Safety Module ". ')
# st.write('If you are going to calculate calories based on average activity level, choose the label "Average Activity Level". ')
# DCA = st.radio(label='Daily Calorie Allowance',
# options=('Average Activity Level','Input From Safety Module '))
# st.write('Amount of calories burnt from the safety module:')
# calorie2 = st.number_input('Calorie (in)', value=120, step=1)

active = st.radio(label='Activity level', 
         options=('Sedentary (little or no exercise)', 
         'Lightly active (light exercise/sports 1-3 days/week)', 
         'Moderately active (moderate exercise/sports 3-5 days/week)', 
         'Very active (hard exercise/sports 6-7 days a week)',
         'Extra active (very hard exercise/sports & physical job or 2x training)'))
goal_wt = st.number_input('Goal weight (lb)', value=wt, step=1)

# calculate current daily calorie need based on Mifflin St. Jeor equation
ht_cm = ht * 2.54
wt_kg = wt / 2.2

if gender == 'Male':
    calorie = 10 * wt_kg + 6.25 * ht_cm - 5 * age + 5 
    st.write('Daily calorie allowance based on Mifflin St.Joer equation is',calorie)
else:
    calorie = 10 * wt_kg + 6.25 * ht_cm - 5 * age - 161
    st.write('Daily calorie allowance based on Mifflin St.Joer equation is',calorie)


# if DCA == 'Average Activity Level':
#     if active == 'Sedentary (little or no exercise)':
#         calorie *= 1.2
#     elif active == 'Lightly active (light exercise/sports 1-3 days/week)':
#         calorie *= 1.375
#     elif active == 'Moderately active (moderate exercise/sports 3-5 days/week)':
#         calorie *= 1.55
#     elif active == 'Very active (hard exercise/sports 6-7 days a week)':
#         calorie *= 1.725
#     else:
#         calorie *= 1.9
# else:
#     if calorie2 == 0 and calorie2<129:
#         calorie *= 1.2
#     elif calorie2 >130 and calorie2<469:
#         calorie *= 1.375
#     elif calorie2 >470 and calorie2<1149:
#         calorie *= 1.55
#     elif calorie2 >1150 and calorie2<1400:
#         calorie *= 1.725
#     else:
#         calorie *= 1.9

if active == 'Sedentary (little or no exercise)':
    calorie *= 1.2
elif active == 'Lightly active (light exercise/sports 1-3 days/week)':
    calorie *= 1.375
elif active == 'Moderately active (moderate exercise/sports 3-5 days/week)':
    calorie *= 1.55
elif active == 'Very active (hard exercise/sports 6-7 days a week)':
    calorie *= 1.725
else:
    calorie *= 1.9

calorie = np.round(calorie)

# output daily calorie need
if goal_wt == wt:
    st.write('Daily calorie need after considering the level of physical activity is', calorie, 'in order to maintain your current weight.')

# calculate weeks to reach goal based on recommendation that losing 1 lb/week
elif goal_wt < wt:
    week = wt - goal_wt 
    new_calorie = calorie - 500
    if new_calorie >= 1200:
        st.write('Daily calorie need after considering the level of physical activity is', new_calorie, 
                 'in order to lose weight and you need', week, 
                 'weeks to reach your goal.')
    else:
        st.warning('Warning! You daily calorie need is lower than 1200.')
        st.warning('Please either increase your goal weight or increase your activity level to ensure adequate daily nutrition.')

else:
    st.warning('Your goal weight is over your current weight.Try adhering to the BMR')


# user input meal preferences
# load data
lda_matrix = pd.read_csv('recipe_lda.csv')
lda_matrix.set_index('title', inplace=True)
df_nutrient = pd.read_csv('recipe_nutrientInfo.csv')
df_nutrient.set_index('title', inplace=True)

quick_meal = st.radio('Do you prefer only quick meals (ready in 30 minutes)?',
                     ('Yes', 'No'))
    
# provide meal choices randomly
@st.cache()
def recipe_choices():
    return np.random.choice(lda_matrix.index.tolist(), 20)
options = st.multiselect('Please choose at least 3 meals you like.', 
                         options=(recipe_choices()))

        
if st.button('Submit'):
    
    if len(options) > 2:
        # use recommender
        ## calculate cosine similarity
        lda_array = lda_matrix.to_numpy()
        cosine_sim = cosine_similarity(lda_array)

        ## creating a Series for recipe titles
        indices = pd.Series(lda_matrix.index)
        ######
        st.write('Recipe names to choose from: ')
        st.write(indices)

        ## get top 100 similar recipes for each option
        rec_recipes = []
        for title in options:
            top_recipes = helperfunctions.recommender(title, indices, lda_matrix, cosine_sim, 100)
            rec_recipes.extend(top_recipes)

        rec_recipes = list(set(rec_recipes))
        ######
        st.write(rec_recipes)

        # use optimizer
        ## calculate protein and calorie needs per meal
        protein_lower = np.round(wt_kg * 0.8    / 3, 1)
        if goal_wt < wt:
            calorie_need = np.round(new_calorie / 3)
        else:
            calorie_need = np.round(calorie / 3)

        ## use optimizer
        if quick_meal == 'Yes':
            helperfunctions.optimizer(rec_recipes, df_nutrient, protein_lower, calorie_need, time='on')
            helperfunctions.optimizer_lunch(rec_recipes, df_nutrient, protein_lower, calorie_need, time='on')
            helperfunctions.optimizer_dinner(rec_recipes, df_nutrient, protein_lower, calorie_need, time='on')
            
        else:
            helperfunctions.optimizer(rec_recipes, df_nutrient, protein_lower, calorie_need)
            helperfunctions.optimizer_lunch(rec_recipes, df_nutrient, protein_lower, calorie_need)
            helperfunctions.optimizer_dinner(rec_recipes, df_nutrient, protein_lower, calorie_need)
           
   
    else:
        st.warning('Please choose at least 3 meals to get a personalized recommendation.')

