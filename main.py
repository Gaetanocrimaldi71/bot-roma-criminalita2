import discord
from discord import app_commands
from discord.ext import commands
import os
from datetime import datetime

# Inizializzazione Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Colori Hex Principali
COLOR_MAIN = 0xE74C3C      # Rosso Roma Evolution
COLOR_SUCCESS = 0x2ECC71   # Verde Operazione Riuscita
COLOR_BLACK = 0x010101     # Nero Profondo Mercato Nero
COLOR_PURPLE = 0x7B2CBF    # Viola Scuro Istituzionale

ROLE_STAFF = "RERP | Staff"
ROLE_ADMIN = "RERP | Amministrazione"

# Configurazione Ruoli con colore NERO (#010101) per il Mercato Nero
ROLES_CONFIG = {
    "RERP | Amministrazione": discord.Color.from_rgb(153, 45, 34),
    "RERP | Staff":           discord.Color.from_rgb(46, 204, 113),
    
    # 👑 ALTA DIRIGENZA ILLEGALE (NERO)
    "Broker Supremo":                  discord.Color.from_str("#010101"),
    "Responsabile Illegale":           discord.Color.from_str("#7B2CBF"),
    "Supervisore Fazioni":             discord.Color.from_str("#9D4EDD"),
    
    # 📦 FORNITORI & TRAFFICHINI (NERI)
    "Fabbro d'Armi":                  discord.Color.from_str("#010101"),
    "Trafficante di Sostanze":        discord.Color.from_str("#010101"),
    "Riciclatore di Denaro":           discord.Color.from_str("#010101"),
    "Contrabbandiero di Componenti":   discord.Color.from_str("#010101"),
    
    # 🏴 FAZIONI & GRUPPI APPROVATI
    "Leader Fazione Ufficiale":        discord.Color.from_str("#C0392B"),
    "Membro Gang / Clan":              discord.Color.from_str("#E74C3C"),
    "Cani Sciolti / Criminali":        discord.Color.from_str("#95A5A6"),
    
    # ⏳ SPORTELLI & ATTESA
    "In Attesa di Approvazione Lore": discord.Color.from_str("#7F8C8D"),
    "Acquirente Accredito NERO":       discord.Color.from_str("#010101")
}

ticket_counter = 0

# ID per dark-web e convalida scena
ROLE_DARKWEB_ID = 1568551074934169680
LOG_CHANNEL_ID = 1568867217943044146
LOG_CONVALIDA_SCENA_ID = 1568911833245421689
ADMIN_TICKET_LINK = "https://discord.com/channels/1454959930602950729/1554441464958681108"

@bot.event
async def on_ready():
    print(f"✅ Bot online come: {bot.user.name}")
    try:
        bot.add_view(FazionePulsanteView())
        bot.add_view(TicketPulsantiDirettiView())
        synced = await bot.tree.sync()
        print(f"🔁 Sincronizzati {len(synced)} comandi slash.")
    except Exception as e:
        print(f"❌ Errore sincronizzazione: {e}")

# ==========================================
# 📢 COMANDO /SAY (manda nel canale corrente)
# ==========================================

