"""
API Analyzer for Backend Trainer

Evaluates API design quality, RESTful compliance, GraphQL schema design,
and WebSocket implementations.
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum


class APIType(Enum):
    REST = "rest"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


@dataclass
class EndpointIssue:
    severity: str
    category: str
    description: str
    endpoint: str
    method: str = ""
    line_number: Optional[int] = None
    recommendation: str = ""


@dataclass
class EndpointAnalysis:
    path: str
    method: str
    handler_file: str
    handler_line: Optional[int] = None
    has_validation: bool = False
    has_authentication: bool = False
    has_documentation: bool = False
    response_type: str = "unknown"
    issues: list[EndpointIssue] = field(default_factory=list)
    score: int = 100


@dataclass
class APIAnalysisResult:
    api_type: APIType
    overall_score: int
    endpoints: list[EndpointAnalysis] = field(default_factory=list)
    issues: list[EndpointIssue] = field(default_factory=list)
    recommendations: list[EndpointIssue] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


class APIAnalyzer:
    """Analyzes API design quality and compliance."""

    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        "fastapi": [r"from\s+fastapi", r"@app\.(get|post|put|delete|patch)", r"FastAPI\(\)"],
        "flask": [r"from\s+flask", r"@app\.route", r"Flask\(__name__\)"],
        "django": [r"from\s+django", r"path\(", r"urlpatterns"],
        "express": [r"require\(['\"]express['\"]", r"app\.(get|post|put|delete)", r"Router\(\)"],
        "nestjs": [r"@Controller", r"@Get\(", r"@Post\(", r"@Injectable"],
    }

    # REST best practices patterns
    REST_PATTERNS = {
        "resource_naming": {
            "good": [r"/api/v\d+/\w+", r"/\w+s(/\{?\w+\}?)?$"],
            "bad": [r"/get\w+", r"/create\w+", r"/delete\w+", r"/update\w+"]
        },
        "versioning": [r"/v\d+/", r"/api/v\d+"],
        "pagination": [r"limit", r"offset", r"page", r"cursor", r"skip", r"take"]
    }

    # Scoring weights
    SCORING_WEIGHTS = {
        "resource_naming": 0.20,
        "http_methods": 0.15,
        "status_codes": 0.15,
        "validation": 0.20,
        "error_handling": 0.15,
        "documentation": 0.15
    }

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.analysis_result = None
        self.detected_framework = None

    def analyze(self, codebase_path: str) -> APIAnalysisResult:
        """Perform complete API analysis."""
        path = Path(codebase_path)
        if not path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")

        # Initialize result
        self.analysis_result = APIAnalysisResult(
            api_type=APIType.UNKNOWN,
            overall_score=0
        )

        # Collect source files
        python_files = list(path.rglob("*.py"))
        js_files = list(path.rglob("*.js")) + list(path.rglob("*.ts"))
        all_files = python_files + js_files

        # Detect framework and API type
        self._detect_framework(all_files)
        self._detect_api_type(all_files)

        # Extract and analyze endpoints
        self._extract_endpoints(all_files)

        # Analyze REST compliance
        if self.analysis_result.api_type in [APIType.REST, APIType.MIXED]:
            self._analyze_rest_compliance()

        # Analyze validation
        self._analyze_validation()

        # Analyze error handling
        self._analyze_error_handling(all_files)

        # Analyze documentation
        self._analyze_documentation(all_files)

        # Calculate scores
        self._calculate_scores()

        # Generate recommendations
        self._generate_recommendations()

        return self.analysis_result

    def _detect_framework(self, files: list[Path]) -> None:
        """Detect which web framework is being used."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                if any(re.search(p, content) for p in patterns):
                    self.detected_framework = framework
                    return

    def _detect_api_type(self, files: list[Path]) -> None:
        """Detect API type (REST, GraphQL, WebSocket, etc.)."""
        has_rest = False
        has_graphql = False
        has_websocket = False

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            # Check for REST
            rest_patterns = [r"@(get|post|put|delete|patch)", r"\.route\(", r"path\(.*,"]
            if any(re.search(p, content, re.IGNORECASE) for p in rest_patterns):
                has_rest = True

            # Check for GraphQL
            graphql_patterns = [r"graphql", r"@Query", r"@Mutation", r"type Query", r"schema \{"]
            if any(re.search(p, content, re.IGNORECASE) for p in graphql_patterns):
                has_graphql = True

            # Check for WebSocket
            ws_patterns = [r"websocket", r"@WebSocket", r"socketio", r"ws://"]
            if any(re.search(p, content, re.IGNORECASE) for p in ws_patterns):
                has_websocket = True

        # Determine API type
        if has_rest and has_graphql:
            self.analysis_result.api_type = APIType.MIXED
        elif has_graphql:
            self.analysis_result.api_type = APIType.GRAPHQL
        elif has_websocket and not has_rest:
            self.analysis_result.api_type = APIType.WEBSOCKET
        elif has_rest:
            self.analysis_result.api_type = APIType.REST
        else:
            self.analysis_result.api_type = APIType.UNKNOWN

    def _extract_endpoints(self, files: list[Path]) -> None:
        """Extract API endpoints from source files."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            # Extract based on detected framework
            if self.detected_framework == "fastapi":
                self._extract_fastapi_endpoints(content, file_path)
            elif self.detected_framework == "flask":
                self._extract_flask_endpoints(content, file_path)
            elif self.detected_framework == "django":
                self._extract_django_endpoints(content, file_path)
            elif self.detected_framework in ["express", "nestjs"]:
                self._extract_js_endpoints(content, file_path)
            else:
                # Generic extraction
                self._extract_generic_endpoints(content, file_path)

    def _extract_fastapi_endpoints(self, content: str, file_path: Path) -> None:
        """Extract FastAPI endpoints."""
        pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(pattern, content, re.IGNORECASE):
            method = match.group(1).upper()
            path = match.group(2)
            line_num = content[:match.start()].count('\n') + 1

            # Check for validation (Pydantic models)
            has_validation = bool(re.search(r':\s*\w+Model\b|:\s*BaseModel\b', content))

            # Check for authentication
            has_auth = bool(re.search(r'Depends\s*\(\s*\w*(auth|token|jwt)', content, re.IGNORECASE))

            endpoint = EndpointAnalysis(
                path=path,
                method=method,
                handler_file=str(file_path),
                handler_line=line_num,
                has_validation=has_validation,
                has_authentication=has_auth
            )
            self.analysis_result.endpoints.append(endpoint)

    def _extract_flask_endpoints(self, content: str, file_path: Path) -> None:
        """Extract Flask endpoints."""
        pattern = r'@\w+\.route\s*\(\s*["\']([^"\']+)["\'](?:.*methods\s*=\s*\[([^\]]+)\])?'
        for match in re.finditer(pattern, content, re.IGNORECASE):
            path = match.group(1)
            methods = match.group(2) if match.group(2) else "GET"
            line_num = content[:match.start()].count('\n') + 1

            # Parse methods
            if isinstance(methods, str):
                methods_list = re.findall(r'["\'](\w+)["\']', methods)
                if not methods_list:
                    methods_list = ["GET"]
            else:
                methods_list = ["GET"]

            for method in methods_list:
                endpoint = EndpointAnalysis(
                    path=path,
                    method=method.upper(),
                    handler_file=str(file_path),
                    handler_line=line_num
                )
                self.analysis_result.endpoints.append(endpoint)

    def _extract_django_endpoints(self, content: str, file_path: Path) -> None:
        """Extract Django URL patterns."""
        pattern = r'path\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(pattern, content):
            path = match.group(1)
            line_num = content[:match.start()].count('\n') + 1

            endpoint = EndpointAnalysis(
                path=f"/{path}",
                method="ANY",  # Django uses class-based views
                handler_file=str(file_path),
                handler_line=line_num
            )
            self.analysis_result.endpoints.append(endpoint)

    def _extract_js_endpoints(self, content: str, file_path: Path) -> None:
        """Extract Express/NestJS endpoints."""
        # Express pattern
        express_pattern = r'(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(express_pattern, content, re.IGNORECASE):
            method = match.group(1).upper()
            path = match.group(2)
            line_num = content[:match.start()].count('\n') + 1

            endpoint = EndpointAnalysis(
                path=path,
                method=method,
                handler_file=str(file_path),
                handler_line=line_num
            )
            self.analysis_result.endpoints.append(endpoint)

        # NestJS pattern
        nest_pattern = r'@(Get|Post|Put|Delete|Patch)\s*\(\s*["\']?([^"\')\s]*)["\']?\s*\)'
        for match in re.finditer(nest_pattern, content):
            method = match.group(1).upper()
            path = match.group(2) or "/"
            line_num = content[:match.start()].count('\n') + 1

            endpoint = EndpointAnalysis(
                path=path,
                method=method,
                handler_file=str(file_path),
                handler_line=line_num
            )
            self.analysis_result.endpoints.append(endpoint)

    def _extract_generic_endpoints(self, content: str, file_path: Path) -> None:
        """Generic endpoint extraction for unknown frameworks."""
        # Look for common route patterns
        patterns = [
            r'(GET|POST|PUT|DELETE|PATCH)\s+["\']([^"\']+)["\']',
            r'route\s*[=:]\s*["\']([^"\']+)["\']'
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                if len(match.groups()) == 2:
                    method, path = match.groups()
                else:
                    method, path = "ANY", match.group(1)

                line_num = content[:match.start()].count('\n') + 1
                endpoint = EndpointAnalysis(
                    path=path,
                    method=method.upper(),
                    handler_file=str(file_path),
                    handler_line=line_num
                )
                self.analysis_result.endpoints.append(endpoint)

    def _analyze_rest_compliance(self) -> None:
        """Analyze REST API compliance."""
        for endpoint in self.analysis_result.endpoints:
            # Check resource naming
            path = endpoint.path

            # Bad: verb-based naming
            if re.search(r'/(get|create|delete|update|fetch)', path, re.IGNORECASE):
                endpoint.issues.append(EndpointIssue(
                    severity="medium",
                    category="naming",
                    description="Verb-based URL naming detected",
                    endpoint=path,
                    method=endpoint.method,
                    recommendation="Use noun-based resource naming (e.g., /users instead of /getUsers)"
                ))

            # Check HTTP method appropriateness
            if endpoint.method == "GET" and ("create" in path.lower() or "delete" in path.lower()):
                endpoint.issues.append(EndpointIssue(
                    severity="high",
                    category="http_method",
                    description="GET method used for state-changing operation",
                    endpoint=path,
                    method=endpoint.method,
                    recommendation="Use POST for create, DELETE for delete operations"
                ))

            # Check for ID in collection endpoints
            if endpoint.method == "POST" and re.search(r'/\d+$|/\{[^}]+\}$', path):
                endpoint.issues.append(EndpointIssue(
                    severity="low",
                    category="rest_convention",
                    description="POST to specific resource ID",
                    endpoint=path,
                    method=endpoint.method,
                    recommendation="POST should target collection endpoints, use PUT/PATCH for specific resources"
                ))

    def _analyze_validation(self) -> None:
        """Analyze input validation across endpoints."""
        endpoints_without_validation = [
            ep for ep in self.analysis_result.endpoints
            if ep.method in ["POST", "PUT", "PATCH"] and not ep.has_validation
        ]

        for endpoint in endpoints_without_validation:
            endpoint.issues.append(EndpointIssue(
                severity="high",
                category="validation",
                description="No input validation detected for state-changing endpoint",
                endpoint=endpoint.path,
                method=endpoint.method,
                recommendation="Add request body validation using schemas (Pydantic, Joi, Zod, etc.)"
            ))

    def _analyze_error_handling(self, files: list[Path]) -> None:
        """Analyze error handling patterns."""
        has_global_handler = False
        has_consistent_format = False

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            # Check for global error handler
            global_patterns = [
                r"@app\.exception_handler",
                r"@app\.errorhandler",
                r"app\.use\s*\(\s*\(err",
                r"ExceptionFilter",
                r"exception_handler"
            ]
            if any(re.search(p, content) for p in global_patterns):
                has_global_handler = True

            # Check for consistent error format
            error_format_patterns = [
                r'"error":\s*\{',
                r'"message":\s*["\']',
                r'"code":\s*["\']',
                r'{"status":'
            ]
            if any(re.search(p, content) for p in error_format_patterns):
                has_consistent_format = True

        if not has_global_handler:
            self.analysis_result.issues.append(EndpointIssue(
                severity="medium",
                category="error_handling",
                description="No global error handler detected",
                endpoint="global",
                recommendation="Implement a global exception handler for consistent error responses"
            ))

        if not has_consistent_format:
            self.analysis_result.issues.append(EndpointIssue(
                severity="low",
                category="error_handling",
                description="Inconsistent or missing error response format",
                endpoint="global",
                recommendation="Define a standard error response schema"
            ))

    def _analyze_documentation(self, files: list[Path]) -> None:
        """Analyze API documentation coverage."""
        has_openapi = False
        has_swagger = False

        for file_path in files:
            # Check for OpenAPI/Swagger files
            if file_path.name in ["openapi.json", "openapi.yaml", "swagger.json", "swagger.yaml"]:
                has_openapi = True
                break

            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            # Check for inline documentation
            if re.search(r"openapi|swagger", content, re.IGNORECASE):
                has_swagger = True

        # Update endpoint documentation status
        for endpoint in self.analysis_result.endpoints:
            endpoint.has_documentation = has_openapi or has_swagger

        if not has_openapi and not has_swagger:
            self.analysis_result.issues.append(EndpointIssue(
                severity="medium",
                category="documentation",
                description="No OpenAPI/Swagger documentation found",
                endpoint="global",
                recommendation="Generate API documentation using OpenAPI 3.0 specification"
            ))

    def _calculate_scores(self) -> None:
        """Calculate API quality scores."""
        if not self.analysis_result.endpoints:
            self.analysis_result.overall_score = 0
            return

        total_score = 100

        # Deduct for global issues
        for issue in self.analysis_result.issues:
            if issue.severity == "high":
                total_score -= 10
            elif issue.severity == "medium":
                total_score -= 5
            elif issue.severity == "low":
                total_score -= 2

        # Calculate per-endpoint scores and aggregate
        endpoint_scores = []
        for endpoint in self.analysis_result.endpoints:
            ep_score = 100
            for issue in endpoint.issues:
                if issue.severity == "high":
                    ep_score -= 15
                elif issue.severity == "medium":
                    ep_score -= 8
                elif issue.severity == "low":
                    ep_score -= 3
            endpoint.score = max(0, ep_score)
            endpoint_scores.append(endpoint.score)

        if endpoint_scores:
            avg_endpoint_score = sum(endpoint_scores) / len(endpoint_scores)
            total_score = int((total_score + avg_endpoint_score) / 2)

        self.analysis_result.overall_score = max(0, min(100, total_score))

        # Update stats
        self.analysis_result.stats = {
            "total_endpoints": len(self.analysis_result.endpoints),
            "endpoints_with_validation": sum(1 for ep in self.analysis_result.endpoints if ep.has_validation),
            "endpoints_with_auth": sum(1 for ep in self.analysis_result.endpoints if ep.has_authentication),
            "endpoints_with_issues": sum(1 for ep in self.analysis_result.endpoints if ep.issues),
            "framework_detected": self.detected_framework or "unknown"
        }

    def _generate_recommendations(self) -> None:
        """Generate API improvement recommendations."""
        stats = self.analysis_result.stats

        # Recommend validation if many endpoints lack it
        if stats.get("total_endpoints", 0) > 0:
            validation_rate = stats.get("endpoints_with_validation", 0) / stats["total_endpoints"]
            if validation_rate < 0.5:
                self.analysis_result.recommendations.append(EndpointIssue(
                    severity="high",
                    category="validation",
                    description=f"Only {validation_rate*100:.0f}% of endpoints have validation",
                    endpoint="global",
                    recommendation="Implement request validation for all state-changing endpoints"
                ))

        # Recommend auth if many endpoints lack it
        if stats.get("total_endpoints", 0) > 0:
            auth_rate = stats.get("endpoints_with_auth", 0) / stats["total_endpoints"]
            if auth_rate < 0.3:
                self.analysis_result.recommendations.append(EndpointIssue(
                    severity="medium",
                    category="security",
                    description=f"Only {auth_rate*100:.0f}% of endpoints have authentication",
                    endpoint="global",
                    recommendation="Review which endpoints require authentication"
                ))

    def get_summary(self) -> dict:
        """Get analysis summary for reporting."""
        if not self.analysis_result:
            return {}

        return {
            "api_type": self.analysis_result.api_type.value,
            "overall_score": self.analysis_result.overall_score,
            "framework": self.detected_framework or "unknown",
            "stats": self.analysis_result.stats,
            "total_issues": len(self.analysis_result.issues) + sum(
                len(ep.issues) for ep in self.analysis_result.endpoints
            ),
            "recommendations_count": len(self.analysis_result.recommendations)
        }

    def generate_openapi_skeleton(self) -> dict[str, Any]:
        """Generate OpenAPI skeleton from detected endpoints."""
        openapi: dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": "API Documentation",
                "version": "1.0.0",
                "description": "Auto-generated API documentation"
            },
            "paths": {}
        }

        for endpoint in self.analysis_result.endpoints:
            path = endpoint.path
            method = endpoint.method.lower()

            if path not in openapi["paths"]:
                openapi["paths"][path] = {}

            openapi["paths"][path][method] = {
                "summary": f"{endpoint.method} {path}",
                "responses": {
                    "200": {"description": "Successful response"},
                    "400": {"description": "Bad request"},
                    "401": {"description": "Unauthorized"},
                    "500": {"description": "Internal server error"}
                }
            }

            if endpoint.method in ["POST", "PUT", "PATCH"]:
                openapi["paths"][path][method]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }

        return openapi


def analyze_api(codebase_path: str, config: Optional[dict] = None) -> dict:
    """Convenience function to analyze API and return summary."""
    analyzer = APIAnalyzer(config)
    result = analyzer.analyze(codebase_path)
    return {
        "result": result,
        "summary": analyzer.get_summary(),
        "openapi_skeleton": analyzer.generate_openapi_skeleton()
    }
