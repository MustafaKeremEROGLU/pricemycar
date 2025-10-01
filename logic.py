import sqlite3
from config import *
import os
from dotenv import load_dotenv

load_dotenv(override=True)
Database = os.environ.get("Database")

class DataBase_M:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
                    
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ilanlar(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ilan_no INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                marka TEXT NOT NULL,
                model TEXT NOT NULL,
                motor TEXT NOT NULL,
                yıl INTEGER NOT NULL,
                km INTEGER NOT NULL,
                tramer INTEGER NOT NULL,
                fiyat INTEGER NOT NULL,
                aciklama TEXT NOT NULL
            );
            """
        )
        conn.commit()
        conn.close()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    # --- Yeni metodlar ---
    def ilan_ekle(self, ilan_no, user_id, marka, model, motor, yıl, km, tramer, fiyat, aciklama):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(
                "INSERT INTO ilanlar (ilan_no, user_id, marka, model, motor, yıl, km, tramer, fiyat, aciklama) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (ilan_no, user_id, marka, model, motor, yıl, km, tramer, fiyat, aciklama)
            )
            conn.commit()

    def ilan_sil(self, ilan_no):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("DELETE FROM ilanlar WHERE ilan_no = ?", (ilan_no,))
            conn.commit()

    def fiyat_guncelle(self, ilan_no, yeni_fiyat):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("UPDATE ilanlar SET fiyat = ? WHERE ilan_no = ?", (yeni_fiyat, ilan_no))
            conn.commit()

    def km_guncelle(self, ilan_no, yeni_km):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("UPDATE ilanlar SET km = ? WHERE ilan_no = ?", (yeni_km, ilan_no))
            conn.commit()

    def ilan_getir(self, ilan_no):
        return self.__select_data("SELECT * FROM ilanlar WHERE ilan_no = ?", (ilan_no,))
    
    def getir_marka_model(self, marka, model):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        sql = "SELECT * FROM ilanlar WHERE marka = ? AND model = ?"
        cursor.execute(sql, (marka, model))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def fiyat_getir(self, ilan_no):
        return self.__select_data("SELECT fiyat FROM ilanlar WHERE ilan_no = ?", (ilan_no,))
    
    def km_getir(self, ilan_no):
        return self.__select_data("SELECT km FROM ilanlar WHERE ilan_no = ?", (ilan_no,))

        
if __name__ == '__main__':
    manager = DataBase_M(Database)
    manager.create_tables()                    
    