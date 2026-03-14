from __future__ import annotations

from dataclasses import dataclass
from math import erf, sqrt


@dataclass(frozen=True)
class ProportionStats:
    successes: int
    trials: int
    rate: float
    ci_low: float
    ci_high: float


@dataclass(frozen=True)
class ProportionComparison:
    metric_name: str
    baseline_group: str
    target_group: str
    baseline: ProportionStats
    target: ProportionStats
    rate_diff: float
    z_score: float | None
    p_value: float | None
    significant: bool
    enough_samples: bool


def _normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))


def wilson_interval(
    successes: int, trials: int, z: float = 1.96
) -> tuple[float, float]:
    if trials == 0:
        return (0.0, 0.0)
    phat = successes / trials
    denominator = 1 + (z**2 / trials)
    center = (phat + (z**2 / (2 * trials))) / denominator
    margin = (
        z * sqrt((phat * (1 - phat) / trials) + (z**2 / (4 * trials**2))) / denominator
    )
    return (round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4))


def proportion_stats(successes: int, trials: int) -> ProportionStats:
    rate = round(successes / trials, 4) if trials else 0.0
    ci_low, ci_high = wilson_interval(successes, trials)
    return ProportionStats(
        successes=successes,
        trials=trials,
        rate=rate,
        ci_low=ci_low,
        ci_high=ci_high,
    )


def compare_two_proportions(
    *,
    metric_name: str,
    baseline_group: str,
    target_group: str,
    baseline_successes: int,
    baseline_trials: int,
    target_successes: int,
    target_trials: int,
    min_trials_for_claim: int = 10,
) -> ProportionComparison:
    baseline = proportion_stats(baseline_successes, baseline_trials)
    target = proportion_stats(target_successes, target_trials)
    enough_samples = (
        baseline_trials >= min_trials_for_claim
        and target_trials >= min_trials_for_claim
    )

    if baseline_trials == 0 or target_trials == 0:
        return ProportionComparison(
            metric_name=metric_name,
            baseline_group=baseline_group,
            target_group=target_group,
            baseline=baseline,
            target=target,
            rate_diff=round(target.rate - baseline.rate, 4),
            z_score=None,
            p_value=None,
            significant=False,
            enough_samples=False,
        )

    pooled = (baseline_successes + target_successes) / (baseline_trials + target_trials)
    standard_error = sqrt(
        pooled * (1 - pooled) * ((1 / baseline_trials) + (1 / target_trials))
    )

    if standard_error == 0:
        z_score = None
        p_value = None
    else:
        z_score = (target.rate - baseline.rate) / standard_error
        p_value = round(2 * (1 - _normal_cdf(abs(z_score))), 6)

    significant = bool(enough_samples and p_value is not None and p_value < 0.05)

    return ProportionComparison(
        metric_name=metric_name,
        baseline_group=baseline_group,
        target_group=target_group,
        baseline=baseline,
        target=target,
        rate_diff=round(target.rate - baseline.rate, 4),
        z_score=round(z_score, 4) if z_score is not None else None,
        p_value=p_value,
        significant=significant,
        enough_samples=enough_samples,
    )
