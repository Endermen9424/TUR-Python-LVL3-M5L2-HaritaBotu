import sqlite3
import matplotlib

matplotlib.use('Agg')  # Matplotlib arka planını, pencere göstermeden dosyaları bellekte kaydetmek için ayarlama
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  # Harita projeksiyonlarıyla çalışmamızı sağlayacak modülü içe aktarma

class DB_Map():
    def __init__(self, database):
        self.database = database  # Veri tabanı yolunu belirleme

    def create_user_table(self):
        conn = sqlite3.connect(self.database)  # Veri tabanına bağlanma
        with conn:
            # Kullanıcı şehirlerini depolamak için bir tablo oluşturma (eğer yoksa)
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  # Değişiklikleri onaylama

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Veri tabanında şehir adına göre sorgulama yapma
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Şehri kullanıcının şehir listesine ekleme
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  # İşlemin başarılı olduğunu belirtme
            else:
                return 0  # Şehir bulunamadı

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Kullanıcının tüm şehirlerini seçme
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  # Kullanıcının şehir listesini döndürme

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Şehrin adına göre koordinatlarını alma
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  # Şehrin koordinatlarını döndürme

    def create_graph(self, path, cities):
        # Harita oluşturma
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()  # Temel harita görüntüsünü ekleme

        # Şehirlerin koordinatlarını alma ve haritaya işaretleme
        coordinats = [self.get_coordinates(city) for city in cities]
        for coord, city in zip(coordinats, cities):
            if coord:
                lat, lon = coord
                ax.plot(lon, lat, marker='o', color='red', markersize=5, transform=ccrs.PlateCarree())
                ax.text(lon + 0.5, lat + 0.5, city, transform=ccrs.PlateCarree())
        plt.title('User Cities Map')
        plt.savefig(path)  # Haritayı belirtilen yola kaydetme
        plt.close()

    def draw_distance(self, city1, city2, path='img/distance.png'):
        # İki şehir arasındaki mesafeyi göstermek için bir çizgi çizme
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()  # Temel harita görüntüsünü ekleme
        coord1 = self.get_coordinates(city1)
        coord2 = self.get_coordinates(city2)
        if coord1 and coord2:
            lat1, lon1 = coord1
            lat2, lon2 = coord2
            ax.plot([lon1, lon2], [lat1, lat2], color='blue', linewidth=2, marker='o', transform=ccrs.PlateCarree())
            ax.text(lon1 + 0.5, lat1 + 0.5, city1, transform=ccrs.PlateCarree())
            ax.text(lon2 + 0.5, lat2 + 0.5, city2, transform=ccrs.PlateCarree())
            plt.title(f'Distance between {city1} and {city2}')
            plt.savefig(path)  # Mesafe haritasını kaydetme
            plt.close()


if __name__ == "__main__":
    m = DB_Map("database.db")  # Veri tabanıyla etkileşime geçecek bir nesne oluşturma
    m.create_user_table()   # Kullanıcı şehirleri tablosunu oluşturma (eğer zaten yoksa)
    m.create_graph("img/map.png", ["Istanbul"])
    m.draw_distance("Istanbul", "Eskisehir", "img/distance.png")
