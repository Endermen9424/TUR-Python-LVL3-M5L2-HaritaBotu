from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN

# Veri tabanı yöneticisini başlatma
manager = DB_Map("database.db")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot başlatıldı!")

@bot.command()
async def start(ctx: commands.Context):
    await ctx.send(f"Merhaba, {ctx.author.name}. Mevcut komutların listesini keşfetmek için !help_me yazın.")

@bot.command()
async def help_me(ctx: commands.Context):
    await ctx.send(
        text="""Mevcut komutlar:\n
             !start - Botu başlatır ve selam verir.\n
             !help_me - Mevcut komutların listesini gösterir.\n
             !show_city <şehir_adı> - Belirtilen şehirle birlikte haritayı gösterir.\n
             !show_my_cities - Kullanıcının kaydettiği şehirlerle birlikte haritayı gösterir.\n
             !remember_city <şehir_adı> - Belirtilen şehri kullanıcının şehirleri arasına kaydeder.\n
             """
    )

@bot.command()
async def show_city(ctx: commands.Context, *, city_name=""):
    manager.create_graph("img/map.png", [city_name])  # Belirtilen şehirle harita oluşturma
    await ctx.send(file=discord.File("img/map.png"))  # Haritayı kullanıcıya gönderme

@bot.command()
async def show_my_cities(ctx: commands.Context):
    cities = manager.select_cities(ctx.author.id)  # Kullanıcının kaydettiği şehirlerin listesini alma

    # Kullanıcının şehirleriyle birlikte haritayı gösterecek komutu yazın

@bot.command()
async def remember_city(ctx: commands.Context, *, city_name=""):
    if manager.add_city(ctx.author.id, city_name):  # Şehir adının format uygunluğunu kontrol etme. Başarılıysa şehri kaydet!
        await ctx.send(f'{city_name} şehri başarıyla kaydedildi!')
    else:
        await ctx.send("Hatalı format. Lütfen şehir adını İngilizce olarak ve komuttan sonra bir boşluk bırakarak girin.")

if __name__ == "__main__":
    bot.run(TOKEN)
