"""Os nós do workflow de simulação adaptativa.

Fluxo:
    preparar_simulacao → executar_simulacao → avaliar_resultado → persistir_simulacao
"""

from __future__ import annotations

import json
from datetime import datetime
import concurrent.futures
from typing import Any, Dict, List

from sqlalchemy.exc import SQLAlchemyError

from assistente_estudos.db.database import SessionLocal
from assistente_estudos.db.models import ResultadoSimulado
from assistente_estudos.nodes.simulation.state import SimulationState
from assistente_estudos.services.llm_service import llm


def _fallback_questions(topic: str, difficulty: str) -> List[Dict[str, Any]]:
    base = topic.strip() or "tema"
    return [
        {
            "topico": base,
            "pergunta": f"Em uma questão sobre {base}, qual alternativa melhor representa o conteúdo central?",
            "opcoes": [
                f"Conceito principal de {base}",
                "Uma ideia sem relação com o tema",
                "Um detalhe secundário isolado",
                "Uma afirmação incorreta",
            ],
            "resposta_correta": f"Conceito principal de {base}",
            "dificuldade": difficulty,
        },
        {
            "topico": base,
            "pergunta": f"Como {base} pode aparecer em um contexto aplicado?",
            "opcoes": [
                f"Na resolução de problemas ligados a {base}",
                "Apenas em memorização mecânica",
                "Sem nenhuma aplicação prática",
                "Somente em exemplos aleatórios",
            ],
            "resposta_correta": f"Na resolução de problemas ligados a {base}",
            "dificuldade": difficulty,
        },
        {
            "topico": base,
            "pergunta": f"Ao estudar {base}, qual atitude ajuda mais no desempenho?",
            "opcoes": [
                "Resolver exercícios com contexto",
                "Ignorar exemplos",
                "Decorar respostas sem entender",
                "Trocar o assunto por outro tema",
            ],
            "resposta_correta": "Resolver exercícios com contexto",
            "dificuldade": difficulty,
        },
    ]


def _fallback_questions_for_count(topic: str, difficulty: str, quantity: int) -> List[Dict[str, Any]]:
    generated: List[Dict[str, Any]] = []
    base_questions = _fallback_questions(topic, difficulty)
    if quantity <= 0:
        return []

    while len(generated) < quantity:
        generated.extend(base_questions)
    return generated[:quantity]


def _extract_topics(state: SimulationState) -> List[str]:
    current_plan = state.get("current_plan", {}) or {}
    topics = current_plan.get("topics", [])
    if isinstance(topics, list):
        return [str(topic) for topic in topics if str(topic).strip()]
    return []


def _build_prompt(topic: str, difficulty: str, quantity: int) -> str:
    return (
        f"Gere {quantity} questões de múltipla escolha sobre '{topic}' (dificuldade: {difficulty}). "
        "Retorne SOMENTE um JSON válido (lista). "
        "Cada item: id, topico, pergunta, opcoes (4 strings), resposta_correta (uma das opções). "
        "Seja direto; não inclua explicações extras."
    )


