import psycopg2

def get_db():
    return psycopg2.connect(
        dbname="balanceiq",
        user="balanceuser",
        password="balancepass",
        host="localhost"
    )