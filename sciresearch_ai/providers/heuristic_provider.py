"""
HeuristicProvider: a lightweight offline provider that generates
semi‑structured research content without requiring access to external
models or APIs.  This provider is designed to return plausible
scientific prose based solely on the input prompt using a handful of
heuristics and templates.  It enables high quality draft papers in
environments where network access is unavailable or API keys are
missing.

The heuristics inspect the prompt for keywords associated with the
different stages of the research loop—planning, experiment design,
debate, and revision.  Depending on the detected intent the provider
returns a tailored response.  If no intent is matched a generic
response is produced that paraphrases the question.

The goal of this provider is not to discover novel science, but to
produce coherent LaTeX sections with reasonable content that passes
basic quality gates (grammar, formatting, logical flow).  You can
extend or refine the heuristics to better suit your domain.
"""

from __future__ import annotations

import re
from typing import List


class HeuristicProvider:
    """A provider that returns canned scientific responses based on simple heuristics."""

    name = "heuristic"

    def __init__(self, **kwargs) -> None:
        # Allow unused keyword arguments for compatibility with other providers
        self.kwargs = kwargs

    def generate(self, prompt: str, n: int = 1, **gen_kwargs) -> List[str]:
        """Generate one or more responses based on simple templates.

        Args:
            prompt: The raw prompt sent by the orchestrator.
            n: Number of completions to return.  For simplicity we
               generate a single response and duplicate it `n` times.
            gen_kwargs: Additional unused generation parameters for
               compatibility with other providers.

        Returns:
            A list of response strings of length `n`.
        """
        response = self._generate_one(prompt)
        return [response for _ in range(n)]

    # ------------------------------------------------------------------
    # Internal helper to generate a single response
    def _generate_one(self, prompt: str) -> str:
        p_lower = prompt.lower().strip()
        # 1) Planning stage: propose objective and plan
        if "concise research objective" in p_lower:
            return (
                "Our objective is to evaluate the performance of a simple machine "
                "learning model on a synthetic regression dataset. The study will "
                "follow three steps: (1) generate a clean synthetic dataset with a "
                "known functional relationship and additive noise; (2) implement "
                "and train a linear regression model and at least one non‑linear "
                "baseline (e.g., polynomial regression); (3) evaluate the models "
                "using root mean squared error (RMSE) and discuss the results."
            )
        # 2) Experiment design and TTC refinement prompts
        if ("refine this plan" in p_lower) or ("experiment protocol" in p_lower):
            return (
                "To execute the study we will write a Python script that:\n"
                "1. Imports numpy and scikit‑learn.\n"
                "2. Generates 1 000 samples (x, y) from y = 3x + noise where noise ∼ N(0,0.5).\n"
                "3. Splits the data into training and test sets.\n"
                "4. Fits a linear regression model and a second‑degree polynomial regression.\n"
                "5. Computes RMSE on the test set for both models.\n"
                "6. Logs the RMSE values to a JSON results file.\n\n"
                "Pseudo‑code:\n"
                "    import numpy as np\n"
                "    from sklearn.linear_model import LinearRegression\n"
                "    from sklearn.preprocessing import PolynomialFeatures\n"
                "    from sklearn.pipeline import make_pipeline\n"
                "    from sklearn.metrics import mean_squared_error\n\n"
                "    def run():\n"
                "        rng = np.random.default_rng(0)\n"
                "        x = rng.uniform(-5, 5, size=(1000, 1))\n"
                "        y = 3 * x + rng.normal(scale=0.5, size=(1000, 1))\n"
                "        x_train, x_test = x[:800], x[800:]\n"
                "        y_train, y_test = y[:800], y[800:]\n"
                "        lin = LinearRegression().fit(x_train, y_train)\n"
                "        poly = make_pipeline(PolynomialFeatures(2), LinearRegression()).fit(x_train, y_train)\n"
                "        rmse_lin = mean_squared_error(y_test, lin.predict(x_test), squared=False)\n"
                "        rmse_poly = mean_squared_error(y_test, poly.predict(x_test), squared=False)\n"
                "        return rmse_lin, rmse_poly\n"
            )
        # 3) Debate prompts: assess well‑posedness and pitfalls
        if ("is the following experiment" in p_lower) or ("identify pitfalls" in p_lower):
            return (
                "The proposed experiment is well‑posed because it defines a clear data‑generating "
                "process, two specific models to compare, and an objective metric (RMSE). However, "
                "there are a few pitfalls: (i) ensure that the noise level is appropriate so the "
                "task is neither trivial nor impossible; (ii) normalise or scale features if the "
                "feature range is wide; (iii) consider multiple random seeds to assess variance. "
                "To address these issues we will fix a master seed, report variance over multiple "
                "runs, and include data standardisation where necessary."
            )
        # 4) Revision prompts: produce an improved methods section.  Check this
        # first because the revision prompt includes the word "critique" which
        # would otherwise trigger the critique handler below.
        if "revise the draft" in p_lower:
            return (
                "This study investigates how well linear and polynomial regression models recover "
                "a known linear relationship from synthetic data. We generate 1 000 samples "
                "according to $y = 3x + \\varepsilon$, where $\\varepsilon \sim \\mathcal{N}(0,0.5)$, and "
                "split them into training and test sets. We then fit a linear regression model and "
                "a second‑degree polynomial regression. Performance is measured by the root mean "
                "squared error (RMSE) on the test set. All code is available in the project’s "
                "`code/` directory, and results are reproducible with the provided random seed."
            )
        # 5) Critique prompts: ask reviewer to critique the draft
        if ("review the following draft" in p_lower) or ("critique" in p_lower):
            return (
                "The draft is concise but lacks context and methodological detail. It should "
                "explicitly state the hypothesis, describe the data generation procedure, and "
                "justify the choice of models. Citations are missing, and equations should be "
                "formatted using LaTeX. The writing should be polished for grammar and clarity."
            )
        # 6) Fallback: paraphrase the request
        cleaned = re.sub("\s+", " ", prompt.strip())
        return (
            f"I have received your request: '{cleaned[:80]}'. "
            "Here is a brief response: this action will be handled in subsequent steps."
        )
