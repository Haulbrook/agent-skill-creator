"""
Backend Trainer Protocols

Inter-agent communication and collaboration protocols:
- Frontend handoff generation
- Collaboration bridge for multi-agent workflows
"""

from .frontend_handoff import (
    FrontendHandoffGenerator,
    HandoffPackage,
    Endpoint,
    DataSchema,
    AuthenticationFlow,
    WebSocketEvent,
    ErrorCode,
    BackendHealthReport,
    create_handoff_package
)

from .collaboration_bridge import (
    CollaborationBridge,
    FrontendCollaborator,
    AgentType,
    MessageType,
    SyncPointType,
    AgentMessage,
    SyncPoint,
    CollaborationSession
)

__all__ = [
    # Handoff
    "FrontendHandoffGenerator",
    "HandoffPackage",
    "Endpoint",
    "DataSchema",
    "AuthenticationFlow",
    "WebSocketEvent",
    "ErrorCode",
    "BackendHealthReport",
    "create_handoff_package",
    # Collaboration
    "CollaborationBridge",
    "FrontendCollaborator",
    "AgentType",
    "MessageType",
    "SyncPointType",
    "AgentMessage",
    "SyncPoint",
    "CollaborationSession",
]
