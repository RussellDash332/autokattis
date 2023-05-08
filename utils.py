def guess_id(guess, data):
    if guess in data: return guess
    reverse_mapping = {v:k for k,v in data.items()}
    if guess in reverse_mapping: return reverse_mapping[guess]

    # Use fuzzy search
    candidates = {**data, **reverse_mapping}
    best = max(candidates, key=lambda c: (fuzz.ratio(guess, c), fuzz.partial_ratio(guess, c)))
    if best in data: return best
    elif best in reverse_mapping: return reverse_mapping[best]
    raise Exception(f'Invalid ID provided! ({guess})')