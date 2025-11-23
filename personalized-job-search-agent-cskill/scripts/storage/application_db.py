"""
Application Tracking Database

Tracks all job applications and their current status.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ApplicationTracker:
    """Tracks job applications and their status."""

    def __init__(self, assets_dir: Path):
        """
        Initialize application tracker.

        Args:
            assets_dir: Directory to store application data
        """
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(exist_ok=True)
        self.db_file = self.assets_dir / "applications.json"
        self.applications = self._load_database()

    def _load_database(self) -> Dict[str, Any]:
        """Load applications database from file."""
        if not self.db_file.exists():
            return {"applications": {}, "metadata": {"total_applications": 0}}

        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading applications database: {e}")
            return {"applications": {}, "metadata": {"total_applications": 0}}

    def _save_database(self):
        """Save applications database to file."""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.applications, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving applications database: {e}")

    def add_application(self, application_data: Dict[str, Any]) -> str:
        """
        Add a new application.

        Args:
            application_data: Application information

        Returns:
            Application ID
        """
        app_id = application_data.get("application_id") or f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        application = {
            "id": app_id,
            "job_id": application_data.get("job_id"),
            "job_title": application_data.get("job_title"),
            "company": application_data.get("company"),
            "applied_date": application_data.get("applied_date") or datetime.now().isoformat(),
            "status": application_data.get("status", "submitted"),
            "platform": application_data.get("platform"),
            "notes": application_data.get("notes", ""),
            "timeline": [
                {
                    "date": datetime.now().isoformat(),
                    "status": "submitted",
                    "note": "Application submitted"
                }
            ]
        }

        self.applications["applications"][app_id] = application
        self.applications["metadata"]["total_applications"] = len(self.applications["applications"])

        self._save_database()
        logger.info(f"Added application {app_id}")
        return app_id

    def update_status(
        self,
        app_id: str,
        new_status: str,
        note: Optional[str] = None
    ) -> bool:
        """
        Update application status.

        Args:
            app_id: Application ID
            new_status: New status
            note: Optional note about the update

        Returns:
            True if updated, False if not found
        """
        if app_id not in self.applications["applications"]:
            return False

        application = self.applications["applications"][app_id]
        application["status"] = new_status
        application["updated_at"] = datetime.now().isoformat()

        # Add to timeline
        timeline_entry = {
            "date": datetime.now().isoformat(),
            "status": new_status,
            "note": note or f"Status changed to {new_status}"
        }
        application["timeline"].append(timeline_entry)

        self._save_database()
        logger.info(f"Updated application {app_id} status to {new_status}")
        return True

    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get application by ID.

        Args:
            app_id: Application ID

        Returns:
            Application data or None
        """
        return self.applications["applications"].get(app_id)

    def get_all_applications(self) -> List[Dict[str, Any]]:
        """
        Get all applications.

        Returns:
            List of all applications
        """
        return list(self.applications["applications"].values())

    def get_applications_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get applications with specific status.

        Args:
            status: Status to filter by

        Returns:
            List of matching applications
        """
        return [
            app for app in self.get_all_applications()
            if app.get("status") == status
        ]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all applications.

        Returns:
            Summary statistics
        """
        applications = self.get_all_applications()

        # Count by status
        status_counts = {}
        for app in applications:
            status = app.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Recent applications
        recent = sorted(
            applications,
            key=lambda x: x.get("applied_date", ""),
            reverse=True
        )[:5]

        return {
            "total_applications": len(applications),
            "by_status": status_counts,
            "recent_applications": recent
        }

    def add_interview(
        self,
        app_id: str,
        interview_data: Dict[str, Any]
    ) -> bool:
        """
        Add interview information to application.

        Args:
            app_id: Application ID
            interview_data: Interview details

        Returns:
            True if added, False if application not found
        """
        if app_id not in self.applications["applications"]:
            return False

        application = self.applications["applications"][app_id]

        if "interviews" not in application:
            application["interviews"] = []

        application["interviews"].append({
            "date": interview_data.get("date"),
            "type": interview_data.get("type"),
            "duration": interview_data.get("duration"),
            "interviewer": interview_data.get("interviewer"),
            "notes": interview_data.get("notes", ""),
            "outcome": interview_data.get("outcome", "pending")
        })

        self.update_status(app_id, "interview_scheduled", "Interview scheduled")
        return True

    def add_offer(
        self,
        app_id: str,
        offer_data: Dict[str, Any]
    ) -> bool:
        """
        Add offer information to application.

        Args:
            app_id: Application ID
            offer_data: Offer details

        Returns:
            True if added, False if application not found
        """
        if app_id not in self.applications["applications"]:
            return False

        application = self.applications["applications"][app_id]
        application["offer"] = {
            "salary": offer_data.get("salary"),
            "equity": offer_data.get("equity"),
            "benefits": offer_data.get("benefits", []),
            "start_date": offer_data.get("start_date"),
            "deadline": offer_data.get("deadline"),
            "received_date": datetime.now().isoformat()
        }

        self.update_status(app_id, "offer_received", "Offer received")
        return True
