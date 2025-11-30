"""
Collaboration Bridge for Backend Trainer

Provides inter-agent communication protocols for working with
frontend agents and other specialized agents.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from datetime import datetime
from enum import Enum


class AgentType(Enum):
    BACKEND_TRAINER = "backend-trainer-cskill"
    FRONTEND_TRAINER = "frontend-trainer-cskill"
    UI_AESTHETIC = "ui-aesthetic-cskill"
    FULLSTACK_COORDINATOR = "fullstack-coordinator-cskill"
    SECURITY_AUDITOR = "security-auditor-cskill"
    PERFORMANCE_OPTIMIZER = "performance-optimizer-cskill"


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    SYNC = "sync"
    HANDOFF = "handoff"
    QUERY = "query"
    UPDATE = "update"


class SyncPointType(Enum):
    API_CONTRACT = "api_contract_validation"
    DATA_TYPES = "data_type_compatibility"
    AUTH_FLOW = "authentication_flow_alignment"
    ERROR_RESPONSES = "error_response_standardization"
    REALTIME_EVENTS = "realtime_event_sync"
    SCHEMA_CHANGES = "schema_change_notification"


@dataclass
class AgentMessage:
    """Message structure for inter-agent communication."""
    message_id: str
    message_type: MessageType
    from_agent: AgentType
    to_agent: AgentType
    timestamp: str
    payload: dict = field(default_factory=dict)
    requires_response: bool = False
    correlation_id: Optional[str] = None  # For request-response tracking


@dataclass
class SyncPoint:
    """Defines a synchronization point between agents."""
    sync_type: SyncPointType
    backend_provides: list[str]
    frontend_confirms: list[str]
    validation_rules: list[str] = field(default_factory=list)
    last_synced: Optional[str] = None
    status: str = "pending"  # pending, synced, conflict


@dataclass
class CollaborationSession:
    """Represents an active collaboration session between agents."""
    session_id: str
    participants: list[AgentType]
    created_at: str
    sync_points: list[SyncPoint] = field(default_factory=list)
    messages: list[AgentMessage] = field(default_factory=list)
    status: str = "active"  # active, paused, completed
    context: dict = field(default_factory=dict)


class CollaborationBridge:
    """
    Manages collaboration between backend trainer and other agents.

    This bridge enables:
    - Structured communication between agents
    - Synchronization of shared artifacts (API contracts, schemas)
    - Conflict detection and resolution
    - Session management for complex workflows
    """

    def __init__(self, agent_type: AgentType = AgentType.BACKEND_TRAINER):
        self.agent_type = agent_type
        self.sessions: dict[str, CollaborationSession] = {}
        self.message_handlers: dict[MessageType, list[Callable]] = {}
        self._message_counter = 0

    def create_session(
        self,
        participants: list[AgentType],
        context: Optional[dict] = None
    ) -> CollaborationSession:
        """Create a new collaboration session."""
        session_id = f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(self.sessions)}"

        # Ensure backend trainer is in participants
        if self.agent_type not in participants:
            participants.append(self.agent_type)

        session = CollaborationSession(
            session_id=session_id,
            participants=participants,
            created_at=datetime.utcnow().isoformat() + "Z",
            context=context or {}
        )

        # Initialize standard sync points
        session.sync_points = self._create_standard_sync_points()

        self.sessions[session_id] = session
        return session

    def _create_standard_sync_points(self) -> list[SyncPoint]:
        """Create standard synchronization points for frontend collaboration."""
        return [
            SyncPoint(
                sync_type=SyncPointType.API_CONTRACT,
                backend_provides=["endpoint_specs", "request_schemas", "response_schemas"],
                frontend_confirms=["consumption_compatibility", "type_bindings"],
                validation_rules=["All endpoints documented", "Request/response types match"]
            ),
            SyncPoint(
                sync_type=SyncPointType.DATA_TYPES,
                backend_provides=["type_definitions", "validation_rules", "nullable_fields"],
                frontend_confirms=["ui_binding_compatibility", "form_validation_rules"],
                validation_rules=["No type mismatches", "Nullable handling defined"]
            ),
            SyncPoint(
                sync_type=SyncPointType.AUTH_FLOW,
                backend_provides=["token_specs", "refresh_mechanism", "session_handling"],
                frontend_confirms=["client_implementation", "token_storage_strategy"],
                validation_rules=["Token lifecycle handled", "Refresh logic implemented"]
            ),
            SyncPoint(
                sync_type=SyncPointType.ERROR_RESPONSES,
                backend_provides=["error_codes", "error_schemas", "retry_guidance"],
                frontend_confirms=["error_ui_mapping", "user_messaging"],
                validation_rules=["All errors handled", "User-friendly messages defined"]
            ),
            SyncPoint(
                sync_type=SyncPointType.REALTIME_EVENTS,
                backend_provides=["event_definitions", "payload_schemas", "connection_specs"],
                frontend_confirms=["subscription_patterns", "reconnection_logic"],
                validation_rules=["Event handlers registered", "Connection recovery handled"]
            )
        ]

    def create_message(
        self,
        message_type: MessageType,
        to_agent: AgentType,
        payload: dict,
        requires_response: bool = False,
        correlation_id: Optional[str] = None
    ) -> AgentMessage:
        """Create a new message to send to another agent."""
        self._message_counter += 1
        message_id = f"msg_{self.agent_type.value}_{self._message_counter}"

        return AgentMessage(
            message_id=message_id,
            message_type=message_type,
            from_agent=self.agent_type,
            to_agent=to_agent,
            timestamp=datetime.utcnow().isoformat() + "Z",
            payload=payload,
            requires_response=requires_response,
            correlation_id=correlation_id
        )

    def send_handoff(
        self,
        session_id: str,
        to_agent: AgentType,
        handoff_data: dict
    ) -> AgentMessage:
        """Send a handoff package to another agent."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        message = self.create_message(
            message_type=MessageType.HANDOFF,
            to_agent=to_agent,
            payload={
                "handoff_type": "full",
                "data": handoff_data,
                "session_id": session_id
            }
        )

        self.sessions[session_id].messages.append(message)
        return message

    def request_sync(
        self,
        session_id: str,
        sync_type: SyncPointType,
        to_agent: AgentType
    ) -> AgentMessage:
        """Request synchronization on a specific sync point."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Find the sync point
        sync_point = next(
            (sp for sp in session.sync_points if sp.sync_type == sync_type),
            None
        )

        if not sync_point:
            raise ValueError(f"Sync point {sync_type} not found in session")

        message = self.create_message(
            message_type=MessageType.SYNC,
            to_agent=to_agent,
            payload={
                "sync_type": sync_type.value,
                "backend_provides": sync_point.backend_provides,
                "validation_rules": sync_point.validation_rules,
                "session_id": session_id
            },
            requires_response=True
        )

        session.messages.append(message)
        return message

    def confirm_sync(
        self,
        session_id: str,
        sync_type: SyncPointType,
        confirmation_data: dict
    ) -> None:
        """Confirm synchronization after receiving response from other agent."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Find and update the sync point
        for sync_point in session.sync_points:
            if sync_point.sync_type == sync_type:
                sync_point.last_synced = datetime.utcnow().isoformat() + "Z"
                sync_point.status = "synced"
                break

    def notify_change(
        self,
        session_id: str,
        change_type: str,
        affected_items: list[str],
        to_agents: Optional[list[AgentType]] = None
    ) -> list[AgentMessage]:
        """Notify other agents of backend changes."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        messages = []

        # Default to all participants except self
        if to_agents is None:
            to_agents = [p for p in session.participants if p != self.agent_type]

        for agent in to_agents:
            message = self.create_message(
                message_type=MessageType.NOTIFICATION,
                to_agent=agent,
                payload={
                    "change_type": change_type,
                    "affected_items": affected_items,
                    "session_id": session_id,
                    "action_required": True
                }
            )
            messages.append(message)
            session.messages.append(message)

        return messages

    def query_frontend(
        self,
        session_id: str,
        query_type: str,
        query_data: dict,
        to_agent: AgentType = AgentType.FRONTEND_TRAINER
    ) -> AgentMessage:
        """Query frontend agent for information."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        message = self.create_message(
            message_type=MessageType.QUERY,
            to_agent=to_agent,
            payload={
                "query_type": query_type,
                "query_data": query_data,
                "session_id": session_id
            },
            requires_response=True
        )

        self.sessions[session_id].messages.append(message)
        return message

    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable[[AgentMessage], Any]
    ) -> None:
        """Register a handler for incoming messages of a specific type."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    def handle_incoming_message(self, message: AgentMessage) -> Optional[Any]:
        """Process an incoming message from another agent."""
        handlers = self.message_handlers.get(message.message_type, [])

        results = []
        for handler in handlers:
            result = handler(message)
            results.append(result)

        return results if results else None

    def get_session_status(self, session_id: str) -> dict:
        """Get the current status of a collaboration session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        return {
            "session_id": session_id,
            "status": session.status,
            "participants": [p.value for p in session.participants],
            "created_at": session.created_at,
            "message_count": len(session.messages),
            "sync_points": [
                {
                    "type": sp.sync_type.value,
                    "status": sp.status,
                    "last_synced": sp.last_synced
                }
                for sp in session.sync_points
            ]
        }

    def complete_session(self, session_id: str) -> dict:
        """Mark a collaboration session as complete."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        session.status = "completed"

        return {
            "session_id": session_id,
            "status": "completed",
            "total_messages": len(session.messages),
            "sync_points_completed": sum(
                1 for sp in session.sync_points if sp.status == "synced"
            ),
            "total_sync_points": len(session.sync_points)
        }

    def export_session(self, session_id: str) -> dict:
        """Export session data for archival or analysis."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        return {
            "session_id": session.session_id,
            "participants": [p.value for p in session.participants],
            "created_at": session.created_at,
            "status": session.status,
            "context": session.context,
            "sync_points": [
                {
                    "type": sp.sync_type.value,
                    "backend_provides": sp.backend_provides,
                    "frontend_confirms": sp.frontend_confirms,
                    "status": sp.status,
                    "last_synced": sp.last_synced
                }
                for sp in session.sync_points
            ],
            "messages": [
                {
                    "id": m.message_id,
                    "type": m.message_type.value,
                    "from": m.from_agent.value,
                    "to": m.to_agent.value,
                    "timestamp": m.timestamp,
                    "payload_keys": list(m.payload.keys())
                }
                for m in session.messages
            ]
        }


