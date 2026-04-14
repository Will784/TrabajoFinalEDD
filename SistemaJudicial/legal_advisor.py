import json
import urllib.request
import urllib.error
from data_structures import LegalArticlesArray


# ─────────────────────────────────────────────
# LEGAL ARTICLES DATABASE  (Array)
# ─────────────────────────────────────────────

class LegalDatabase:

    def __init__(self):
        self._array = LegalArticlesArray(capacity=300)
        self._seed_articles()

    def _seed_articles(self) -> None:
        articles = [
            # Homicidio
            {"code": "CP-103", "title": "Homicidio simple", "category": "Homicidio",
             "description": "El que matare a otro incurrirá en prisión de trece (13) a veinticinco (25) años.",
             "min_years": 13, "max_years": 25},
            {"code": "CP-104", "title": "Homicidio agravado", "category": "Homicidio",
             "description": "Pena aumentada a 25-40 años cuando concurran circunstancias de agravación.",
             "min_years": 25, "max_years": 40},

            # Robo
            {"code": "CP-239", "title": "Hurto simple", "category": "Robo agravado",
             "description": "El que se apodere de una cosa mueble ajena con fines de provecho.",
             "min_years": 2, "max_years": 6},
            {"code": "CP-240", "title": "Hurto calificado", "category": "Robo agravado",
             "description": "Pena de prisión de seis (6) a catorce (14) años.",
             "min_years": 6, "max_years": 14},

            # Fraude
            {"code": "CP-246", "title": "Estafa", "category": "Fraude financiero",
             "description": "El que obtenga provecho ilícito para sí o para un tercero.",
             "min_years": 2, "max_years": 8},
            {"code": "CP-323", "title": "Lavado de activos", "category": "Fraude financiero",
             "description": "Pena de prisión de diez (10) a treinta (30) años.",
             "min_years": 10, "max_years": 30},

            # Drogas
            {"code": "L-30-1986-Art33", "title": "Tráfico de estupefacientes",
             "category": "Tráfico de estupefacientes",
             "description": "Pena de prisión de diez (10) a veinte (20) años.",
             "min_years": 10, "max_years": 20},

            # Violencia doméstica
            {"code": "L-1257-2008", "title": "Violencia intrafamiliar",
             "category": "Violencia doméstica",
             "description": "Prisión de cuatro (4) a ocho (8) años.",
             "min_years": 4, "max_years": 8},

            # Delitos informáticos
            {"code": "L-1273-2009-Art269", "title": "Acceso abusivo a sistemas informáticos",
             "category": "Delitos informáticos",
             "description": "Prisión de cuarenta y ocho (48) a noventa y seis (96) meses.",
             "min_years": 4, "max_years": 8},

            # Corrupción
            {"code": "CP-397", "title": "Peculado por apropiación",
             "category": "Corrupción",
             "description": "Prisión de seis (6) a quince (15) años.",
             "min_years": 6, "max_years": 15},
            {"code": "CP-405", "title": "Cohecho propio", "category": "Corrupción",
             "description": "Prisión de cinco (5) a diez (10) años.",
             "min_years": 5, "max_years": 10},

            # Secuestro
            {"code": "CP-168", "title": "Secuestro simple", "category": "Secuestro",
             "description": "Prisión de doce (12) a veinte (20) años.",
             "min_years": 12, "max_years": 20},
            {"code": "CP-169", "title": "Secuestro extorsivo", "category": "Secuestro",
             "description": "Prisión de dieciocho (18) a veintiocho (28) años.",
             "min_years": 18, "max_years": 28},

            # Principios generales
            {"code": "CP-ART3", "title": "Principio de legalidad", "category": "General",
             "description": "Nadie podrá ser juzgado sino conforme a las leyes preexistentes al acto.",
             "min_years": 0, "max_years": 0},
            {"code": "CP-ART29", "title": "Debido proceso", "category": "General",
             "description": "Toda persona se presume inocente mientras no se le haya declarado judicialmente culpable.",
             "min_years": 0, "max_years": 0},
            {"code": "CP-ART55", "title": "Circunstancias de atenuación punitiva",
             "category": "General",
             "description": "La pena se reducirá hasta en una tercera parte si hay confesión antes de sentencia.",
             "min_years": 0, "max_years": 0},
        ]
        for art in articles:
            self._array.add(art)

    def get_articles_for_crime(self, crime_type: str) -> list:
        specific = self._array.search_by_category(crime_type)
        general = self._array.search_by_category("General")
        return specific + general

    def get_all(self) -> list:
        return self._array.to_list()

    def get_by_index(self, index: int) -> dict:
        return self._array.get(index)

    def __len__(self) -> int:
        return len(self._array)




    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.legal_db = LegalDatabase()

    def _build_case_context(self, case, question: str) -> str:
        evidence_list = case.get_all_evidence()
        evidence_text = "\n".join([
            f"- [{e['evidence_type']}] {e['name']}: {e['description']} (Relevancia: {e['relevance_score']}/10)"
            for e in evidence_list
        ]) if evidence_list else "Sin evidencia registrada aún."

        articles = self.legal_db.get_articles_for_crime(case.crime_type)
        articles_text = "\n".join([
            f"- {a['code']}: {a['title']} ({a['min_years']}-{a['max_years']} años)"
            for a in articles[:6]
        ])

        notes_text = "\n".join([f"- {n['text']}" for n in case.get('notes', [])]) if isinstance(case, dict) else \
                     "\n".join([f"- {n['text']}" for n in case.notes])

        if isinstance(case, dict):
            c = case
        else:
            c = case.to_dict()

        return f"""
=== EXPEDIENTE JUDICIAL ===
Caso: {c['case_id']} | {c['title']}
Tipo de delito: {c['crime_type']}
Acusado: {c['defendant']}
Fiscal: {c['prosecutor']}
Juez: {c['judge']}
Etapa actual: {c['current_stage']}
Descripción: {c['description']}

--- EVIDENCIA ({c['evidence_count']} elementos) ---
{evidence_text}

--- ARTÍCULOS LEGALES APLICABLES ---
{articles_text}

--- NOTAS DEL CASO ---
{notes_text if notes_text else 'Sin notas.'}

=== CONSULTA DEL OPERADOR JUDICIAL ===
{question}
"""

    def ask(self, case, question: str) -> str:
        """Send a question about a case to the AI and return the response."""
        if not self.api_key:
            return self._fallback_response(case, question)

        context = self._build_case_context(case, question)

        payload = {
            "model": self.MODEL,
            "max_tokens": self.MAX_TOKENS,
            "system": self.SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": context}],
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.API_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["content"][0]["text"]
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            return f"Error de API ({e.code}): {body}"
        except Exception as e:
            return f"Error de conexión: {str(e)}"

    def _fallback_response(self, case, question: str) -> str:
        """
        Demo fallback when no API key is provided.
        Generates a structured legal analysis based on local logic.
        """
        if isinstance(case, dict):
            c = case
        else:
            c = case.to_dict()

        evidence_list = c.get("evidence", [])
        evidence_count = len(evidence_list)
        avg_relevance = sum(e["relevance_score"] for e in evidence_list) / max(evidence_count, 1)

        articles = self.legal_db.get_articles_for_crime(c["crime_type"])
        main_article = articles[0] if articles else {"code": "CP-ART3", "title": "Principio de legalidad", "min_years": 0, "max_years": 10}

        # Heuristic verdict
        if avg_relevance >= 7 and evidence_count >= 3:
            verdict = "Culpable"
            confidence = "Alta"
            sentence_range = f"{main_article['min_years']} - {main_article['max_years']} años"
        elif avg_relevance >= 5 and evidence_count >= 2:
            verdict = "Culpable con atenuantes"
            confidence = "Moderada"
            sentence_range = f"{main_article['min_years']} - {int(main_article['max_years']*0.7)} años (reducción por atenuantes)"
        else:
            verdict = "Dudas razonables / No culpable"
            confidence = "Baja"
            sentence_range = "Absolución recomendada"

        evidence_summary = "\n".join([
            f"  • {e['name']} (Tipo: {e['evidence_type']}, Relevancia: {e['relevance_score']}/10)"
            for e in evidence_list
        ]) or "  • No se ha incorporado evidencia al expediente."

        articles_text = "\n".join([
            f"  • {a['code']}: {a['title']} — Pena: {a['min_years']}-{a['max_years']} años"
            for a in articles[:4]
        ])

        return f"""## 📋 Análisis Jurídico

**Dr. Justus** — Asesor Legal del Sistema Judicial

Sobre el caso **{c['case_id']} – {c['title']}** ({c['crime_type']}), acusado: **{c['defendant']}**.

Etapa procesal actual: **{c['current_stage']}**

---

## ⚖️ Artículos Aplicables

{articles_text}

---

## 🔍 Evaluación de Evidencia

Se han incorporado **{evidence_count} elemento(s)** probatorio(s) al expediente:

{evidence_summary}

**Relevancia promedio:** {avg_relevance:.1f}/10  
**Solidez probatoria:** {"Alta ✅" if avg_relevance >= 7 else "Moderada ⚠️" if avg_relevance >= 5 else "Débil ❌"}

---

## 🏛️ Recomendación de Sentencia

| Criterio | Evaluación |
|---|---|
| Veredicto sugerido | **{verdict}** |
| Confianza | {confidence} |
| Rango de pena | {sentence_range} |

**Justificación:** Basado en el análisis de la evidencia disponible y la aplicación del artículo {main_article['code']}, 
{"la acumulación de evidencia con alta relevancia permite establecer responsabilidad penal con suficiente certeza." if verdict == "Culpable" else "la evidencia presenta inconsistencias que generan duda razonable sobre la culpabilidad del acusado." if "No culpable" in verdict else "existe evidencia suficiente pero se recomiendan circunstancias atenuantes conforme al Art. CP-55."}



*— Dr. Justus, Asesor Legal del Sistema Judicial Inteligente*"""
