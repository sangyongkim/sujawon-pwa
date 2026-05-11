"""
암기노트 마크다운을 파싱해서 data_SECTION.js 생성 (전 섹션)
"""
import re, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, '..')

# html_files=None → 폴더에서 자동 감지
# html_files=dict  → 번호 불일치 섹션 수동 지정 (댐: 08번 없음, 09부터 시작)
SECTIONS = [
    {'name': '하천계획', 'html_files': None},
    {'name': '방재', 'html_files': {
        # HTML 05번(위험지구 후보지 위험요인 분석)이 마크다운에 없어서
        # 토픽 05부터 HTML 번호가 +1 오프셋
        1:  "01자연재해위험개선지구.html",
        2:  "02재해영향평가 등의 협의.html",
        3:  "03자연재해저감종합계획 개요.html",
        4:  "04자연재해 위험지구 예비후보지 선정.html",
        5:  "06자연재해저감대첵 시행계획수립.html",
        6:  "07비상대처계획(EAP).html",
        7:  "08재해복구사업 사전심의.html",
        8:  "09재해복구사업 분석평가.html",
        9:  "10지구단위 홍수방어기준.html",
        10: "11지하공간 침수방지를 위한 수방기준.html",
        11: "12재해지도.html",
        12: "13엘리뇨,라니냐.html",
        13: "14기후변화에 따른 수자원분야 대응.html",
        14: "15기후변화에 따른 가뭄대책.html",
        15: "16하천건천화.html",
        16: "17저영향개발(LIM).html",
        17: "18지역별 방재성능목표 설정기준.html",
        18: "19도시침수피해원인 및 대책.html",
        19: "20우수유출저감시설.html",
        20: "21저류시설 유지관리.html",
        21: "22물분쟁의 형태와 분쟁의 관리 및 해소방안.html",
        22: "23남북한 공유하천 물분쟁 해소방안.html",
        23: "24자연재해저감종합계획의 비구조적대책.html",
        24: "25소규모공공시설.html",
    }},
    {'name': '하천공학', 'html_files': None},
    {'name': '수문학',   'html_files': None},
    {'name': '댐', 'html_files': {
        # HTML 폴더에서 08번 없음 → 토픽 08부터 HTML 번호가 +1 오프셋
        1:  "01댐위치선정.html",
        2:  "02댐형식결정.html",
        3:  "03저수지용량배분.html",
        4:  "04댐저수지 운영방법.html",
        5:  "05여수로.html",
        6:  "06댐 여수로 수문.html",
        7:  "07여수로의 에너지감세공.html",
        8:  "09유수전환시설.html",
        9:  "10조압수조.html",
        10: "11댐 여수로 공동현상과 공기연행.html",
        11: "12기존댐 치수능력 증대방안.html",
        12: "13저수지 퇴사.html",
    }},
]


def auto_html_files(section_name):
    """폴더의 HTML 파일에서 숫자 prefix → filename 매핑 자동 생성"""
    folder = os.path.join(ROOT, section_name)
    mapping = {}
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith('.html'):
            continue
        m = re.match(r'^(\d+)', fname)
        if m:
            mapping[int(m.group(1))] = fname
    return mapping


def md_to_html(text):
    """간단한 마크다운 → HTML 변환"""
    lines = text.split('\n')
    html_lines = []
    in_table = False
    in_ol = False
    in_ul = False
    table_rows = []

    def flush_list():
        nonlocal in_ol, in_ul
        if in_ul:
            html_lines.append('</ul>')
            in_ul = False
        if in_ol:
            html_lines.append('</ol>')
            in_ol = False

    def flush_table():
        nonlocal in_table, table_rows
        if in_table and table_rows:
            html_lines.append('<table class="md-table">')
            for ri, row in enumerate(table_rows):
                cells = [c.strip() for c in row.strip('|').split('|')]
                tag = 'th' if ri == 0 else 'td'
                html_lines.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
            html_lines.append('</table>')
            table_rows = []
            in_table = False

    def inline(s):
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
        return s

    for line in lines:
        stripped = line.strip()
        if not stripped or re.match(r'^-{3,}$', stripped):
            flush_table()
            flush_list()
            continue

        if stripped.startswith('|'):
            if re.match(r'^\|[-| :]+\|$', stripped):
                continue
            in_table = True
            table_rows.append(stripped)
            continue
        else:
            flush_table()

        if stripped.startswith('#### '):
            flush_list()
            html_lines.append(f'<h4>{inline(stripped[5:])}</h4>')
        elif stripped.startswith('### '):
            flush_list()
            html_lines.append(f'<h3>{inline(stripped[4:])}</h3>')
        elif stripped.startswith('## '):
            flush_list()
            html_lines.append(f'<h2>{inline(stripped[3:])}</h2>')
        elif stripped.startswith('# '):
            flush_list()
            html_lines.append(f'<h1>{inline(stripped[2:])}</h1>')
        elif re.match(r'^\d+\.\s', stripped):
            if not in_ol:
                flush_list()
                html_lines.append('<ol>')
                in_ol = True
            html_lines.append(f'<li>{inline(re.sub(r"^\d+\.\s", "", stripped))}</li>')
        elif re.match(r'^\s+[-*]\s', line):
            if not in_ul:
                html_lines.append('<ul class="sub">')
                in_ul = True
            html_lines.append(f'<li>{inline(stripped.lstrip("-* "))}</li>')
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if in_ol:
                html_lines.append(f'<li class="sub-li">{inline(stripped[2:])}</li>')
            else:
                if not in_ul:
                    flush_list()
                    html_lines.append('<ul>')
                    in_ul = True
                html_lines.append(f'<li>{inline(stripped[2:])}</li>')
        elif stripped.startswith('**') and stripped.endswith('**'):
            flush_list()
            html_lines.append(f'<p class="label">{inline(stripped)}</p>')
        else:
            flush_list()
            html_lines.append(f'<p>{inline(stripped)}</p>')

    flush_table()
    flush_list()
    return '\n'.join(html_lines)


