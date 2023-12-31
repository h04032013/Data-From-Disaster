# -*- coding: utf-8 -*-

#Import all needed libraries or dependency
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""# **STEP 1) Data Collection and Exploration: loading in data with pandas**"""

data =  pd.read_csv('train.csv')

#displaying data to see what actually worked
data

#loosely look at correlation between different values and final results
import seaborn as sns

sns.heatmap(data.corr(), cmap='YlGnBu')
plt.show

#Result: Strong Negative correlation between survival and passenger social class

"""# **STEP 2: Data Preprocessing**"""

#Shuffling the data set
from sklearn.model_selection import StratifiedShuffleSplit

#split object is the sstratified shuffle split
#data will just be split once with a test size of 20%
split = StratifiedShuffleSplit(n_splits= 1, test_size=0.2)
#for the columns in the data, split it
#Assure that survived and non-survived are equally distributed in both test/train groups
for train_indices,test_indices in split.split(data, data[["Survived","Pclass","Sex"]]):
  #New shuffle data sets
    strat_train_set = data.loc[train_indices]
    strat_test_set = data.loc[test_indices]

#Testing out if shuffle worked
strat_test_set

#Histogram of different distributions - Train
plt.subplot(1,2,1)
strat_train_set['Survived'].hist()
strat_train_set['Pclass'].hist()

#Histogram of different distributions - Test
plt.subplot(1,2,2)
strat_train_set['Survived'].hist()
strat_train_set['Pclass'].hist()

plt.show()

#Each graph is a set, both have similar distributions of values

#Continue handle missing values and "Scale or normalize numerical features" - imputation

#See missing values
strat_train_set.info()

#There are 138 missing age values out of 712
#Make a class to create a "base and "estimate" the missing values based on the mean
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer

class AgeImputer(BaseEstimator, TransformerMixin):

    def fit (self, X, y=None):
      return self

#This method will do the actual work of transforming the values
#X is the dataframe
    def transform (self, X):
      imputer = SimpleImputer(strategy="mean")
      X['Age'] = imputer.fit_transform(X[['Age']])
      return X

#Encoding categorical values into numerical
from sklearn.preprocessing import OneHotEncoder

class FeatureEncoder(BaseEstimator, TransformerMixin):

    def fit(self, X, y = None):
      return self
#Pipeline in ML: 1. data fed into pandas
# 2. From pandas df, fed into AgeImputer
# 3. From imputer, fed into encoder
    def transform(self, X):

      encoder = OneHotEncoder()
      matrix = encoder.fit_transform(X[['Embarked']]).toarray()

      column_names = ["C","S","Q","N",]

      for i in range(len(matrix.T)):
        X[column_names[i]] = matrix.T[i]

      matrix = encoder.fit_transform(X[['Sex']]).toarray()

      column_names = ["Female", "Male"]

      for i in range(len(matrix.T)):
        X[column_names[i]] = matrix.T[i]

      return X

#Dropping cloumns that were encoded or insignificant

class FeatureDropper (BaseEstimator, TransformerMixin):

  def fit (self, X, y=None):
    return self

  def transform(self, X):
    return X.drop(["Embarked","Name","Ticket","Cabin","Sex","N"], axis = 1, errors = "ignore")

#Establishing the pipeline in the code for data
from sklearn.pipeline import Pipeline

pipeline = Pipeline ([("ageimputer", AgeImputer()),
                      ("featureencoder", FeatureEncoder()),
                      ("featuredropper", FeatureDropper())])

#Setting training data through the preprocessing pipeline
strat_train_set = pipeline.fit_transform(strat_train_set)

strat_train_set

strat_train_set.info()
#No more NaN values, missing values have been imputed or dropped

#Scale the data
#So no specific feature dominates
#All input features will have a similar scale

from sklearn.preprocessing import StandardScaler

X = strat_train_set.drop(['Survived'],axis=1)
Y = strat_train_set['Survived']

scaler = StandardScaler()
X_data = scaler.fit_transform(X)
Y_data = Y.to_numpy()

X_data
#Check this! The data is an array of values :)

"""# **STEP 4: Model Selection**"""

#We will use the Random Forests method to train a model
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
#CrossValidation for a tree

clf = RandomForestClassifier()

#Hyperparameters
param_grid = [{
    "n_estimators": [10, 100, 200, 500], "max_depth": [None, 5, 10], "min_samples_split": [2,3,4]
}]

#Iterate through param grid, 3 folds (from cv),use accuracy metric
grid_search = GridSearchCV(clf, param_grid, cv=3, scoring="accuracy", return_train_score=True)
grid_search.fit(X_data, Y_data)

"""(Model Tuning - Step 6?)"""

final_clf = grid_search.best_estimator_

final_clf

"""# **STEP 5: Model Training & Evaluation**"""

#Repeat training process with test set
strat_test_set = pipeline.fit_transform(strat_test_set)

X_test = strat_test_set.drop(['Survived'],axis=1)
Y_test = strat_test_set['Survived']

scaler = StandardScaler()
X_data_test = scaler.fit_transform(X_test)
Y_data_test = Y_test.to_numpy()

final_clf.score(X_data_test, Y_data_test)

final_data = pipeline.fit_transform(data)
final_data

X_final = final_data.drop(['Survived'],axis=1)
Y_final = final_data['Survived']

scaler = StandardScaler()
X_data_final = scaler.fit_transform(X_final)
Y_data_final = Y_final.to_numpy()

prod_clf = RandomForestClassifier()

#Hyperparameters
param_grid = [{
    "n_estimators": [10, 100, 200, 500], "max_depth": [None, 5, 10], "min_samples_split": [2,3,4]
}]

#Iterate through param grid, 3 folds (from cv),use accuracy metric
grid_search = GridSearchCV(prod_clf, param_grid, cv=3, scoring="accuracy", return_train_score=True)
grid_search.fit(X_data_final, Y_data_final)

"""# **STEP** 6: Model Tuning"""

prod_final_clf = grid_search.best_estimator_

prod_final_clf

titanic_test_data = pd.read_csv('test.csv')
final_test_data = pipeline.fit_transform(titanic_test_data)

X_final_test = final_test_data
#final_test_data.info()
#fill (impute) null value with forward val
X_final_test = X_final_test.fillna(method="ffill")

scaler = StandardScaler()
X_data_final_test = scaler.fit_transform(X_final_test)

"""# **EXTRA: Kaggle Submission**"""

predictions = prod_final_clf.predict(X_data_final_test)

final_df = pd.DataFrame(titanic_test_data['PassengerId'])
final_df['Survived'] = predictions
final_df.to_csv('predictions.csv', index=False)
