import os
import sys

# Allow local imports
sys.path.insert(0, os.path.dirname(__file__))

from court_system import CourtSystem

# ─── Try to import Flask ────────────────────────────────────────────────────
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("Flask not found. Installing...")
    os.system("pip install flask flask-cors --break-system-packages -q")
    from flask import Flask, request, jsonify
    from flask_cors import CORS

# ─── Application setup ──────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# Initialize court system (optionally pass ANTHROPIC_API_KEY env var)
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
court = CourtSystem(api_key=API_KEY)


# ─── Utility ────────────────────────────────────────────────────────────────
def success(data: dict = None, **kwargs):
    payload = {"success": True}
    if data:
        payload.update(data)
    payload.update(kwargs)
    return jsonify(payload)


def error(message: str, status: int = 400):
    return jsonify({"success": False, "message": message}), status


# ─── CASES ──────────────────────────────────────────────────────────────────

@app.route("/api/cases", methods=["GET"])
def list_cases():
    cases = [c.to_dict() for c in court.get_all_cases()]
    return success(cases=cases)


@app.route("/api/cases", methods=["POST"])
def create_case():
    body = request.get_json(force=True)
    required = ["title", "description", "crime_type", "defendant", "prosecutor", "judge"]
    for field in required:
        if not body.get(field, "").strip():
            return error(f"El campo '{field}' es obligatorio.")

    case = court.create_case(
        title=body["title"].strip(),
        description=body["description"].strip(),
        crime_type=body["crime_type"].strip(),
        defendant=body["defendant"].strip(),
        prosecutor=body["prosecutor"].strip(),
        judge=body["judge"].strip(),
    )
    return success(case=case.to_dict()), 201


@app.route("/api/cases/<case_id>", methods=["GET"])
def get_case(case_id):
    case = court.get_case(case_id)
    if not case:
        return error("Caso no encontrado.", 404)
    return success(case=case.to_dict())


# ─── STAGE ──────────────────────────────────────────────────────────────────

@app.route("/api/cases/<case_id>/advance", methods=["POST"])
def advance_stage(case_id):
    result = court.advance_case_stage(case_id)
    if not result["success"]:
        return error(result["message"])
    return success(**result)


@app.route("/api/cases/<case_id>/revert", methods=["POST"])
def revert_stage(case_id):
    result = court.revert_case_stage(case_id)
    if not result["success"]:
        return error(result["message"])
    return success(**result)


# ─── EVIDENCE ───────────────────────────────────────────────────────────────

@app.route("/api/cases/<case_id>/evidence", methods=["POST"])
def add_evidence(case_id):
    body = request.get_json(force=True)
    required = ["name", "description", "evidence_type", "relevance_score"]
    for field in required:
        if field not in body:
            return error(f"El campo '{field}' es obligatorio.")

    result = court.add_evidence(
        case_id,
        name=body["name"],
        description=body["description"],
        evidence_type=body["evidence_type"],
        relevance_score=int(body["relevance_score"]),
    )
    if not result["success"]:
        return error(result["message"])
    return success(**result), 201


# ─── AI ADVISOR ─────────────────────────────────────────────────────────────

@app.route("/api/cases/<case_id>/ask", methods=["POST"])
def ask_advisor(case_id):
    body = request.get_json(force=True)
    question = body.get("question", "").strip()
    if not question:
        return error("La pregunta no puede estar vacía.")

    result = court.ask_advisor(case_id, question)
    if not result["success"]:
        return error(result["message"])
    return success(**result)


# ─── VERDICT ────────────────────────────────────────────────────────────────

@app.route("/api/cases/<case_id>/resolve", methods=["POST"])
def resolve_case(case_id):
    body = request.get_json(force=True)
    verdict = body.get("verdict", "").strip()
    if not verdict:
        return error("El veredicto es obligatorio.")

    result = court.resolve_case(
        case_id,
        verdict=verdict,
        sentence_years=int(body.get("sentence_years", 0)),
        ai_analysis=body.get("ai_analysis", ""),
    )
    if not result["success"]:
        return error(result["message"])
    return success(**result)


# ─── NOTES ──────────────────────────────────────────────────────────────────

@app.route("/api/cases/<case_id>/notes", methods=["POST"])
def add_note(case_id):
    body = request.get_json(force=True)
    note = body.get("note", "").strip()
    if not note:
        return error("La nota no puede estar vacía.")
    result = court.add_note(case_id, note)
    if not result["success"]:
        return error(result["message"])
    return success(**result)


# ─── METRICS ────────────────────────────────────────────────────────────────

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    return success(metrics=court.get_metrics())


# ─── LEGAL ARTICLES ─────────────────────────────────────────────────────────

@app.route("/api/laws", methods=["GET"])
def get_laws():
    crime_type = request.args.get("crime_type")
    articles = court.get_legal_articles(crime_type)
    return success(articles=articles)


# ─── QUEUE / HISTORY ────────────────────────────────────────────────────────

@app.route("/api/queue", methods=["GET"])
def get_queue():
    queue_cases = [c.to_dict() for c in court.get_pending_queue()]
    return success(queue=queue_cases)


@app.route("/api/history", methods=["GET"])
def get_history():
    history = [c.to_dict() for c in court.get_history()]
    return success(history=history)


# ─── CONFIG ─────────────────────────────────────────────────────────────────

@app.route("/api/config/apikey", methods=["POST"])
def set_api_key():
    body = request.get_json(force=True)
    key = body.get("api_key", "").strip()
    court.advisor.api_key = key
    return success(message="API Key actualizada correctamente.")


@app.route("/api/config", methods=["GET"])
def get_config():
    return success(
        has_api_key=bool(court.advisor.api_key),
        crime_types=[
            "Homicidio", "Robo agravado", "Fraude financiero",
            "Tráfico de estupefacientes", "Violencia doméstica",
            "Delitos informáticos", "Corrupción", "Secuestro"
        ],
        evidence_types=["Documental", "Testimonial", "Física", "Digital", "Pericial"],
        verdict_options=["Culpable", "No culpable", "Culpable con atenuantes"],
        stages=["Investigación", "Juicio", "Sentencia"],
    )


# ─── MAIN ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*55}")
    print(f"  ⚖️  SISTEMA JUDICIAL INTELIGENTE — Backend")
    print(f"{'='*55}")
    print(f"  Servidor:  http://localhost:{port}")
    print(f"  API Key:   {'✅ Configurada' if API_KEY else '⚠️  No configurada (modo demo)'}")
    print(f"{'='*55}\n")
    app.run(debug=True, port=port, host="0.0.0.0")
