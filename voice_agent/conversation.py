from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Optional

MAX_LOAN_AMOUNT = 7_500_000


@dataclass
class AgentState:
    company_name: str = "Home Credit"
    customer_name: str = "Rahul"
    agent_name: str = "Priya"
    agent_gender: str = "female"
    language_to_speak: str = "English"

    customer_verified: Optional[bool] = None
    busy_customer: bool = False
    callback_time: Optional[str] = None
    callback_time_requested: bool = False
    offer_presented: bool = False
    transfer_required: bool = False
    disqualified: bool = False
    pending_max_loan_confirmation: bool = False
    final_handoff_done: bool = False

    property_type: Optional[str] = None
    ownership_status: Optional[str] = None
    documents_available: Optional[bool] = None
    loan_amount: Optional[int] = None
    occupation: Optional[str] = None
    income_mode: Optional[str] = None
    market_value: Optional[int] = None
    tenure: Optional[int] = None
    conversation_history: list[str] = field(default_factory=list)


QUESTION_ORDER = [
    "property_type",
    "ownership_status",
    "documents_available",
    "loan_amount",
    "occupation",
    "income_mode",
    "market_value",
    "tenure",
]


def normalize_text(text: str) -> str:
    return " ".join((text or "").lower().split())


def parse_rupee_amount(raw_text: str) -> Optional[int]:
    if raw_text is None:
        return None
    text = normalize_text(raw_text).replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lakhs|crore|crores|rupees|rs|rs\.)?", text)
    if not match:
        match = re.search(r"(\d+(?:\.\d+)?)", text)
        if not match:
            return None
    amount = float(match.group(1))
    unit = match.group(2) or ""
    if "crore" in unit:
        amount *= 10000000
    elif "lakh" in unit:
        amount *= 100000
    return int(amount)


def _ask_for_max_loan(state: AgentState) -> str:
    return "The current offer is available for up to Rs 75 lakhs. Would you like to proceed with the maximum eligible amount of Rs 75 lakhs?"


def _set_property_type(state: AgentState, value: str) -> None:
    state.property_type = value


def _set_ownership(state: AgentState, value: str) -> None:
    state.ownership_status = value


def _set_documents(state: AgentState, value: bool) -> None:
    state.documents_available = value


def _set_occupation(state: AgentState, value: str) -> None:
    state.occupation = value


def _set_income_mode(state: AgentState, value: str) -> None:
    state.income_mode = value


def _extract_customer_identity(state: AgentState, text: str) -> bool:
    cues = [
        "this is ",
        "this is rahul",
        "yes this is",
        "speaking",
        "yes it's me",
        "hello this is",
    ]
    return any(cue in text for cue in cues)


def _capture_eligibility_facts(state: AgentState, text: str) -> None:
    if "residential" in text or "house" in text or "flat" in text or "apartment" in text:
        state.property_type = "residential"
    if "commercial" in text or "shop" in text or "office" in text:
        state.property_type = "commercial"
    if "industrial" in text or "factory" in text or "warehouse" in text:
        state.property_type = "industrial"
    if "agricultural" in text or "farm land" in text or "agri" in text or "farmland" in text:
        state.disqualified = True

    if "joint" in text or "with my wife" in text or "with my husband" in text or "with my brother" in text or "with my partner" in text:
        state.ownership_status = "joint"
    if "sole" in text or "my own" in text or "only i" in text or "self owned" in text:
        state.ownership_status = "sole"

    if "original" in text and ("available" in text or "ready" in text or "with me" in text or "at home" in text):
        state.documents_available = True
    if "photocopy" in text or "copy only" in text or "no original" in text or "not available" in text:
        state.documents_available = False

    if "loan" in text or "borrow" in text or "need" in text or "amount" in text:
        amount = parse_rupee_amount(text)
        if amount is not None:
            if amount > MAX_LOAN_AMOUNT:
                state.pending_max_loan_confirmation = True
            else:
                state.loan_amount = amount

    if "salaried" in text or "salary" in text or "employee" in text or "job" in text:
        state.occupation = "salaried"
    if "self employed" in text or "business" in text or "own business" in text or "self-employed" in text:
        state.occupation = "self-employed"

    if "bank" in text or "bank account" in text or "salary in bank" in text:
        state.income_mode = "bank"
    if "cash" in text or "cash income" in text:
        state.income_mode = "cash"

    if "worth" in text or "value" in text or "market value" in text or "property" in text:
        amount = parse_rupee_amount(text)
        if amount is not None:
            state.market_value = amount

    if "year" in text or "years" in text:
        years = re.search(r"(\d+)\s*year", text)
        if years:
            state.tenure = int(years.group(1))


def _is_busy_customer(text: str) -> bool:
    busy_terms = [
        "busy right now",
        "i am busy",
        "currently busy",
        "not a good time",
        "call me back",
        "can you call later",
    ]
    return any(term in text for term in busy_terms)


def _should_transfer(text: str) -> bool:
    transfer_terms = [
        "existing loan",
        "already have a loan",
        "reduce my emi",
        "emi reduction",
        "loan transfer",
        "balance transfer",
    ]
    return any(term in text for term in transfer_terms)


