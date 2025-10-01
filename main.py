import discord
from discord.ext import commands
from discord.ui import *
import random
import os
from dotenv import load_dotenv
from logic import DataBase_M

load_dotenv(override=True)
TOKEN = os.environ.get("TOKEN")
Database = os.environ.get("Database")

db = DataBase_M(Database)


class ArabaVerisi:
    def __init__(self, arabamarka, arabamodel, arabamotor, yıl, km, tramer):
        self.arabamarka = arabamarka
        self.arabamodel = arabamodel
        self.arabamotor = arabamotor
        self.yıl = yıl
        self.km = km
        self.tramer = tramer

    def __str__(self):
        return (f"{self.arabamarka}, {self.arabamodel}, {self.arabamotor} motorlu araba "
                f"{self.yıl} yılında trafiğe çıkmış, {self.km} km'de ve {self.tramer} TL tramer kaydı var.")

    def fiyat_hesapla(self):
        fiyat = 900000  # Başlangıç fiyatı

        # Popüler araç markalarına göre fiyat artışı
        markalar = {
            "volkswagen": 50000, "mercedes": 800000, "bmw": 700000, "audi": 600000, "toyota": 100000,
            "ford": 200000, "opel": 150000, "peugeot": 120000, "renault": 100000, "fiat": 80000,
            "mazda": 300000, "kia": 250000, "hyundai": 200000, "nissan": 400000, "honda": 350000,
            "jeep": 450000, "subaru": 500000, "mini": 600000, "lexus": 900000, "porsche": 1500000,
            "volvo": 750000, "mitsubishi": 300000, "suzuki": 200000, "chrysler": 350000,
            "cadillac": 1200000, "chevrolet": 400000, "dodge": 500000, "buick": 600000, "infiniti": 800000
        }

        # En pahalı 2 modelin fiyat artışı
        pahali_modeller = {
            "volkswagen": {"passat": 150000, "touareg": 200000},
            "mercedes": {"s-class": 500000, "gle": 350000},
            "bmw": {"7-series": 400000, "x5": 350000},
            "audi": {"a8": 450000, "q7": 400000},
            "toyota": {"landcruiser": 300000, "supra": 350000},
            "ford": {"mustang": 250000, "expedition": 200000},
            "opel": {"insignia": 100000, "grandland": 150000},
            "peugeot": {"5008": 350000, "3008": 150000},
            "renault": {"koleos": 100000, "talisman": 120000},
            "fiat": {"500x": 150000, "tipo": 100000},
            # Diğer markaların pahalı modellerini burada tanımlayabilirsiniz
        }

        # Marka fiyat artırma
        marka_lower = self.arabamarka.lower()
        if marka_lower in markalar:
            fiyat += markalar[marka_lower]

        # Modelin pahalı 2 modeline göre fiyat artışı
        model_lower = self.arabamodel.lower()
        if marka_lower in pahali_modeller:
            if model_lower in pahali_modeller[marka_lower]:
                fiyat += pahali_modeller[marka_lower][model_lower]

        fiyat -= (2025 - self.yıl) * 12500  # Yıl düşüşü
        fiyat -= self.km * 0.5  # Kilometreye göre düşüş
        fiyat -= self.tramer * 0.8  # Tramer kaydına göre düşüş
        return max(100000, int(fiyat))  # Minimum fiyat

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="<", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print("BOT KULLANIMA AÇIK")

@bot.command()
async def fiyat(ctx, arabamarka: str, arabamodel: str, arabamotor: str, yıl: int, km: int, tramer: int):
    araba = ArabaVerisi(arabamarka, arabamodel, arabamotor, yıl, km, tramer)
    tahmini_fiyat = araba.fiyat_hesapla()

    embed = discord.Embed(title="🚗 Araç Bilgisi ve Fiyat Tahmini", color=0x00ff00)
    embed.add_field(name="Araç", value=str(araba), inline=False)
    embed.add_field(name="Tahmini Fiyat", value=f"{tahmini_fiyat} TL", inline=False)
    # Hızlı sat fiyatı
    embed.add_field(name="Hızlı Sat Fiyatı", value=f"{tahmini_fiyat - 80000} TL", inline=False)

    await ctx.send(embed=embed)


