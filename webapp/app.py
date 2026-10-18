import os
import json
import random
import re
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Try to enable gzip compression if flask_compress is available
try:
    from flask_compress import Compress
    Compress(app)
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(BASE_DIR, 'questions.json')

with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    ALL_QUESTIONS = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    stats = {
        'total': len(ALL_QUESTIONS),
        'single': sum(1 for q in ALL_QUESTIONS if q['type'] == 'single'),
        'multi': sum(1 for q in ALL_QUESTIONS if q['type'] == 'multi'),
    }
    return jsonify(stats)

@app.route('/api/questions')
def get_questions():
    mode = request.args.get('mode', 'all')
    qs = []
    for i, q in enumerate(ALL_QUESTIONS):
        if mode != 'all' and q['type'] != mode:
            continue
        qs.append({
            '_idx': i,
            'id': q.get('id', f"q_{i}"),
            'category': q.get('category', ''),
            'question': q['question'],
            'options': q.get('options', []),
            'type': q['type']
        })
    if request.args.get('shuffle', '0') == '1':
        random.shuffle(qs)
    return jsonify({'total': len(qs), 'questions': qs})

@app.route('/api/test')
def get_test():
    mode = request.args.get('mode', 'standard100')
    count_param = request.args.get('count')
    
    singles = [dict(q, _idx=i) for i, q in enumerate(ALL_QUESTIONS) if q['type'] == 'single']
    multis = [dict(q, _idx=i) for i, q in enumerate(ALL_QUESTIONS) if q['type'] == 'multi']
    
    if mode == 'standard100':
        sel_s = random.sample(singles, min(70, len(singles)))
        sel_m = random.sample(multis, min(30, len(multis)))
        selected = sel_s + sel_m
        random.shuffle(selected)
    elif mode == 'random50':
        sel_s = random.sample(singles, min(35, len(singles)))
        sel_m = random.sample(multis, min(15, len(multis)))
        selected = sel_s + sel_m
        random.shuffle(selected)
    elif mode == 'single50':
        selected = random.sample(singles, min(50, len(singles)))
    elif mode == 'multi30':
        selected = random.sample(multis, min(30, len(multis)))
    else:
        pool = []
        for i, q in enumerate(ALL_QUESTIONS):
            if mode != 'all' and q['type'] != mode:
                continue
            pool.append(dict(q, _idx=i))
        
        count = int(count_param) if count_param and count_param.isdigit() else min(50, len(pool))
        count = min(count, len(pool))
        selected = random.sample(pool, count)
        random.shuffle(selected)
    
    # Strip answers for test
    clean_questions = []
    for q in selected:
        clean_questions.append({
            '_idx': q['_idx'],
            'id': q.get('id', f"q_{q['_idx']}"),
            'category': q.get('category', ''),
            'question': q['question'],
            'options': q.get('options', []),
            'type': q['type']
        })
    return jsonify({'total': len(clean_questions), 'questions': clean_questions})

@app.route('/api/browse')
def browse():
    mode = request.args.get('mode', 'all')
    qs = []
    for i, q in enumerate(ALL_QUESTIONS):
        if mode != 'all' and q['type'] != mode:
            continue
        qs.append({
            '_idx': i,
            'id': q.get('id', f"q_{i}"),
            'category': q.get('category', ''),
            'question': q['question'],
            'options': q.get('options', []),
            'answer': q['answer'],
            'type': q['type']
        })
    return jsonify({'total': len(qs), 'questions': qs})

@app.route('/api/check/<int:idx>')
def check_answer(idx):
    if 0 <= idx < len(ALL_QUESTIONS):
        return jsonify({
            'index': idx,
            'answer': ALL_QUESTIONS[idx]['answer'],
            'type': ALL_QUESTIONS[idx]['type']
        })
    return jsonify({'error': 'not found'}), 404

@app.route('/api/grade', methods=['POST'])
def grade_test():
    data = request.get_json() or {}
    user_answers = data.get('answers', {})
    indices = data.get('indices', [])
    correct = 0
    total_scorable = 0
    details = []
    
    for i, orig_idx in enumerate(indices):
        if orig_idx < 0 or orig_idx >= len(ALL_QUESTIONS):
            continue
        q = ALL_QUESTIONS[orig_idx]
        user_ans = str(user_answers.get(str(i), '')).strip()
        correct_ans = str(q['answer']).strip()
        q_type = q['type']
        
        is_correct = False
        if q_type == 'single':
            total_scorable += 1
            is_correct = user_ans.upper() == correct_ans.upper()
        elif q_type == 'multi':
            total_scorable += 1
            u_sorted = ''.join(sorted(user_ans.upper().replace(' ', '')))
            c_sorted = ''.join(sorted(correct_ans.upper().replace(' ', '')))
            is_correct = u_sorted == c_sorted
        else:
            total_scorable += 1
            is_correct = user_ans == correct_ans
            
        if is_correct:
            correct += 1
            
        details.append({
            'index': i,
            '_idx': orig_idx,
            'user_answer': user_ans,
            'correct_answer': correct_ans,
            'is_correct': is_correct,
            'question': q['question'],
            'options': q.get('options', []),
            'type': q_type,
            'category': q.get('category', '')
        })
        
    score = round(correct / total_scorable * 100, 1) if total_scorable > 0 else 0
    return jsonify({
        'total': len(indices),
        'scorable_total': total_scorable,
        'correct': correct,
        'score': score,
        'details': details
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"马克思主义基本原理刷题系统已启动！访问地址: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
