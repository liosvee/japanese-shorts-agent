"""Convert provider character alignments to phrase captions; no guessed timing."""
import math
import re


def cues(alignment, max_chars=42, max_seconds=3.0):
    chars = alignment['characters']
    starts = alignment['character_start_times_seconds']
    ends = alignment['character_end_times_seconds']
    if not chars or not len(chars) == len(starts) == len(ends):
        raise ValueError('Missing or mismatched alignment arrays.')
    if any(not isinstance(c, str) or len(c) != 1 for c in chars):
        raise ValueError('Alignment must contain individual characters.')
    if any(not math.isfinite(s) or not math.isfinite(e) or s < 0 or e < s for s, e in zip(starts, ends)):
        raise ValueError('Invalid alignment timestamps.')
    if any(b < a for a, b in zip(starts, starts[1:])):
        raise ValueError('Alignment timestamps are not ordered.')
    if any(b < a for a, b in zip(ends, ends[1:])):
        raise ValueError('Alignment end timestamps are not ordered.')
    if re.search(r'[\u3040-\u30ff\u3400-\u9fff]', ''.join(chars)):
        # Japanese has no reliable word spaces. Bound cue length and time using
        # provider character alignment; prefer punctuation when encountered.
        # This is character-based wrapping, not a Japanese syntactic parser.
        result, start = [], 0
        limit = min(max_chars, 18)
        for i, char in enumerate(chars):
            if i > start and (i-start >= limit or ends[i]-starts[start] > max_seconds):
                text = ''.join(chars[start:i]).strip()
                if text: result.append((text, starts[start], ends[i-1]))
                start = i
            if char in '。！？!?\n' or i == len(chars)-1:
                text = ''.join(chars[start:i+1]).strip()
                if text: result.append((text, starts[start], ends[i]))
                start = i+1
        return result
    words = [(m.group(), starts[m.start()], ends[m.end()-1]) for m in re.finditer(r'\S+', ''.join(chars))]
    result, group = [], []
    for word in words:
        if group and (len(' '.join(w[0] for w in group)) + len(word[0]) + 1 > max_chars or word[2] - group[0][1] > max_seconds):
            result.append((' '.join(w[0] for w in group), group[0][1], group[-1][2]))
            group = []
        group.append(word)
        if word[0].endswith(('.', '!', '?')):
            result.append((' '.join(w[0] for w in group), group[0][1], group[-1][2]))
            group = []
    if group:
        result.append((' '.join(w[0] for w in group), group[0][1], group[-1][2]))
    return result


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}'


def srt(alignment):
    return '\n\n'.join(f'{i}\n{timestamp(start)} --> {timestamp(end)}\n{text}'
                       for i, (text, start, end) in enumerate(cues(alignment), 1)) + '\n'

