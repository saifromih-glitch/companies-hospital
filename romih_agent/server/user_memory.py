"""
Romih per-user memory - remembers conversation context
Stores industry, business type, and recent consultations
"""
import json, os

class UserMemory:
    def __init__(self):
        self.db_url = os.environ.get("DATABASE_URL", "")
        self._init()
    
    def _get_conn(self):
        import psycopg2
        return psycopg2.connect(self.db_url)
    
    def _init(self):
        if not self.db_url:
            return
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS romih_memory (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(chat_id, key)
                )
            """)
            # Add columns to romih_users if they don't exist
            for col in ["industry TEXT", "business_name TEXT", "business_size TEXT"]:
                try:
                    cur.execute(f"ALTER TABLE romih_users ADD COLUMN {col}")
                except:
                    pass
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"UserMemory init: {e}")
    
    def remember(self, chat_id: int, key: str, value: str):
        """Store a fact about the user"""
        if not self.db_url:
            return
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO romih_memory (chat_id, key, value, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (chat_id, key) DO UPDATE SET value = %s, updated_at = NOW()
            """, (chat_id, key, value, value))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"UserMemory.remember: {e}")
    
    def recall(self, chat_id: int, key: str = None) -> dict:
        """Retrieve user facts. If key is None, return all."""
        if not self.db_url:
            return {}
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            if key:
                cur.execute("SELECT key, value FROM romih_memory WHERE chat_id = %s AND key = %s", (chat_id, key))
            else:
                cur.execute("SELECT key, value FROM romih_memory WHERE chat_id = %s ORDER BY updated_at DESC LIMIT 20", (chat_id,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return {r[0]: r[1] for r in rows}
        except Exception as e:
            print(f"UserMemory.recall: {e}")
            return {}
    
    def recall_context(self, chat_id: int) -> str:
        """Return user context as text for system prompt injection"""
        facts = self.recall(chat_id)
        if not facts:
            return ""
        
        lines = ["\nمعلومات عن المستخدم (من الذاكرة):"]
        labels = {
            "industry": "القطاع",
            "business_name": "اسم العمل",
            "business_size": "حجم العمل",
            "last_question": "آخر استفسار",
            "last_goal": "آخر هدف",
        }
        for k, v in facts.items():
            label = labels.get(k, k)
            lines.append(f"- {label}: {v}")
        
        # Remove if only has non-useful keys
        if len(facts) <= 1:
            return ""
        
        return "\n".join(lines)
    
    def extract_and_remember(self, chat_id: int, user_message: str, bot_response: str):
        """Auto-extract key facts from conversation"""
        if not self.db_url or not user_message:
            return
        
        # Store last question
        self.remember(chat_id, "last_question", user_message[:200])
        
        # Simple pattern matching for industry
        industries = {
            "ورشة": "ورشة سيارات",
            "سيارات": "ورشة سيارات",
            "فندق": "فنادق",
            "فنادق": "فنادق",
            "عمرة": "عمرة وحج",
            "حج": "عمرة وحج",
            "مطعم": "مطاعم",
            "مقاولات": "مقاولات",
            "تجارة": "تجارة",
            "تجزئة": "تجارة",
        }
        for keyword, industry in industries.items():
            if keyword in user_message:
                self.remember(chat_id, "industry", industry)
                break
        
        # Extract goals if mentioned
        if "هدف" in user_message or "أريد" in user_message:
            # Take first 100 chars after goal mention
            for marker in ["الهدف:", "أريد:", "عاوز:"]:
                if marker in user_message:
                    goal_start = user_message.find(marker) + len(marker)
                    goal_text = user_message[goal_start:goal_start+100].strip()
                    if goal_text:
                        self.remember(chat_id, "last_goal", goal_text)
                        break

# Global instance
memory = UserMemory()
