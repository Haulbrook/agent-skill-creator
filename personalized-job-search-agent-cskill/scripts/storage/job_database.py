"""
Job Database Module

Handles storage and retrieval of job listings discovered during searches.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class JobDatabase:
    """Database for storing and managing job listings."""

    def __init__(self, assets_dir: Path):
        """
        Initialize job database.

        Args:
            assets_dir: Directory to store job data
        """
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(exist_ok=True)
        self.db_file = self.assets_dir / "jobs_database.json"
        self.jobs = self._load_database()

    def _load_database(self) -> Dict[str, Any]:
        """Load job database from file."""
        if not self.db_file.exists():
            return {"jobs": {}, "metadata": {"total_jobs": 0}}

        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading job database: {e}")
            return {"jobs": {}, "metadata": {"total_jobs": 0}}

    def _save_database(self):
        """Save job database to file."""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.jobs, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving job database: {e}")

    def _generate_job_id(self, job: Dict[str, Any]) -> str:
        """
        Generate unique ID for a job.

        Args:
            job: Job dictionary

        Returns:
            Unique job ID
        """
        # Create ID from company + title + location
        unique_string = f"{job.get('company')}_{job.get('title')}_{job.get('location')}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

    def save_job(self, job: Dict[str, Any]) -> str:
        """
        Save a single job to database.

        Args:
            job: Job dictionary

        Returns:
            Job ID
        """
        job_id = job.get("id") or self._generate_job_id(job)
        job["id"] = job_id
        job["saved_at"] = datetime.now().isoformat()

        self.jobs["jobs"][job_id] = job
        self.jobs["metadata"]["total_jobs"] = len(self.jobs["jobs"])

        self._save_database()
        return job_id

    def save_jobs(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """
        Save multiple jobs to database.

        Args:
            jobs: List of job dictionaries

        Returns:
            List of job IDs
        """
        job_ids = []
        for job in jobs:
            job_id = self.save_job(job)
            job_ids.append(job_id)

        logger.info(f"Saved {len(job_ids)} jobs to database")
        return job_ids

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job dictionary or None
        """
        return self.jobs["jobs"].get(job_id)

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Get all jobs from database.

        Returns:
            List of all jobs
        """
        return list(self.jobs["jobs"].values())

    def search_jobs(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search jobs in database.

        Args:
            query: Search query string
            filters: Filter criteria

        Returns:
            List of matching jobs
        """
        jobs = self.get_all_jobs()

        # Apply text search if query provided
        if query:
            query_lower = query.lower()
            jobs = [
                job for job in jobs
                if query_lower in job.get("title", "").lower()
                or query_lower in job.get("company", "").lower()
                or query_lower in job.get("description", "").lower()
            ]

        # Apply filters
        if filters:
            if "min_salary" in filters:
                jobs = [
                    job for job in jobs
                    if job.get("salary_range", [0])[0] >= filters["min_salary"]
                ]

            if "location" in filters:
                location_filter = filters["location"].lower()
                jobs = [
                    job for job in jobs
                    if location_filter in job.get("location", "").lower()
                ]

            if "min_match_score" in filters:
                jobs = [
                    job for job in jobs
                    if job.get("match_score", 0) >= filters["min_match_score"]
                ]

        return jobs

    def get_top_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top matching jobs based on match score.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of top matching jobs
        """
        jobs = self.get_all_jobs()

        # Filter jobs with match scores
        scored_jobs = [job for job in jobs if "match_score" in job]

        # Sort by match score
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)

        return scored_jobs[:limit]

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job from database.

        Args:
            job_id: Job ID

        Returns:
            True if deleted, False if not found
        """
        if job_id in self.jobs["jobs"]:
            del self.jobs["jobs"][job_id]
            self.jobs["metadata"]["total_jobs"] = len(self.jobs["jobs"])
            self._save_database()
            return True
        return False

    def clear_old_jobs(self, days: int = 30) -> int:
        """
        Clear jobs older than specified days.

        Args:
            days: Number of days

        Returns:
            Number of jobs deleted
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        jobs_to_delete = []

        for job_id, job in self.jobs["jobs"].items():
            posted_date = job.get("posted_date")
            if posted_date:
                try:
                    job_date = datetime.fromisoformat(posted_date)
                    if job_date < cutoff_date:
                        jobs_to_delete.append(job_id)
                except:
                    pass

        for job_id in jobs_to_delete:
            self.delete_job(job_id)

        logger.info(f"Deleted {len(jobs_to_delete)} old jobs")
        return len(jobs_to_delete)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Statistics dictionary
        """
        jobs = self.get_all_jobs()

        # Calculate stats
        total_jobs = len(jobs)
        jobs_with_scores = [j for j in jobs if "match_score" in j]

        avg_score = 0
        if jobs_with_scores:
            avg_score = sum(j["match_score"] for j in jobs_with_scores) / len(jobs_with_scores)

        # Count by platform
        platforms = {}
        for job in jobs:
            platform = job.get("source", "unknown")
            platforms[platform] = platforms.get(platform, 0) + 1

        return {
            "total_jobs": total_jobs,
            "jobs_with_scores": len(jobs_with_scores),
            "average_match_score": round(avg_score, 2),
            "jobs_by_platform": platforms,
            "database_size_kb": self.db_file.stat().st_size / 1024 if self.db_file.exists() else 0
        }
