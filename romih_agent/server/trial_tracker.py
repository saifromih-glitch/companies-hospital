"""
Quick trial tracking system for Romih Agent
Store in Railway PostgreSQL, creates table automatically
"""
import os, json
from datetime import datetime, timedelta

TRIAL_DAYS = 10
ADMIN_CHAT_ID = 5660460079  # Mohammed

class TrialTracker:
    def __init__(self):
        self.db_url = os.environ.get("DATABASE_URL", "")
        self._init_table()
    
    def _get_conn(self):
        import psycopg2
        return psycopg2.connect(self.db_url)
    
    def _init_table(self):
        if not self.db_url:
            return
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS romih_users (
                    chat_id BIGINT PRIMARY KEY,
                    name TEXT,
                    trial_start TIMESTAMP DEFAULT NOW(),
                    trial_end TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'active'
                )
            """)
            # Ensure admin exists
            cur.execute("""
                INSERT INTO romih_users (chat_id, name, trial_end, is_admin, status)
                VALUES (%s, 'Mohammed Romih', '2099-12-31', TRUE, 'admin')
                ON CONFLICT (chat_id) DO UPDATE SET is_admin = TRUE, status = 'admin'
            """, (ADMIN_CHAT_ID,))
            conn.commit()
            cur.close()
            conn.close()
            print("TrialTracker: DB ready")
        except Exception as e:
            print(f"TrialTracker: DB init skipped ({e})")
    
    def check(self, chat_id: int, name: str = "") -> dict:
        """Returns {allowed: bool, message: str, days_left: int}"""
        if chat_id == ADMIN_CHAT_ID:
            return {"allowed": True, "message": "", "is_admin": True}
        
        if not self.db_url:
            return {"allowed": True, "message": ""}  # no DB = allow all
        
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("SELECT trial_start, trial_end, status FROM romih_users WHERE chat_id = %s", (chat_id,))
            row = cur.fetchone()
            
            if not row:
                # New user - register
                now = datetime.utcnow()
                trial_end = now + timedelta(days=TRIAL_DAYS)
                cur.execute("""
                    INSERT INTO romih_users (chat_id, name, trial_start, trial_end, status)
                    VALUES (%s, %s, %s, %s, 'trial')
                """, (chat_id, name, now, trial_end))
                conn.commit()
                days_left = TRIAL_DAYS
                allowed = True
                message = ""
            else:
                trial_start, trial_end, status = row
                if status == 'admin' or status == 'paid':
                    allowed = True
                    message = ""
                    days_left = 999
                elif trial_end and datetime.utcnow() > trial_end:
                    allowed = False
                    days_left = 0
                    message = "انتهت الفترة التجريبية المجانية (١٠ أيام). للاشتراك: https://t.me/RomihAgentbot"
                else:
                    allowed = True
                    days_left = (trial_end - datetime.utcnow()).days + 1 if trial_end else TRIAL_DAYS
                    message = ""
            
            cur.close()
            conn.close()
            return {"allowed": allowed, "message": message, "days_left": days_left}
        except Exception as e:
            print(f"TrialTracker: check failed ({e})")
            return {"allowed": True, "message": ""}  # fail open

# Global instance
tracker = TrialTracker()
