"""
SatQuery AI — Services Package
Provides lazy-loaded entry points to prevent circular imports between
services and specialist inference executors.
"""

def __getattr__(name: str):
    if name == "AnalysisService":
        from .analysis_service import AnalysisService
        return AnalysisService
    if name == "execute_agent_request":
        from .orchestration_service import execute_agent_request
        return execute_agent_request
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["AnalysisService", "execute_agent_request"]
