# Smooth animation curves for any camera or object move. mono() never overshoots, so a move can't wobble backwards between keys. Give one curve to a whole move: two paths joined at a handover cause a visible kink.
import math
def mono(keys):
    T = [k[0] for k in keys]; V = [k[1] for k in keys]; d = [(V[i + 1] - V[i]) / (T[i + 1] - T[i]) for i in range(len(T) - 1)]; m = [d[0]] + [0 if d[i - 1] * d[i] <= 0 else 2 * d[i - 1] * d[i] / (d[i - 1] + d[i]) for i in range(1, len(d))] + [d[-1]]
    def f(t):
        if t <= T[0]: return V[0]
        if t >= T[-1]: return V[-1]
        i = 0
        while t > T[i + 1]: i += 1
        h = T[i + 1] - T[i]; u = (t - T[i]) / h; return (2 * u ** 3 - 3 * u ** 2 + 1) * V[i] + (u ** 3 - 2 * u ** 2 + u) * h * m[i] + (-2 * u ** 3 + 3 * u ** 2) * V[i + 1] + (u ** 3 - u ** 2) * h * m[i + 1]
    return f
def tracks(keys): n = len(keys[0][1]); fs = [mono([(t, v[i]) for t, v in keys]) for i in range(n)]; return lambda t: [g(t) for g in fs]
def sm(k): k = max(0, min(1, k)); return k * k * (3 - 2 * k)
