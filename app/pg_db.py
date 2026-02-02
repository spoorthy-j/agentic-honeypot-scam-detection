import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def insert_scam_message(message: str, scam_type: str, confidence: float, source: str = "user"):
    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO scam_messages (message, scam_type, confidence, source)
                VALUES (:m, :t, :c, :s)
            """),
            {"m": message, "t": scam_type, "c": float(confidence), "s": source}
        )
        db.commit()
    finally:
        db.close()

def fetch_latest_messages(limit: int = 20):
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT id, message, scam_type, confidence, source, detected_at
                FROM scam_messages
                ORDER BY detected_at DESC
                LIMIT :lim
            """),
            {"lim": int(limit)}
        ).mappings().all()
        return [dict(r) for r in rows]
    finally:
        db.close()

def fetch_stats(days: int = 7):
    db = SessionLocal()
    try:
        total = db.execute(
            text("SELECT COUNT(*) AS c FROM scam_messages")
        ).mappings().first()["c"]

        by_type = db.execute(
            text("""
                SELECT COALESCE(scam_type,'UNKNOWN') AS scam_type, COUNT(*) AS c
                FROM scam_messages
                GROUP BY COALESCE(scam_type,'UNKNOWN')
                ORDER BY c DESC
            """)
        ).mappings().all()

        by_source = db.execute(
            text("""
                SELECT COALESCE(source,'unknown') AS source, COUNT(*) AS c
                FROM scam_messages
                GROUP BY COALESCE(source,'unknown')
                ORDER BY c DESC
            """)
        ).mappings().all()

        # last N days time-series
        timeseries = db.execute(
            text("""
                SELECT DATE(detected_at) AS day, COUNT(*) AS c
                FROM scam_messages
                WHERE detected_at >= NOW() - (:d || ' days')::interval
                GROUP BY DATE(detected_at)
                ORDER BY day ASC
            """),
            {"d": int(days)}
        ).mappings().all()

        return {
            "total": int(total),
            "by_type": [dict(r) for r in by_type],
            "by_source": [dict(r) for r in by_source],
            "timeseries": [{"day": str(r["day"]), "count": int(r["c"])} for r in timeseries],
        }
    finally:
        db.close()
