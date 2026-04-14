from typing import Optional
from models import Case, Evidence, CRIME_TYPES
from data_structures import CaseQueue, CaseHistoryList
from legal_advisor import LegalAdvisor, LegalDatabase


class CourtSystem:
    """
    Central judicial system that orchestrates:
    - CaseQueue      → FIFO queue of pending cases
    - CaseHistoryList → singly-linked list of all cases
    - LegalDatabase  → array of legal articles
    - LegalAdvisor   → AI-powered advisor
    """

    def __init__(self, api_key: str = ""):
        # Data structures
        self._queue: CaseQueue = CaseQueue()         
        self._history: CaseHistoryList = CaseHistoryList()  
        self._active_cases: dict = {}                

        # Services
        self.legal_db: LegalDatabase = LegalDatabase()
        self.advisor: LegalAdvisor = LegalAdvisor(api_key)

        # Metrics
        self._total_created: int = 0
        self._total_resolved: int = 0
        self._verdict_counts: dict = {
            "Culpable": 0,
            "No culpable": 0,
            "Culpable con atenuantes": 0,
        }
        self._total_duration_days: float = 0.0

        # Seed demo cases
        self._seed_demo_cases()

    # ─── CASE MANAGEMENT ────────────────────────────────────────────────────

    def create_case(
        self,
        title: str,
        description: str,
        crime_type: str,
        defendant: str,
        prosecutor: str,
        judge: str,
    ) -> Case:
        case = Case(title, description, crime_type, defendant, prosecutor, judge)
        self._active_cases[case.case_id] = case
        self._history.append(case)
        self._queue.enqueue(case)
        self._total_created += 1
        return case

    def get_case(self, case_id: str) -> Optional[Case]:
        return self._active_cases.get(case_id)

    def get_all_cases(self) -> list:
        return list(self._active_cases.values())

    def get_pending_queue(self) -> list:
        """Returns all cases currently in the FIFO queue."""
        return self._queue.to_list()

    def get_history(self) -> list:
        """Returns all cases from the singly-linked list history."""
        return self._history.to_list()

    # ─── STAGE MANAGEMENT ───────────────────────────────────────────────────

    def advance_case_stage(self, case_id: str) -> dict:
        case = self.get_case(case_id)
        if not case:
            return {"success": False, "message": "Caso no encontrado."}
        if case.is_resolved:
            return {"success": False, "message": "El caso ya fue resuelto."}

        new_stage = case.advance_stage()
        if new_stage:
            return {"success": True, "new_stage": new_stage, "case": case.to_dict()}
        return {"success": False, "message": "El caso ya está en la etapa final."}

    def revert_case_stage(self, case_id: str) -> dict:
        case = self.get_case(case_id)
        if not case:
            return {"success": False, "message": "Caso no encontrado."}

        prev_stage = case.revert_stage()
        if prev_stage:
            return {"success": True, "new_stage": prev_stage, "case": case.to_dict()}
        return {"success": False, "message": "El caso ya está en la primera etapa."}

    # ─── EVIDENCE MANAGEMENT ────────────────────────────────────────────────

    def add_evidence(
        self,
        case_id: str,
        name: str,
        description: str,
        evidence_type: str,
        relevance_score: int,
    ) -> dict:
        case = self.get_case(case_id)
        if not case:
            return {"success": False, "message": "Caso no encontrado."}

        evidence = Evidence(name, description, evidence_type, relevance_score)
        case.add_evidence(evidence)
        return {"success": True, "evidence": evidence.to_dict(), "case": case.to_dict()}

    # ─── VERDICT / RESOLUTION ───────────────────────────────────────────────

    def resolve_case(
        self,
        case_id: str,
        verdict: str,
        sentence_years: int = 0,
        ai_analysis: str = "",
    ) -> dict:
        case = self.get_case(case_id)
        if not case:
            return {"success": False, "message": "Caso no encontrado."}
        if case.is_resolved:
            return {"success": False, "message": "El caso ya fue resuelto."}

        case.resolve(verdict, sentence_years, ai_analysis)

        # Update metrics
        self._total_resolved += 1
        if verdict in self._verdict_counts:
            self._verdict_counts[verdict] += 1
        else:
            self._verdict_counts[verdict] = 1
        if case.duration_days:
            self._total_duration_days += case.duration_days

        return {"success": True, "case": case.to_dict()}

    # ─── AI ADVISOR ─────────────────────────────────────────────────────────

    def ask_advisor(self, case_id: str, question: str) -> dict:
        case = self.get_case(case_id)
        if not case:
            return {"success": False, "message": "Caso no encontrado."}

        response = self.advisor.ask(case, question)
        case.add_note(f"[IA] Consulta: {question[:80]}...")
        return {"success": True, "response": response}

    # ─── NOTES ──────────────────────────────────────────────────────────────

    def add_note(self, case_id: str, note: str) -> dict:
        case = self.get_case(case_id)
        if not case:
            return {"success": False, "message": "Caso no encontrado."}
        case.add_note(note)
        return {"success": True, "case": case.to_dict()}

    # ─── METRICS ────────────────────────────────────────────────────────────

    def get_metrics(self) -> dict:
        avg_duration = (
            self._total_duration_days / self._total_resolved
            if self._total_resolved > 0
            else 0
        )
        pending_count = sum(
            1 for c in self._active_cases.values() if not c.is_resolved
        )
        resolved_cases = [c for c in self._active_cases.values() if c.is_resolved]

        return {
            "total_cases": self._total_created,
            "resolved": self._total_resolved,
            "pending": pending_count,
            "avg_duration_days": round(avg_duration, 1),
            "verdict_distribution": self._verdict_counts,
            "crime_type_distribution": self._get_crime_distribution(),
            "queue_size": len(self._queue),
            "history_size": len(self._history),
            "legal_articles_loaded": len(self.legal_db),
        }

    def _get_crime_distribution(self) -> dict:
        dist = {}
        for case in self._active_cases.values():
            dist[case.crime_type] = dist.get(case.crime_type, 0) + 1
        return dist

    # ─── LEGAL DB ───────────────────────────────────────────────────────────

    def get_legal_articles(self, crime_type: Optional[str] = None) -> list:
        if crime_type:
            return self.legal_db.get_articles_for_crime(crime_type)
        return self.legal_db.get_all()

    # ─── DEMO DATA ──────────────────────────────────────────────────────────

    def _seed_demo_cases(self) -> None:
        demos = [
            {
                "title": "Caso García - Fraude Empresarial",
                "description": "El acusado presuntamente desvió fondos corporativos por un valor de $2.3 mil millones de pesos mediante operaciones ficticias entre 2021 y 2023.",
                "crime_type": "Fraude financiero",
                "defendant": "Ricardo García Montoya",
                "prosecutor": "Fiscal Adriana Reyes",
                "judge": "Dr. Fernando Castellanos",
            },
            {
                "title": "Operación Nocturna - Tráfico de Estupefacientes",
                "description": "Captura en flagrancia con 50 kg de sustancias controladas en zona industrial de la ciudad. Tres implicados, uno en etapa de juicio.",
                "crime_type": "Tráfico de estupefacientes",
                "defendant": "Carlos Meneses Vargas",
                "prosecutor": "Fiscal Luis Bermúdez",
                "judge": "Dra. Sandra Ospina",
            },
            {
                "title": "Caso Torres - Violencia Doméstica Agravada",
                "description": "Denuncia reiterada por violencia física y psicológica. Existen 4 denuncias previas y registro médico forense de lesiones.",
                "crime_type": "Violencia doméstica",
                "defendant": "Andrés Torres Ríos",
                "prosecutor": "Fiscal María Salcedo",
                "judge": "Dr. Jaime Rodríguez",
            },
        ]

        for d in demos:
            case = self.create_case(**d)

        # Add some evidence to the first case
        first_id = list(self._active_cases.keys())[0]
        self.add_evidence(first_id, "Transferencias bancarias", "Registros de 47 transferencias irregulares detectadas por auditoría interna.", "Documental", 9)
        self.add_evidence(first_id, "Testimonio contador", "Contador de la empresa declara haber recibido órdenes directas del acusado.", "Testimonial", 8)
        self.advance_case_stage(first_id)

        # Second case - advance to Juicio
        second_id = list(self._active_cases.keys())[1]
        self.add_evidence(second_id, "Análisis químico", "Informe de laboratorio confirma naturaleza de sustancias incautadas.", "Física", 10)
        self.add_evidence(second_id, "Video vigilancia", "Cámaras de seguridad capturaron el intercambio.", "Documental", 9)
        self.advance_case_stage(second_id)
        self.advance_case_stage(second_id)

        # Resolve a demo case
        third_id = list(self._active_cases.keys())[2]
        self.add_evidence(third_id, "Informe médico forense", "Lesiones documentadas compatibles con violencia física repetida.", "Documental", 9)
        self.add_evidence(third_id, "Registro llamadas", "Interceptación de comunicaciones con amenazas explícitas.", "Documental", 8)
        self.advance_case_stage(third_id)
        self.advance_case_stage(third_id)
        self.resolve_case(
            third_id,
            "Culpable",
            6,
            "Evidencia contundente. Se aplica Art. L-1257-2008. Pena: 6 años."
        )