# ----------------------------
# Fiyat Güncelleme Modalı
# ----------------------------
# ----------------------------
class FiyatModal(discord.ui.Modal, title="💰 Yeni Fiyat Belirle"):
    yeni_fiyat = discord.ui.TextInput(label="Yeni fiyatı giriniz", placeholder="Örn: 250000", required=True)

    def __init__(self, ilan_no: int, ilan_sahibi: int):
        super().__init__()
        self.ilan_no = ilan_no
        self.ilan_sahibi = ilan_sahibi

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.ilan_sahibi:
            await interaction.response.send_message(
                "⚠️ Bu ilan size ait değil, fiyatını güncelleyemezsiniz.",
                ephemeral=True
            )
            return

        db.fiyat_guncelle(self.ilan_no, int(self.yeni_fiyat.value))
        await interaction.response.send_message(
            f"✅ İlan `{self.ilan_no}` için fiyat {self.yeni_fiyat.value} TL olarak güncellendi.",
            ephemeral=True
        )

class kmModal(discord.ui.Modal, title="🛣️ Yeni Kilometre Belirle"):
    yeni_km = discord.ui.TextInput(label="🛣️ Yeni Kilometre giriniz", placeholder="Örn: 125000", required=True)

    def __init__(self, ilan_no: int, ilan_sahibi: int):
        super().__init__()
        self.ilan_no = ilan_no
        self.ilan_sahibi = ilan_sahibi

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.ilan_sahibi:
            await interaction.response.send_message(
                "⚠️ Bu ilan size ait değil, kilometresini güncelleyemezsiniz.",
                ephemeral=True
            )
            return

        db.km_guncelle(self.ilan_no, int(self.yeni_km.value))
        await interaction.response.send_message(
            f"✅ İlan `{self.ilan_no}` için kilometre {self.yeni_km.value} olarak güncellendi.",
            ephemeral=True
        )       
