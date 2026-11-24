MATERIALS = ["Cotton", "Polyester", "Wool", "Silk", "Denim", "Blended fabric", "Other"]
CONDITIONS = ["Good condition", "Slightly damaged", "Heavily damaged", "Contaminated or potentially infectious"]
GEN_CATS = ["College", "Hostel", "Tailoring Shop", "Hotel", "Hospital", "Individual"]
ITEM_TYPES = ["Clothes", "Uniforms", "Lab coats", "Bedsheets & linen", "Curtains & drapes", "Fabric scraps", "Event fabrics", "Other"]
FTYPES = ["Textile recycling company", "Donation centre", "NGO", "Upcycling organization", "Authorized waste collection agency"]
RESTRICTED = "Restricted or contaminated textiles"
SUITABLE = {
    "Reusable textiles": ["Donation centre", "NGO"],
    "Recyclable cotton": ["Textile recycling company"],
    "Recyclable synthetic textiles": ["Textile recycling company"],
    "Upcycling materials": ["Upcycling organization", "NGO"],
    "Material recovery": ["Textile recycling company", "Upcycling organization"],
    RESTRICTED: ["Authorized waste collection agency"],
}

def classify(material, cond, generator="Individual"):
    """Rule-based classification from material, condition and contamination status."""
    if cond.startswith("Contaminated"):
        cat = RESTRICTED
        why = "Contaminated or potentially infectious textiles must never enter ordinary donation or recycling channels."
        act = "Segregate in a labelled bag and hand over to an authorized biomedical waste handler under applicable rules."
    elif cond == "Good condition":
        cat = "Reusable textiles"
        why = "Clean, usable fabric keeps the most value when reused directly."
        act = "Wash if needed and offer to a donation centre or NGO."
    elif material in ("Cotton", "Denim"):
        cat = "Recyclable cotton"
        why = "Damaged cotton or denim suits recycling at facilities that accept cellulose fibres."
        act = "Remove buttons, zips and trims, then request collection by a recycler that accepts cotton."
    elif material == "Polyester":
        cat = "Recyclable synthetic textiles"
        why = "Polyester can go to synthetic fibre recyclers, subject to their intake rules."
        act = "Sort by colour and confirm with a synthetic fibre recycler before dispatch."
    elif cond == "Slightly damaged":
        cat = "Upcycling materials"
        why = "Wool, silk and blends in fair shape are better suited to craft and upcycling than to mixed recycling."
        act = "Offer to an upcycling organization or NGO that accepts this material."
    else:
        cat = "Material recovery"
        why = "Heavily damaged wool, silk or blended fabric is hard to reuse or recycle directly."
        act = "Ask a recycler or upcycler whether they can recover it. Acceptance depends on their actual capability."
    if generator == "Hospital" and cat != RESTRICTED:
        act += " Hospital source: confirm with infection control that the fabric was not exposed to patients."
    return dict(category=cat, destination=" / ".join(SUITABLE[cat]), reason=why, action=act)
