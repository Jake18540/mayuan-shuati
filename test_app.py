import os
import json
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(BASE_DIR, 'questions.json')

class TestMayuanDatasetAndIntegrity(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(QUESTIONS_FILE), "questions.json must exist")
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)

    def test_question_count_and_types(self):
        self.assertEqual(len(self.questions), 539, "Total questions must be exactly 539")
        singles = [q for q in self.questions if q['type'] == 'single']
        multis = [q for q in self.questions if q['type'] == 'multi']
        self.assertEqual(len(singles), 380, "Single choice count must be 380")
        self.assertEqual(len(multis), 159, "Multi choice count must be 159")

    def test_question_structure(self):
        seen_ids = set()
        for idx, q in enumerate(self.questions):
            self.assertIn('id', q, f"Question at {idx} missing id")
            self.assertIn('category', q, f"Question at {idx} missing category")
            self.assertIn('num', q, f"Question at {idx} missing num")
            self.assertIn('type', q, f"Question at {idx} missing type")
            self.assertIn('question', q, f"Question at {idx} missing question text")
            self.assertIn('options', q, f"Question at {idx} missing options")
            self.assertIn('answer', q, f"Question at {idx} missing answer")
            
            self.assertTrue(len(q['options']) >= 2, f"Question {q['id']} has less than 2 options")
            self.assertTrue(len(q['answer']) >= 1, f"Question {q['id']} has empty answer")
            self.assertNotIn(q['id'], seen_ids, f"Duplicate id {q['id']}")
            seen_ids.add(q['id'])

    def test_single_file_index_html(self):
        html_path = os.path.join(BASE_DIR, 'index.html')
        self.assertTrue(os.path.exists(html_path), "index.html must exist in root")
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('var RAW_QUESTIONS =', html, "index.html must embed RAW_QUESTIONS")
        self.assertIn('539', html, "index.html must mention 539 questions")

    def test_webapp_sync(self):
        web_q = os.path.join(BASE_DIR, 'webapp', 'questions.json')
        web_html = os.path.join(BASE_DIR, 'webapp', 'templates', 'index.html')
        self.assertTrue(os.path.exists(web_q), "webapp/questions.json must exist")
        self.assertTrue(os.path.exists(web_html), "webapp/templates/index.html must exist")
        
        with open(web_q, 'r', encoding='utf-8') as f:
            q_data = json.load(f)
        self.assertEqual(len(q_data), len(self.questions), "webapp/questions.json must match root")

if __name__ == '__main__':
    unittest.main()
