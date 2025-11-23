"""Comparison Engine - Compare multiple job opportunities side-by-side."""

from typing import Dict, List, Any


class ComparisonEngine:
    """Compare multiple jobs and provide recommendations."""

    def compare(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple jobs side-by-side.

        Args:
            jobs: List of job dictionaries

        Returns:
            Comparison results with recommendations
        """
        if len(jobs) < 2:
            return {"error": "Need at least 2 jobs to compare"}

        comparison = {
            "jobs": jobs,
            "comparison_table": self._build_comparison_table(jobs),
            "recommendation": self._generate_recommendation(jobs),
            "best_in_category": self._find_best_in_categories(jobs)
        }

        return comparison

    def _build_comparison_table(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build comparison table."""
        return {
            "salaries": [j.get("salary_range") for j in jobs],
            "locations": [j.get("location") for j in jobs],
            "match_scores": [j.get("match_score", 0) for j in jobs]
        }

    def _generate_recommendation(self, jobs: List[Dict[str, Any]]) -> str:
        """Generate recommendation for best job."""
        best_job = max(jobs, key=lambda j: j.get("match_score", 0))
        return f"Recommend: {best_job.get('title')} at {best_job.get('company')}"

    def _find_best_in_categories(self, jobs: List[Dict[str, Any]]) -> Dict[str, str]:
        """Find best job in each category."""
        return {
            "highest_salary": max(jobs, key=lambda j: j.get("salary_range", [0])[1] if j.get("salary_range") else 0).get("title"),
            "best_match": max(jobs, key=lambda j: j.get("match_score", 0)).get("title")
        }