def _parse_llm_response(response: Any) -> List[Dict[str, Any]]:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
        except Exception:
            return []
    else:
        parsed = content

    if isinstance(parsed, dict):
        parsed = parsed.get("questoes") or parsed.get("questions") or [parsed]

    if not isinstance(parsed, list):
        return []

    def _get_field(obj: Dict[str, Any], candidates: List[str]):
        for k in candidates:
            if k in obj:
                return obj.get(k)
        return None

    normalized: List[Dict[str, Any]] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue

        pergunta = _get_field(item, ["pergunta", "question", "prompt", "texto"])
        opcoes = _get_field(item, ["opcoes", "alternativas", "options", "choices", "alternatives"])
        resposta = _get_field(item, ["resposta_correta", "gabarito", "answer", "correct", "resposta"])

        if pergunta is None:
            continue

        # Normalize options to list of strings
        if isinstance(opcoes, str):
            try:
                # try parse stringified list
                op = json.loads(opcoes)
                if isinstance(op, list):
                    opcoes = op
            except Exception:
                # fallback: split by newline or ';'
                parts = [p.strip() for p in opcoes.split("\n") if p.strip()] if isinstance(opcoes, str) else []
                if parts:
                    opcoes = parts

        if not isinstance(opcoes, list):
            opcoes = []

        # Ensure all options are strings and unique
        cleaned = []
        for o in opcoes:
            if o is None:
                continue
            s = str(o).strip()
            if s and s not in cleaned:
                cleaned.append(s)

        # If fewer than 4, append generic distractors
        filler_index = 1
        while len(cleaned) < 4:
            candidate = f"Opção incorreta {filler_index}"
            if candidate not in cleaned:
                cleaned.append(candidate)
            filler_index += 1

        # If more than 4, trim but try to keep the indicated correct answer
        if len(cleaned) > 4:
            # try to keep item that matches resposta
            if resposta:
                resp_str = str(resposta).strip()
                if resp_str in cleaned:
                    # put correct answer first, then others
                    cleaned.remove(resp_str)
                    cleaned = [resp_str] + cleaned[:3]
                else:
                    cleaned = cleaned[:4]
            else:
                cleaned = cleaned[:4]

        if len(cleaned) != 4:
            continue

        # Determine resposta_correta value
        resposta_correta = None
        if resposta:
            r = str(resposta).strip()
            # if resposta indicates index (0-based or 1-based)
            if r.isdigit():
                idx = int(r)
                if 0 <= idx < len(cleaned):
                    resposta_correta = cleaned[idx]
                elif 1 <= idx <= len(cleaned):
                    resposta_correta = cleaned[idx - 1]
            else:
                # try to match exact option
                for opt in cleaned:
                    if opt.lower() == r.lower():
                        resposta_correta = opt
                        break

        # if still unknown, assume first option is correct (fallback)
        if not resposta_correta:
            resposta_correta = cleaned[0]

        normalized.append({
            "pergunta": str(pergunta).strip(),
            "opcoes": cleaned,
            "resposta_correta": resposta_correta,
        })

    return normalized


