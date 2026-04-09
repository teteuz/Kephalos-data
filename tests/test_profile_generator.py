"""
Unit tests for KephalosData simulation services
"""

import unittest
from unittest.mock import Mock, patch
import json
from backend.app.services.oasis_profile_generator import OasisProfileGenerator, OasisAgentProfile


class TestOasisProfileGenerator(unittest.TestCase):
    """Test cases for profile generation improvements"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = OasisProfileGenerator(
            api_key="test_key",
            base_url="https://api.openai.com/v1",
            model_name="gpt-3.5-turbo",
            zep_api_key=None
        )

    def test_individual_prompt_includes_type_specific_instructions(self):
        """Test that individual prompts include type-specific instructions"""
        prompt = self.generator._build_individual_persona_prompt(
            "John Doe", "student", "A computer science student",
            {"major": "CS"}, "Some context"
        )

        # Check for type-specific content
        self.assertIn("academic interests", prompt.lower())
        self.assertIn("social activism", prompt.lower())
        self.assertIn("realistic for the entity type", prompt)

    def test_group_prompt_includes_organizational_focus(self):
        """Test that group prompts include organizational focus"""
        prompt = self.generator._build_group_persona_prompt(
            "MIT University", "university", "Leading research university",
            {"location": "Cambridge"}, "Academic context"
        )

        # Check for organizational content
        self.assertIn("academic excellence", prompt.lower())
        self.assertIn("research output", prompt.lower())
        self.assertIn("stakeholder interactions", prompt)

    def test_profile_validation(self):
        """Test profile data validation"""
        profile = OasisAgentProfile(
            user_id=1,
            user_name="testuser",
            name="Test User",
            bio="A test bio",
            persona="A detailed persona description",
            age=25,
            gender="male",
            mbti="INTJ",
            country="USA",
            profession="Engineer",
            interested_topics=["Tech", "AI"]
        )

        # Test serialization
        data = profile.to_dict()
        self.assertEqual(data["user_id"], 1)
        self.assertEqual(data["age"], 25)
        self.assertIn("Tech", data["interested_topics"])

    @patch('backend.app.services.oasis_profile_generator.OpenAI')
    def test_llm_fallback_to_rule_based(self, mock_openai):
        """Test that LLM failures fall back to rule-based generation"""
        # Mock LLM failure
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        result = self.generator._generate_profile_with_llm(
            "Test Entity", "student", "A student", {}, "context"
        )

        # Should return rule-based result
        self.assertIn("age", result)
        self.assertIn("gender", result)
        self.assertIn("bio", result)


if __name__ == '__main__':
    unittest.main()