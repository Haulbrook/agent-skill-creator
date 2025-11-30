"""
Database Analyzer for Backend Trainer

Evaluates database schema design, query patterns, ORM usage,
and data access layer efficiency.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"
    UNKNOWN = "unknown"


class ORMType(Enum):
    SQLALCHEMY = "sqlalchemy"
    DJANGO_ORM = "django_orm"
    PRISMA = "prisma"
    TYPEORM = "typeorm"
    SEQUELIZE = "sequelize"
    MONGOOSE = "mongoose"
    RAW_SQL = "raw_sql"
    UNKNOWN = "unknown"


@dataclass
class DatabaseIssue:
    severity: str
    category: str
    description: str
    file_path: str = ""
    line_number: Optional[int] = None
    query: str = ""
    recommendation: str = ""


@dataclass
class TableAnalysis:
    name: str
    columns: list[dict] = field(default_factory=list)
    primary_key: Optional[str] = None
    foreign_keys: list[dict] = field(default_factory=list)
    indexes: list[str] = field(default_factory=list)
    issues: list[DatabaseIssue] = field(default_factory=list)


@dataclass
class QueryAnalysis:
    query_type: str
    location: str
    line_number: Optional[int] = None
    has_n_plus_one_risk: bool = False
    missing_index_hint: bool = False
    complexity: str = "simple"
    issues: list[DatabaseIssue] = field(default_factory=list)


@dataclass
class DatabaseAnalysisResult:
    database_type: DatabaseType
    orm_type: ORMType
    overall_score: int
    tables: list[TableAnalysis] = field(default_factory=list)
    queries: list[QueryAnalysis] = field(default_factory=list)
    issues: list[DatabaseIssue] = field(default_factory=list)
    recommendations: list[DatabaseIssue] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


class DatabaseAnalyzer:
    """Analyzes database design and data access patterns."""

    # ORM detection patterns
    ORM_PATTERNS = {
        ORMType.SQLALCHEMY: [r"from\s+sqlalchemy", r"Base\s*=\s*declarative_base", r"Session\("],
        ORMType.DJANGO_ORM: [r"from\s+django\.db", r"models\.Model", r"objects\.filter"],
        ORMType.PRISMA: [r"@prisma/client", r"prisma\.", r"PrismaClient"],
        ORMType.TYPEORM: [r"from\s+['\"]typeorm['\"]", r"@Entity", r"@Column"],
        ORMType.SEQUELIZE: [r"require\(['\"]sequelize['\"]", r"Sequelize\.", r"sequelize\.define"],
        ORMType.MONGOOSE: [r"require\(['\"]mongoose['\"]", r"mongoose\.Schema", r"mongoose\.model"],
    }

    # Database detection patterns
    DB_PATTERNS = {
        DatabaseType.POSTGRESQL: [r"postgresql://", r"psycopg2", r"asyncpg", r"pg\."],
        DatabaseType.MYSQL: [r"mysql://", r"pymysql", r"mysql2", r"mysqlclient"],
        DatabaseType.SQLITE: [r"sqlite://", r"sqlite3", r"\.db['\"]"],
        DatabaseType.MONGODB: [r"mongodb://", r"pymongo", r"mongoose"],
        DatabaseType.REDIS: [r"redis://", r"redis\.", r"ioredis"],
    }

    # N+1 query patterns
    N_PLUS_ONE_PATTERNS = [
        r"for\s+\w+\s+in\s+\w+:.*\n.*\.query\(",
        r"for\s+\w+\s+in\s+\w+:.*\n.*\.find\(",
        r"forEach.*\n.*\.findOne\(",
        r"for.*await.*find",
        r"\.all\(\).*\n.*for.*\n.*\.get\(",
    ]

    # Missing index hint patterns
    MISSING_INDEX_PATTERNS = [
        r"WHERE\s+\w+\s*=",
        r"\.filter\(\w+\s*=",
        r"ORDER\s+BY\s+\w+",
        r"GROUP\s+BY\s+\w+",
    ]

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.analysis_result = None

    def analyze(self, codebase_path: str) -> DatabaseAnalysisResult:
        """Perform complete database analysis."""
        path = Path(codebase_path)
        if not path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")

        # Initialize result
        self.analysis_result = DatabaseAnalysisResult(
            database_type=DatabaseType.UNKNOWN,
            orm_type=ORMType.UNKNOWN,
            overall_score=0
        )

        # Collect source files
        source_files = (
            list(path.rglob("*.py")) +
            list(path.rglob("*.js")) +
            list(path.rglob("*.ts"))
        )

        # Collect schema files
        schema_files = (
            list(path.rglob("*.sql")) +
            list(path.rglob("**/migrations/*.py")) +
            list(path.rglob("**/schema.prisma"))
        )

        # Detect database and ORM
        self._detect_database(source_files)
        self._detect_orm(source_files)

        # Analyze models/schema
        self._analyze_models(source_files)
        self._analyze_schema_files(schema_files)

        # Analyze queries
        self._analyze_queries(source_files)

        # Check for N+1 queries
        self._detect_n_plus_one(source_files)

        # Analyze transaction handling
        self._analyze_transactions(source_files)

        # Analyze connection handling
        self._analyze_connections(source_files)

        # Calculate scores
        self._calculate_scores()

        # Generate recommendations
        self._generate_recommendations()

        return self.analysis_result

    def _detect_database(self, files: list[Path]) -> None:
        """Detect which database is being used."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for db_type, patterns in self.DB_PATTERNS.items():
                if any(re.search(p, content, re.IGNORECASE) for p in patterns):
                    self.analysis_result.database_type = db_type
                    return

    def _detect_orm(self, files: list[Path]) -> None:
        """Detect which ORM is being used."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for orm_type, patterns in self.ORM_PATTERNS.items():
                if any(re.search(p, content) for p in patterns):
                    self.analysis_result.orm_type = orm_type
                    return

        # Check for raw SQL usage
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            raw_sql_patterns = [r"\.execute\s*\(\s*['\"]SELECT", r"cursor\.", r"\.raw\s*\("]
            if any(re.search(p, content, re.IGNORECASE) for p in raw_sql_patterns):
                self.analysis_result.orm_type = ORMType.RAW_SQL
                return

    def _analyze_models(self, files: list[Path]) -> None:
        """Analyze ORM model definitions."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            # SQLAlchemy models
            if self.analysis_result.orm_type == ORMType.SQLALCHEMY:
                self._analyze_sqlalchemy_models(content, file_path)

            # Django models
            elif self.analysis_result.orm_type == ORMType.DJANGO_ORM:
                self._analyze_django_models(content, file_path)

            # TypeORM entities
            elif self.analysis_result.orm_type == ORMType.TYPEORM:
                self._analyze_typeorm_models(content, file_path)

    def _analyze_sqlalchemy_models(self, content: str, file_path: Path) -> None:
        """Analyze SQLAlchemy model definitions."""
        # Find class definitions that inherit from Base
        class_pattern = r"class\s+(\w+)\s*\([^)]*Base[^)]*\):"
        for match in re.finditer(class_pattern, content):
            table_name = match.group(1)
            table = TableAnalysis(name=table_name)

            # Find column definitions
            col_pattern = r"(\w+)\s*=\s*Column\s*\(([^)]+)\)"
            for col_match in re.finditer(col_pattern, content):
                col_name = col_match.group(1)
                col_def = col_match.group(2)
                table.columns.append({
                    "name": col_name,
                    "definition": col_def
                })

                # Check for primary key
                if "primary_key=True" in col_def:
                    table.primary_key = col_name

            # Find relationships without lazy loading specification
            rel_pattern = r"relationship\s*\([^)]+\)"
            for rel_match in re.finditer(rel_pattern, content):
                rel_def = rel_match.group(0)
                if "lazy=" not in rel_def:
                    table.issues.append(DatabaseIssue(
                        severity="medium",
                        category="orm_usage",
                        description=f"Relationship without explicit lazy loading strategy in {table_name}",
                        file_path=str(file_path),
                        recommendation="Specify lazy loading strategy (lazy='select', 'joined', 'subquery', etc.)"
                    ))

            # Check for missing indexes on foreign keys
            fk_pattern = r"ForeignKey\s*\(['\"]([^'\"]+)['\"]\)"
            for fk_match in re.finditer(fk_pattern, content):
                table.foreign_keys.append({"reference": fk_match.group(1)})

            self.analysis_result.tables.append(table)

    def _analyze_django_models(self, content: str, file_path: Path) -> None:
        """Analyze Django model definitions."""
        class_pattern = r"class\s+(\w+)\s*\(.*models\.Model.*\):"
        for match in re.finditer(class_pattern, content):
            table_name = match.group(1)
            table = TableAnalysis(name=table_name)

            # Find field definitions
            field_pattern = r"(\w+)\s*=\s*models\.(\w+Field)\s*\(([^)]*)\)"
            for field_match in re.finditer(field_pattern, content):
                field_name = field_match.group(1)
                field_type = field_match.group(2)
                field_args = field_match.group(3)

                table.columns.append({
                    "name": field_name,
                    "type": field_type,
                    "args": field_args
                })

                # Check for ForeignKey without related_name
                if field_type == "ForeignKey" and "related_name" not in field_args:
                    table.issues.append(DatabaseIssue(
                        severity="low",
                        category="orm_usage",
                        description=f"ForeignKey '{field_name}' without related_name in {table_name}",
                        file_path=str(file_path),
                        recommendation="Add related_name for clearer reverse relationships"
                    ))

            # Check for missing Meta class with indexes
            if "class Meta:" not in content:
                table.issues.append(DatabaseIssue(
                    severity="low",
                    category="schema",
                    description=f"Model {table_name} missing Meta class",
                    file_path=str(file_path),
                    recommendation="Add Meta class to define indexes, ordering, and constraints"
                ))

            self.analysis_result.tables.append(table)

    def _analyze_typeorm_models(self, content: str, file_path: Path) -> None:
        """Analyze TypeORM entity definitions."""
        entity_pattern = r"@Entity\s*\([^)]*\)\s*(?:export\s+)?class\s+(\w+)"
        for match in re.finditer(entity_pattern, content):
            table_name = match.group(1)
            table = TableAnalysis(name=table_name)

            # Find column definitions
            col_pattern = r"@Column\s*\([^)]*\)\s*(\w+):"
            for col_match in re.finditer(col_pattern, content):
                table.columns.append({"name": col_match.group(1)})

            self.analysis_result.tables.append(table)

    def _analyze_schema_files(self, files: list[Path]) -> None:
        """Analyze raw SQL schema files."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            if file_path.suffix == ".sql":
                self._analyze_sql_schema(content, file_path)

    def _analyze_sql_schema(self, content: str, file_path: Path) -> None:
        """Analyze SQL CREATE TABLE statements."""
        table_pattern = r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`'\"]?(\w+)[`'\"]?\s*\(([^;]+)\)"
        for match in re.finditer(table_pattern, content, re.IGNORECASE | re.DOTALL):
            table_name = match.group(1)
            table_def = match.group(2)

            table = TableAnalysis(name=table_name)

            # Check for primary key
            if "PRIMARY KEY" not in table_def.upper():
                table.issues.append(DatabaseIssue(
                    severity="high",
                    category="schema",
                    description=f"Table {table_name} missing primary key",
                    file_path=str(file_path),
                    recommendation="Add PRIMARY KEY constraint"
                ))

            # Check for foreign key constraints
            if "REFERENCES" in table_def.upper() and "FOREIGN KEY" not in table_def.upper():
                table.issues.append(DatabaseIssue(
                    severity="medium",
                    category="schema",
                    description=f"Table {table_name} has references without explicit FOREIGN KEY constraint",
                    file_path=str(file_path),
                    recommendation="Use explicit FOREIGN KEY constraints for better integrity"
                ))

            self.analysis_result.tables.append(table)

    def _analyze_queries(self, files: list[Path]) -> None:
        """Analyze database queries for performance issues."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            # Find raw SQL queries
            sql_patterns = [
                (r'["\']SELECT\s+\*\s+FROM', "select_star"),
                (r'["\']SELECT[^"\']+FROM[^"\']+(?!WHERE)[^"\']*["\']', "missing_where"),
                (r'LIKE\s+[\'"][%]', "leading_wildcard"),
            ]

            for pattern, query_type in sql_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content[:match.start()].count('\n') + 1
                    query = QueryAnalysis(
                        query_type=query_type,
                        location=str(file_path),
                        line_number=line_num
                    )

                    if query_type == "select_star":
                        query.issues.append(DatabaseIssue(
                            severity="medium",
                            category="query",
                            description="SELECT * usage detected",
                            file_path=str(file_path),
                            line_number=line_num,
                            recommendation="Select only required columns for better performance"
                        ))
                    elif query_type == "leading_wildcard":
                        query.issues.append(DatabaseIssue(
                            severity="high",
                            category="query",
                            description="Leading wildcard in LIKE clause",
                            file_path=str(file_path),
                            line_number=line_num,
                            recommendation="Leading wildcards prevent index usage - consider full-text search"
                        ))

                    self.analysis_result.queries.append(query)

    def _detect_n_plus_one(self, files: list[Path]) -> None:
        """Detect potential N+1 query patterns."""
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            for pattern in self.N_PLUS_ONE_PATTERNS:
                for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
                    line_num = content[:match.start()].count('\n') + 1
                    self.analysis_result.issues.append(DatabaseIssue(
                        severity="high",
                        category="n_plus_one",
                        description="Potential N+1 query pattern detected",
                        file_path=str(file_path),
                        line_number=line_num,
                        recommendation="Use eager loading (joinedload, prefetch_related) or batch queries"
                    ))

    def _analyze_transactions(self, files: list[Path]) -> None:
        """Analyze transaction handling patterns."""
        has_transaction_management = False

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            transaction_patterns = [
                r"\.begin\(\)",
                r"\.commit\(\)",
                r"@transaction",
                r"with\s+.*session",
                r"\.atomic\(",
                r"BEGIN\s+TRANSACTION"
            ]

            if any(re.search(p, content, re.IGNORECASE) for p in transaction_patterns):
                has_transaction_management = True
                break

        if not has_transaction_management:
            self.analysis_result.issues.append(DatabaseIssue(
                severity="medium",
                category="transactions",
                description="No explicit transaction management detected",
                file_path="",
                recommendation="Implement transaction boundaries for data consistency"
            ))

    def _analyze_connections(self, files: list[Path]) -> None:
        """Analyze database connection handling."""
        has_connection_pooling = False

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue

            pool_patterns = [
                r"pool_size",
                r"max_connections",
                r"connection_pool",
                r"Pool\(",
                r"pooling\s*=\s*True"
            ]

            if any(re.search(p, content, re.IGNORECASE) for p in pool_patterns):
                has_connection_pooling = True
                break

        if not has_connection_pooling:
            self.analysis_result.recommendations.append(DatabaseIssue(
                severity="low",
                category="connections",
                description="No connection pooling configuration detected",
                file_path="",
                recommendation="Configure connection pooling for better performance"
            ))

    def _calculate_scores(self) -> None:
        """Calculate database quality scores."""
        base_score = 100

        # Deduct for issues
        for issue in self.analysis_result.issues:
            if issue.severity == "critical":
                base_score -= 20
            elif issue.severity == "high":
                base_score -= 10
            elif issue.severity == "medium":
                base_score -= 5
            elif issue.severity == "low":
                base_score -= 2

        # Deduct for table issues
        for table in self.analysis_result.tables:
            for issue in table.issues:
                if issue.severity == "high":
                    base_score -= 8
                elif issue.severity == "medium":
                    base_score -= 4
                elif issue.severity == "low":
                    base_score -= 2

        # Deduct for query issues
        for query in self.analysis_result.queries:
            for issue in query.issues:
                if issue.severity == "high":
                    base_score -= 8
                elif issue.severity == "medium":
                    base_score -= 4

        self.analysis_result.overall_score = max(0, min(100, base_score))

        # Update stats
        self.analysis_result.stats = {
            "database_type": self.analysis_result.database_type.value,
            "orm_type": self.analysis_result.orm_type.value,
            "tables_analyzed": len(self.analysis_result.tables),
            "queries_analyzed": len(self.analysis_result.queries),
            "total_issues": len(self.analysis_result.issues) + sum(
                len(t.issues) for t in self.analysis_result.tables
            ) + sum(len(q.issues) for q in self.analysis_result.queries)
        }

    def _generate_recommendations(self) -> None:
        """Generate database improvement recommendations."""
        # Check for missing indexes
        tables_without_indexes = [
            t for t in self.analysis_result.tables
            if not t.indexes and t.foreign_keys
        ]

        if tables_without_indexes:
            self.analysis_result.recommendations.append(DatabaseIssue(
                severity="medium",
                category="indexing",
                description=f"{len(tables_without_indexes)} tables may need indexes on foreign key columns",
                file_path="",
                recommendation="Add indexes on frequently queried foreign key columns"
            ))

    def get_summary(self) -> dict:
        """Get analysis summary for reporting."""
        if not self.analysis_result:
            return {}

        return {
            "database_type": self.analysis_result.database_type.value,
            "orm_type": self.analysis_result.orm_type.value,
            "overall_score": self.analysis_result.overall_score,
            "stats": self.analysis_result.stats,
            "total_issues": self.analysis_result.stats.get("total_issues", 0),
            "recommendations_count": len(self.analysis_result.recommendations)
        }


def analyze_database(codebase_path: str, config: Optional[dict] = None) -> dict:
    """Convenience function to analyze database and return summary."""
    analyzer = DatabaseAnalyzer(config)
    result = analyzer.analyze(codebase_path)
    return {
        "result": result,
        "summary": analyzer.get_summary()
    }
