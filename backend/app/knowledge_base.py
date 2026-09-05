KNOWLEDGE_BASE = [
    {
        "id": "kb1",
        "title": "Refund Policy",
        "content": "Refunds are issued within 5-7 business days. Duplicate charges are refunded automatically once confirmed by our billing team, no dispute required. Customers can also request a refund within 30 days of any purchase for any reason."
    },
    {
        "id": "kb2",
        "title": "Account Lockouts",
        "content": "Accounts lock after 5 failed login attempts within 15 minutes, for security. Unlock by resetting your password via the 'Forgot Password' link, or by waiting 30 minutes for the lock to expire automatically."
    },
    {
        "id": "kb3",
        "title": "Two-Factor Authentication Issues",
        "content": "If a 2FA code doesn't arrive, check that SMS isn't blocked by your carrier, or switch to the authenticator app method in Account Settings > Security. Backup codes generated at 2FA setup can also be used to log in."
    },
    {
        "id": "kb4",
        "title": "Known Bug: Export Feature",
        "content": "There is a known issue where CSV exports can appear blank on Safari browsers. Workaround: use Chrome or Firefox, or use the 'Download as PDF' option instead. A fix is scheduled for the next release."
    },
    {
        "id": "kb5",
        "title": "Subscription Cancellation",
        "content": "Subscriptions can be cancelled anytime from Account Settings > Billing > Cancel Plan. Cancellation takes effect at the end of the current billing period; no partial refunds are issued for unused time, except in cases of billing error."
    },
    {
        "id": "kb6",
        "title": "Feature Request Process",
        "content": "Feature requests are logged and reviewed monthly by the product team. There is no guaranteed timeline for implementation. Customers can upvote existing requests on our public roadmap page."
    },
]

def search_knowledge_base(query: str, top_k: int = 2) -> list[dict]:
    """Simple keyword-overlap search — no embeddings needed for a small KB like this."""
    query_words = set(query.lower().split())
    scored = []
    for doc in KNOWLEDGE_BASE:
        doc_words = set((doc["title"] + " " + doc["content"]).lower().split())
        overlap = len(query_words & doc_words)
        if overlap > 0:
            scored.append((overlap, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]