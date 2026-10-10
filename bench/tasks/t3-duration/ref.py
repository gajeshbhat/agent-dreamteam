import re
def parse_duration(s):
    if not re.fullmatch(r'(\d+[dhms])+', s): raise ValueError(s)
    u = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
    return sum(int(n) * u[c] for n, c in re.findall(r'(\d+)([dhms])', s))
