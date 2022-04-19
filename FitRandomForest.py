# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 20:19:24 2022

@author: CLaug
"""
from sklearn.ensemble import RandomForestRegressor

# FIt random forest 

classifier = RandomForestRegressor(n_estimators=100, criterion='mse', random_state=1)
classifier.fit(X_train,y_train)

y_pred = classifier.predict(X_test)

print(mean_squared_error(y_test, y_pred))
