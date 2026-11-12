"""SpecGuard-Core: Domain-Agnostic Multi-Agent Verification Skeleton."""

from .models import (
    EARSClause,
    VerificationDAG,
    AtomicClaim,
    CounterexampleWitness,
    AgentTraceStep,
    AuditReport,
    ConfusionMatrixMetrics,
)
from .compiler import EARSCompiler, SpecCompilationError
from .crew_orchestrator import CrewOrchestrator, DomainAdapter
from .evaluator import BenchmarkEvaluator

__all__ = [
    "EARSClause",
    "VerificationDAG",
    "AtomicClaim",
    "CounterexampleWitness",
    "AgentTraceStep",
    "AuditReport",
    "ConfusionMatrixMetrics",
    "EARSCompiler",
    "SpecCompilationError",
    "CrewOrchestrator",
    "DomainAdapter",
    "BenchmarkEvaluator",
]