def get_next_question(state: AgentState) -> Optional[str]:
    if state.disqualified:
        return None
    if state.transfer_required:
        return None
    if state.busy_customer:
        return "Certainly, I understand. What would be a convenient time for us to call you back?"
    if state.pending_max_loan_confirmation:
        return _ask_for_max_loan(state)
    if state.customer_verified is not True:
        return f"Hello, may I speak with {state.customer_name}?"
    if not state.offer_presented:
        return "As one of our valued customers, you may be eligible for a special Loan Against Property offer of up to Rs 75 lakhs. I would like to ask a few quick questions to check whether you qualify."

    if state.property_type is None:
        return "What type of property do you own?"
    if state.ownership_status is None:
        return "Is the property in your sole name or is it jointly owned?"
    if state.documents_available is None:
        return "Do you have the original property documents available for verification?"
    if state.loan_amount is None:
        return "How much loan amount do you need?"
    if state.occupation is None or state.income_mode is None:
        return "What is your occupation, and is your income received through the bank or in cash?"
    if state.market_value is None:
        return "Approximately what is the current market value of the property?"
    if state.tenure is None:
        return "What repayment tenure do you prefer in years?"

    return "Thank you. I am noting the information and will continue with the next question."


def handle_customer_utterance(state: AgentState, utterance: str) -> dict:
    text = normalize_text(utterance)
    state.conversation_history.append(utterance)

    if not text:
        return {"status": "continue", "response": "Please tell me a little more about your situation.", "next_question": get_next_question(state)}

    if state.callback_time_requested:
        state.callback_time = utterance.strip()
        state.callback_time_requested = False
        return {
            "status": "callback",
            "response": "Thank you. We will call you back at that convenient time. Goodbye.",
            "next_question": None,
        }

    if state.pending_max_loan_confirmation:
        if "yes" in text or "proceed" in text or "okay" in text or "sure" in text:
            state.loan_amount = MAX_LOAN_AMOUNT
            state.pending_max_loan_confirmation = False
            return {
                "status": "continue",
                "response": "Thank you. I have updated the maximum eligible amount to Rs 75 lakhs and will continue.",
                "next_question": get_next_question(state),
            }
        if "no" in text or "not interested" in text or "cancel" in text:
            state.disqualified = True
            return {
                "status": "ended",
                "response": "Thank you for your time. We can revisit this later if needed.",
                "next_question": None,
            }

    if state.customer_verified is None and (
        _extract_customer_identity(state, text)
        or text in {"yes", "yes it is", "that's me", "that is me", "yep", "yeah"}
    ):
        state.customer_verified = True
        state.offer_presented = True
        return {
            "status": "verified",
            "response": (
                f"Thank you, {state.customer_name}. As one of our valued customers, "
                "you may be eligible for a special Loan Against Property offer of up to Rs 75 lakhs. "
                "I would like to ask a few quick questions to check whether you qualify."
            ),
            "next_question": get_next_question(state),
        }

    if state.customer_verified is not True and _is_busy_customer(text):
        state.busy_customer = True
        state.customer_verified = False
        state.callback_time_requested = True
        return {
            "status": "callback_pending",
            "response": "Certainly, I understand. What would be a convenient time for us to call you back?",
            "next_question": None,
        }

    if _should_transfer(text):
        state.transfer_required = True
        return {
            "status": "transfer",
            "response": "Thank you for clarifying. Since you already have an existing loan on the property, this would need to be handled by our loan-transfer specialist. A specialist will contact you shortly regarding this. Thank you for your time.",
            "next_question": None,
        }

    if state.customer_verified is None and not _extract_customer_identity(state, text):
        return {
            "status": "continue",
            "response": f"Hello, may I speak with {state.customer_name}?",
            "next_question": get_next_question(state),
        }

    _capture_eligibility_facts(state, text)

    if state.disqualified:
        return {
            "status": "disqualified",
            "response": "Thank you for your time. Based on the information provided, you do not meet the criteria for this specific offer at this time.",
            "next_question": None,
        }

    if state.documents_available is False or state.income_mode == "cash":
        state.disqualified = True
        return {
            "status": "disqualified",
            "response": "Thank you for your time. Based on the information provided, you do not meet the criteria for this specific offer at this time.",
            "next_question": None,
        }

    if state.tenure is not None and not 3 <= state.tenure <= 15:
        state.disqualified = True
        return {
            "status": "disqualified",
            "response": "Thank you for your time. This offer requires a repayment tenure between 3 and 15 years, so you do not meet the criteria for this specific offer at this time.",
            "next_question": None,
        }

    if state.transfer_required:
        return {
            "status": "transfer",
            "response": "Thank you for clarifying. Since you already have an existing loan on the property, this would need to be handled by our loan-transfer specialist. A specialist will contact you shortly regarding this. Thank you for your time.",
            "next_question": None,
        }

    if not state.offer_presented and state.customer_verified is True:
        state.offer_presented = True
        return {
            "status": "continue",
            "response": "As one of our valued customers, you may be eligible for a special Loan Against Property offer of up to Rs 75 lakhs. I would like to ask a few quick questions to check whether you qualify.",
            "next_question": get_next_question(state),
        }

    if state.pending_max_loan_confirmation:
        return {
            "status": "awaiting_max_confirmation",
            "response": _ask_for_max_loan(state),
            "next_question": _ask_for_max_loan(state),
        }

    required_fields = [
        "property_type",
        "ownership_status",
        "documents_available",
        "loan_amount",
        "occupation",
        "income_mode",
        "market_value",
        "tenure",
    ]
    if state.offer_presented and all(getattr(state, key) is not None for key in required_fields):
        state.final_handoff_done = True
        return {
            "status": "complete",
            "response": "Thank you. Based on the information provided, you appear to be eligible for the offer. A senior loan expert will contact you shortly regarding the exact interest rates and next steps.",
            "next_question": None,
        }

    next_question = get_next_question(state)
    if next_question is None:
        state.final_handoff_done = True
        return {
            "status": "complete",
            "response": "Thank you. Based on the information provided, you appear to be eligible for the offer. A senior loan expert will contact you shortly regarding the exact interest rates and next steps.",
            "next_question": None,
        }

    return {
        "status": "continue",
        "response": "Thank you. I have noted that information.",
        "next_question": next_question,
    }
