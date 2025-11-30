"""
Session Manager - Manages training sessions and persistence.

This module handles:
- Session creation and ID generation
- Session state persistence
- Session recovery and resumption
- Applied recommendations tracking
"""

import json
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SessionManager:
    """
    Manages training sessions for the Personal Trainer Agent.

    Handles persistence of session state to enable:
    - Resuming interrupted sessions
    - Tracking long-running training
    - Auditing changes and recommendations

    Usage:
        manager = SessionManager(storage_path)

        # Generate session ID
        session_id = manager.generate_session_id()

        # Save session
        manager.save_session(session)

        # Load session
        session_data = manager.load_session(session_id)

        # List all sessions
        all_sessions = manager.list_sessions()
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the session manager.

        Args:
            storage_dir: Directory for storing session data
        """
        self.storage_dir = storage_dir or Path.home() / ".personal_trainer_agent" / "sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._recommendations_dir = self.storage_dir / "recommendations"
        self._recommendations_dir.mkdir(exist_ok=True)

    def generate_session_id(self) -> str:
        """
        Generate a unique session ID.

        Returns:
            Unique session identifier
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique = uuid.uuid4().hex[:8]
        return f"session_{timestamp}_{unique}"

    def save_session(self, session: Any) -> bool:
        """
        Save session state to storage.

        Args:
            session: Session object to save

        Returns:
            True if saved successfully
        """
        try:
            session_data = self._serialize_session(session)
            session_file = self.storage_dir / f"{session.session_id}.json"

            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)

            return True

        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def _serialize_session(self, session: Any) -> Dict[str, Any]:
        """Serialize session object to dictionary."""
        if hasattr(session, '__dataclass_fields__'):
            data = {}
            for field_name in session.__dataclass_fields__:
                value = getattr(session, field_name)
                if hasattr(value, '__dataclass_fields__'):
                    data[field_name] = asdict(value)
                elif hasattr(value, 'value'):  # Enum
                    data[field_name] = value.value
                else:
                    data[field_name] = value
            return data
        return dict(session) if isinstance(session, dict) else {"data": str(session)}

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session from storage.

        Args:
            session_id: ID of session to load

        Returns:
            Session data dictionary or None if not found
        """
        session_file = self.storage_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    def load_all_active(self) -> List[Dict[str, Any]]:
        """
        Load all active sessions.

        Returns:
            List of active session data dictionaries
        """
        active_sessions = []

        for session_file in self.storage_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    if data.get("status") == "active":
                        active_sessions.append(data)
            except Exception as e:
                print(f"Error loading {session_file}: {e}")
                continue

        return active_sessions

    def list_sessions(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List all sessions with optional filtering.

        Args:
            status: Filter by status (active, completed)
            limit: Maximum number of sessions to return

        Returns:
            List of session summaries
        """
        sessions = []

        for session_file in sorted(
            self.storage_dir.glob("session_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit * 2]:  # Load extra in case filtering reduces count

            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)

                    if status and data.get("status") != status:
                        continue

                    sessions.append({
                        "session_id": data.get("session_id"),
                        "agent_name": data.get("agent_profile", {}).get("name", "Unknown"),
                        "status": data.get("status", "unknown"),
                        "started_at": data.get("started_at"),
                        "iterations": data.get("iterations_completed", 0),
                        "mode": data.get("mode")
                    })

                    if len(sessions) >= limit:
                        break

            except Exception:
                continue

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and its artifacts.

        Args:
            session_id: ID of session to delete

        Returns:
            True if deleted successfully
        """
        session_file = self.storage_dir / f"{session_id}.json"

        if session_file.exists():
            try:
                session_file.unlink()

                # Also delete recommendations file if exists
                rec_file = self._recommendations_dir / f"{session_id}_recommendations.json"
                if rec_file.exists():
                    rec_file.unlink()

                return True
            except Exception as e:
                print(f"Error deleting session: {e}")
                return False

        return False

    def record_applied_recommendation(
        self,
        session_id: str,
        recommendation: Dict[str, Any],
        result: str = "applied"
    ) -> None:
        """
        Record that a recommendation was applied.

        Args:
            session_id: Session ID
            recommendation: The recommendation that was applied
            result: Result of applying (applied, skipped, failed)
        """
        rec_file = self._recommendations_dir / f"{session_id}_recommendations.json"

        # Load existing recommendations
        existing = []
        if rec_file.exists():
            try:
                with open(rec_file, 'r') as f:
                    existing = json.load(f)
            except Exception:
                existing = []

        # Add new recommendation record
        existing.append({
            "recommendation": recommendation,
            "result": result,
            "applied_at": datetime.now().isoformat()
        })

        # Save
        with open(rec_file, 'w') as f:
            json.dump(existing, f, indent=2, default=str)

    def get_applied_recommendations(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all applied recommendations for a session.

        Args:
            session_id: Session ID

        Returns:
            List of applied recommendation records
        """
        rec_file = self._recommendations_dir / f"{session_id}_recommendations.json"

        if not rec_file.exists():
            return []

        try:
            with open(rec_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def export_session(
        self,
        session_id: str,
        export_path: Path
    ) -> bool:
        """
        Export session data for sharing or backup.

        Args:
            session_id: Session ID to export
            export_path: Path to export to

        Returns:
            True if exported successfully
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return False

        recommendations = self.get_applied_recommendations(session_id)

        export_data = {
            "session": session_data,
            "recommendations": recommendations,
            "exported_at": datetime.now().isoformat()
        }

        try:
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting session: {e}")
            return False

    def import_session(self, import_path: Path) -> Optional[str]:
        """
        Import a session from exported data.

        Args:
            import_path: Path to import from

        Returns:
            Session ID of imported session, or None if failed
        """
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)

            session_data = import_data.get("session", {})
            recommendations = import_data.get("recommendations", [])

            # Generate new session ID
            old_id = session_data.get("session_id", "")
            new_id = self.generate_session_id()
            session_data["session_id"] = new_id
            session_data["imported_from"] = old_id
            session_data["imported_at"] = datetime.now().isoformat()

            # Save session
            session_file = self.storage_dir / f"{new_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)

            # Save recommendations
            if recommendations:
                rec_file = self._recommendations_dir / f"{new_id}_recommendations.json"
                with open(rec_file, 'w') as f:
                    json.dump(recommendations, f, indent=2, default=str)

            return new_id

        except Exception as e:
            print(f"Error importing session: {e}")
            return None

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get overall statistics about all sessions.

        Returns:
            Statistics dictionary
        """
        all_sessions = self.list_sessions(limit=1000)

        active = sum(1 for s in all_sessions if s.get("status") == "active")
        completed = sum(1 for s in all_sessions if s.get("status") == "completed")
        total_iterations = sum(s.get("iterations", 0) for s in all_sessions)

        return {
            "total_sessions": len(all_sessions),
            "active_sessions": active,
            "completed_sessions": completed,
            "total_iterations": total_iterations,
            "average_iterations": total_iterations / len(all_sessions) if all_sessions else 0
        }
