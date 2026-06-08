import json
import random
from flask import Flask, render_template, jsonify, request
from flask_compress import Compress

app = Flask(__name__)
Compress(app)

with open('questions.json', 'r', encoding='utf-8') as f:
    ALL_QUESTIONS = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/questions')
def get_questions():
    mode = request.args.get('mode', 'all')
    qs = []
    for i, q in enumerate(ALL_QUESTIONS):
        if mode == 'single' and len(q['answer']) != 1:
            continue
        if mode == 'multi' and len(q['answer']) == 1:
            continue
        qs.append({
            '_idx': i, 'question': q['question'], 'options': q['options'],
            'type': 'single' if len(q['answer']) == 1 else 'multi'
        })
    if request.args.get('shuffle', '0') == '1':
        random.shuffle(qs)
    return jsonify({'total': len(qs), 'questions': qs})

@app.route('/api/test')
def get_test():
    mode = request.args.get('mode', 'all')
    pool = []
    for i, q in enumerate(ALL_QUESTIONS):
        if mode == 'single' and len(q['answer']) != 1:
            continue
        if mode == 'multi' and len(q['answer']) == 1:
            continue
        pool.append({
            '_idx': i, 'question': q['question'], 'options': q['options'],
            'type': 'single' if len(q['answer']) == 1 else 'multi'
        })
    count = min(100, len(pool))
    selected = random.sample(pool, count)
    random.shuffle(selected)
    return jsonify({'total': len(selected), 'questions': selected})

@app.route('/api/browse')
def browse():
    mode = request.args.get('mode', 'all')
    qs = []
    for i, q in enumerate(ALL_QUESTIONS):
        if mode == 'single' and len(q['answer']) != 1:
            continue
        if mode == 'multi' and len(q['answer']) == 1:
            continue
        qs.append({
            '_idx': i, 'question': q['question'], 'options': q['options'],
            'answer': q['answer'],
            'type': 'single' if len(q['answer']) == 1 else 'multi'
        })
    return jsonify({'total': len(qs), 'questions': qs})

@app.route('/api/check/<int:idx>')
def check_answer(idx):
    if 0 <= idx < len(ALL_QUESTIONS):
        return jsonify({'index': idx, 'answer': ALL_QUESTIONS[idx]['answer']})
    return jsonify({'error': 'not found'}), 404

@app.route('/api/grade', methods=['POST'])
def grade_test():
    data = request.get_json()
    user_answers = data.get('answers', {})
    indices = data.get('indices', [])
    correct = 0
    details = []
    for i, orig_idx in enumerate(indices):
        if orig_idx < 0 or orig_idx >= len(ALL_QUESTIONS):
            continue
        q = ALL_QUESTIONS[orig_idx]
        user_ans = user_answers.get(str(i), '').strip().upper()
        correct_ans = q['answer'].strip().upper()
        user_sorted = ''.join(sorted(user_ans.replace(' ', '')))
        correct_sorted = ''.join(sorted(correct_ans.replace(' ', '')))
        is_correct = user_sorted == correct_sorted
        if is_correct:
            correct += 1
        details.append({
            'index': i, 'user_answer': user_ans, 'correct_answer': correct_ans,
            'is_correct': is_correct, 'question': q['question'], 'options': q['options']
        })
    return jsonify({
        'total': len(indices), 'correct': correct,
        'score': round(correct / len(indices) * 100, 1) if indices else 0, 'details': details
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
