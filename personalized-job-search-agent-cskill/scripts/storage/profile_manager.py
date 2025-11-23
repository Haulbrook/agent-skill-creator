"""
User Profile Management Module

Handles creation, storage, and retrieval of user profile data
including skills, preferences, and job search criteria.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ProfileManager:
    """Manages user profile data for personalized job search."""

    def __init__(self, assets_dir: Path):
        """
        Initialize profile manager.

        Args:
            assets_dir: Directory to store profile data
        """
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(exist_ok=True)
        self.profile_file = self.assets_dir / "user_profile.json"
        self.preferences_file = self.assets_dir / "preferences.json"

    def create_or_update_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new profile or update existing one.

        Args:
            profile_data: Dictionary containing profile information

        Returns:
            Created/updated profile
        """
        # Load existing profile if it exists
        existing_profile = self.get_profile() or {}

        # Merge with new data
        profile = self._merge_profile_data(existing_profile, profile_data)

        # Add metadata
        profile["updated_at"] = datetime.now().isoformat()
        if "created_at" not in profile:
            profile["created_at"] = datetime.now().isoformat()

        # Validate profile
        if not self._validate_profile(profile):
            raise ValueError("Invalid profile data")

        # Save profile
        self._save_profile(profile)

        logger.info("Profile created/updated successfully")
        return profile

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get current user profile.

        Returns:
            Profile dictionary or None if no profile exists
        """
        if not self.profile_file.exists():
            return None

        try:
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            return None

    def update_skills(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update user skills.

        Args:
            skills: List of skill dictionaries

        Returns:
            Updated profile
        """
        profile = self.get_profile() or {}

        if "professional" not in profile:
            profile["professional"] = {}

        profile["professional"]["skills"] = skills
        return self.create_or_update_profile(profile)

    def update_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update job search preferences.

        Args:
            preferences: Preferences dictionary

        Returns:
            Updated profile
        """
        profile = self.get_profile() or {}
        profile["preferences"] = preferences
        return self.create_or_update_profile(profile)

    def extract_from_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract profile information from resume text.

        Args:
            resume_text: Resume text content

        Returns:
            Extracted profile data
        """
        # This would use AI/NLP to extract information
        # For now, return a structured template
        return {
            "message": "Resume parsing would happen here",
            "suggestion": "Use AI to extract: name, email, skills, experience, education"
        }

    def get_skill_summary(self) -> Dict[str, Any]:
        """
        Get summary of user skills.

        Returns:
            Skills summary with categories
        """
        profile = self.get_profile()
        if not profile or "professional" not in profile:
            return {"error": "No profile found"}

        skills = profile.get("professional", {}).get("skills", [])

        # Categorize skills
        technical_skills = []
        soft_skills = []
        other_skills = []

        for skill in skills:
            category = skill.get("category", "other")
            if category == "technical":
                technical_skills.append(skill)
            elif category == "soft":
                soft_skills.append(skill)
            else:
                other_skills.append(skill)

        return {
            "total_skills": len(skills),
            "technical": technical_skills,
            "soft": soft_skills,
            "other": other_skills
        }

    def _merge_profile_data(
        self,
        existing: Dict[str, Any],
        new: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge existing and new profile data."""
        merged = existing.copy()

        for key, value in new.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self._merge_profile_data(merged[key], value)
            else:
                merged[key] = value

        return merged

    def _validate_profile(self, profile: Dict[str, Any]) -> bool:
        """
        Validate profile data.

        Args:
            profile: Profile dictionary

        Returns:
            True if valid, False otherwise
        """
        # Basic validation
        # In production, this would be more comprehensive
        return True

    def _save_profile(self, profile: Dict[str, Any]):
        """Save profile to file."""
        with open(self.profile_file, 'w') as f:
            json.dump(profile, f, indent=2)

    def export_profile(self, format: str = "json") -> str:
        """
        Export profile in specified format.

        Args:
            format: Export format (json, pdf, txt)

        Returns:
            Exported profile data
        """
        profile = self.get_profile()
        if not profile:
            return "No profile to export"

        if format == "json":
            return json.dumps(profile, indent=2)
        elif format == "txt":
            return self._profile_to_text(profile)
        else:
            return f"Format {format} not supported yet"

    def _profile_to_text(self, profile: Dict[str, Any]) -> str:
        """Convert profile to human-readable text."""
        lines = ["=== USER PROFILE ===\n"]

        # Personal info
        if "personal" in profile:
            lines.append("Personal Information:")
            for key, value in profile["personal"].items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        # Professional info
        if "professional" in profile:
            lines.append("Professional Information:")
            prof = profile["professional"]

            if "current_role" in prof:
                lines.append(f"  Current Role: {prof['current_role']}")
            if "experience_years" in prof:
                lines.append(f"  Experience: {prof['experience_years']} years")

            if "skills" in prof:
                lines.append(f"  Skills ({len(prof['skills'])}):")
                for skill in prof["skills"]:
                    lines.append(f"    - {skill['name']} ({skill.get('proficiency', 'N/A')})")

            lines.append("")

        # Preferences
        if "preferences" in profile:
            lines.append("Job Search Preferences:")
            prefs = profile["preferences"]

            if "desired_roles" in prefs:
                lines.append(f"  Desired Roles: {', '.join(prefs['desired_roles'])}")
            if "salary_min" in prefs and "salary_max" in prefs:
                lines.append(f"  Salary Range: ${prefs['salary_min']:,} - ${prefs['salary_max']:,}")
            if "locations" in prefs:
                lines.append(f"  Locations: {', '.join(prefs['locations'])}")

        return "\n".join(lines)


def create_sample_profile() -> Dict[str, Any]:
    """Create a sample profile for testing."""
    return {
        "personal": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123",
            "location": "San Francisco, CA"
        },
        "professional": {
            "current_role": "Senior Software Engineer",
            "experience_years": 8,
            "skills": [
                {
                    "name": "Python",
                    "years": 8,
                    "proficiency": "expert",
                    "category": "technical"
                },
                {
                    "name": "JavaScript",
                    "years": 6,
                    "proficiency": "advanced",
                    "category": "technical"
                },
                {
                    "name": "AWS",
                    "years": 5,
                    "proficiency": "advanced",
                    "category": "technical"
                },
                {
                    "name": "Docker",
                    "years": 4,
                    "proficiency": "advanced",
                    "category": "technical"
                },
                {
                    "name": "Leadership",
                    "years": 3,
                    "proficiency": "intermediate",
                    "category": "soft"
                }
            ],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "school": "Stanford University",
                    "year": 2015
                }
            ],
            "certifications": [
                "AWS Solutions Architect",
                "Kubernetes CKAD"
            ]
        },
        "preferences": {
            "desired_roles": [
                "Staff Engineer",
                "Senior Software Engineer",
                "Tech Lead"
            ],
            "industries": ["fintech", "healthtech", "saas"],
            "salary_min": 150000,
            "salary_desired": 175000,
            "salary_max": 200000,
            "locations": ["remote", "san francisco", "new york"],
            "company_sizes": ["startup", "midsize"],
            "work_types": ["remote", "hybrid"],
            "benefits_priorities": [
                "work_life_balance",
                "equity",
                "learning_budget",
                "health_insurance"
            ],
            "dealbreakers": [
                "no_remote_option",
                "below_salary_min",
                "excessive_overtime",
                "poor_culture"
            ]
        },
        "career_goals": {
            "short_term": "Advance to Staff Engineer role at a growing startup",
            "long_term": "Become VP of Engineering or start own company",
            "learning_goals": [
                "System design at scale",
                "Team leadership",
                "Product strategy"
            ]
        }
    }
