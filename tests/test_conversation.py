import unittest
import json
import os
from unittest.mock import patch
from urllib.request import Request

from voice_agent.conversation import AgentState, get_next_question, handle_customer_utterance
from voice_agent.bolna_client import BolnaError, place_outbound_call, validate_phone_number


class ConversationFlowTests(unittest.TestCase):
    def test_busy_customer_flow(self):
        state = AgentState(customer_verified=None)
        result = handle_customer_utterance(state, "I am busy right now.")
        self.assertEqual(result["status"], "callback_pending")
        self.assertTrue(state.busy_customer)
        self.assertIn("call you back", get_next_question(state).lower() if get_next_question(state) else "")
        follow_up = handle_customer_utterance(state, "Tomorrow after 3 PM")
        self.assertEqual(follow_up["status"], "callback")
        self.assertEqual(state.callback_time, "Tomorrow after 3 PM")

    def test_transfer_flow(self):
        state = AgentState(customer_verified=True, offer_presented=True)
        result = handle_customer_utterance(state, "I already have a loan and want to reduce my EMI.")
        self.assertEqual(result["status"], "transfer")
        self.assertTrue(state.transfer_required)

    def test_agriculture_disqualification(self):
        state = AgentState(customer_verified=True, offer_presented=True)
        result = handle_customer_utterance(state, "It is agricultural land.")
        self.assertEqual(result["status"], "disqualified")
        self.assertTrue(state.disqualified)

    def test_out_of_order_answers_are_respected(self):
        state = AgentState(customer_verified=True, offer_presented=True)
        result = handle_customer_utterance(state, "It is residential, jointly owned, and worth around 80 lakh.")
        self.assertEqual(state.property_type, "residential")
        self.assertEqual(state.ownership_status, "joint")
        self.assertEqual(state.market_value, 8000000)
        self.assertIn("original property documents", (get_next_question(state) or "").lower())

    def test_max_loan_confirmation_flow(self):
        state = AgentState(customer_verified=True, offer_presented=True)
        result = handle_customer_utterance(state, "I need 90 lakh.")
        self.assertTrue(state.pending_max_loan_confirmation)
        self.assertIn("75 lakhs", result["response"])

    def test_cash_income_is_disqualified(self):
        state = AgentState(customer_verified=True, offer_presented=True)
        result = handle_customer_utterance(state, "I am self-employed and receive income in cash.")
        self.assertEqual(result["status"], "disqualified")
        self.assertTrue(state.disqualified)

    def test_invalid_tenure_is_disqualified(self):
        state = AgentState(customer_verified=True, offer_presented=True)
        result = handle_customer_utterance(state, "I would like a 2 year tenure.")
        self.assertEqual(result["status"], "disqualified")

    def test_customer_name_is_used_in_greeting(self):
        state = AgentState(customer_name="Asha")
        self.assertEqual(get_next_question(state), "Hello, may I speak with Asha?")

    def test_customer_can_complete_qualification(self):
        state = AgentState(customer_verified=True, offer_presented=True)
        answers = [
            "residential",
            "sole owner",
            "original documents are available",
            "I need 50 lakh",
            "I am salaried and income comes through bank",
            "The property is worth 80 lakh",
            "I want a 10 year tenure",
        ]
        result = None
        for answer in answers:
            result = handle_customer_utterance(state, answer)
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "complete")


class BolnaClientTests(unittest.TestCase):
    def test_validates_international_phone_number(self):
        self.assertEqual(validate_phone_number(" +919876543210 "), "+919876543210")
        with self.assertRaises(ValueError):
            validate_phone_number("9876543210")

    @patch.dict(os.environ, {"BOLNA_API_KEY": "test-key", "BOLNA_AGENT_ID": "agent-123"})
    @patch("voice_agent.bolna_client.urlopen")
    def test_places_call_with_bolna(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps(
            {"execution_id": "123e4567-e89b-12d3-a456-426614174000", "status": "queued"}
        ).encode()

        result = place_outbound_call("+919876543210")

        self.assertEqual(result["status"], "queued")
        request = mock_urlopen.call_args.args[0]
        self.assertIsInstance(request, Request)
        self.assertEqual(request.full_url, "https://api.bolna.ai/call")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(
            json.loads(request.data),
            {"agent_id": "agent-123", "recipient_phone_number": "+919876543210"},
        )

    @patch.dict(os.environ, {"BOLNA_AGENT_ID": "agent-123"}, clear=True)
    def test_missing_bolna_key_is_reported(self):
        with self.assertRaisesRegex(BolnaError, "BOLNA_API_KEY"):
            place_outbound_call("+919876543210")


if __name__ == "__main__":
    unittest.main()
