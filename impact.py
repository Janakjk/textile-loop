from database import query, requests_df

def _sum(df):
    return float(df.quantity_kg.sum()) if len(df) else 0.0

def stats(exclude_demo=False):
    """Calculate circularity metrics. Optionally exclude sample/demo records for actual live statistics."""
    w_filter = "WHERE is_demo=0" if exclude_demo else ""
    total = _sum(query(f"SELECT quantity_kg FROM waste_records {w_filter}"))
    r = requests_df(exclude_demo=exclude_demo)
    
    p_sql = ("SELECT p.outcome, p.quantity_kg, rd.ftype "
             "FROM processing_records p "
             "JOIN collection_requests cr ON cr.id=p.collection_id "
             "JOIN waste_records w ON w.id=cr.waste_id "
             "JOIN recycler_directory rd ON rd.id=cr.recycler_id "
             "WHERE p.verified=1 ")
    if exclude_demo:
        p_sql += "AND w.is_demo=0 "
    p = query(p_sql)
    
    # Donated specifically via NGOs & Donation centres vs general reuse vs mechanical recycling
    donated = _sum(p[(p.outcome == "Reused") & (p.ftype.isin(["Donation centre", "NGO"]))])
    reused = _sum(p[p.outcome == "Reused"])
    recycled = _sum(p[p.outcome == "Recycled"])
    
    collected = _sum(r[r.status.isin(["Collected", "Processing", "Reused", "Recycled", "Disposed"])])
    disposal = _sum(r[r.status.isin(["Collected", "Processing", "Disposed"]) & (r.ftype == "Authorized waste collection agency")])
    diverted = reused + recycled
    pending = _sum(r[r.status.isin(["Pending", "Approved", "Scheduled"])])
    in_process = _sum(r[r.status == "Processing"])
    active_partners = int(query("SELECT COUNT(DISTINCT id) AS n FROM recycler_directory").n[0])
    
    return dict(
        total=total,
        collected=collected,
        donated=donated,
        reused=reused,
        recycled=recycled,
        disposal=disposal,
        diverted=diverted,
        pending=pending,
        awaiting=max(total - collected, 0),
        in_process=in_process,
        active_partners=active_partners,
        pct=100 * diverted / total if total else 0,
        recovery=100 * diverted / collected if collected else 0
    )
