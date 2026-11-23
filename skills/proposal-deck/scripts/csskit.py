"""Tiny CSS parser and serializer used by build.py (Python stdlib only).
parse_css(text) -> list of nodes:
  {'t':'rule','sel':str,'decls':[(prop,val,imp)]}
  {'t':'at','name':'media'|'supports'|...,'prelude':str,'children':[nodes]}   (block at-rules holding rules)
  {'t':'raw','text':str}   (keyframes, font-face, other at-rules kept verbatim)
"""
import re

def strip_comments(s):
    out, i, n = [], 0, len(s)
    while i < n:
        if s.startswith('/*', i):
            j = s.find('*/', i + 2)
            i = n if j < 0 else j + 2
            continue
        c = s[i]
        if c in '"\'':
            j = i + 1
            while j < n and s[j] != c:
                j += 2 if s[j] == '\\' else 1
            out.append(s[i:j + 1]); i = j + 1; continue
        out.append(c); i += 1
    return ''.join(out)

def _match(s, i):
    """s[i] == '{' ; return index of matching '}'"""
    depth, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in '"\'':
            j = i + 1
            while j < n and s[j] != c:
                j += 2 if s[j] == '\\' else 1
            i = j + 1; continue
        if c == '(':
            # skip url(...) / data uris containing braces safely
            j, d = i + 1, 1
            while j < n and d:
                if s[j] == '(': d += 1
                elif s[j] == ')': d -= 1
                j += 1
            i = j; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    raise ValueError('unbalanced braces')

def split_top(s, sep):
    parts, depth, cur, q = [], 0, [], None
    for c in s:
        if q:
            cur.append(c)
            if c == q: q = None
            continue
        if c in '"\'': q = c; cur.append(c); continue
        if c in '([': depth += 1
        elif c in ')]': depth -= 1
        if c == sep and depth == 0:
            parts.append(''.join(cur)); cur = []
        else:
            cur.append(c)
    parts.append(''.join(cur))
    return parts

def parse_decls(body):
    out = []
    for d in split_top(body, ';'):
        d = d.strip()
        if not d or ':' not in d: continue
        p, v = d.split(':', 1)
        p = p.strip(); v = v.strip()
        imp = False
        m = re.search(r'\s*!\s*important\s*$', v, re.I)
        if m:
            imp = True; v = v[:m.start()].strip()
        out.append((p if p.startswith('--') else p.lower(), v, imp))
    return out

def parse_css(text, _stripped=False):
    s = text if _stripped else strip_comments(text)
    nodes, i, n = [], 0, len(s)
    while i < n:
        while i < n and s[i] in ' \t\r\n;': i += 1
        if i >= n: break
        j = s.find('{', i)
        k = s.find(';', i)
        if s[i] == '@' and (k >= 0 and (j < 0 or k < j)):
            nodes.append({'t': 'raw', 'text': s[i:k + 1].strip()}); i = k + 1; continue
        if j < 0: break
        prelude = s[i:j].strip()
        e = _match(s, j)
        body = s[j + 1:e]
        if prelude.startswith('@'):
            name = re.match(r'@([\w-]+)', prelude).group(1).lower()
            if name in ('media', 'supports', 'container', 'layer'):
                nodes.append({'t': 'at', 'name': name, 'prelude': prelude, 'children': parse_css(body, True)})
            else:
                nodes.append({'t': 'raw', 'text': prelude + '{' + body.strip() + '}', 'name': name, 'prelude': prelude})
        else:
            nodes.append({'t': 'rule', 'sel': ' '.join(prelude.split()), 'decls': parse_decls(body)})
        i = e + 1
    return nodes

def decl_str(decls):
    return ';'.join('%s:%s%s' % (p, v, '!important' if imp else '') for p, v, imp in decls)

def serialize(nodes, indent=''):
    out = []
    for nd in nodes:
        if nd['t'] == 'rule':
            if nd['decls']:
                out.append('%s%s{%s}' % (indent, nd['sel'], decl_str(nd['decls'])))
        elif nd['t'] == 'at':
            inner = serialize(nd['children'], indent)
            if inner.strip():
                out.append('%s%s{\n%s\n%s}' % (indent, nd['prelude'], inner, indent))
        elif nd['t'] == 'comment':
            out.append(indent + nd['text'])
        else:
            out.append(indent + nd['text'])
    return '\n'.join(out)

# ---------- specificity ----------
_pseudo_el = re.compile(r'::?(before|after|first-line|first-letter|placeholder|marker|selection|backdrop)\b')
def specificity(sel):
    s = re.sub(r'"[^"]*"|\'[^\']*\'', '', sel)
    a = b = c = 0
    # :not(), :is(), :has() count their argument (approximation: count inside)
    s2 = re.sub(r':(not|is|has|where)\(', ' ', s)
    if ':where(' in s:
        s2 = re.sub(r':where\([^)]*\)', ' ', s)
    a = len(re.findall(r'#[\w-]+', s2))
    b = len(re.findall(r'\.[\w-]+', s2)) + len(re.findall(r'\[[^\]]+\]', s2)) + \
        len(re.findall(r'(?<!:):(?!not|is|has|where)[\w-]+', s2)) - len(re.findall(r'(?<!:):(before|after)\b', s2))
    els = re.sub(r'#[\w-]+|\.[\w-]+|\[[^\]]+\]|::?[\w-]+(\([^)]*\))?', ' ', s2)
    c = len([t for t in re.split(r'[\s>+~*()]+', els) if re.match(r'^[a-zA-Z][\w-]*$', t)])
    c += len(_pseudo_el.findall(s))
    return (a, b, c)

def classes_in(sel):
    return re.findall(r'\.([A-Za-z_][\w-]*)', re.sub(r'"[^"]*"|\'[^\']*\'', '', sel))
