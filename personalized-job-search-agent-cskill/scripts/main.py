#!/usr/bin/env python3
"""
Personalized Job Search Agent - Main Orchestration Module

This is the main entry point for the job search agent. It orchestrates all
functionality including profile management, job search, scoring, and applications.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent
AGENT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = AGENT_DIR / "assets"

# Ensure assets directory exists
ASSETS_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import local modules
try:
    from storage.profile_manager import ProfileManager
    from storage.job_database import JobDatabase
    from storage.application_db import ApplicationTracker
    from search.unified_search import UnifiedJobSearch
    from analysis.job_scorer import JobScorer
    from analysis.comparison_engine import ComparisonEngine
    from application.cover_letter_gen import CoverLetterGenerator
    from application.application_tracker import ApplicationManager
except ImportError as e:
    logger.warning(f"Could not import modules: {e}")
    logger.info("Running in initialization mode")


class PersonalizedJobSearchAgent:
    """
    Main agent class that orchestrates all job search functionality.
    """

    def __init__(self, assets_dir: Path = ASSETS_DIR):
        """Initialize the job search agent."""
        self.assets_dir = assets_dir
        self.assets_dir.mkdir(exist_ok=True)

        # Initialize components
        self.profile_manager = None
        self.job_database = None
        self.app_tracker = None
        self.job_search = None
        self.job_scorer = None
        self.comparison_engine = None
        self.cover_letter_gen = None
        self.app_manager = None

        self._initialize_components()

    def _initialize_components(self):
        """Initialize all agent components."""
        try:
            self.profile_manager = ProfileManager(self.assets_dir)
            self.job_database = JobDatabase(self.assets_dir)
            self.app_tracker = ApplicationTracker(self.assets_dir)

            # Initialize search and analysis components
            self.job_search = UnifiedJobSearch()
            self.job_scorer = JobScorer()
            self.comparison_engine = ComparisonEngine()
            self.cover_letter_gen = CoverLetterGenerator()
            self.app_manager = ApplicationManager(self.assets_dir)

            logger.info("Job search agent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing components: {e}")

    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update user profile.

        Args:
            profile_data: Dictionary containing user profile information

        Returns:
            Created/updated profile dictionary
        """
        logger.info("Creating/updating user profile")

        if not self.profile_manager:
            return {"error": "Profile manager not initialized"}

        profile = self.profile_manager.create_or_update_profile(profile_data)

        return {
            "status": "success",
            "message": "Profile created/updated successfully",
            "profile": profile
        }

    def search_jobs(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict] = None,
        use_profile: bool = True
    ) -> Dict[str, Any]:
        """
        Search for jobs across multiple platforms.

        Args:
            query: Optional search query string
            filters: Optional filters to apply
            use_profile: Whether to use profile for personalized search

        Returns:
            Dictionary with search results
        """
        logger.info("Searching for jobs...")

        if not self.job_search or not self.profile_manager:
            return {"error": "Search components not initialized"}

        # Get profile if using personalized search
        profile = None
        if use_profile:
            profile = self.profile_manager.get_profile()
            if not profile:
                return {
                    "error": "No profile found. Please create a profile first.",
                    "suggestion": "Use create_profile() to set up your profile"
                }

        # Perform search
        try:
            results = self.job_search.search(
                query=query,
                filters=filters,
                profile=profile
            )

            # Score each job if profile exists
            if profile and results.get("jobs"):
                scored_jobs = []
                for job in results["jobs"]:
                    score = self.job_scorer.score_job(job, profile)
                    job["match_score"] = score["total_score"]
                    job["score_breakdown"] = score["breakdown"]
                    job["analysis"] = score.get("analysis", {})
                    scored_jobs.append(job)

                # Sort by score
                scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
                results["jobs"] = scored_jobs

            # Save jobs to database
            if results.get("jobs"):
                self.job_database.save_jobs(results["jobs"])

            return {
                "status": "success",
                "count": len(results.get("jobs", [])),
                "jobs": results.get("jobs", []),
                "platforms_searched": results.get("platforms", [])
            }

        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return {"error": str(e)}

    def analyze_job(self, job_id: str) -> Dict[str, Any]:
        """
        Perform detailed analysis of a specific job.

        Args:
            job_id: Unique identifier for the job

        Returns:
            Detailed analysis results
        """
        logger.info(f"Analyzing job {job_id}")

        if not self.job_database or not self.profile_manager:
            return {"error": "Required components not initialized"}

        # Get job from database
        job = self.job_database.get_job(job_id)
        if not job:
            return {"error": f"Job {job_id} not found"}

        # Get profile
        profile = self.profile_manager.get_profile()
        if not profile:
            return {"error": "Profile not found. Please create a profile first."}

        # Perform detailed analysis
        try:
            analysis = self.job_scorer.detailed_analysis(job, profile)
            return {
                "status": "success",
                "job": job,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Error analyzing job: {e}")
            return {"error": str(e)}

    def compare_jobs(self, job_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple jobs side-by-side.

        Args:
            job_ids: List of job IDs to compare

        Returns:
            Comparison results
        """
        logger.info(f"Comparing {len(job_ids)} jobs")

        if not self.job_database or not self.comparison_engine:
            return {"error": "Required components not initialized"}

        # Get jobs from database
        jobs = []
        for job_id in job_ids:
            job = self.job_database.get_job(job_id)
            if job:
                jobs.append(job)

        if len(jobs) < 2:
            return {"error": "Need at least 2 jobs to compare"}

        # Perform comparison
        try:
            comparison = self.comparison_engine.compare(jobs)
            return {
                "status": "success",
                "comparison": comparison
            }
        except Exception as e:
            logger.error(f"Error comparing jobs: {e}")
            return {"error": str(e)}

    def apply_to_job(
        self,
        job_id: str,
        auto_submit: bool = False,
        custom_cover_letter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply to a specific job.

        Args:
            job_id: Unique identifier for the job
            auto_submit: Whether to automatically submit (default: False)
            custom_cover_letter: Optional custom cover letter

        Returns:
            Application result
        """
        logger.info(f"Applying to job {job_id}")

        if not all([self.job_database, self.profile_manager,
                   self.cover_letter_gen, self.app_manager]):
            return {"error": "Required components not initialized"}

        # Get job and profile
        job = self.job_database.get_job(job_id)
        if not job:
            return {"error": f"Job {job_id} not found"}

        profile = self.profile_manager.get_profile()
        if not profile:
            return {"error": "Profile not found"}

        # Generate cover letter if not provided
        cover_letter = custom_cover_letter
        if not cover_letter:
            logger.info("Generating cover letter...")
            cover_letter = self.cover_letter_gen.generate(job, profile)

        # Prepare application
        application_data = {
            "job_id": job_id,
            "job": job,
            "profile": profile,
            "cover_letter": cover_letter,
            "auto_submit": auto_submit
        }

        # Submit application
        try:
            result = self.app_manager.submit_application(application_data)

            # Track application
            if result.get("status") == "success":
                self.app_tracker.add_application({
                    "job_id": job_id,
                    "job_title": job.get("title"),
                    "company": job.get("company"),
                    "applied_date": result.get("timestamp"),
                    "status": "submitted",
                    "application_id": result.get("application_id")
                })

            return result

        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return {"error": str(e)}

    def get_application_status(self, application_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of applications.

        Args:
            application_id: Optional specific application ID

        Returns:
            Application status information
        """
        if not self.app_tracker:
            return {"error": "Application tracker not initialized"}

        try:
            if application_id:
                status = self.app_tracker.get_application(application_id)
                return {
                    "status": "success",
                    "application": status
                }
            else:
                all_apps = self.app_tracker.get_all_applications()
                return {
                    "status": "success",
                    "applications": all_apps,
                    "summary": self.app_tracker.get_summary()
                }
        except Exception as e:
            logger.error(f"Error getting application status: {e}")
            return {"error": str(e)}

    def get_recommendations(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get personalized job recommendations.

        Args:
            limit: Maximum number of recommendations

        Returns:
            List of recommended jobs
        """
        logger.info("Getting personalized recommendations")

        # Search with profile
        search_result = self.search_jobs(use_profile=True)

        if search_result.get("error"):
            return search_result

        # Get top matches
        jobs = search_result.get("jobs", [])
        recommendations = jobs[:limit]

        return {
            "status": "success",
            "count": len(recommendations),
            "recommendations": recommendations
        }


# CLI Interface Functions
def handle_cli_command(agent: PersonalizedJobSearchAgent, command: str, args: List[str]):
    """Handle CLI commands."""

    if command == "create-profile":
        print("📋 Profile Creation Wizard")
        print("Let's set up your job search profile...\n")
        # This would be an interactive profile creation
        # For now, return instructions
        return {
            "message": "Profile creation interactive mode",
            "instruction": "Please provide your profile information"
        }

    elif command == "search":
        query = " ".join(args) if args else None
        return agent.search_jobs(query=query)

    elif command == "recommendations":
        limit = int(args[0]) if args else 10
        return agent.get_recommendations(limit=limit)

    elif command == "status":
        return agent.get_application_status()

    else:
        return {
            "error": f"Unknown command: {command}",
            "available_commands": [
                "create-profile", "search", "recommendations", "status"
            ]
        }


def main():
    """Main entry point for CLI usage."""
    print("🎯 Personalized Job Search Agent")
    print("=" * 50)

    # Initialize agent
    agent = PersonalizedJobSearchAgent()

    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = sys.argv[2:] if len(sys.argv) > 2 else []

        result = handle_cli_command(agent, command, args)
        print(json.dumps(result, indent=2))
    else:
        print("\nUsage:")
        print("  python main.py <command> [args]")
        print("\nCommands:")
        print("  create-profile    - Create your job search profile")
        print("  search [query]    - Search for jobs")
        print("  recommendations   - Get personalized recommendations")
        print("  status           - Check application status")
        print("\nOr use the Claude Code interface for full functionality!")


if __name__ == "__main__":
    main()
