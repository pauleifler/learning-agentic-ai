---
type: concept
status: learning
domain:
  - agentic-ai
created: 2026-07-16
confidence: 1
tags:
  - ai/agents
category: Data & Analytics
---


# Statistics - Bootstrapping

## Definition

Bootstrapping is a statistical resampling technique used to estimate the uncertainty of a statistic when only a limited amount of data is available.

It repeatedly creates new samples from the original data by sampling **with replacement**, allowing us to estimate how much a statistic (such as a mean or difference in means) might vary.

## Why it matters

Real-world datasets are often small.

Instead of relying on a single observed value, bootstrapping estimates the range of values that could reasonably occur due to random variation.

This helps distinguish meaningful changes from normal noise.

## How it works

1. Start with the observed dataset.

2. Randomly sample from it **with replacement**.

3. Calculate the statistic of interest.

4. Repeat thousands of times.

5. Examine the distribution of the calculated statistics.

6. Use percentiles to estimate confidence intervals.

Unlike traditional statistical tests, bootstrapping makes relatively few assumptions about the underlying distribution of the data.

## Example

Suppose QPR earned:

```text

3

3

1

0

3

1

```

Average:

```text

1.83 PPG

```

A bootstrap sample might be:

```text

3

3

3

1

1

0

```

Average:

```text

1.83

```

Another sample:

```text

1

0

0

3

1

3

```

Average:

```text

1.33

```

Repeating this process thousands of times produces a distribution of plausible averages, allowing us to estimate uncertainty.

## Failure modes

Bootstrapping is less reliable when:

- The dataset is extremely small.
- The sample is not representative of the population.
- Observations are highly dependent (e.g. strong time dependence or changing conditions).
- The data contains systematic bias.

In football analytics, factors such as opponent strength, injuries and fixture difficulty mean that bootstrap results should be interpreted alongside domain knowledge.

## Implementation

Typical workflow:

```python

recent_points = recent_matches["points"].to_numpy()

bootstrap_samples = []

for _ in range(5000):

    sample = rng.choice(

        recent_points,

        size=len(recent_points),

        replace=True,

    )

    bootstrap_samples.append(sample.mean())

lower, upper = np.percentile(

    bootstrap_samples,

    [2.5, 97.5],

)

```

If the confidence interval excludes zero when comparing two groups, the observed difference is more likely to reflect a genuine change rather than random variation.
## Interview explanation

Bootstrapping is a resampling technique used to estimate the uncertainty of a statistic without making strong assumptions about the underlying data distribution. In my Football Copilot project, I used bootstrapping to compare a team's recent points per game with its earlier-season performance. Rather than relying on the raw difference alone, I generated thousands of resampled datasets to estimate a confidence interval, allowing the application to distinguish meaningful improvements from normal variation.

## Related concepts

- [[Confidence Intervals]]
- [[Statistical Significance]]
- [[Hypothesis Testing]]
- [[Sampling]]
- [[Variance]]

## Sources

- *An Introduction to Statistical Learning* — James, Witten, Hastie & Tibshirani
- *Computer Age Statistical Inference* — Bradley Efron & Trevor Hastie
- NumPy Documentation

## Key takeaways

- Bootstrapping estimates uncertainty from existing data.
- It samples **with replacement**.
- Thousands of resamples approximate repeated experiments.
- Confidence intervals are often more informative than raw differences.
- It is especially useful when sample sizes are modest or distributional assumptions are uncertain.
- Bootstrapping estimates uncertainty; it does not prove causation.