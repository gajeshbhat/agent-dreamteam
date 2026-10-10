def roman_to_int(s):
    v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    if not s or any(c not in v for c in s): raise ValueError(s)
    t = 0
    for i, c in enumerate(s):
        t += -v[c] if i + 1 < len(s) and v[c] < v[s[i + 1]] else v[c]
    return t