# ----------------------------
# İlan Ayarları Butonları
# ----------------------------
class SettingsView(discord.ui.View):
    def __init__(self, ilan_no: int, ilan_sahibi: int):
        super().__init__(timeout=None)
        self.ilan_no = ilan_no
        self.ilan_sahibi = ilan_sahibi

    @discord.ui.button(label="🗑️ İlanı Sil", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ilan_sahibi:
            await interaction.response.send_message(
                "⚠️ Bu ilan size ait değil, silemezsiniz.",
                ephemeral=True
            )
            return

        db.ilan_sil(self.ilan_no)
        await interaction.response.send_message(
            f"❌ İlan `{self.ilan_no}` silindi.",
            ephemeral=True
        )

    @discord.ui.button(label="💰 Fiyat Güncelle", style=discord.ButtonStyle.primary)
    async def update_price_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = FiyatModal(self.ilan_no, self.ilan_sahibi)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🛣️ Kilometre Güncelle", style=discord.ButtonStyle.secondary)
    async def update_km_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        kmmodal = kmModal(self.ilan_no, self.ilan_sahibi)
        await interaction.response.send_modal(kmmodal)    

# ----------------------------
# Komut
# ----------------------------
@bot.command()
async def ilanver(ctx, marka: str, model: str, motor: str, yıl: int, km: int, tramer: int, fiyat: int, *, aciklama:str):
    ilan_no = random.randint(1, 100000)

    # DB'ye ekleme → ilanı oluşturan kişi ctx.author
    db.ilan_ekle(ilan_no, ctx.author.id, marka, model, motor, yıl, km, tramer, fiyat, aciklama)

    embed = discord.Embed(
        title="🚗 Araba İlanı Oluşturuldu",
        description=f"{marka} {model}, {motor} motorlu\n{yıl} model, {km} km, {tramer} TL tramer\n--------Açıklama--------\n{aciklama}",
        color=discord.Color.green()
    )
    embed.add_field(name="💰 Fiyat", value=f"{fiyat} TL", inline=False)
    embed.add_field(name="🆔 İlan No", value=str(ilan_no), inline=False)

    await ctx.author.send(embed=embed)  # DM ile gönder
    
@bot.command()
async def settings(ctx, ilan_no: int):
    ilan = db.ilan_getir(ilan_no)
    if not ilan:
        await ctx.send("⚠️ Böyle bir ilan bulunamadı.")
        return

    # DB'den ilan bilgisi (ilk kayıt)
    ilan_data = ilan[0]
    ilan_sahibi = ilan_data[2]  # user_id sütunu

    ilan_km = db.km_getir(ilan_no)
    ilan_fiyat = db.fiyat_getir(ilan_no)

    embed = discord.Embed(
        title="⚙️ İlan Ayarları",
        description=f"""İlan Numaranız: `{ilan_no}\nİlanınızın fiyatı: {ilan_fiyat}\nİlanınızın kilometres,: {ilan_km}`
                        """,
        color=discord.Color.orange()
    )
    embed.add_field(name="Seçenekler", value="Aşağıdaki butonlardan birini seçebilirsiniz:")

    view = SettingsView(ilan_no, ilan_sahibi)
    await ctx.send(embed=embed, view=view)

@bot.command()
async def ilanara(ctx, marka: str, model: str):
    ilanlar = db.getir_marka_model(marka, model)
    
    if not ilanlar:
        await ctx.send(f"⚠️ `{marka} {model}` için herhangi bir ilan bulunamadı.")
        return

    for ilan in ilanlar:
        # İlan tuple: (ilan_no, user_id, marka, model, motor, yıl, km, tramer, fiyat)
        ilan_no = ilan[1]
        ilan_sahibi_id = ilan[2]
        motor = ilan[5]
        yıl = ilan[6]
        km = ilan[7]
        tramer = ilan[8]
        fiyat = ilan[9]
        aciklama = ilan[10]

        embed = discord.Embed(
            title=f"🔎 {marka} {model} İlanı",
            color=discord.Color.blue()
        )
        embed.add_field(name="🚗 • Marka & Model", value=f"{marka} {model}, {motor} motorlu", inline=False)
        embed.add_field(name="📅 • Model Yılı", value=f"{yıl}", inline=False)
        embed.add_field(name="🛣️ • Kilometre", value=f"{km} km", inline=False)
        embed.add_field(name="💳 • Tramer", value=f"{tramer} TL tramer", inline=False)
        embed.add_field(name="💰 • Fiyat", value=f"{fiyat} TL", inline=False)
        embed.add_field(name="📝 • Açıklama", value=aciklama, inline=False)

        view = View()
        button = Button(label="İlan sahibine ulaş!", style=discord.ButtonStyle.link, url=f"https://discord.com/users/{ilan_sahibi_id}")
        view.add_item(button)

        await ctx.send(embed=embed, view=view)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 PriceMyCar Yardım Menüsü",
        description="Aşağıda tüm komutların açıklamalarını bulabilirsiniz:",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="💰 `<fiyat <marka> <model> <motor> <yıl> <km> <tramer>`",
        value="Girilen bilgilerle aracın tahmini fiyatını hesaplar.\n"
              "Örn: `<fiyat bmw x5 3.0 2019 60000 20000`",
        inline=False
    )

    embed.add_field(
        name="📢 `<ilanver <marka> <model> <motor> <yıl> <km> <tramer> <fiyat> <aciklama>`",
        value="Yeni bir araç ilanı oluşturur ve size özel DM gönderir.\n"
              "Örn: `<ilanver fiat egea 1.3 2017 120000 5000 450000 öğretmenden temiz alıcısına hayırlı olsun pazarlık vardır`",
        inline=False
    )

    embed.add_field(
        name="🔍 `<ilanara <marka> <model>`",
        value="Girilen marka ve modele uygun ilanları arar ve listeler.\n"
              "Örn: `<ilanara fiat egea`",
        inline=False
    )

    embed.add_field(
        name="⚙️ `<settings <ilan_no>`",
        value="Size ait ilan için fiyat, kilometre güncelleme veya ilan silme seçeneklerini açar.",
        inline=False
    )

    embed.set_footer(text="PriceMyCar • İyi satışlar 🚗")

    await ctx.send(embed=embed)

bot.run(TOKEN)