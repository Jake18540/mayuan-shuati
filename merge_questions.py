from docx import Document
import re
import json

def parse_docx(fname):
    doc = Document(fname)
    questions = []
    i = 0
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    section_headers = {'导论','绪论','第一章','第二章','第三章','第四章','第五章','第六章','第七章','第八章'}
    
    while i < len(lines):
        line = lines[i]
        if line.startswith('“马克思主义') or line in ('一、单项选择题','一、多项选择题','二、多项选择题') or line in section_headers:
            i += 1
            continue
        
        if re.match(r'^\d+[、.．)）]\s*', line):
            q_text = line
            options = []
            i += 1
            answer = ''
            while i < len(lines):
                nl = lines[i]
                if '正确答案' in nl:
                    answer = nl.replace('正确答案：','').replace('正确答案:','').strip()
                    i += 1
                    break
                elif re.match(r'^[A-H][、.．)\s]', nl):
                    options.append(nl)
                    i += 1
                elif re.match(r'^\d+[、.．)）]\s*', nl):
                    break
                else:
                    if options:
                        options[-1] += nl
                    else:
                        q_text += nl
                    i += 1
            if answer:
                questions.append({'question': q_text, 'options': options, 'answer': answer})
        else:
            i += 1
    
    return questions

def normalize(text):
    """Normalize question text for dedup comparison"""
    t = re.sub(r'\s+', '', text)
    t = re.sub(r'[（(]\s*[）)]', '', t)  # empty parentheses
    t = t.replace('（）','').replace('()','').replace(' ','')
    # remove leading number
    t = re.sub(r'^\d+[、.．)）]', '', t)
    return t

q1 = parse_docx('马克思主义基本原理题库.docx')
q2 = parse_docx('马原理80％题库.docx')
print(f'File 1: {len(q1)} questions')
print(f'File 2: {len(q2)} questions')

# Merge and dedup
merged = list(q1)
seen = {normalize(q['question']) for q in q1}
dup_count = 0
for q in q2:
    nq = normalize(q['question'])
    if nq in seen:
        dup_count += 1
    else:
        seen.add(nq)
        merged.append(q)

print(f'Duplicates removed: {dup_count}')
print(f'Merged total: {len(merged)}')

with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print('Saved to questions.json')
