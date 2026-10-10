def parse_csv_line(line):
    out, cur, i, q = [], '', 0, False
    while i < len(line):
        c = line[i]
        if q:
            if c == '"':
                if line[i + 1:i + 2] == '"': cur += '"'; i += 1
                else: q = False
            else: cur += c
        elif c == '"': q = True
        elif c == ',': out.append(cur); cur = ''
        else: cur += c
        i += 1
    if q: raise ValueError('unterminated quote')
    out.append(cur)
    return out
