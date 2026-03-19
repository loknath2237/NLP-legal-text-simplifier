import re
from nltk.tokenize import sent_tokenize

# Legal context keywords (importance indicators)
LEGAL_KEYWORDS = [
    "agreement", "contract", "tenant", "landlord", "owner",
    "rent", "payment", "notice", "vacate", "terminate",
    "court", "law", "property", "premises", "months", "days",
    "shall", "must", "liable", "failure", "breach"
]

# Common legal filler words to ignore
FILLER_PHRASES = [
    "hereby", "hereinafter", "whereas",
    "thereof", "therein", "therefore",
    "it is hereby", "under the instructions"
]

def simplify_legal_text(text):
    """
    Context-aware legal text simplification without losing meaning
    """

    # 1️⃣ Sentence segmentation
    sentences = sent_tokenize(text)

    if not sentences:
        return "No meaningful legal content found."

    important_sentences = []

    # 2️⃣ Remove filler-heavy sentences
    for s in sentences:
        s_lower = s.lower()
        if any(f in s_lower for f in FILLER_PHRASES):
            continue
        important_sentences.append(s.strip())

    # 3️⃣ Score sentences based on legal context
    scored_sentences = []
    for s in important_sentences:
        score = sum(1 for k in LEGAL_KEYWORDS if k in s.lower())
        scored_sentences.append((score, s))

    # Sort by importance
    scored_sentences.sort(reverse=True, key=lambda x: x[0])

    # 4️⃣ Adaptive summarization (context safe)
    total = len(sentences)

    if total <= 6:
        keep = total
    elif total <= 12:
        keep = max(4, total // 2)
    else:
        keep = max(5, total // 3)

    selected = [s for score, s in scored_sentences if score > 0][:keep]

    # Fallback if scoring removes everything
    if not selected:
        selected = sentences[:keep]

    # 5️⃣ Final simplified summary
    simplified_text = " ".join(selected)

    # 6️⃣ Light rewriting for clarity (NOT meaning change)
    simplified_text = re.sub(
        r"shall be liable to",
        "will be responsible for",
        simplified_text,
        flags=re.IGNORECASE
    )

    simplified_text = re.sub(
        r"hereby required to",
        "must",
        simplified_text,
        flags=re.IGNORECASE
    )

    return simplified_text.strip()