class FrontendCollaborator:
    """
    Specialized collaborator for working with frontend agents.

    Provides higher-level methods for common collaboration patterns.
    """

    def __init__(self):
        self.bridge = CollaborationBridge(AgentType.BACKEND_TRAINER)
        self.current_session: Optional[CollaborationSession] = None

    def start_collaboration(self, context: Optional[dict] = None) -> str:
        """Start a new collaboration session with frontend agent."""
        session = self.bridge.create_session(
            participants=[AgentType.FRONTEND_TRAINER],
            context=context
        )
        self.current_session = session
        return session.session_id

    def send_api_contract(self, api_contract: dict) -> AgentMessage:
        """Send API contract to frontend for validation."""
        if not self.current_session:
            raise RuntimeError("No active collaboration session")

        return self.bridge.send_handoff(
            session_id=self.current_session.session_id,
            to_agent=AgentType.FRONTEND_TRAINER,
            handoff_data={
                "type": "api_contract",
                "contract": api_contract
            }
        )

    def notify_schema_change(self, changes: list[dict]) -> list[AgentMessage]:
        """Notify frontend of database schema changes."""
        if not self.current_session:
            raise RuntimeError("No active collaboration session")

        return self.bridge.notify_change(
            session_id=self.current_session.session_id,
            change_type="schema_change",
            affected_items=[c.get("table", "unknown") for c in changes]
        )

    def request_ui_requirements(self, for_feature: str) -> AgentMessage:
        """Request UI requirements for a specific feature."""
        if not self.current_session:
            raise RuntimeError("No active collaboration session")

        return self.bridge.query_frontend(
            session_id=self.current_session.session_id,
            query_type="ui_requirements",
            query_data={"feature": for_feature}
        )

    def sync_data_types(self) -> AgentMessage:
        """Synchronize data type definitions with frontend."""
        if not self.current_session:
            raise RuntimeError("No active collaboration session")

        return self.bridge.request_sync(
            session_id=self.current_session.session_id,
            sync_type=SyncPointType.DATA_TYPES,
            to_agent=AgentType.FRONTEND_TRAINER
        )

    def complete_collaboration(self) -> dict:
        """Complete the current collaboration session."""
        if not self.current_session:
            raise RuntimeError("No active collaboration session")

        result = self.bridge.complete_session(self.current_session.session_id)
        self.current_session = None
        return result

    def get_status(self) -> dict:
        """Get status of current collaboration."""
        if not self.current_session:
            return {"status": "no_active_session"}

        return self.bridge.get_session_status(self.current_session.session_id)
