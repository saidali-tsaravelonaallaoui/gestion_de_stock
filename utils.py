import mysql.connector
from mysql.connector import Error
import csv

def get_categories(cursor):
    try:
        cursor.execute("SELECT name FROM category")
        categories = [row[0] for row in cursor.fetchall()]
        return categories
    except Error as e:
        print("Erreur lors de la récupération des catégories :", e)
        return []
