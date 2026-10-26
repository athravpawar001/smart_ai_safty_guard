"""
Database module for Smart AI Safety Guard with Automated Testing.
Handles SQLite database initialization, parameterized CRUD operations,
and relational integrity across test cases, AI responses, safety evaluations, and test results.
"""

import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "safety_guard.db")


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database with row factory and foreign key enforcement.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initialize SQLite database and create required tables if they don't exist:
    - Test_Cases
    - AI_Responses
    - Safety_Results
    - Test_Results
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Test_Cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test_Cases (
                Test_ID TEXT PRIMARY KEY,
                Prompt TEXT NOT NULL,
                Category TEXT NOT NULL,
                Expected_Result TEXT NOT NULL,
                Description TEXT
            );
        """)

        # 2. AI_Responses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AI_Responses (
                Response_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Test_ID TEXT NOT NULL,
                AI_Model TEXT NOT NULL,
                Response_Text TEXT NOT NULL,
                Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Test_ID) REFERENCES Test_Cases(Test_ID) ON DELETE CASCADE
            );
        """)

        # 3. Safety_Results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Safety_Results (
                Safety_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Response_ID INTEGER NOT NULL,
                Safety_Status TEXT NOT NULL,
                Safety_Category TEXT NOT NULL,
                Warning TEXT,
                FOREIGN KEY (Response_ID) REFERENCES AI_Responses(Response_ID) ON DELETE CASCADE
            );
        """)

        # 4. Test_Results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Test_Results (
                Result_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Test_ID TEXT NOT NULL,
                Actual_Result TEXT NOT NULL,
                Expected_Result TEXT NOT NULL,
                Test_Status TEXT NOT NULL,
                Remarks TEXT,
                Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Test_ID) REFERENCES Test_Cases(Test_ID) ON DELETE CASCADE
            );
        """)

        # 5. Analysis_History table for ad-hoc safety checks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Analysis_History (
                Analysis_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Prompt TEXT,
                Response_Text TEXT NOT NULL,
                AI_Model TEXT DEFAULT 'Local Rule Guard',
                Safety_Status TEXT NOT NULL,
                Safety_Category TEXT NOT NULL,
                Risk_Score REAL NOT NULL,
                Confidence TEXT NOT NULL,
                Warning TEXT,
                Reasons TEXT,
                Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        logger.info("Database initialized successfully at %s", db_path)


# ==============================================================================
# Test Cases Operations
# ==============================================================================

