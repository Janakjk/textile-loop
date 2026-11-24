from database import PROCESSING_OUTCOMES, query, requests_df

def _sum(df):
    return float(df.quantity_kg.sum()) if len(df) else 0.0

def stats():
    """Circularity metrics from registered batches only. Sample records are excluded, so an empty registry is 0 kg."""
    total = _sum(query("SELECT quantity_kg FROM waste_records WHERE is_demo=0"))
    r = requests_df(exclude_demo=True)
    p = query(
        "SELECT p.outcome, p.quantity_kg, rd.ftype "
        "FROM processing_records p "
        "JOIN collection_requests cr ON cr.id=p.collection_id "
        "JOIN waste_records w ON w.id=cr.waste_id "
        "JOIN recycler_directory rd ON rd.id=cr.recycler_id "
        "WHERE p.verified=1 AND w.is_demo=0"
    )
    donated = _sum(p[(p.outcome == "Reused") & (p.ftype.isin(["Donation centre", "NGO"]))])
    reused = _sum(p[p.outcome == "Reused"])
    recycled = _sum(p[p.outcome == "Recycled"])
    upcycled = _sum(p[p.outcome == "Upcycled (Craft Products)"])
    collected_states = ["Collected", "Processing", *PROCESSING_OUTCOMES, "Disposed"]
    collected = _sum(r[r.status.isin(collected_states)])
    disposal = _sum(r[r.status.isin(["Collected", "Processing", "Disposed"]) & (r.ftype == "Authorized waste collection agency")])
    diverted = reused + recycled + upcycled
    pending = _sum(r[r.status.isin(["Pending", "Approved", "Scheduled"])])
    in_process = _sum(r[r.status == "Processing"])
    active_partners = int(query("SELECT COUNT(DISTINCT id) AS n FROM recycler_directory").n[0])
    return dict(
        total=total,
        collected=collected,
        donated=donated,
        reused=reused,
        recycled=recycled,
        upcycled=upcycled,
        disposal=disposal,
        diverted=diverted,
        pending=pending,
        awaiting=max(total - collected, 0),
        in_process=in_process,
        active_partners=active_partners,
        pct=100 * diverted / total if total else 0,
        recovery=100 * diverted / collected if collected else 0
    )
