import requests
from bs4 import BeautifulSoup as bs
import sqlite3


class DataBase:
    def __init__(self, db_name='sites.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create()

    def create(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                url TEXT
            )
        ''')
        self.connection.commit()

    def insert(self, name, url):
        self.cursor.execute('INSERT INTO sites (name, url) VALUES (?, ?)', (name, url))
        self.connection.commit()

    def select_url(self, name):
        self.cursor.execute('SELECT url FROM sites WHERE name = ?', (name,))
        return self.cursor.fetchone()

    def select_all(self):
        self.cursor.execute('SELECT * FROM sites')
        return self.cursor.fetchall()

    def clear(self):
        self.cursor.execute('DELETE FROM sites')
        self.connection.commit()


class Parcing:
    def __init__(self, db):
        self.db = db
        self.results = []

    def parse(self, url, site_name):
        r = requests.get(url)
        html = bs(r.text, "html.parser")

        if site_name == 'Sinoptik':
            temperature_tags = html.find_all('td', class_='p6 bR cur')
            results = [tag.text for tag in temperature_tags]
            self.results.extend(results)
        elif site_name == 'Auto.Ria':
            address = html.find_all('a', class_='address')
            results = [tag.text for tag in address]
            self.results.extend(results)
        elif site_name == 'NBY':
            td_tags = html.find_all('td')
            results = [tag.text for tag in td_tags]
            self.results.extend(results)

    def show_results(self):
        if not self.results:
            print("No results available.")
            return

        print("Results:")
        for result in self.results:
            print(result)

    def interface(self):
        while True:
            choice = input("Choose an option:\n1. Add site\n2. Parse site\n3. Show results\n4. Clear database\n5. Exit\n")

            if choice == '1':
                name = input("Enter site name (NBY, Sinoptik, Auto.Ria): ")
                if name == 'NBY':
                    url = 'https://bank.gov.ua/ua/markets/exchangerates'
                elif name == 'Sinoptik':
                    url = 'https://ua.sinoptik.ua/'
                elif name == 'Auto.Ria':
                    url = 'https://auto.ria.com/uk/legkovie/lamborghini/?page=1'
                else:
                    print("Invalid site name. Supported names are NBY, Sinoptik, and Auto.Ria.")
                    continue

                self.db.insert(name, url)
                print(f"Site {name} added to the database.")

            elif choice == '2':
                name = input("Enter site name to parse (NBY, Sinoptik, Auto.Ria): ")
                url = self.db.select_url(name)
                if url:
                    url = url[0]
                    self.results = []  # Очистити список результатів перед новим парсингом
                    self.parse(url, name)
                    print("Site parsed successfully.")
                else:
                    print("Site not found in the database.")

            elif choice == '3':
                self.show_results()

            elif choice == '4':
                self.db.clear()
                print("Database cleared.")

            elif choice == '5':
                break

            else:
                print("Invalid choice. Please choose a valid option.")

    def run(self):
        self.interface()


if __name__ == "__main__":
    db = DataBase()
    parser = Parcing(db)
    parser.run()
    db.connection.close()
