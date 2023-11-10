import numpy as np
from statsmodels.regression import linear_model
import statsmodels as sm
import pandas as pd
import statsmodels.formula.api as smf
import os
import scipy.stats as stats
import shap
from statsmodels.regression import linear_model
import statsmodels as sm
import lightgbm as lgb
from pathlib import Path
import scipy
from scipy.stats import mannwhitneyu
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error
import json
import matplotlib.pyplot as plt
import eli5
from eli5.sklearn import PermutationImportance

def run_anova_on_dataframe(df_full_pitchsplit):
    df_full_pitchsplit_anova = df_full_pitchsplit.copy()

    unique_probe_words = df_full_pitchsplit_anova['ProbeWord'].unique()

    df_full_pitchsplit_anova = df_full_pitchsplit_anova.reset_index(drop=True)

    df_full_pitchsplit_anova['ProbeWord'] = pd.Categorical(df_full_pitchsplit_anova['ProbeWord'],
                                                           categories=unique_probe_words, ordered=True)
    df_full_pitchsplit_anova['ProbeWord'] = df_full_pitchsplit_anova['ProbeWord'].cat.codes

    df_full_pitchsplit_anova['BrainArea'] = df_full_pitchsplit_anova['BrainArea'].astype('category')

    # cast the probe word category as an int
    df_full_pitchsplit_anova['ProbeWord'] = df_full_pitchsplit_anova['ProbeWord'].astype('int')
    df_full_pitchsplit_anova['PitchShift'] = df_full_pitchsplit_anova['PitchShift'].astype('int')
    df_full_pitchsplit_anova['Below-chance'] = df_full_pitchsplit_anova['Below-chance'].astype('int')

    df_full_pitchsplit_anova["ProbeWord"] = pd.to_numeric(df_full_pitchsplit_anova["ProbeWord"])
    df_full_pitchsplit_anova["PitchShift"] = pd.to_numeric(df_full_pitchsplit_anova["PitchShift"])
    df_full_pitchsplit_anova["Below_chance"] = pd.to_numeric(df_full_pitchsplit_anova["Below-chance"])
    df_full_pitchsplit_anova["Score"] = pd.to_numeric(df_full_pitchsplit_anova["Score"])
    # change the columns to the correct type

    # remove all rows where the score is NaN
    df_full_pitchsplit_anova = df_full_pitchsplit_anova.dropna(subset=['Score'])
    # nest ferret as a variable , ,look at the relative magnittud eo fthe coefficients for both lightgbm model and anova
    print(df_full_pitchsplit_anova.dtypes)
    # now run anova
    formula = 'Score ~ C(ProbeWord) + C(PitchShift) +C(BrainArea)+C(SingleUnit)'
    model = smf.ols(formula, data=df_full_pitchsplit_anova).fit()
    anova_table = sm.stats.anova.anova_lm(model, typ=3)
    # get the coefficient of determination
    print(model.rsquared)
    print(anova_table)
    return anova_table, model


def create_gen_frac_variable(df_full_pitchsplit, high_score_threshold = False, index_or_frac = 'frac'):
    for unit_id in df_full_pitchsplit['ID'].unique():
        # Check how many scores for that unit are above 60%
        df_full_pitchsplit_unit = df_full_pitchsplit[df_full_pitchsplit['ID'] == unit_id]
        #filter for the above-chance scores
        mean_scores = df_full_pitchsplit_unit['Score'].mean()
        #add the mean score to the dataframe
        df_full_pitchsplit.loc[df_full_pitchsplit['ID'] == unit_id, 'MeanScore'] = mean_scores
        #if the mean score is below 0.75, then we can't calculate the gen frac
        if high_score_threshold == True:
            if len(df_full_pitchsplit_unit) == 0 or mean_scores < 0.60:
                df_full_pitchsplit.loc[df_full_pitchsplit['ID'] == unit_id, 'GenFrac'] = np.nan
                continue
        else:
            if len(df_full_pitchsplit_unit) == 0 :
                df_full_pitchsplit.loc[df_full_pitchsplit['ID'] == unit_id, 'GenFrac'] = np.nan
                continue
        above_60_scores = df_full_pitchsplit_unit[
            df_full_pitchsplit_unit['Score'] >= 0.60 ]  # Replace 'score_column' with the actual column name

        # Check how many probe words are below 60%

        below_60_probe_words = df_full_pitchsplit_unit[df_full_pitchsplit_unit[
                                                           'Score'] < 0.60]  # Replace 'probe_words_column' with the actual column name
        max_score = df_full_pitchsplit_unit.max()['Score']
        min_score = df_full_pitchsplit_unit.min()['Score']
        if index_or_frac == 'index':
            gen_frac = (max_score - min_score) / (max_score+min_score)
        else:
            gen_frac = len(above_60_scores) / (len(above_60_scores) + len(below_60_probe_words))


        df_full_pitchsplit.loc[df_full_pitchsplit['ID'] == unit_id, 'GenFrac'] = gen_frac
        # Now you can do something with the counts, for example, print them
        # print(f"Unit ID: {unit_id}")
        # print(f"Number of scores above 60%: {len(above_60_scores)}")
        # print(f"Number of probe words below 60%: {len(below_60_probe_words)}")
        # print("-------------------")
    return df_full_pitchsplit

