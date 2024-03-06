import numpy as np
import scipy.stats as stats
from scipy.stats import poisson
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Question 1a - generate gs variable
# gs is generated as a random normal distribution using the mean and standard deviation presented in the problem statement
# Plotted with matplotlib
gs_mean, gs_std = 7.25, 0.875
gs = np.random.normal(gs_mean, gs_std, 10000)
plt.hist(gs, density=True, bins=30)
plt.ylabel("Probability")
plt.xlabel("gs")
plt.title("Histogram of gs")
plt.show()


# Question 1b: Generate ak, pp, and ptime variables with associated plots
# Generate 10000 random multivariate normal samples with all means set to 0 and covariance as specified
def plotvars(dataset, varname, column):
    plt.hist(dataset[:, column], density=True, bins=30)
    plt.ylabel("Probability")
    plt.xlabel(varname)
    plt.title("Histogram of " + varname)
    plt.show()


# Create sample table
means = [0, 0, 0]
covariance = {
    "ak": [1.0, 0.6, -0.9],
    "pp": [0.6, 1.0, -0.5],
    "ptime": [-0.9, -0.5, 1.0],
}
cov = pd.DataFrame(data=covariance)
samples = np.random.multivariate_normal(means, cov, size=10000)

# plot ak
plotvars(samples, "ak", 0)

# plot pp
plotvars(samples, "pp", 1)

# plot ptime
plotvars(samples, "ptime", 2)


# Question 1c: Probability integral transform - apply cdf function to each variable
u = stats.norm.cdf(samples)
plotvars(u, "U[:, 0] (ak)", 0)
plotvars(u, "U[:, 1] (pp)", 1)
plotvars(u, "U[:, 2] (ptime)", 2)


# Question 1d: Inverse transform samping - apply quantile function for desired probability distributions
def plotvars2(dataset, varname, xaxis):
    plt.hist(dataset, density=True, bins=30)
    plt.ylabel("Probability")
    plt.xlabel(xaxis)
    plt.title("Histogram of " + varname)
    plt.show()


# plot ak
ak = poisson.ppf(u[:, 0], 5)
plotvars2(ak, "ak", "Number of air knots in a case")

# plot pp
pp = poisson.ppf(u[:, 1], 15)
plotvars2(pp, "pp", "Number of times resident passes point in a case")

# plot ptime
ptime = poisson.ppf(u[:, 2], 120, 30)
plotvars2(ptime, "ptime", "Time resident spent practicing this week")


# Question 1e: Correlations between variables
print(np.corrcoef(ak, pp))
print(np.corrcoef(ak, ptime))
print(np.corrcoef(pp, ptime))


def showCorrelations(var1, var2, xaxis, yaxis):
    plt.scatter(var1, var2)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title("Correlation of " + xaxis + " vs. " + yaxis)
    plt.show()


showCorrelations(ak, pp, "ak", "pp")
showCorrelations(ak, ptime, "ak", "ptime")
showCorrelations(pp, ptime, "pp", "ptime")
showCorrelations(gs, ak, "gs", "ak")
showCorrelations(gs, pp, "gs", "pp")
showCorrelations(gs, ptime, "gs", "ptime")


# Question 2.1: Sample correlation matrix
# Assume given X = i data samples (x1, x2, ..., xi) where each sample is a 4D vector
# Therefore, xij = jth variable in ith sample. k = rows in matrix

# FORMULA:
# Si[i][j] =  sum((xij - mean(xj))*(xik - mean(xk)))/(sqrt(sum(xij - mean(xj))^2)*(sqrt(sum(xik - mean(xk))^2))


# Question 2.2:
# Calculate new sums with just the new element i, and then you can average in the previous correlation S(i-1) to estimate the new S(i)

S = pd.DataFrame([1])  # Initialize S1 = 1

for i in range(1, 101):
    xi = np.random.rand(1)  # new element

    newMean = (np.mean(S[: i - 1]) * (i - 1) + xi) / i

    S[i] = (
        S[i - 1] * (i - 1) + (xi - newMean)
    ) / i  # creates new value for S[i] using values from S[i-1]

plt.matshow(S.corr())
plt.show()
