def wrap(text, width):
    lines, cur = [], ''
    for w in text.split():
        if not cur: cur = w
        elif len(cur) + 1 + len(w) <= width: cur += ' ' + w
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