def _invoke_llm_with_timeout(prompt: str, timeout_seconds: int = 15) -> Any:
    """Invoca o LLM com timeout; retorna o resultado ou lança concurrent.futures.TimeoutError."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(llm.invoke, prompt)
        try:
            return future.result(timeout=timeout_seconds)
        except concurrent.futures.TimeoutError:
            try:
                future.cancel()
            except Exception:
                pass
            raise


def preparar_simulacao_node(state: SimulationState) -> SimulationState:
    """Gera as questões do simulado adaptadas ao plano e nível do usuário.

    Usa o LLM quando disponível e faz fallback local se a resposta vier inválida.
    """
    difficulty = state.get("nivel_dificuldade", "intermediario")
    topics = _extract_topics(state)
    requested = int(state.get("quantity_questions") or 5)
    if requested < 1:
        requested = 5
    MAX_TOTAL = 10
    total_questions = min(requested, MAX_TOTAL)

    questions: List[Dict[str, Any]] = []
    n_topics = len(topics) or 0
    if n_topics == 0:
        return state

    base = total_questions // n_topics
    remainder = total_questions % n_topics

    for i, topic in enumerate(topics):
        per_topic = base + (1 if i < remainder else 0)
        if per_topic <= 0:
            continue

        try:
            # tente chamar o LLM com timeout; em caso de TimeoutError irá para fallback
            response = _invoke_llm_with_timeout(_build_prompt(topic, difficulty, per_topic), timeout_seconds=12)
            # guarde resposta bruta para depuração se necessário
            try:
                state.setdefault("llm_raw_responses", []).append(getattr(response, "content", response))
            except Exception:
                pass
            parsed = _parse_llm_response(response)
        except concurrent.futures.TimeoutError:
            parsed = []
        except Exception:
            parsed = []

        if not parsed:
            parsed = _fallback_questions_for_count(topic, difficulty, per_topic)

        if len(parsed) > per_topic:
            parsed = parsed[:per_topic]

        for item in parsed:
            item.setdefault("topico", topic)
            item.setdefault("dificuldade", difficulty)

        questions.extend(parsed)

    state["questoes"] = questions
    return state


def executar_simulacao_node(state: SimulationState) -> SimulationState:
    """Processa as respostas do usuário e ajusta a dificuldade dinamicamente.

    Faz uma correção simples comparando `respostas` com `questoes`, consolida um
    resumo em `simulation_output` e ajusta `nivel_dificuldade` de forma básica.
    """
    questions = state.get("questoes", []) or []
    respostas = state.get("respostas", []) or []

    def _normalize(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, dict):
            for key in ("resposta", "answer", "valor", "value", "opcao"):
                if key in value:
                    return _normalize(value.get(key))
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return str(value).strip().lower()

    def _question_key(question: Dict[str, Any], index: int) -> str:
        return _normalize(question.get("pergunta")) or f"questao-{index}"

    answers_by_key: Dict[str, Any] = {}
    for index, resposta in enumerate(respostas):
        if isinstance(resposta, dict):
            if "indice_questao" in resposta:
                try:
                    question_index = int(resposta.get("indice_questao"))
                    if 0 <= question_index < len(questions):
                        answers_by_key[_question_key(questions[question_index], question_index)] = resposta
                        continue
                except Exception:
                    pass

            pergunta = resposta.get("pergunta") or resposta.get("question")
            if pergunta:
                answers_by_key[_normalize(pergunta)] = resposta
                continue

        if index < len(questions):
            answers_by_key[_question_key(questions[index], index)] = resposta

    total = 0
    acertos = 0
    detalhes: List[Dict[str, Any]] = []

    for index, question in enumerate(questions):
        total += 1
        key = _question_key(question, index)
        raw_answer = answers_by_key.get(key)

        if isinstance(raw_answer, dict):
            user_answer = raw_answer.get("resposta") or raw_answer.get("answer") or raw_answer.get("valor") or raw_answer.get("value")
        else:
            user_answer = raw_answer

        correct_answer = question.get("resposta_correta")
        is_correct = _normalize(user_answer) == _normalize(correct_answer) and _normalize(user_answer) != ""

        if is_correct:
            acertos += 1

        detalhes.append(
            {
                "pergunta": question.get("pergunta"),
                "resposta_usuario": user_answer,
                "resposta_correta": correct_answer,
                "correto": is_correct,
                "topico": question.get("topico"),
            }
        )

    percentual = round((acertos / total) * 100, 2) if total else 0.0
    dificuldade_atual = str(state.get("nivel_dificuldade", "intermediario")).lower()

    if percentual >= 80:
        nova_dificuldade = "avancado" if dificuldade_atual != "avancado" else dificuldade_atual
    elif percentual < 50:
        nova_dificuldade = "basico" if dificuldade_atual != "basico" else dificuldade_atual
    else:
        nova_dificuldade = "intermediario"

    state["nivel_dificuldade"] = nova_dificuldade
    state["simulation_output"] = {
        "total_questoes": total,
        "acertos": acertos,
        "percentual_acerto": percentual,
        "nivel_dificuldade_ajustado": nova_dificuldade,
        "detalhes": detalhes,
    }
    return state


def avaliar_resultado_node(state: SimulationState) -> SimulationState:
    """Calcula a taxa de acerto por tópico e consolida simulation_output.

    Consolida as métricas por tópico sem perder o resumo global produzido na etapa anterior.
    """
    simulation_output = state.get("simulation_output", {}) or {}
    detalhes = simulation_output.get("detalhes", []) or []

    por_topico: Dict[str, Dict[str, Any]] = {}
    total_questoes = 0
    total_acertos = 0

    for item in detalhes:
        if not isinstance(item, dict):
            continue

        topico = str(item.get("topico") or "geral")
        correto = bool(item.get("correto", False))

        if topico not in por_topico:
            por_topico[topico] = {
                "total": 0,
                "acertos": 0,
                "erros": 0,
                "percentual_acerto": 0.0,
            }

        por_topico[topico]["total"] += 1
        total_questoes += 1

        if correto:
            por_topico[topico]["acertos"] += 1
            total_acertos += 1
        else:
            por_topico[topico]["erros"] += 1

    for topico, resumo in por_topico.items():
        total = resumo["total"]
        resumo["percentual_acerto"] = round((resumo["acertos"] / total) * 100, 2) if total else 0.0

    percentual_global = round((total_acertos / total_questoes) * 100, 2) if total_questoes else 0.0

    simulation_output.update(
        {
            "por_topico": por_topico,
            "total_questoes": total_questoes,
            "acertos": total_acertos,
            "percentual_acerto": percentual_global,
        }
    )
    state["simulation_output"] = simulation_output
    return state


def persistir_simulacao_node(state: SimulationState) -> SimulationState:
    """Salva o resultado do simulado no banco.

    Persiste no banco de dados como fonte única de armazenamento.
    """
    try:
        usuario_id = state.get("usuario_id")
        if not usuario_id:
            raise ValueError("usuario_id ausente no estado da simulação")

        simulation_output = state.get("simulation_output", {}) or {}
        por_topico = simulation_output.get("por_topico", {}) or {}
        current_plan = state.get("current_plan", {}) or {}
        disciplina_padrao = str(current_plan.get("discipline") or current_plan.get("disciplina") or current_plan.get("subject") or "simulacao")

        db = SessionLocal()
        inserted_ids: List[str] = []
        try:
            if por_topico:
                for topico, resumo in por_topico.items():
                    total_questoes = int(resumo.get("total", 0) or 0)
                    acertos = int(resumo.get("acertos", 0) or 0)
                    taxa_acerto = round((acertos / total_questoes), 4) if total_questoes else 0.0
                    resultado = ResultadoSimulado(
                        usuario_id=str(usuario_id),
                        disciplina=disciplina_padrao,
                        topico=str(topico),
                        data=datetime.utcnow(),
                        total_questoes=total_questoes,
                        acertos=acertos,
                        taxa_acerto=taxa_acerto,
                        nivel_dificuldade=str(state.get("nivel_dificuldade", "intermediario")),
                    )
                    db.add(resultado)
                    db.flush()
                    inserted_ids.append(str(resultado.id))
            else:
                total_questoes = int(simulation_output.get("total_questoes", len(state.get("questoes", [])) or 0) or 0)
                acertos = int(simulation_output.get("acertos", 0) or 0)
                taxa_acerto = round((acertos / total_questoes), 4) if total_questoes else 0.0
                topico = str(current_plan.get("subject") or current_plan.get("topico") or "geral")
                resultado = ResultadoSimulado(
                    usuario_id=str(usuario_id),
                    disciplina=disciplina_padrao,
                    topico=topico,
                    data=datetime.utcnow(),
                    total_questoes=total_questoes,
                    acertos=acertos,
                    taxa_acerto=taxa_acerto,
                    nivel_dificuldade=str(state.get("nivel_dificuldade", "intermediario")),
                )
                db.add(resultado)
                db.flush()
                inserted_ids.append(str(resultado.id))

            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        state["simulado_id"] = inserted_ids[0] if len(inserted_ids) == 1 else ",".join(inserted_ids)
        state["persistido"] = True
        state["persistido_em"] = datetime.utcnow().isoformat()
        state["persistencia"] = {
            "db": "resultados_simulados",
            "ids": inserted_ids,
        }
        return state
    except (SQLAlchemyError, ValueError, Exception) as exc:
        state["persistido"] = False
        state["erro"] = f"Falha ao persistir simulado: {exc}"
        return state