def add_test_case(test_id: str, prompt: str, category: str, expected_result: str, 
                  description: str = "", db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Insert a single test case into Test_Cases using parameterized query.
    Returns True if successful, False if Test_ID already exists or error.
    """
    sql = """
        INSERT INTO Test_Cases (Test_ID, Prompt, Category, Expected_Result, Description)
        VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection(db_path) as conn:
            conn.execute(sql, (test_id.strip(), prompt.strip(), category.strip(), 
                               expected_result.strip(), description.strip()))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        logger.warning("Test_ID '%s' already exists in Test_Cases.", test_id)
        return False
    except Exception as e:
        logger.error("Error adding test case: %s", e)
        raise e


def bulk_add_test_cases(test_cases: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> Tuple[int, int]:
    """
    Bulk insert test cases. Skips duplicates.
    Returns tuple: (inserted_count, skipped_count).
    """
    inserted = 0
    skipped = 0
    sql = """
        INSERT OR IGNORE INTO Test_Cases (Test_ID, Prompt, Category, Expected_Result, Description)
        VALUES (?, ?, ?, ?, ?)
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        for tc in test_cases:
            cursor.execute(sql, (
                str(tc.get("Test_ID", "")).strip(),
                str(tc.get("Prompt", "")).strip(),
                str(tc.get("Category", "")).strip(),
                str(tc.get("Expected_Result", "")).strip(),
                str(tc.get("Description", "")).strip(),
            ))
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        conn.commit()
    return inserted, skipped


def get_all_test_cases(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Retrieve all test cases as a pandas DataFrame.
    """
    sql = "SELECT Test_ID, Prompt, Category, Expected_Result, Description FROM Test_Cases ORDER BY Test_ID ASC"
    with get_db_connection(db_path) as conn:
        return pd.read_sql_query(sql, conn)


def get_test_case_by_id(test_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific test case by Test_ID.
    """
    sql = "SELECT Test_ID, Prompt, Category, Expected_Result, Description FROM Test_Cases WHERE Test_ID = ?"
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(sql, (test_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def update_test_case(test_id: str, prompt: str, category: str, expected_result: str,
                     description: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Update an existing test case.
    """
    sql = """
        UPDATE Test_Cases 
        SET Prompt = ?, Category = ?, Expected_Result = ?, Description = ?
        WHERE Test_ID = ?
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(sql, (prompt.strip(), category.strip(), expected_result.strip(), 
                                    description.strip(), test_id.strip()))
        conn.commit()
        return cursor.rowcount > 0


def delete_test_case(test_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Delete a test case by Test_ID. Cascades to related responses/results.
    """
    sql = "DELETE FROM Test_Cases WHERE Test_ID = ?"
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(sql, (test_id,))
        conn.commit()
        return cursor.rowcount > 0


# ==============================================================================
# AI Responses, Safety Results & Test Results Operations
# ==============================================================================

def record_test_run(
    test_id: str,
    ai_model: str,
    response_text: str,
    safety_status: str,
    safety_category: str,
    warning: str,
    actual_result: str,
    expected_result: str,
    test_status: str,
    remarks: str,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, int]:
    """
    Atomically records a test execution across AI_Responses, Safety_Results, and Test_Results.
    Returns dictionary with generated IDs: {'response_id', 'safety_id', 'result_id'}.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Insert AI_Responses
        cursor.execute("""
            INSERT INTO AI_Responses (Test_ID, AI_Model, Response_Text)
            VALUES (?, ?, ?)
        """, (test_id, ai_model, response_text))
        response_id = cursor.lastrowid

        # 2. Insert Safety_Results
        cursor.execute("""
            INSERT INTO Safety_Results (Response_ID, Safety_Status, Safety_Category, Warning)
            VALUES (?, ?, ?, ?)
        """, (response_id, safety_status, safety_category, warning))
        safety_id = cursor.lastrowid

        # 3. Insert Test_Results
        cursor.execute("""
            INSERT INTO Test_Results (Test_ID, Actual_Result, Expected_Result, Test_Status, Remarks)
            VALUES (?, ?, ?, ?, ?)
        """, (test_id, actual_result, expected_result, test_status, remarks))
        result_id = cursor.lastrowid

        conn.commit()

        return {
            "response_id": response_id,
            "safety_id": safety_id,
            "result_id": result_id
        }


def get_dashboard_metrics(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Calculates key metrics for the Dashboard:
    - Total test cases
    - Total test executions
    - Passed tests
    - Failed tests
    - Suspicious results
    - Potentially unsafe detections
    - Unsafe detections
    - Safe detections
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # Total test cases defined
        cursor.execute("SELECT COUNT(*) FROM Test_Cases")
        total_cases = cursor.fetchone()[0]

        # Total test executions
        cursor.execute("SELECT COUNT(*) FROM Test_Results")
        total_executions = cursor.fetchone()[0]

        # Passed, Failed, Suspicious
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN Test_Status = 'PASS' THEN 1 ELSE 0 END) AS passed,
                SUM(CASE WHEN Test_Status = 'FAIL' THEN 1 ELSE 0 END) AS failed,
                SUM(CASE WHEN Test_Status = 'SUSPICIOUS' THEN 1 ELSE 0 END) AS suspicious
            FROM Test_Results
        """)
        row = cursor.fetchone()
        passed = row[0] or 0
        failed = row[1] or 0
        suspicious = row[2] or 0

        # Safety status breakdown from Safety_Results
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN Safety_Status = 'Safe' THEN 1 ELSE 0 END) AS safe_cnt,
                SUM(CASE WHEN Safety_Status = 'Potentially Unsafe' THEN 1 ELSE 0 END) AS pot_unsafe_cnt,
                SUM(CASE WHEN Safety_Status = 'Unsafe' THEN 1 ELSE 0 END) AS unsafe_cnt,
                SUM(CASE WHEN Safety_Status = 'Suspicious' THEN 1 ELSE 0 END) AS susp_cnt
            FROM Safety_Results
        """)
        s_row = cursor.fetchone()
        safe_cnt = s_row[0] or 0
        pot_unsafe_cnt = s_row[1] or 0
        unsafe_cnt = s_row[2] or 0
        susp_cnt = s_row[3] or 0

        return {
            "total_test_cases": total_cases,
            "total_executions": total_executions,
            "passed": passed,
            "failed": failed,
            "suspicious": suspicious,
            "safe_count": safe_cnt,
            "potentially_unsafe_count": pot_unsafe_cnt,
            "unsafe_count": unsafe_cnt,
            "suspicious_safety_count": susp_cnt
        }


def get_recent_activity(limit: int = 10, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Fetch the most recent testing activity joining Test_Results, Test_Cases, and Safety_Results.
    """
    sql = """
        SELECT 
            tr.Result_ID,
            tr.Test_ID,
            tc.Prompt,
            tc.Category AS Test_Category,
            tr.Expected_Result,
            tr.Actual_Result,
            tr.Test_Status,
            tr.Remarks,
            tr.Timestamp
        FROM Test_Results tr
        LEFT JOIN Test_Cases tc ON tr.Test_ID = tc.Test_ID
        ORDER BY tr.Result_ID DESC
        LIMIT ?
    """
    with get_db_connection(db_path) as conn:
        return pd.read_sql_query(sql, conn, params=(limit,))


def get_full_test_history(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Retrieve full historical test records with linked AI responses and safety status.
    """
    sql = """
        SELECT 
            tr.Result_ID,
            tr.Test_ID,
            tc.Category AS Test_Category,
            tc.Prompt,
            ar.Response_Text AS AI_Response,
            ar.AI_Model,
            tr.Expected_Result,
            tr.Actual_Result AS Actual_Safety_Status,
            sr.Safety_Category AS Detected_Category,
            sr.Warning,
            tr.Test_Status,
            tr.Remarks,
            tr.Timestamp
        FROM Test_Results tr
        LEFT JOIN Test_Cases tc ON tr.Test_ID = tc.Test_ID
        LEFT JOIN AI_Responses ar ON tr.Test_ID = ar.Test_ID
        LEFT JOIN Safety_Results sr ON ar.Response_ID = sr.Response_ID
        ORDER BY tr.Result_ID DESC
    """
    with get_db_connection(db_path) as conn:
        return pd.read_sql_query(sql, conn)


def get_safety_category_distribution(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Distribution of detected safety categories from Safety_Results.
    """
    sql = """
        SELECT Safety_Category, COUNT(*) AS Count
        FROM Safety_Results
        GROUP BY Safety_Category
        ORDER BY Count DESC
    """
    with get_db_connection(db_path) as conn:
        return pd.read_sql_query(sql, conn)


def clear_test_history(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Clear all execution history (AI_Responses, Safety_Results, Test_Results),
    while preserving Test_Cases.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Test_Results;")
        cursor.execute("DELETE FROM Safety_Results;")
        cursor.execute("DELETE FROM AI_Responses;")
        conn.commit()
        logger.info("Test execution history cleared.")