def parse_topics(md_path, html_map):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'^## (\d+)\. (.+?)$', re.MULTILINE)
    matches = list(pattern.finditer(content))

    topics = []
    for i, m in enumerate(matches):
        num = int(m.group(1))
        header = m.group(2).strip()
        title = re.sub(r'\s*★+\s*$', '', header).strip()
        stars = header.count('★')

        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        body = content[start:end]

        short_raw = ''
        essay_raw = ''

        if '### [단답형]' in body and '### [서술형]' in body:
            short_raw = body.split('### [단답형]')[1].split('### [서술형]')[0]
            essay_raw = body.split('### [서술형]')[1]
        elif '### [단답형]' in body:
            short_raw = body.split('### [단답형]')[1]
        elif '### [서술형]' in body:
            essay_raw = body.split('### [서술형]')[1]
        else:
            short_raw = body

        bullets = []
        for line in short_raw.strip().split('\n'):
            s = line.strip()
            if s.startswith('- ') or s.startswith('* '):
                bullets.append(s[2:])
            elif re.match(r'^\d+\.\s', s):
                bullets.append(s)
            elif s.startswith('**') and ':' in s:
                bullets.append(s)
            elif s and not s.startswith('|') and not s.startswith('#') and not re.match(r'^[-|:]+$', s):
                if s.strip('-').strip():
                    bullets.append(s)

        essay_html = md_to_html(essay_raw.strip())

        topics.append({
            'id': num,
            'title': title,
            'stars': stars,
            'bullets': [b for b in bullets if b.strip()],
            'essay': essay_html,
            'file': html_map.get(num, ''),
        })

    return topics


def parse_appendix(md_path):
    """핵심수치 / 법규 테이블 파싱"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    numbers_html = ''
    laws_html = ''

    if '## 핵심 수치 총정리' in content:
        sec = content.split('## 핵심 수치 총정리')[1].split('## ')[0]
        numbers_html = md_to_html(sec.strip())

    if '## 법규 조문 정리' in content:
        rest = content.split('## 법규 조문 정리')[1]
        sec = rest.split('## ')[0] if '## ' in rest else rest
        laws_html = md_to_html(sec.strip())

    return numbers_html, laws_html


if __name__ == '__main__':
    for sec_cfg in SECTIONS:
        name = sec_cfg['name']
        md_path = os.path.join(ROOT, f'암기노트_{name}.md')

        html_map = sec_cfg['html_files']
        if html_map is None:
            html_map = auto_html_files(name)

        topics = parse_topics(md_path, html_map)
        numbers_html, laws_html = parse_appendix(md_path)

        topics_json = json.dumps(topics, ensure_ascii=False, indent=2)

        js = f"""// Auto-generated by generate_data.py — {name}
window.SECTION_DATA = window.SECTION_DATA || {{}};
window.SECTION_DATA["{name}"] = {{
  topics: {topics_json},
  numbersHtml: {json.dumps(numbers_html, ensure_ascii=False)},
  lawsHtml: {json.dumps(laws_html, ensure_ascii=False)}
}};
"""
        out_path = os.path.join(BASE, f'data_{name}.js')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(js)

        print(f"[{name}] {len(topics)}개 토픽 → data_{name}.js")
        for t in topics:
            stars_str = '★' * t['stars']
            print(f"  [{t['id']:02d}] {t['title']} {stars_str} | 단답형 {len(t['bullets'])}항목 | html={t['file'] or '없음'}")
