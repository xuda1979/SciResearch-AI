"""Utilities to run small synthetic experiments used by the orchestrator.

This module contains helper functions to execute toy machine
learning experiments in environments where external network
access is unavailable.  The primary function, `run_synthetic_regression`,
generates a synthetic dataset with a simple linear relationship,
fits both a linear regression and a polynomial regression model,
and returns the root mean squared error (RMSE) for each model.

The function is designed to be deterministic so that repeated
invocations yield identical results.  It uses NumPy and
scikit‑learn, which are included in the repository’s requirements.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error


def run_synthetic_regression(n_samples: int = 1000, noise_sigma: float = 0.5, seed: int = 0) -> tuple[float, float]:
    """Run a simple regression experiment and return RMSE values.

    This helper implements the experimental protocol described in
    the heuristic provider: generate data with a linear relationship
    (``y = 3x + noise``), split into training and test sets, fit both
    a linear and a second‑degree polynomial regression, and compute
    RMSE on the held‑out test data.

    Args:
        n_samples: Total number of (x, y) samples to generate.
        noise_sigma: Standard deviation of the additive Gaussian noise.
        seed: Random seed for reproducibility.

    Returns:
        A tuple ``(rmse_linear, rmse_poly)`` containing the RMSE of
        the linear model and the polynomial model, respectively.
    """
    # Set up a reproducible random number generator
    rng = np.random.default_rng(seed)
    # Generate input features uniformly in the range [-5, 5]
    x = rng.uniform(-5.0, 5.0, size=(n_samples, 1))
    # Generate targets according to a linear function with Gaussian noise
    y = 3.0 * x + rng.normal(scale=noise_sigma, size=(n_samples, 1))
    # Split into training and test sets (80/20 split)
    n_train = int(0.8 * n_samples)
    x_train, x_test = x[:n_train], x[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]
    # Fit a simple linear regression
    lin = LinearRegression().fit(x_train, y_train)
    # Fit a second‑degree polynomial regression using a pipeline
    poly = make_pipeline(PolynomialFeatures(2), LinearRegression()).fit(x_train, y_train)
    # Compute RMSE on the test set
    rmse_lin = mean_squared_error(y_test, lin.predict(x_test), squared=False)
    rmse_poly = mean_squared_error(y_test, poly.predict(x_test), squared=False)
    return float(rmse_lin), float(rmse_poly)