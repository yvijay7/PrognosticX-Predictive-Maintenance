"""
PrognosticX - SQLite Database Layer
Stores machines, real-time sensor logs, fault predictions, RUL estimates,
maintenance orders, alerts, and what-if simulation history.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "prognosticx.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Machines Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS machines (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        location TEXT NOT NULL,
        criticality TEXT NOT NULL,
        status TEXT NOT NULL,
        installation_date TEXT,
        last_maintenance TEXT
    )
    """)
    
    # 2. Sensor Readings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        temperature REAL NOT NULL,
        vibration REAL NOT NULL,
        rpm REAL NOT NULL,
        pressure REAL NOT NULL,
        load_pct REAL NOT NULL,
        operating_hours REAL NOT NULL,
        FOREIGN KEY(machine_id) REFERENCES machines(id)
    )
    """)
    
    # 3. Fault Predictions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fault_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        fault_class INTEGER NOT NULL,
        fault_type TEXT NOT NULL,
        confidence REAL NOT NULL,
        severity TEXT NOT NULL,
        contributing_factors TEXT,
        FOREIGN KEY(machine_id) REFERENCES machines(id)
    )
    """)
    
    # 4. RUL Predictions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rul_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        predicted_rul REAL NOT NULL,
        time_to_critical REAL NOT NULL,
        degradation_trend TEXT NOT NULL,
        health_score REAL NOT NULL,
        FOREIGN KEY(machine_id) REFERENCES machines(id)
    )
    """)
    
    # 5. Maintenance Plans Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        priority TEXT NOT NULL,
        priority_score REAL NOT NULL,
        recommended_action TEXT NOT NULL,
        suggested_window TEXT NOT NULL,
        reason TEXT NOT NULL,
        inspection_checklist TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(machine_id) REFERENCES machines(id)
    )
    """)
    
    # 6. Alerts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        level TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        acknowledged INTEGER DEFAULT 0,
        FOREIGN KEY(machine_id) REFERENCES machines(id)
    )
    """)
    
    # 7. What-If Simulation History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        scenario_name TEXT NOT NULL,
        sim_temperature REAL NOT NULL,
        sim_vibration REAL NOT NULL,
        sim_rpm REAL NOT NULL,
        sim_pressure REAL NOT NULL,
        sim_load REAL NOT NULL,
        res_health REAL NOT NULL,
        res_fault_risk REAL NOT NULL,
        res_fault_name TEXT NOT NULL,
        res_rul REAL NOT NULL,
        res_priority TEXT NOT NULL
    )
    """)
    
    # Populate default machines if empty
    cursor.execute("SELECT COUNT(*) as count FROM machines")
    if cursor.fetchone()["count"] == 0:
        default_machines = [
            ("MCH-001", "CNC Milling Unit 1 (Alpha)", "CNC Milling", "Shop Floor 1", "HIGH", "ACTIVE", "2024-01-15", "2026-08-10"),
            ("MCH-002", "Lathe Spindle Motor 2 (Beta)", "Industrial Lathe", "Shop Floor 1", "MEDIUM", "ACTIVE", "2024-03-20", "2026-08-25"),
            ("MCH-003", "Hydraulic Compressor (Gamma)", "Hydraulic Pump", "Utility Bay", "CRITICAL", "WARNING", "2023-11-05", "2026-07-30"),
            ("MCH-004", "Conveyor Drive Motor (Delta)", "Induction Motor", "Assembly Line A", "LOW", "ACTIVE", "2024-06-12", "2026-08-28"),
            ("MCH-005", "High-Torque Extruder (Epsilon)", "Extruder", "Molding Zone", "HIGH", "MAINTENANCE", "2023-08-19", "2026-08-01")
        ]
        cursor.executemany("""
        INSERT INTO machines (id, name, type, location, criticality, status, installation_date, last_maintenance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, default_machines)
        
        # Add starter alerts
        starter_alerts = [
            ("MCH-003", "2026-09-02 18:30:00", "CRITICAL", "Thermal Anomaly Spike Detected", "Cylinder core temp exceeded 85°C with high continuous load.", "Reduce hydraulic operating pressure and inspect heat dissipation fins.", 0),
            ("MCH-001", "2026-09-02 19:15:00", "WARNING", "Vibration Drift Near Warning Limit", "Vibration RMS trend reached 3.85 mm/s. Bearing wear suspected.", "Schedule grease lubrication check during next shift transition.", 0),
            ("MCH-002", "2026-09-02 20:00:00", "INFO", "RUL Routine Re-baseline Complete", "Operational RUL updated to 2,740 operating hours.", "Normal operation confirmed.", 1)
        ]
        cursor.executemany("""
        INSERT INTO alerts (machine_id, timestamp, level, title, description, recommended_action, acknowledged)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, starter_alerts)
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("PrognosticX SQLite database initialized successfully.")
