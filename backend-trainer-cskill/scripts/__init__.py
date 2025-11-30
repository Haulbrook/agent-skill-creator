"""
Backend Trainer Scripts

Main entry point for backend analysis and collaboration tools.
"""

from .analyzers import (
    ArchitectureAnalyzer,
    analyze_architecture,
    APIAnalyzer,
    analyze_api,
    DatabaseAnalyzer,
    analyze_database,
    SecurityAnalyzer,
    analyze_security,
    PerformanceAnalyzer,
    analyze_performance,
)

from .protocols import (
    FrontendHandoffGenerator,
    create_handoff_package,
    CollaborationBridge,
    FrontendCollaborator,
)


def run_full_analysis(codebase_path: str) -> dict:
    """
    Run complete backend analysis on a codebase.

    Args:
        codebase_path: Path to the codebase to analyze

    Returns:
        Dictionary containing all analysis results
    """
    results = {
        "architecture": analyze_architecture(codebase_path),
        "api": analyze_api(codebase_path),
        "database": analyze_database(codebase_path),
        "security": analyze_security(codebase_path),
        "performance": analyze_performance(codebase_path),
    }

    # Calculate overall score
    scores = [
        results["architecture"]["summary"].get("overall_score", 0),
        results["api"]["summary"].get("overall_score", 0),
        results["database"]["summary"].get("overall_score", 0),
        results["security"]["summary"].get("overall_score", 0),
        results["performance"]["summary"].get("overall_score", 0),
    ]

    results["overall"] = {
        "score": sum(scores) // len(scores) if scores else 0,
        "architecture_score": scores[0],
        "api_score": scores[1],
        "database_score": scores[2],
        "security_score": scores[3],
        "performance_score": scores[4],
    }

    return results


def generate_frontend_handoff(
    codebase_path: str,
    output_dir: str = "./handoff"
) -> dict:
    """
    Generate a complete frontend handoff package.

    Args:
        codebase_path: Path to the codebase
        output_dir: Directory to write handoff files

    Returns:
        Handoff package dictionary
    """
    from pathlib import Path

    # Run analyses
    api_result = analyze_api(codebase_path)
    arch_result = analyze_architecture(codebase_path)
    sec_result = analyze_security(codebase_path)
    perf_result = analyze_performance(codebase_path)
    db_result = analyze_database(codebase_path)

    # Create handoff generator
    generator = create_handoff_package(
        api_analysis=api_result,
        architecture_analysis=arch_result,
        security_analysis=sec_result,
        performance_analysis=perf_result,
        database_analysis=db_result
    )

    # Generate outputs
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generator.export_to_json(str(output_path / "api-contract.json"))
    generator.export_typescript_file(str(output_path / "types.ts"))

    # Write summary
    summary = generator.generate_handoff_summary()
    with open(output_path / "HANDOFF_SUMMARY.md", 'w') as f:
        f.write(summary)

    return generator.generate_package()


__all__ = [
    # Analyzers
    "ArchitectureAnalyzer",
    "analyze_architecture",
    "APIAnalyzer",
    "analyze_api",
    "DatabaseAnalyzer",
    "analyze_database",
    "SecurityAnalyzer",
    "analyze_security",
    "PerformanceAnalyzer",
    "analyze_performance",
    # Protocols
    "FrontendHandoffGenerator",
    "create_handoff_package",
    "CollaborationBridge",
    "FrontendCollaborator",
    # Convenience functions
    "run_full_analysis",
    "generate_frontend_handoff",
]
