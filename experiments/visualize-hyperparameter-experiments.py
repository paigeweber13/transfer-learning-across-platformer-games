import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

### survival rates
survival_data = pd.read_csv('experiments/smw-first-to-4000-survival-rate.csv')
survival_data.sort_values('survival', inplace=True)

survival_rate = np.around(np.array(survival_data['survival']), 2)
num_generations = np.array(survival_data['num_generations_before_success'])
time_to_success = np.array(survival_data['total_time'])

model = make_pipeline(PolynomialFeatures(2), LinearRegression())
model.fit(survival_rate.reshape(1, -1), time_to_success.reshape(1, -1))

plt.figure(figsize=(10,7))
# plt.plot(survival_rate, num_generations)
plt.plot(survival_rate, time_to_success)
plt.plot(model.predict(survival_rate.reshape(1, -1)))
plt.show()
