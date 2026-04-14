import uuid
from datetime import datetime
from typing import Optional
from data_structures import EvidenceStack, StagePipeline


# Judicial stages (user-facing labels stay in Spanish, internal ids in English)
STAGES = ["Investigación", "Juicio", "Sentencia"]

CRIME_TYPES = [
    "Homicidio", "Robo agravado", "Fraude financiero",
    "Tráfico de estupefacientes", "Violencia doméstica",
    "Delitos informáticos", "Corrupción", "Secuestro",
]

VERDICT_OPTIONS = ["Culpable", "No culpable", "Culpable con atenuantes"]


class Evidence:
    """
    Represents a single piece of evidence.
    Stored in an EvidenceStack (LIFO).
    """

    def __init__(
        self,
        name: str,
        description: str,
        evidence_type: str,
        relevance_score: int,  # 1-10
    ):
        self.evidence_id: str = str(uuid.uuid4())[:8].upper()
        self.name = name
        self.description = description
        self.evidence_type = evidence_type   # e.g. "Documental", "Testimonial", "Física"
        self.relevance_score = max(1, min(10, relevance_score))
        self.added_at: datetime = datetime.now()

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "name": self.name,
            "description": self.description,
            "evidence_type": self.evidence_type,
            "relevance_score": self.relevance_score,
            "added_at": self.added_at.isoformat(),
        }


class Case:
    """
    Represents a judicial case with its full lifecycle.
    Uses:
      - EvidenceStack  → for evidence (LIFO)
      - StagePipeline  → doubly-linked list for stage navigation
    """

    def __init__(
        self,
        title: str,
        description: str,
        crime_type: str,
        defendant: str,
        prosecutor: str,
        judge: str,
    ):
        self.case_id: str = f"EXP-{str(uuid.uuid4())[:6].upper()}"
        self.title = title
        self.description = description
        self.crime_type = crime_type
        self.defendant = defendant
        self.prosecutor = prosecutor
        self.judge = judge

        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.resolved_at: Optional[datetime] = None

        # Evidence stack (LIFO)
        self.evidence_stack: EvidenceStack = EvidenceStack()

        # Stage pipeline (doubly linked list)
        self.pipeline: StagePipeline = StagePipeline()
        for stage in STAGES:
            self.pipeline.add_stage(stage)

        self.verdict: Optional[str] = None
        self.sentence_years: Optional[int] = None
        self.ai_analysis: Optional[str] = None
        self.notes: list = []

        # Metrics
        self.duration_days: Optional[float] = None

    # ── Evidence management ──────────────────────────────

    def add_evidence(self, evidence: Evidence) -> None:
        self.evidence_stack.push(evidence)  # stores Evidence objects
        self.updated_at = datetime.now()

    def get_all_evidence(self) -> list:
        """Returns evidence as list of dicts (LIFO order)."""
        return [e.to_dict() for e in self.evidence_stack.to_list()]

    # ── Stage navigation ─────────────────────────────────

    def advance_stage(self) -> Optional[str]:
        result = self.pipeline.advance()
        if result:
            self.updated_at = datetime.now()
        return result

    def revert_stage(self) -> Optional[str]:
        result = self.pipeline.revert()
        if result:
            self.updated_at = datetime.now()
        return result

    @property
    def current_stage(self) -> str:
        return self.pipeline.current_stage or "Investigación"

    @property
    def is_resolved(self) -> bool:
        return self.verdict is not None

    def resolve(self, verdict: str, sentence_years: int = 0, ai_analysis: str = "") -> None:
        self.verdict = verdict
        self.sentence_years = sentence_years
        self.ai_analysis = ai_analysis
        self.resolved_at = datetime.now()
        self.duration_days = (self.resolved_at - self.created_at).total_seconds() / 86400

    def add_note(self, note: str) -> None:
        self.notes.append({
            "text": note,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    # ── Serialization ────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "title": self.title,
            "description": self.description,
            "crime_type": self.crime_type,
            "defendant": self.defendant,
            "prosecutor": self.prosecutor,
            "judge": self.judge,
            "current_stage": self.current_stage,
            "stages": self.pipeline.to_list(),
            "evidence": self.get_all_evidence(),  # already list of dicts
            "evidence_count": len(self.evidence_stack),
            "verdict": self.verdict,
            "sentence_years": self.sentence_years,
            "ai_analysis": self.ai_analysis,
            "notes": self.notes,
            "is_resolved": self.is_resolved,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "duration_days": round(self.duration_days, 2) if self.duration_days else None,
            "has_next_stage": self.pipeline.has_next,
            "has_prev_stage": self.pipeline.has_prev,
        }