def runlgbmmodel_score(df_use):
    col = 'Score'

    unique_probe_words = df_use['ProbeWord'].unique()
    unique_IDs = df_use['ID'].unique()
    df_use = df_use.reset_index(drop=True)

    df_use['ProbeWord'] = pd.Categorical(df_use['ProbeWord'],
                                                           categories=unique_probe_words, ordered=True)
    df_use['ID'] = pd.Categorical(df_use['ID'],categories=unique_IDs, ordered=True)

    df_use['ProbeWord'] = df_use['ProbeWord'].cat.codes

    df_use['BrainArea'] = df_use['BrainArea'].astype('category')

    # cast the probe word category as an int
    df_use['ProbeWord'] = df_use['ProbeWord'].astype('int')
    df_use['PitchShift'] = df_use['PitchShift'].astype('int')
    df_use['Below-chance'] = df_use['Below-chance'].astype('int')

    df_use["ProbeWord"] = pd.to_numeric(df_use["ProbeWord"])
    df_use["PitchShift"] = pd.to_numeric(df_use["PitchShift"])
    df_use["Below_chance"] = pd.to_numeric(df_use["Below-chance"])
    df_use["Score"] = pd.to_numeric(df_use["Score"])
    #only remove the below chance scores
    df_use = df_use[df_use['Below-chance'] == 0]


    dfx = df_use.loc[:, df_use.columns != col]
    # remove ferret as possible feature
    # col = 'ID'
    # dfx = dfx.loc[:, dfx.columns != col]
    col2 = 'SingleUnit'
    dfx = dfx.loc[:, dfx.columns != col2]
    col3 = 'GenFrac'
    dfx = dfx.loc[:, dfx.columns != col3]
    col4 = 'MeanScore'
    dfx = dfx.loc[:, dfx.columns != col4]
    col5 = 'Below-chance'
    dfx = dfx.loc[:, dfx.columns != col5]
    col6 = 'Below_chance'
    dfx = dfx.loc[:, dfx.columns != col6]

    #remove any rows

    X_train, X_test, y_train, y_test = train_test_split(dfx, df_use['Score'], test_size=0.2,
                                                        random_state=42, shuffle=True)

    dtrain = lgb.Dataset(X_train, label=y_train)
    dtest = lgb.Dataset(X_test, label=y_test)

    param = {'max_depth': 2, 'eta': 1, 'objective': 'reg:squarederror'}
    param['nthread'] = 4
    param['eval_metric'] = 'auc'
    evallist = [(dtrain, 'train'), (dtest, 'eval')]
    xg_reg = lgb.LGBMRegressor(colsample_bytree=0.3, learning_rate=0.1,
                               max_depth=10, alpha=10, n_estimators=10, verbose=1)

    xg_reg.fit(X_train, y_train, eval_metric='MSE', verbose=1)
    ypred = xg_reg.predict(X_test)
    lgb.plot_importance(xg_reg)
    plt.title('feature importances for the lstm decoding score  model')

    plt.show()

    kfold = KFold(n_splits=10)
    results = cross_val_score(xg_reg, X_train, y_train, scoring='neg_mean_squared_error', cv=kfold)
    results_TEST = cross_val_score(xg_reg, X_test, y_test, scoring='neg_mean_squared_error', cv=kfold)

    mse = mean_squared_error(ypred, y_test)
    print("neg MSE on test set: %.2f" % (np.mean(results_TEST)*100))
    print("negative MSE on train set: %.2f%%" % (np.mean(results) * 100.0))
    print(results)
    shap_values = shap.TreeExplainer(xg_reg).shap_values(dfx)
    fig, ax = plt.subplots(figsize=(15, 15))
    # title kwargs still does nothing so need this workaround for summary plots

    fig, ax = plt.subplots(1, figsize=(10, 10), dpi = 300)

    shap.summary_plot(shap_values,dfx,  max_display=20)
    plt.show()
    #partial dependency plot of the pitch shift versus naive color coded by naive

    shap.dependence_plot("PitchShift", shap_values, dfx, interaction_index='Naive', show=True)
    #run a permutation importance test
    from sklearn.inspection import permutation_importance
    perm = permutation_importance(xg_reg, random_state=1).fit(X_test, y_test)
    #plot the permutation importance
    import eli5
    from eli5.sklearn import PermutationImportance
    perm = PermutationImportance(xg_reg, random_state=1).fit(X_test, y_test)

    eli5.show_weights(perm, feature_names=X_test.columns.tolist())



    labels = [item.get_text() for item in ax.get_yticklabels()]
    print(labels)
