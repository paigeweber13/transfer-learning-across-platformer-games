actions = [
            [0, 0, 0, 1, 0, 1],
            [0, 0, 0, 1, 1, 1],
        ]
def _get_actions(a):
    return actions[a.index(max(a))]

output = [0.1, 0.1, 0.05, 0.2, 0.5, 0.05]

print(_get_actions(output))