"""
Frontend Handoff Protocol for Backend Trainer

Generates comprehensive handoff packages for frontend agents/developers
including API contracts, TypeScript interfaces, and documentation.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class Endpoint:
    path: str
    method: str
    description: str = ""
    request_schema: dict = field(default_factory=dict)
    response_schema: dict = field(default_factory=dict)
    error_responses: dict = field(default_factory=dict)
    authentication: str = "none"
    rate_limit: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class DataSchema:
    name: str
    fields: dict = field(default_factory=dict)
    relationships: list[str] = field(default_factory=list)
    validation_rules: dict = field(default_factory=dict)


@dataclass
class AuthenticationFlow:
    auth_type: str  # jwt, oauth, session, api_key
    login_endpoint: str = ""
    refresh_endpoint: str = ""
    logout_endpoint: str = ""
    token_location: str = "header"  # header, cookie, query
    token_lifetime: str = ""
    refresh_lifetime: str = ""
    additional_notes: list[str] = field(default_factory=list)


@dataclass
class WebSocketEvent:
    name: str
    direction: str  # server_to_client, client_to_server, bidirectional
    payload_schema: dict = field(default_factory=dict)
    description: str = ""


@dataclass
class ErrorCode:
    code: str
    http_status: int
    message: str
    has_details: bool = False
    handling_suggestion: str = ""


@dataclass
class BackendHealthReport:
    architecture_score: int
    security_score: int
    performance_score: int
    api_score: int
    database_score: int
    issues_to_resolve: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class HandoffPackage:
    handoff_version: str = "1.0"
    generated_by: str = "backend-trainer-cskill"
    generated_at: str = ""
    target_agent: str = "frontend-trainer-cskill"

    # API Contracts
    endpoints: list[Endpoint] = field(default_factory=list)
    openapi_spec: dict = field(default_factory=dict)

    # Data Schemas
    data_schemas: list[DataSchema] = field(default_factory=list)
    typescript_interfaces: str = ""

    # Authentication
    authentication: Optional[AuthenticationFlow] = None

    # Real-time
    websocket_events: list[WebSocketEvent] = field(default_factory=list)
    sse_streams: list[dict] = field(default_factory=list)

    # Error Handling
    error_codes: list[ErrorCode] = field(default_factory=list)

    # Backend Health
    backend_health: Optional[BackendHealthReport] = None

    # Compatibility Notes
    compatibility_notes: list[str] = field(default_factory=list)
    pending_backend_work: list[str] = field(default_factory=list)
    frontend_considerations: list[str] = field(default_factory=list)


class FrontendHandoffGenerator:
    """Generates handoff packages for frontend integration."""

    def __init__(self):
        self.package = HandoffPackage(
            generated_at=datetime.utcnow().isoformat() + "Z"
        )

    def add_endpoint(self, endpoint: Endpoint) -> None:
        """Add an endpoint to the handoff package."""
        self.package.endpoints.append(endpoint)

    def add_endpoints_from_analysis(self, api_analysis: dict) -> None:
        """Add endpoints from API analyzer results."""
        if "result" not in api_analysis:
            return

        for ep in api_analysis["result"].endpoints:
            endpoint = Endpoint(
                path=ep.path,
                method=ep.method,
                authentication="required" if ep.has_authentication else "none"
            )
            self.package.endpoints.append(endpoint)

    def add_data_schema(self, schema: DataSchema) -> None:
        """Add a data schema to the handoff package."""
        self.package.data_schemas.append(schema)

    def set_authentication(self, auth: AuthenticationFlow) -> None:
        """Set authentication flow details."""
        self.package.authentication = auth

    def add_websocket_event(self, event: WebSocketEvent) -> None:
        """Add a WebSocket event definition."""
        self.package.websocket_events.append(event)

    def add_error_code(self, error: ErrorCode) -> None:
        """Add an error code definition."""
        self.package.error_codes.append(error)

    def set_backend_health(self, health: BackendHealthReport) -> None:
        """Set backend health report."""
        self.package.backend_health = health

    def set_health_from_analysis(
        self,
        architecture_result: dict,
        security_result: dict,
        performance_result: dict,
        api_result: dict,
        database_result: dict
    ) -> None:
        """Set backend health from analyzer results."""
        issues: list[dict] = []
        recommendations: list[str] = []

        # Collect issues from each analyzer
        if "result" in architecture_result:
            for rec in architecture_result["result"].recommendations:
                issues.append({
                    "category": "architecture",
                    "severity": rec.severity,
                    "description": rec.description
                })

        if "result" in security_result:
            for issue in security_result["result"].issues:
                if issue.severity.value in ["critical", "high"]:
                    issues.append({
                        "category": "security",
                        "severity": issue.severity.value,
                        "description": issue.description
                    })

        self.package.backend_health = BackendHealthReport(
            architecture_score=architecture_result.get("summary", {}).get("overall_score", 0),
            security_score=security_result.get("summary", {}).get("overall_score", 0),
            performance_score=performance_result.get("summary", {}).get("overall_score", 0),
            api_score=api_result.get("summary", {}).get("overall_score", 0),
            database_score=database_result.get("summary", {}).get("overall_score", 0),
            issues_to_resolve=issues[:10],  # Top 10 issues
            recommendations=recommendations
        )

    def generate_openapi_spec(self) -> dict[str, Any]:
        """Generate OpenAPI 3.0 specification from endpoints."""
        spec: dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": "Backend API",
                "version": "1.0.0",
                "description": "API documentation for frontend integration"
            },
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {}
            }
        }

        # Add authentication scheme if defined
        if self.package.authentication:
            if self.package.authentication.auth_type == "jwt":
                spec["components"]["securitySchemes"]["bearerAuth"] = {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            elif self.package.authentication.auth_type == "api_key":
                spec["components"]["securitySchemes"]["apiKey"] = {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }

        # Add endpoints
        for endpoint in self.package.endpoints:
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}

            method = endpoint.method.lower()
            spec["paths"][endpoint.path][method] = {
                "summary": endpoint.description or f"{endpoint.method} {endpoint.path}",
                "tags": endpoint.tags or ["default"],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema or {"type": "object"}
                            }
                        }
                    }
                }
            }

            # Add request body for POST/PUT/PATCH
            if method in ["post", "put", "patch"] and endpoint.request_schema:
                spec["paths"][endpoint.path][method]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }

            # Add error responses
            for status, error in endpoint.error_responses.items():
                spec["paths"][endpoint.path][method]["responses"][str(status)] = {
                    "description": error
                }

            # Add security if authenticated
            if endpoint.authentication != "none":
                spec["paths"][endpoint.path][method]["security"] = [
                    {"bearerAuth": []}
                ]

        # Add schemas from data schemas
        for schema in self.package.data_schemas:
            spec["components"]["schemas"][schema.name] = {
                "type": "object",
                "properties": schema.fields
            }

        self.package.openapi_spec = spec
        return spec

    def generate_typescript_interfaces(self) -> str:
        """Generate TypeScript interfaces from data schemas."""
        lines = [
            "// Auto-generated TypeScript interfaces",
            "// Generated by backend-trainer-cskill",
            f"// Generated at: {self.package.generated_at}",
            ""
        ]

        for schema in self.package.data_schemas:
            lines.append(f"export interface {schema.name} {{")
            for field_name, field_def in schema.fields.items():
                ts_type = self._json_type_to_typescript(field_def)
                lines.append(f"  {field_name}: {ts_type};")
            lines.append("}")
            lines.append("")

        # Generate error response type
        if self.package.error_codes:
            lines.append("export interface ApiError {")
            lines.append("  code: string;")
            lines.append("  message: string;")
            lines.append("  details?: Record<string, unknown>;")
            lines.append("  timestamp: string;")
            lines.append("}")
            lines.append("")

            # Generate error code enum
            lines.append("export enum ErrorCodes {")
            for error in self.package.error_codes:
                lines.append(f"  {error.code} = '{error.code}',")
            lines.append("}")
            lines.append("")

        # Generate WebSocket event types
        if self.package.websocket_events:
            lines.append("// WebSocket Events")
            for event in self.package.websocket_events:
                interface_name = self._to_pascal_case(event.name) + "Event"
                lines.append(f"export interface {interface_name} {{")
                lines.append(f"  type: '{event.name}';")
                lines.append("  payload: {")
                for field_name, field_def in event.payload_schema.items():
                    ts_type = self._json_type_to_typescript(field_def)
                    lines.append(f"    {field_name}: {ts_type};")
                lines.append("  };")
                lines.append("}")
                lines.append("")

        self.package.typescript_interfaces = "\n".join(lines)
        return self.package.typescript_interfaces

    def _json_type_to_typescript(self, json_type: Any) -> str:
        """Convert JSON schema type to TypeScript type."""
        if isinstance(json_type, dict):
            if "type" in json_type:
                base_type = json_type["type"]
                if base_type == "string":
                    return "string"
                elif base_type == "number" or base_type == "integer":
                    return "number"
                elif base_type == "boolean":
                    return "boolean"
                elif base_type == "array":
                    items = json_type.get("items", {})
                    item_type = self._json_type_to_typescript(items)
                    return f"{item_type}[]"
                elif base_type == "object":
                    return "Record<string, unknown>"
            elif "$ref" in json_type:
                ref = json_type["$ref"].split("/")[-1]
                return ref
        elif isinstance(json_type, str):
            type_map = {
                "string": "string",
                "number": "number",
                "integer": "number",
                "boolean": "boolean",
                "object": "Record<string, unknown>",
                "array": "unknown[]"
            }
            return type_map.get(json_type, "unknown")

        return "unknown"

    def _to_pascal_case(self, s: str) -> str:
        """Convert string to PascalCase."""
        parts = s.replace("-", "_").replace(".", "_").split("_")
        return "".join(part.capitalize() for part in parts)

    def add_compatibility_note(self, note: str) -> None:
        """Add a compatibility note for frontend."""
        self.package.compatibility_notes.append(note)

    def add_pending_work(self, work: str) -> None:
        """Add pending backend work item."""
        self.package.pending_backend_work.append(work)

    def add_frontend_consideration(self, consideration: str) -> None:
        """Add frontend consideration."""
        self.package.frontend_considerations.append(consideration)

    def generate_standard_error_codes(self) -> None:
        """Generate standard error codes."""
        standard_errors = [
            ErrorCode("AUTH_001", 401, "Invalid credentials", handling_suggestion="Redirect to login"),
            ErrorCode("AUTH_002", 401, "Token expired", handling_suggestion="Attempt token refresh"),
            ErrorCode("AUTH_003", 403, "Insufficient permissions", handling_suggestion="Show access denied message"),
            ErrorCode("VAL_001", 400, "Validation failed", True, "Display field-specific errors"),
            ErrorCode("VAL_002", 400, "Invalid request format", handling_suggestion="Check request structure"),
            ErrorCode("RES_001", 404, "Resource not found", handling_suggestion="Show not found page or message"),
            ErrorCode("RES_002", 409, "Resource conflict", handling_suggestion="Prompt user to resolve conflict"),
            ErrorCode("RATE_001", 429, "Rate limit exceeded", handling_suggestion="Implement exponential backoff"),
            ErrorCode("SRV_001", 500, "Internal server error", handling_suggestion="Show generic error, log for debugging"),
            ErrorCode("SRV_002", 503, "Service unavailable", handling_suggestion="Show maintenance message"),
        ]

        for error in standard_errors:
            self.package.error_codes.append(error)

    def generate_package(self) -> dict:
        """Generate the complete handoff package."""
        # Generate OpenAPI spec
        self.generate_openapi_spec()

        # Generate TypeScript interfaces
        self.generate_typescript_interfaces()

        # Convert to dictionary
        return self._to_dict(self.package)

    def _to_dict(self, obj: Any) -> Any:
        """Convert dataclass to dictionary recursively."""
        if hasattr(obj, "__dataclass_fields__"):
            return {k: self._to_dict(v) for k, v in asdict(obj).items() if v is not None}
        elif isinstance(obj, list):
            return [self._to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._to_dict(v) for k, v in obj.items()}
        else:
            return obj

    def export_to_json(self, output_path: str) -> None:
        """Export handoff package to JSON file."""
        package_dict = self.generate_package()
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(package_dict, f, indent=2)

    def export_typescript_file(self, output_path: str) -> None:
        """Export TypeScript interfaces to file."""
        self.generate_typescript_interfaces()
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.package.typescript_interfaces)

    def generate_handoff_summary(self) -> str:
        """Generate a human-readable handoff summary."""
        lines = [
            "# Frontend Handoff Summary",
            "",
            f"Generated: {self.package.generated_at}",
            f"Target: {self.package.target_agent}",
            "",
            "## API Overview",
            f"- Total Endpoints: {len(self.package.endpoints)}",
            f"- Data Schemas: {len(self.package.data_schemas)}",
            f"- WebSocket Events: {len(self.package.websocket_events)}",
            f"- Error Codes: {len(self.package.error_codes)}",
            "",
        ]

        # Authentication
        if self.package.authentication:
            lines.extend([
                "## Authentication",
                f"- Type: {self.package.authentication.auth_type}",
                f"- Login: {self.package.authentication.login_endpoint}",
                f"- Token Location: {self.package.authentication.token_location}",
                f"- Token Lifetime: {self.package.authentication.token_lifetime}",
                ""
            ])

        # Endpoints by method
        methods: dict[str, list] = {}
        for ep in self.package.endpoints:
            if ep.method not in methods:
                methods[ep.method] = []
            methods[ep.method].append(ep.path)

        lines.append("## Endpoints by Method")
        for method, paths in methods.items():
            lines.append(f"\n### {method}")
            for path in paths:
                lines.append(f"- {path}")

        # Backend Health
        if self.package.backend_health:
            lines.extend([
                "",
                "## Backend Health",
                f"- Architecture: {self.package.backend_health.architecture_score}/100",
                f"- Security: {self.package.backend_health.security_score}/100",
                f"- Performance: {self.package.backend_health.performance_score}/100",
                f"- API Design: {self.package.backend_health.api_score}/100",
                f"- Database: {self.package.backend_health.database_score}/100",
            ])

        # Pending Work
        if self.package.pending_backend_work:
            lines.append("\n## Pending Backend Work")
            for work in self.package.pending_backend_work:
                lines.append(f"- {work}")

        # Frontend Considerations
        if self.package.frontend_considerations:
            lines.append("\n## Frontend Considerations")
            for consideration in self.package.frontend_considerations:
                lines.append(f"- {consideration}")

        return "\n".join(lines)


def create_handoff_package(
    api_analysis: Optional[dict] = None,
    architecture_analysis: Optional[dict] = None,
    security_analysis: Optional[dict] = None,
    performance_analysis: Optional[dict] = None,
    database_analysis: Optional[dict] = None
) -> FrontendHandoffGenerator:
    """Create a handoff package from analysis results."""
    generator = FrontendHandoffGenerator()

    # Add endpoints from API analysis
    if api_analysis:
        generator.add_endpoints_from_analysis(api_analysis)

    # Set health from all analyses
    if all([architecture_analysis, security_analysis, performance_analysis,
            api_analysis, database_analysis]):
        generator.set_health_from_analysis(
            architecture_analysis,
            security_analysis,
            performance_analysis,
            api_analysis,
            database_analysis
        )

    # Generate standard error codes
    generator.generate_standard_error_codes()

    # Add common frontend considerations
    generator.add_frontend_consideration("Handle token refresh on 401 responses")
    generator.add_frontend_consideration("Implement optimistic updates for better UX")
    generator.add_frontend_consideration("Cache GET responses where appropriate")

    return generator