@bot.tree.command(name="say", description="[STAFF] Fa scrivere un messaggio al bot nel canale corrente")
@app_commands.describe(messaggio="Il messaggio da far scrivere al bot")
@app_commands.checks.has_permissions(manage_messages=True)
async def say(interaction: discord.Interaction, messaggio: str):
    print(f"[SAY] {interaction.user} ({interaction.user.id}) ha usato /say: {messaggio[:100]}")
    
    try:
        await interaction.channel.send(messaggio)
        await interaction.response.send_message("✅ Messaggio inviato.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)

# ==========================================
# 🧹 COMANDO /CLEAR
# ==========================================

@bot.tree.command(name="clear", description="[STAFF] Cancella un certo numero di messaggi dal canale")
@app_commands.describe(amount="Numero di messaggi da cancellare (1-100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
    print(f"[CLEAR] {interaction.user} ({interaction.user.id}) ha usato /clear {amount}")
    
    try:
        # Defer per evitare timeout mentre cancella
        await interaction.response.defer(ephemeral=True)
        
        deleted = await interaction.channel.purge(limit=amount)
        
        await interaction.followup.send(
            f"Hai cancellato **{len(deleted)}** messaggi.",
            ephemeral=True
        )
    except Exception as e:
        try:
            await interaction.followup.send(f"❌ Errore durante la cancellazione: {e}", ephemeral=True)
        except:
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)

# ==========================================
# 🌑 COMANDO /DARK-WEB + SISTEMA ACCETTAZIONE
# ==========================================

class DarkWebView(discord.ui.View):
    def __init__(self, richiedente: discord.Member, motivo: str):
        super().__init__(timeout=None)
        self.richiedente = richiedente
        self.motivo = motivo

    async def check_role(self, interaction: discord.Interaction) -> bool:
        if not any(r.id == ROLE_DARKWEB_ID for r in interaction.user.roles):
            await interaction.response.send_message("❌ Solo chi ha il ruolo autorizzato può accettare o rifiutare queste richieste.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Accetta", style=discord.ButtonStyle.success, emoji="✅")
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_role(interaction):
            return

        print(f"[DARK-WEB] {interaction.user} ({interaction.user.id}) ha ACCETTATO la richiesta di {self.richiedente} ({self.richiedente.id})")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

        # Assegna i ruoli di accesso criminalità
        try:
            ruolo1 = interaction.guild.get_role(1568904831371051069)
            ruolo2 = interaction.guild.get_role(1568904977815179385)
            if ruolo1:
                await self.richiedente.add_roles(ruolo1, reason="Richiesta Dark Web accettata")
            if ruolo2:
                await self.richiedente.add_roles(ruolo2, reason="Richiesta Dark Web accettata")
        except Exception as e:
            print(f"[DARK-WEB] Errore assegnazione ruoli: {e}")

        embed = discord.Embed(
            title="✅ RICHIESTA ACCETTATA",
            description=f"La richiesta di accesso alla criminalità di {self.richiedente.mention} è stata **accettata** da {interaction.user.mention}.\n\nRuoli assegnati correttamente.",
            color=COLOR_SUCCESS,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Motivo originale", value=self.motivo, inline=False)
        await interaction.response.send_message(embed=embed)

        try:
            dm_embed = discord.Embed(
                title="✅ Richiesta Accettata",
                description="La tua richiesta di accesso alla criminalità è stata **accettata**.\nTi sono stati assegnati i ruoli relativi.\nLo staff ti contatterà a breve.",
                color=COLOR_SUCCESS
            )
            await self.richiedente.send(embed=dm_embed)
        except:
            await interaction.followup.send("⚠️ Non sono riuscito a mandare il DM all'utente (ha i DM chiusi).", ephemeral=True)

    @discord.ui.button(label="Rifiuta", style=discord.ButtonStyle.danger, emoji="❌")
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_role(interaction):
            return

        print(f"[DARK-WEB] {interaction.user} ({interaction.user.id}) ha RIFIUTATO la richiesta di {self.richiedente} ({self.richiedente.id})")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

        embed = discord.Embed(
            title="❌ RICHIESTA RIFIUTATA",
            description=f"La richiesta di accesso alla criminalità di {self.richiedente.mention} è stata **rifiutata** da {interaction.user.mention}.",
            color=COLOR_MAIN,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Motivo originale", value=self.motivo, inline=False)
        await interaction.response.send_message(embed=embed)

        try:
            dm_embed = discord.Embed(
                title="❌ Richiesta Rifiutata",
                description="La tua richiesta di accesso alla criminalità è stata **rifiutata**.",
                color=COLOR_MAIN
            )
            await self.richiedente.send(embed=dm_embed)
        except:
            await interaction.followup.send("⚠️ Non sono riuscito a mandare il DM all'utente (ha i DM chiusi).", ephemeral=True)


class DarkWebModal(discord.ui.Modal, title="🌑 Accesso Dark Web / Criminalità"):
    motivo = discord.ui.TextInput(
        label="Motivo della richiesta",
        style=discord.TextStyle.paragraph,
        placeholder="Spiega perché vuoi accedere alla criminalità...",
        min_length=10,
        max_length=1000,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        print(f"[DARK-WEB] {interaction.user} ({interaction.user.id}) ha inviato una richiesta dark-web")

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            return await interaction.response.send_message("❌ Canale di log non trovato.", ephemeral=True)

        embed = discord.Embed(
            title="🌑 NUOVA RICHIESTA ACCESSO CRIMINALITÀ",
            description=f"**Richiedente:** {interaction.user.mention} (`{interaction.user.id}`)\n**Server:** {interaction.guild.name}",
            color=COLOR_BLACK,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="📋 Motivo", value=self.motivo.value, inline=False)
        embed.set_footer(text="Roma Evolution RP • Dark Web")

        view = DarkWebView(richiedente=interaction.user, motivo=self.motivo.value)
        await log_channel.send(embed=embed, view=view)

        await interaction.response.send_message(
            "✅ La tua richiesta è stata inviata allo staff. Riceverai risposta in DM.",
            ephemeral=True
        )


@bot.tree.command(name="dark-web", description="Richiedi l'accesso alla criminalità (Dark Web)")
async def dark_web(interaction: discord.Interaction):
    print(f"[DARK-WEB] {interaction.user} ({interaction.user.id}) ha aperto il comando /dark-web")
    await interaction.response.send_modal(DarkWebModal())

# ==========================================
# 🎬 COMANDO /CONVALIDA_SCENA
# ==========================================

class ConvalidaScenaView(discord.ui.View):
    def __init__(self, richiedente: discord.Member, tipo_scena: str, soldi: str, prova: str):
        super().__init__(timeout=None)
        self.richiedente = richiedente
        self.tipo_scena = tipo_scena
        self.soldi = soldi
        self.prova = prova

    async def check_role(self, interaction: discord.Interaction) -> bool:
        if not any(r.id == ROLE_DARKWEB_ID for r in interaction.user.roles):
            await interaction.response.send_message("❌ Solo chi ha il ruolo autorizzato può accettare o rifiutare queste richieste.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Accetta", style=discord.ButtonStyle.success, emoji="✅")
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_role(interaction):
            return

        print(f"[CONVALIDA] {interaction.user} ({interaction.user.id}) ha ACCETTATO la scena di {self.richiedente} ({self.richiedente.id})")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

        embed = discord.Embed(
            title="✅ SCENA CONVALIDATA",
            description=f"La scena di {self.richiedente.mention} è stata **accettata** da {interaction.user.mention}.",
            color=COLOR_SUCCESS,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="🎬 Tipo Scena", value=self.tipo_scena, inline=True)
        embed.add_field(name="💰 Importo richiesto", value=self.soldi, inline=True)
        embed.add_field(name="📎 Prova", value=self.prova, inline=False)
        await interaction.response.send_message(embed=embed)

        # DM all'utente
        try:
            dm_embed = discord.Embed(
                title="✅ Scena Convalidata",
                description=(
                    f"La tua scena è stata **convalidata**.\n\n"
                    f"**Importo richiesto:** {self.soldi}\n\n"
                    f"Apri un ticket amministrativo qui:\n{ADMIN_TICKET_LINK}\n\n"
                    f"e manda questa prova insieme alla richiesta di pagamento."
                ),
                color=COLOR_SUCCESS
            )
            dm_embed.add_field(name="📎 Prova", value=self.prova, inline=False)
            dm_embed.set_footer(text="Roma Evolution RP • Convalida Scene")
            await self.richiedente.send(embed=dm_embed)
        except:
            await interaction.followup.send("⚠️ Non sono riuscito a mandare il DM all'utente (ha i DM chiusi).", ephemeral=True)

    @discord.ui.button(label="Rifiuta", style=discord.ButtonStyle.danger, emoji="❌")
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_role(interaction):
            return

        print(f"[CONVALIDA] {interaction.user} ({interaction.user.id}) ha RIFIUTATO la scena di {self.richiedente} ({self.richiedente.id})")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

        embed = discord.Embed(
            title="❌ SCENA RIFIUTATA",
            description=f"La scena di {self.richiedente.mention} è stata **rifiutata** da {interaction.user.mention}.",
            color=COLOR_MAIN,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="🎬 Tipo Scena", value=self.tipo_scena, inline=True)
        embed.add_field(name="💰 Importo richiesto", value=self.soldi, inline=True)
        embed.add_field(name="📎 Prova", value=self.prova, inline=False)
        await interaction.response.send_message(embed=embed)

        try:
            dm_embed = discord.Embed(
                title="❌ Scena Rifiutata",
                description="La tua richiesta di convalida scena è stata **rifiutata**.",
                color=COLOR_MAIN
            )
            await self.richiedente.send(embed=dm_embed)
        except:
            await interaction.followup.send("⚠️ Non sono riuscito a mandare il DM all'utente (ha i DM chiusi).", ephemeral=True)


class ConvalidaScenaModal(discord.ui.Modal, title="🎬 Convalida Scena"):
    tipo_scena = discord.ui.TextInput(
        label="Tipo di scena",
        style=discord.TextStyle.short,
        placeholder="Es: Rapina, Rapimento, Furto auto...",
        min_length=3,
        max_length=100,
        required=True
    )
    soldi = discord.ui.TextInput(
        label="Soldi richiesti",
        style=discord.TextStyle.short,
        placeholder="Es: 5000€ oppure 15.000$",
        min_length=1,
        max_length=50,
        required=True
    )
    prova = discord.ui.TextInput(
        label="Prova (link video / foto)",
        style=discord.TextStyle.paragraph,
        placeholder="Incolla qui il link del video o della foto della scena...",
        min_length=5,
        max_length=500,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        print(f"[CONVALIDA] {interaction.user} ({interaction.user.id}) ha inviato una richiesta di convalida scena")

        log_channel = interaction.guild.get_channel(LOG_CONVALIDA_SCENA_ID)
        if not log_channel:
            return await interaction.response.send_message("❌ Canale di log non trovato.", ephemeral=True)

        embed = discord.Embed(
            title="🎬 NUOVA RICHIESTA CONVALIDA SCENA",
            description=f"**Richiedente:** {interaction.user.mention} (`{interaction.user.id}`)",
            color=COLOR_PURPLE,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="🎬 Tipo di scena", value=self.tipo_scena.value, inline=True)
        embed.add_field(name="💰 Soldi richiesti", value=self.soldi.value, inline=True)
        embed.add_field(name="📎 Prova", value=self.prova.value, inline=False)
        embed.set_footer(text="Roma Evolution RP • Convalida Scene")

        view = ConvalidaScenaView(
            richiedente=interaction.user,
            tipo_scena=self.tipo_scena.value,
            soldi=self.soldi.value,
            prova=self.prova.value
        )
        await log_channel.send(embed=embed, view=view)

        await interaction.response.send_message(
            "✅ La tua richiesta di convalida scena è stata inviata allo staff. Riceverai risposta in DM.",
            ephemeral=True
        )


@bot.tree.command(name="convalida_scena", description="Richiedi la convalida di una scena (con prova foto/video)")
async def convalida_scena(interaction: discord.Interaction):
    print(f"[CONVALIDA] {interaction.user} ({interaction.user.id}) ha aperto il comando /convalida_scena")
    await interaction.response.send_modal(ConvalidaScenaModal())

# ==========================================
# 📌 COMANDO LISTINO PREZZI TABELLARE IN €
# ==========================================

@bot.tree.command(name="listino_imposta", description="[MERCATO NERO] Genera la tabella prezzi ufficiale (OGGETTO | CATEGORIA | PREZZO €)")
@app_commands.describe(
    item1="Oggetto 1, Categoria, Prezzo € (Es: AK-47, Armi, 15000)",
    item2="Oggetto 2, Categoria, Prezzo € (Es: Radio, Equip, 1500)",
    item3="Oggetto 3, Categoria, Prezzo € (Opzionale)",
    item4="Oggetto 4, Categoria, Prezzo € (Opzionale)",
    item5="Oggetto 5, Categoria, Prezzo € (Opzionale)",
    item6="Oggetto 6, Categoria, Prezzo € (Opzionale)",
    item7="Oggetto 7, Categoria, Prezzo € (Opzionale)",
    item8="Oggetto 8, Categoria, Prezzo € (Opzionale)",
    item9="Oggetto 9, Categoria, Prezzo € (Opzionale)",
    item10="Oggetto 10, Categoria, Prezzo € (Opzionale)"
)
async def listino_imposta(
    interaction: discord.Interaction, 
    item1: str,
    item2: str = None, item3: str = None, item4: str = None, item5: str = None,
    item6: str = None, item7: str = None, item8: str = None, item9: str = None, item10: str = None
):
    print(f"[LISTINO] {interaction.user} ({interaction.user.id}) ha usato /listino_imposta")
    
    ruoli_autorizzati = ["Broker Supremo", "Fabbro d'Armi", "Trafficante di Sostanze", "Contrabbandiero di Componenti", "Riciclatore di Denaro", ROLE_ADMIN]
    ha_permesso = any(discord.utils.get(interaction.user.roles, name=r) for r in ruoli_autorizzati) or interaction.user.guild_permissions.administrator

    if not ha_permesso:
        return await interaction.response.send_message("❌ Non possiedi un ruolo del Mercato Nero autorizzato.", ephemeral=True)

    canale_listino = discord.utils.get(interaction.guild.text_channels, name="📌・listino-prezzi-forniture")
    if not canale_listino:
        return await interaction.response.send_message("❌ Canale `#📌・listino-prezzi-forniture` non trovato.", ephemeral=True)

    items = [item1, item2, item3, item4, item5, item6, item7, item8, item9, item10]
    items_validi = [it for it in items if it is not None]

    tabella_testo = "```ascii\n"
    tabella_testo += f"┌──────────────────────────┬──────────────────┬──────────────┐\n"
    tabella_testo += f"│ OGGETTO                  │ CATEGORIA        │ PREZZO €     │\n"
    tabella_testo += f"├──────────────────────────┼──────────────────┼──────────────┤\n"

    for it in items_validi:
        parts = [p.strip() for p in it.split(",")]
        nome_obj = parts[0][:24] if len(parts) > 0 else "Oggetto"
        cat_obj = parts[1][:16] if len(parts) > 1 else "Generale"
        prezzo_obj = parts[2][:10] if len(parts) > 2 else "0"
        if not prezzo_obj.endswith("€"):
            prezzo_obj += " €"

        tabella_testo += f"│ {nome_obj:<24} │ {cat_obj:<16} │ {prezzo_obj:<12} │\n"

    tabella_testo += f"└──────────────────────────┴──────────────────┴──────────────┘\n"
    tabella_testo += "```"

    embed_listino = discord.Embed(
        title="📌 MERCATO NERO — TABELLA UFFICIALE FORNITURE",
        description=tabella_testo,
        color=COLOR_BLACK
    )
    embed_listino.set_footer(text=f"Aggiornato da: {interaction.user.display_name} • Roma Evolution RP")

    await canale_listino.send(embed=embed_listino)
    await interaction.response.send_message(f"✅ Listino tabellare inviato in {canale_listino.mention}!", ephemeral=True)

# ==========================================
# 🛡️ COMANDI DI GESTIONE STAFF
# ==========================================

@bot.tree.command(name="warn", description="[STAFF] Assegna un avvertimento ufficiale ad un utente")
@app_commands.describe(utente="Membro da sanzionare", motivo="Motivo del warn")
@app_commands.checks.has_permissions(kick_members=True)
async def warn_user(interaction: discord.Interaction, utente: discord.Member, motivo: str):
    print(f"[WARN] {interaction.user} ({interaction.user.id}) ha warnato {utente} — Motivo: {motivo}")
    
    embed = discord.Embed(
        title="⚠️ UTENTE WARNATO",
        description=f"L'utente {utente.mention} ha ricevuto un avvertimento ufficiale.",
        color=COLOR_MAIN
    )
    embed.add_field(name="📋 Motivazione", value=motivo, inline=False)
    embed.add_field(name="👮♂️ Moderatore", value=interaction.user.mention, inline=True)
    embed.set_footer(text="Roma Evolution RP • Moderazione Staff")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="[STAFF] Espelli un utente dal server Discord")
@app_commands.describe(utente="Utente da espellere", motivo="Motivazione dell'espulsione")
@app_commands.checks.has_permissions(kick_members=True)
async def kick_user(interaction: discord.Interaction, utente: discord.Member, motivo: str):
    print(f"[KICK] {interaction.user} ({interaction.user.id}) ha kickato {utente} — Motivo: {motivo}")
    
    try:
        await utente.kick(reason=motivo)
        embed = discord.Embed(
            title="👢 UTENTE ESPULSO",
            description=f"L'utente **{utente.display_name}** è stato espulso dal server.",
            color=COLOR_MAIN
        )
        embed.add_field(name="📄 Motivazione", value=motivo, inline=False)
        embed.add_field(name="👮♂️ Staff", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Errore nell'espulsione: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="[STAFF] Banna permanentemente un utente dal server")
@app_commands.describe(utente="Utente da bannare", motivo="Motivazione del ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_user(interaction: discord.Interaction, utente: discord.Member, motivo: str):
    print(f"[BAN] {interaction.user} ({interaction.user.id}) ha bannato {utente} — Motivo: {motivo}")
    
    try:
        await utente.ban(reason=motivo)
        embed = discord.Embed(
            title="🔨 UTENTE BANNATO",
            description=f"L'utente {utente.mention} è stato bannato con successo dal server.",
            color=COLOR_MAIN
        )
        embed.add_field(name="📄 Motivazione", value=motivo, inline=False)
        embed.add_field(name="👮♂️ Staff Responsabile", value=interaction.user.mention, inline=True)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Errore durante il ban: {e}", ephemeral=True)

@bot.tree.command(name="strike_fazione", description="[STAFF] Assegna uno strike ufficiale ad una fazione")
@app_commands.describe(nome_fazione="Nome della fazione", motivo="Motivazione dello strike", num_strike="Numero strike (es. 1/3, 2/3)")
@app_commands.checks.has_permissions(manage_roles=True)
async def strike_fazione(interaction: discord.Interaction, nome_fazione: str, motivo: str, num_strike: str = "1/3"):
    print(f"[STRIKE] {interaction.user} ({interaction.user.id}) ha dato strike a {nome_fazione}")
    
    embed = discord.Embed(
        title="⚠️ STRIKE FAZIONE ASSEGNATO",
        description=f"È stata notificata una sanzione ufficiale alla fazione **{nome_fazione}**.",
        color=COLOR_MAIN
    )
    embed.add_field(name="📊 Livello Strike", value=f"`{num_strike}`", inline=True)
    embed.add_field(name="👮♂️ Gestore Responsabile", value=interaction.user.mention, inline=True)
    embed.add_field(name="📋 Motivazione Sanzione", value=motivo, inline=False)
    embed.set_footer(text="Roma Evolution RP • Gestione Criminalità")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="fazione_ban", description="[STAFF] Disattiva o banna una fazione per violazioni gravi")
@app_commands.describe(nome_fazione="Nome della fazione", motivo="Motivazione della chiusura")
@app_commands.checks.has_permissions(manage_roles=True)
async def fazione_ban(interaction: discord.Interaction, nome_fazione: str, motivo: str):
    print(f"[FAZIONE_BAN] {interaction.user} ({interaction.user.id}) ha bannato la fazione {nome_fazione}")
    
    embed = discord.Embed(
        title="🚫 FAZIONE DISATTIVATA / BANNATA",
        description=f"La fazione **{nome_fazione}** è stata disciolta ed inserita in Blacklist Criminalità.",
        color=COLOR_MAIN
    )
    embed.add_field(name="📄 Motivazione Chiusura", value=motivo, inline=False)
    embed.add_field(name="🛡️ Gestore Crim", value=interaction.user.mention, inline=True)
    embed.set_footer(text="Roma Evolution RP • Gestione Criminalità")
    await interaction.response.send_message(embed=embed)

# ==========================================
# 🎫 SISTEMA TICKET A SELEZIONE DIRETTI
# ==========================================

class TicketPulsantiDirettiView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def apri_ticket_categoria(self, interaction: discord.Interaction, scelta: str, nome_tipo: str, operatori_nomi: list):
        global ticket_counter
        ticket_counter += 1
        guild = interaction.guild

        print(f"[TICKET] {interaction.user} ha aperto ticket {nome_tipo}-{ticket_counter:04d}")

        nome_canale = f"🎫┃{nome_tipo}-{ticket_counter:04d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        for nome_op in operatori_nomi:
            ruolo_op = discord.utils.get(guild.roles, name=nome_op)
            if ruolo_op:
                overwrites[ruolo_op] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        cat_mercato = discord.utils.get(guild.categories, name="RERP ── 🛒 SPORTELLO ORDINI E INCONTRI ──")
        canale_ticket = await guild.create_text_channel(
            name=nome_canale,
            category=cat_mercato,
            overwrites=overwrites
        )

        menzioni_op = " ".join([r.mention for r in [discord.utils.get(guild.roles, name=n) for n in operatori_nomi] if r])

        embed_ticket = discord.Embed(
            title=f"📦 SPORTELLO MERCATO NERO — {scelta.upper()}",
            description=f"Benvenuto {interaction.user.mention}!\n\n"
                        f"Un operatore del reparto **{scelta.upper()}** prenderà in carico la tua richiesta a breve.\n\n"
                        f"📌 **Operatori Preposti:** {menzioni_op}\n"
                        f"⏳ **Nota:** Non menzionare lo staff o i fornitori nei canali pubblici.",
            color=COLOR_PURPLE
        )
        embed_ticket.set_footer(text="Roma Evolution RP • Sistema Ordini & Logistica")

        await canale_ticket.send(content=f"{interaction.user.mention} {menzioni_op}", embed=embed_ticket, view=TicketChiudiView())
        await interaction.response.send_message(f"✅ Ticket aperto con successo in {canale_ticket.mention}!", ephemeral=True)

    @discord.ui.button(label="Approvazione Gang", style=discord.ButtonStyle.secondary, custom_id="btn_tkt_gang", emoji="🏴")
    async def tkt_gang(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apri_ticket_categoria(interaction, "Approvazione Gang & Clan", "gang", ["Responsabile Illegale", "Supervisore Fazioni"])

    @discord.ui.button(label="Ordini Armi", style=discord.ButtonStyle.secondary, custom_id="btn_tkt_armi", emoji="📦")
    async def tkt_armi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apri_ticket_categoria(interaction, "Ordini Armi e Componenti", "armi", ["Broker Supremo", "Fabbro d'Armi"])

    @discord.ui.button(label="Sostanze & Merci", style=discord.ButtonStyle.secondary, custom_id="btn_tkt_sostanze", emoji="🧪")
    async def tkt_sostanze(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apri_ticket_categoria(interaction, "Sostanze e Merci Contrabbandate", "sostanze", ["Broker Supremo", "Trafficante di Sostanze"])

    @discord.ui.button(label="Riciclaggio Denaro", style=discord.ButtonStyle.secondary, custom_id="btn_tkt_riciclaggio", emoji="💰")
    async def tkt_riciclaggio(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.apri_ticket_categoria(interaction, "Riciclaggio Denaro", "riciclaggio", ["Riciclatore di Denaro"])


class TicketChiudiView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def chiudi(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"[TICKET] {interaction.user} ha chiuso il ticket {interaction.channel.name}")
        await interaction.response.send_message("🔒 Il ticket verrà eliminato a breve...")
        await interaction.channel.delete(reason="Ticket chiuso dall'utente o dallo Staff")

# ==========================================
# 📋 MODULO FAZIONI & CANALE STAFF LOG
# ==========================================

class FazioneModal(discord.ui.Modal, title="🏛️ REGISTRAZIONE NUOVA FAZIONE"):
    nome_fazione = discord.ui.TextInput(label="Nome Fazione / Gang", placeholder="Es: Famiglia Corleone, Bloods...", min_length=3, max_length=50, required=True)
    tag_fazione = discord.ui.TextInput(label="Tag / Acronimo Ufficiale", placeholder="Es: [COR], [BLD]", min_length=2, max_length=6, required=True)
    membri_iniziali = discord.ui.TextInput(label="Numero Membri Iniziali", placeholder="Es: 5 membri attivi", max_length=20, required=True)
    zona_hq = discord.ui.TextInput(label="HQ / Zona Operativa", placeholder="Es: Suburbia, Zona Industriale...", max_length=100, required=True)
    lore_fazione = discord.ui.TextInput(label="Lore & Background", style=discord.TextStyle.paragraph, placeholder="Racconta la storia e gli obiettivi...", min_length=20, max_length=1000, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        print(f"[FAZIONE] {interaction.user} ha inviato candidatura fazione: {self.nome_fazione.value}")
        
        canale_staff_log = discord.utils.get(interaction.guild.text_channels, name="📂・archivio-approvazioni-lore")
        
        embed_staff = discord.Embed(
            title="📥 NUOVA CANDIDATURA FAZIONE RICEVUTA",
            description="Una nuova organizzazione criminale richiede l'approvazione ufficiale.",
            color=COLOR_MAIN
        )
        embed_staff.add_field(name="📌 Nome & Tag", value=f"**{self.nome_fazione.value}** `{self.tag_fazione.value}`", inline=True)
        embed_staff.add_field(name="👥 Membri Iniziali", value=self.membri_iniziali.value, inline=True)
        embed_staff.add_field(name="📍 HQ / Base Operativa", value=self.zona_hq.value, inline=True)
        embed_staff.add_field(name="📜 Background & Lore", value=f"```\n{self.lore_fazione.value}\n```", inline=False)
        embed_staff.add_field(name="👤 Richiedente", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
        embed_staff.set_footer(text="Roma Evolution RP • Gestione Criminalità")

        if canale_staff_log:
            await canale_staff_log.send(embed=embed_staff, view=FazioneGestioneStaffView(self.nome_fazione.value, interaction.user))

        embed_conferma = discord.Embed(
            title="✅ RICHIESTA INVIATA CON SUCCESSO",
            description="La scheda della tua fazione è stata inoltrata al canale privato dello Staff della **Gestione Criminalità**.",
            color=COLOR_SUCCESS
        )
        await interaction.response.send_message(embed=embed_conferma, ephemeral=True)


class FazionePulsanteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Crea Fazione", style=discord.ButtonStyle.secondary, custom_id="btn_crea_fazione", emoji="📜")
    async def apri_modulo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FazioneModal())


class FazioneGestioneStaffView(discord.ui.View):
    def __init__(self, nome_fazione: str, richiedente: discord.User):
        super().__init__(timeout=None)
        self.nome_fazione = nome_fazione
        self.richiedente = richiedente

    @discord.ui.button(label="Approva Fazione", style=discord.ButtonStyle.success, emoji="✅")
    async def approva(self, interaction: discord.Interaction, button: discord.ui.Button):
        resp_role = discord.utils.get(interaction.guild.roles, name="Responsabile Illegale")
        sup_role = discord.utils.get(interaction.guild.roles, name="Supervisore Fazioni")
        
        if not (resp_role in interaction.user.roles or sup_role in interaction.user.roles or interaction.user.guild_permissions.administrator):
            return await interaction.response.send_message("❌ Permessi insufficienti.", ephemeral=True)

        print(f"[FAZIONE] {interaction.user} ha APPROVATO la fazione {self.nome_fazione}")

        embed = discord.Embed(
            title="✅ FAZIONE APPROVATA UFFICIALMENTE",
            description=f"La fazione **{self.nome_fazione}** (Richiesta da {self.richiedente.mention}) è stata approvata da {interaction.user.mention}.",
            color=COLOR_SUCCESS
        )
        await interaction.response.send_message(embed=embed)
        self.stop()

    @discord.ui.button(label="Rifiuta Fazione", style=discord.ButtonStyle.danger, emoji="❌")
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        resp_role = discord.utils.get(interaction.guild.roles, name="Responsabile Illegale")
        sup_role = discord.utils.get(interaction.guild.roles, name="Supervisore Fazioni")
        
        if not (resp_role in interaction.user.roles or sup_role in interaction.user.roles or interaction.user.guild_permissions.administrator):
            return await interaction.response.send_message("❌ Permessi insufficienti.", ephemeral=True)

        print(f"[FAZIONE] {interaction.user} ha RIFIUTATO la fazione {self.nome_fazione}")

        embed = discord.Embed(
            title="❌ FAZIONE RIFIUTATA",
            description=f"La candidatura per la fazione **{self.nome_fazione}** è stata respinta da {interaction.user.mention}.",
            color=COLOR_MAIN
        )
        await interaction.response.send_message(embed=embed)
        self.stop()

# ==========================================
# ⚙️ SETUP AUTOMATICO SERVER
# ==========================================

@bot.tree.command(name="server_setup", description="[ADMIN] Reset completo del server e ricreazione di tutti i canali, ruoli e ticket")
@app_commands.checks.has_permissions(administrator=True)
async def server_setup(interaction: discord.Interaction):
    print(f"[SETUP] {interaction.user} ({interaction.user.id}) ha avviato /server_setup")
    
    await interaction.response.defer(thinking=True)
    guild = interaction.guild

    # 1. ELIMINAZIONE TOTALE CANALI & CATEGORIE
    for channel in list(guild.channels):
        try:
            await channel.delete(reason="Reset totale per setup server")
        except Exception:
            pass

    # 2. CREAZIONE RUOLI CON COLORI E NERO PROFONDO (#010101)
    for nome_ruolo, colore in ROLES_CONFIG.items():
        if not discord.utils.get(guild.roles, name=nome_ruolo):
            await guild.create_role(name=nome_ruolo, color=colore, hoist=True, reason="Setup automatico Mercato Nero")

    role_resp = discord.utils.get(guild.roles, name="Responsabile Illegale")
    role_broker = discord.utils.get(guild.roles, name="Broker Supremo")
    role_sup = discord.utils.get(guild.roles, name="Supervisore Fazioni")
    role_approved = discord.utils.get(guild.roles, name="Leader Fazione Ufficiale")

    # --- CATEGORIA 1: COMUNICATI E REGOLE ILLEGALE ---
    cat_1 = await guild.create_category("RERP ── 📢 COMUNICATI E REGOLE ILLEGALE ──")
    await cat_1.set_permissions(guild.default_role, read_messages=True, send_messages=False)
    
    ch_regolamento = await guild.create_text_channel("📜・regolamento-azioni-criminali", category=cat_1)
    ch_annunci = await guild.create_text_channel("📢・annunci-mercato-nero", category=cat_1)
    
    await guild.create_text_channel("📌・listino-prezzi-forniture", category=cat_1)

    if role_resp: await ch_regolamento.set_permissions(role_resp, send_messages=True)
    if role_broker: await ch_annunci.set_permissions(role_broker, send_messages=True)

    # --- CATEGORIA 2: SPORTELLO ORDINI E INCONTRI ---
    cat_2 = await guild.create_category("RERP ── 🛒 SPORTELLO ORDINI E INCONTRI ──")
    ch_ticket = await guild.create_text_channel("🎫・crea-ticket-nero", category=cat_2)
    await guild.create_text_channel("📋・orari-consegne-e-drop", category=cat_2)

    embed_ticket_main = discord.Embed(
        title="📦 MERCATO NERO - UNIONE FORNITORI",
        description="Una volta aperto il ticket cliccando sul pulsante desiderato, risponderà direttamente l'operatore preposto alla tua richiesta:\n\n"
                    "🏴 **Approvazione Gang & Clan**\nInvio lore, richiesta territorio e colori ufficiali.\n"
                    "• *Operatori:* Responsabile Illegale, Supervisore Fazioni\n\n"
                    "📦 **Ordini Armi e Componenti**\nRichiesta di casse d'armi, munizioni o pezzi speciali.\n"
                    "• *Operatori:* Broker Supremo, Fabbro d'Armi\n\n"
                    "🧪 **Sostanze e Merci Contrabbandate**\nRichiesta lotti di sostanze o attrezzatura da scasso.\n"
                    "• *Operatori:* Broker Supremo, Trafficante di Sostanze\n\n"
                    "💰 **Riciclaggio Denaro & Pulizia**\nConversione del denaro sporco delle rapine o riscatti.\n"
                    "• *Operatori:* Riciclatore di Denaro\n\n"
                    "⏳ *Non menzionare lo staff o i fornitori nei canali pubblici.*",
        color=COLOR_BLACK
    )
    embed_ticket_main.set_footer(text="Roma Evolution RP • Mercato Nero")
    await ch_ticket.send(embed=embed_ticket_main, view=TicketPulsantiDirettiView())

    # --- CATEGORIA 3: FAZIONI E REGISTRO BANDA ---
    overwrites_cat3 = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role_resp: discord.PermissionOverwrite(read_messages=True) if role_resp else None,
        role_sup: discord.PermissionOverwrite(read_messages=True) if role_sup else None,
        role_approved: discord.PermissionOverwrite(read_messages=True) if role_approved else None
    }
    overwrites_cat3 = {k: v for k, v in overwrites_cat3.items() if v is not None}
    
    cat_3 = await guild.create_category("RERP ── 🏴 FAZIONI E REGISTRO BANDA ──", overwrites=overwrites_cat3)
    await guild.create_text_channel("📂・registro-gang-ufficiali", category=cat_3)
    await guild.create_text_channel("🗺️・mappatura-territori", category=cat_3)
    await guild.create_text_channel("🤝・patti-e-alleanze", category=cat_3)
    
    ch_richieste = await guild.create_text_channel("📥┃richieste-fazioni", category=cat_3)
    await ch_richieste.set_permissions(guild.default_role, read_messages=True, send_messages=False)

    embed_fazione_main = discord.Embed(
        title="🏛️ REGISTRAZIONE FAZIONI & CLAN",
        description="Benvenuto nel canale di registrazione ufficiale per le organizzazioni criminali di **Roma Evolution RP**.\n\n"
                    "Clicca sul pulsante qui sotto per compilare il modulo ed inviare la tua candidatura direttamente alla Gestione Staff.",
        color=COLOR_MAIN
    )
    embed_fazione_main.set_footer(text="Roma Evolution RP • Sistema Gestione Fazioni")
    await ch_richieste.send(embed=embed_fazione_main, view=FazionePulsanteView())

    # --- CATEGORIA 4: CHAT INTERNA & LOGISTICA STAFF ---
    overwrites_cat4 = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role_resp: discord.PermissionOverwrite(read_messages=True) if role_resp else None,
        role_broker: discord.PermissionOverwrite(read_messages=True) if role_broker else None,
        role_sup: discord.PermissionOverwrite(read_messages=True) if role_sup else None
    }
    overwrites_cat4 = {k: v for k, v in overwrites_cat4.items() if v is not None}
    
    cat_4 = await guild.create_category("RERP ── 🔒 CHAT INTERNA & LOGISTICA STAFF ──", overwrites=overwrites_cat4)
    await guild.create_text_channel("💬・chat-staff-illegale", category=cat_4)
    await guild.create_text_channel("📦・gestione-stock-armi", category=cat_4)
    await guild.create_text_channel("📂・archivio-approvazioni-lore", category=cat_4)
    await guild.create_text_channel("📜・log-transazioni-chiare", category=cat_4)

    ch_conferma = await guild.create_text_channel("⚙️・setup-completato", category=cat_1)
    embed_res = discord.Embed(
        title="⚙️ RESET E SETUP COMPLETATI!",
        description="Il server è stato ricreato ed è pronto. Il canale `#📌・listino-prezzi-forniture` è vuoto e pronto per essere popolato con `/listino_imposta`!",
        color=COLOR_SUCCESS
    )
    await ch_conferma.send(embed=embed_res)

# ==========================================
# 🟢 COMANDI GENERALI
# ==========================================

@bot.tree.command(name="fazione_crea", description="Richiedi l'apertura di una fazione (Apre il modulo compilabile)")
async def fazione_crea(interaction: discord.Interaction):
    print(f"[FAZIONE] {interaction.user} ha usato /fazione_crea")
    await interaction.response.send_modal(FazioneModal())

@bot.tree.command(name="fazioni_attive", description="Visualizza il catalogo delle fazioni approvate")
async def fazioni_attive(interaction: discord.Interaction):
    print(f"[FAZIONE] {interaction.user} ha usato /fazioni_attive")
    
    embed = discord.Embed(
        title="🏴 ROMA EVOLUTION RP — FAZIONI ATTIVE",
        description="Al momento **non risultano organizzazioni registrate**.\nUsa il canale `#📥┃richieste-fazioni` per candidare la tua gang!",
        color=COLOR_BLACK
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mercatonero_list", description="Catalogo rapido oggetti contrabbando")
async def mercatonero_list(interaction: discord.Interaction):
    print(f"[MERCATO] {interaction.user} ha usato /mercatonero_list")
    
    embed = discord.Embed(
        title="🖤 MERCATO NERO — OGGETTI DISPONIBILI",
        description="Consulta il canale `#📌・listino-prezzi-forniture` per la tabella prezzi pubblicata dai Fornitori!",
        color=COLOR_BLACK
    )
    embed.set_footer(text="Roma Evolution RP • Mercato Nero")
    await interaction.response.send_message(embed=embed)

@server_setup.error
async def on_admin_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, (app_commands.MissingRole, app_commands.MissingPermissions)):
        await interaction.response.send_message("❌ Devi essere Amministratore del server per eseguire il reset e il setup.", ephemeral=True)

# ==========================================
# AVVIO BOT
# ==========================================


bot.run("DISCORD_TOKEN")
