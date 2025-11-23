"""
Job Scoring Algorithm

Intelligent matching algorithm that scores jobs based on user profile
and preferences. Uses weighted scoring across multiple dimensions.
"""

import logging
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)


class JobScorer:
    """Scores jobs based on user profile and preferences."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize job scorer.

        Args:
            weights: Optional custom weights for scoring dimensions
        """
        # Default weights (should sum to 1.0)
        self.weights = weights or {
            "skills": 0.35,      # Skills match is most important
            "salary": 0.25,      # Salary alignment
            "location": 0.15,    # Location preference
            "company": 0.10,     # Company fit
            "benefits": 0.10,    # Benefits package
            "culture": 0.05      # Culture fit
        }

    def score_job(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score a job against user profile.

        Args:
            job: Job dictionary
            profile: User profile dictionary

        Returns:
            Dictionary with total score and breakdown
        """
        # Calculate individual dimension scores
        scores = {
            "skills": self._score_skills(job, profile),
            "salary": self._score_salary(job, profile),
            "location": self._score_location(job, profile),
            "company": self._score_company(job, profile),
            "benefits": self._score_benefits(job, profile),
            "culture": self._score_culture(job, profile)
        }

        # Calculate weighted total
        total_score = sum(
            scores[dimension] * self.weights[dimension]
            for dimension in scores
        )

        return {
            "total_score": round(total_score, 2),
            "breakdown": {k: round(v, 2) for k, v in scores.items()},
            "analysis": self._generate_analysis(job, profile, scores)
        }

    def _score_skills(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> float:
        """
        Score skills match.

        Args:
            job: Job dictionary
            profile: User profile dictionary

        Returns:
            Skills match score (0-100)
        """
        user_skills = set()
        prof_data = profile.get("professional", {})

        # Extract user skills
        for skill in prof_data.get("skills", []):
            user_skills.add(skill["name"].lower())

        # Extract required job skills
        job_skills_required = set()
        job_skills_nice = set()

        for skill in job.get("requirements", []):
            if isinstance(skill, str):
                job_skills_required.add(skill.lower())

        for skill in job.get("nice_to_have", []):
            if isinstance(skill, str):
                job_skills_nice.add(skill.lower())

        # Calculate match
        if not job_skills_required:
            return 75.0  # No specific requirements = decent match

        required_match = len(user_skills & job_skills_required)
        required_total = len(job_skills_required)

        nice_match = len(user_skills & job_skills_nice)
        nice_total = len(job_skills_nice) if job_skills_nice else 1

        # Score: 70% from required, 30% from nice-to-have
        required_score = (required_match / required_total) * 70
        nice_score = (nice_match / nice_total) * 30 if nice_total > 0 else 0

        total_score = required_score + nice_score

        # Bonus for exceeding requirements
        if required_match > required_total:
            total_score = min(100, total_score + 10)

        return total_score

    def _score_salary(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> float:
        """
        Score salary alignment.

        Args:
            job: Job dictionary
            profile: User profile dictionary

        Returns:
            Salary match score (0-100)
        """
        prefs = profile.get("preferences", {})

        salary_min = prefs.get("salary_min", 0)
        salary_desired = prefs.get("salary_desired", salary_min)
        salary_max = prefs.get("salary_max", salary_desired * 1.5)

        # Get job salary range
        job_salary_range = job.get("salary_range", [])

        if not job_salary_range or len(job_salary_range) < 2:
            return 50.0  # Unknown salary = neutral

        job_min = job_salary_range[0]
        job_max = job_salary_range[1]
        job_mid = (job_min + job_max) / 2

        # Score based on how salary compares to preferences
        if job_mid >= salary_desired:
            # At or above desired salary
            score = 90 + min(10, (job_mid - salary_desired) / salary_desired * 10)
        elif job_mid >= salary_min:
            # Between min and desired
            range_position = (job_mid - salary_min) / (salary_desired - salary_min)
            score = 50 + (range_position * 40)
        else:
            # Below minimum
            score = max(0, 50 * (job_mid / salary_min))

        return min(100, score)

    def _score_location(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> float:
        """
        Score location preference match.

        Args:
            job: Job dictionary
            profile: User profile dictionary

        Returns:
            Location match score (0-100)
        """
        prefs = profile.get("preferences", {})
        preferred_locations = [loc.lower() for loc in prefs.get("locations", [])]

        job_location = job.get("location", "").lower()

        # Perfect match for remote if preferred
        if "remote" in preferred_locations and "remote" in job_location:
            return 100.0

        # Check for location matches
        for pref_loc in preferred_locations:
            if pref_loc in job_location or job_location in pref_loc:
                return 100.0

        # Partial match for hybrid
        if "hybrid" in job_location and "remote" in preferred_locations:
            return 75.0

        # No match
        return 30.0

    def _score_company(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> float:
        """
        Score company fit.

        Args:
            job: Job dictionary
            profile: User profile dictionary

        Returns:
            Company fit score (0-100)
        """
        prefs = profile.get("preferences", {})

        score = 50.0  # Base score

        # Check company size preference
        preferred_sizes = prefs.get("company_sizes", [])
        company_info = job.get("company_info", {})

        if preferred_sizes and company_info.get("size"):
            if company_info["size"].lower() in [s.lower() for s in preferred_sizes]:
                score += 20

        # Check industry preference
        preferred_industries = prefs.get("industries", [])
        if preferred_industries and company_info.get("industry"):
            if company_info["industry"].lower() in [i.lower() for i in preferred_industries]:
                score += 20

        # Check company rating if available
        if company_info.get("rating"):
            rating = company_info["rating"]
            if rating >= 4.0:
                score += 10
            elif rating >= 3.5:
                score += 5

        return min(100, score)

    def _score_benefits(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> float:
        """
        Score benefits package.

        Args:
            job: Job dictionary
            profile: User profile dictionary

        Returns:
            Benefits match score (0-100)
        """
        prefs = profile.get("preferences", {})
        priority_benefits = prefs.get("benefits_priorities", [])

        job_benefits = job.get("benefits", [])

        if not priority_benefits:
            # No preferences, score based on number of benefits
            return min(100, len(job_benefits) * 10)

        # Score based on priority benefits match
        matches = 0
        for benefit in priority_benefits:
            benefit_lower = benefit.lower().replace("_", " ")
            for job_benefit in job_benefits:
                if benefit_lower in job_benefit.lower():
                    matches += 1
                    break

        score = (matches / len(priority_benefits)) * 100
        return score

    def _score_culture(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> float:
        """
        Score culture fit.

        Args:
            job: Job dictionary
            profile: User profile dictionary

        Returns:
            Culture fit score (0-100)
        """
        # This would analyze company reviews, values, etc.
        # For now, return a moderate score
        company_info = job.get("company_info", {})

        score = 50.0

        # Check work-life balance indicators
        if "work_life_balance" in profile.get("preferences", {}).get("benefits_priorities", []):
            culture_rating = company_info.get("culture_ratings", {}).get("work_life_balance", 3.0)
            score += (culture_rating - 3.0) * 10

        return min(100, max(0, score))

    def _generate_analysis(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any],
        scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Generate human-readable analysis.

        Args:
            job: Job dictionary
            profile: User profile dictionary
            scores: Score breakdown

        Returns:
            Analysis dictionary
        """
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []

        for dimension, score in scores.items():
            if score >= 80:
                strengths.append(dimension)
            elif score < 60:
                weaknesses.append(dimension)

        # Generate recommendation
        total_score = sum(scores[d] * self.weights[d] for d in scores)

        if total_score >= 90:
            recommendation = "STRONGLY RECOMMEND - Excellent match"
            action = "Apply immediately"
        elif total_score >= 75:
            recommendation = "RECOMMEND - Very good match"
            action = "Apply soon"
        elif total_score >= 60:
            recommendation = "CONSIDER - Decent match"
            action = "Review carefully before applying"
        else:
            recommendation = "NOT RECOMMENDED - Poor match"
            action = "Look for better opportunities"

        return {
            "recommendation": recommendation,
            "action": action,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "match_category": self._get_match_category(total_score)
        }

    def _get_match_category(self, score: float) -> str:
        """Get match category from score."""
        if score >= 90:
            return "Excellent Match ⭐⭐⭐⭐⭐"
        elif score >= 75:
            return "Great Match ⭐⭐⭐⭐"
        elif score >= 60:
            return "Good Match ⭐⭐⭐"
        elif score >= 45:
            return "Decent Match ⭐⭐"
        else:
            return "Poor Match ⭐"

    def detailed_analysis(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate detailed analysis with explanations.

        Args:
            job: Job dictionary
            profile: User profile dictionary

        Returns:
            Detailed analysis
        """
        score_result = self.score_job(job, profile)

        # Add detailed explanations
        detailed = score_result.copy()

        # Skills analysis
        detailed["skills_analysis"] = self._detailed_skills_analysis(job, profile)

        # Salary analysis
        detailed["salary_analysis"] = self._detailed_salary_analysis(job, profile)

        # Missing skills
        detailed["missing_skills"] = self._get_missing_skills(job, profile)

        return detailed

    def _detailed_skills_analysis(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed skills analysis."""
        user_skills = {s["name"].lower() for s in profile.get("professional", {}).get("skills", [])}
        required_skills = {s.lower() for s in job.get("requirements", []) if isinstance(s, str)}
        nice_skills = {s.lower() for s in job.get("nice_to_have", []) if isinstance(s, str)}

        matched_required = user_skills & required_skills
        missing_required = required_skills - user_skills
        matched_nice = user_skills & nice_skills

        return {
            "matched_required": list(matched_required),
            "missing_required": list(missing_required),
            "matched_nice": list(matched_nice),
            "match_percentage": (len(matched_required) / len(required_skills) * 100) if required_skills else 100
        }

    def _detailed_salary_analysis(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed salary analysis."""
        prefs = profile.get("preferences", {})
        salary_range = job.get("salary_range", [0, 0])

        return {
            "offered_range": salary_range,
            "your_min": prefs.get("salary_min"),
            "your_desired": prefs.get("salary_desired"),
            "your_max": prefs.get("salary_max"),
            "meets_minimum": salary_range[0] >= prefs.get("salary_min", 0) if salary_range else False,
            "meets_desired": salary_range[1] >= prefs.get("salary_desired", 0) if salary_range else False
        }

    def _get_missing_skills(
        self,
        job: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> List[str]:
        """Get list of skills user is missing for the job."""
        user_skills = {s["name"].lower() for s in profile.get("professional", {}).get("skills", [])}
        required_skills = {s.lower() for s in job.get("requirements", []) if isinstance(s, str)}
        nice_skills = {s.lower() for s in job.get("nice_to_have", []) if isinstance(s, str)}

        missing = (required_skills | nice_skills) - user_skills
        return list(missing)
