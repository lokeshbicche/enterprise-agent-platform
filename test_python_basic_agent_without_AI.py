"""Unit tests for python_basic_agent_without_AI.py. Run with:  python -m unittest -v"""

import unittest

from python_basic_agent_without_AI import BasicAgent, calculator_tool


class TestCalculator(unittest.TestCase):
    def test_expression(self):
        self.assertEqual(calculator_tool("(12 + 8) * 3"), "(12 + 8) * 3 = 60")

    def test_power_caret(self):
        self.assertEqual(calculator_tool("2 ^ 10"), "2 ** 10 = 1024")

    def test_rejects_code(self):
        with self.assertRaises(ValueError):
            calculator_tool("__import__('os')")


class TestBasicAgent(unittest.TestCase):
    def setUp(self):
        self.agent = BasicAgent(verbose=False)

    def test_think_picks_calculator(self):
        plan = self.agent.think("calculate 1 + 1")
        self.assertEqual([s.tool_name for s in plan], ["calculator"])

    def test_multi_step_plan(self):
        plan = self.agent.think("what time is it and then calculate 2 * 3")
        self.assertEqual([s.tool_name for s in plan], ["time", "calculator"])

    def test_and_inside_text_is_not_split(self):
        plan = self.agent.think("count words in cats and dogs")
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0].tool_input, "cats and dogs")

    def test_remember_and_recall(self):
        self.agent.run("remember my city is Hyderabad")
        self.assertEqual(self.agent.run("what is my city"), "city is Hyderabad.")

    def test_tool_error_does_not_crash(self):
        self.assertIn("division by zero", self.agent.run("calculate 1 / 0"))

    def test_unknown_task(self):
        self.assertIn("don't know how", self.agent.run("sing me a song"))

    def test_empty_input(self):
        self.assertIn("help", self.agent.run("   "))

    def test_history_is_recorded(self):
        self.agent.run("calculate 2 + 2")
        roles = [h["role"] for h in self.agent.memory.history]
        self.assertEqual(roles, ["user", "tool", "agent"])


if __name__ == "__main__":
    unittest.main()
