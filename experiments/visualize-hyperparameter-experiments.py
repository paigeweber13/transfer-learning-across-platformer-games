import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

### survival rates
survival_data = pd.read_csv('experiments/smw-first-to-4000-survival-rate.csv')
# drop the one case with 0.3 survival rate
survival_data = survival_data[survival_data.survival != 0.3]
survival_data.sort_values('survival', inplace=True)

# aggregate all results by survival rate, take mean of them
# survival_data = survival_data.groupby('survival', as_index=False).mean()

# create numpy arrays
survival_rate = np.around(np.array(survival_data['survival']), 2).reshape(-1, 1)
num_generations = np.array(survival_data['num_generations_before_success'])
time_to_success = np.array(survival_data['total_time'])

time_with_ones = np.column_stack((np.ones(survival_rate.shape), 
                                  time_to_success))
polynomial_features = PolynomialFeatures(degree=2)
linear_regression = LinearRegression()
model = Pipeline([("polynomial_features", polynomial_features),
                     ("linear_regression", linear_regression)])
# print(survival_rate)
# print(time_with_ones)
model.fit(survival_rate, time_with_ones)
time_regression = model.predict(survival_rate)
time_regression = time_regression[:,1]
# print(time_regression)
# print(time_to_success)

plt.figure(figsize=(10,7))
# plt.plot(survival_rate, num_generations)
plt.scatter(survival_rate, time_to_success)
plt.plot(survival_rate, time_regression)
plt.title('Training speed with varying survival rates')
plt.xlabel('Survival rate')
plt.ylabel('Time to success')
plt.show()

### pop_size
# pop_data = pd.read_csv('experiments/smw-first-to-4000-pop-size.csv')
# pop_data.sort_values('pop_size', inplace=True)

# np_pop_size = np.array(pop_data['pop_size']).reshape(-1, 1)
# np_time = np.array(pop_data['total_time'])
# np_time_ones = np.column_stack((np.ones(np_time.shape), np_time))

# polynomial_features = PolynomialFeatures(degree=2)
# linear_regression = LinearRegression()
# model = Pipeline([("polynomial_features", polynomial_features),
#                      ("linear_regression", linear_regression)])
# model.fit(np_pop_size, np_time_ones)
# time_regression = model.predict(np_pop_size)
# time_regression = time_regression[:,1]

# plt.figure(figsize=(10,7))
# # plt.plot(survival_rate, num_generations)
# plt.scatter(np_pop_size, np_time)
# plt.plot(np_pop_size, time_regression)
# plt.show()
