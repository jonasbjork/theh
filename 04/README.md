# Minnesanteckningar – Active Directory, Kerberos & System Hacking

> [!INFO]
> Föreläsningen spelades in med Röstmemo på min macbook och har transkriberats med MacWhisper (Whisper C++ Swedish model) och sedan sammanfattats av Claude AI Opus 5.5. *Notera att AI kan göra fel och att jag inte gått genom innehållet för att säkerställa att det är korrekt.*

*(Anteckningar från dagens föreläsning. Kom ihåg: tentan bygger på presentationerna, så håll koll på portnummer och begrepp!)*

## Grundbegrepp att ha koll på

- **Identitet** – vem eller *vad* som gör något i ett system. Behöver inte vara en människa, kan vara en maskin eller en applikation (t.ex. via en API-nyckel).
- **Konto** – en identitet vi har i systemet. Inte riktigt samma sak som identitet, men nära besläktat (konto = användarnamn + lösenord, identitet kan också vara bara en nyckel).
- **Behörighet** – vad vi får göra med identiteten (läsa fil, ändra fil, installera program).
- **Evidens** – bevis. Kan vi läsa en fil måste vi kunna *visa* att det går.
- **Återtest** – vi testar igen efter att kunden åtgärdat en sårbarhet, för att verifiera att den faktiskt är borta.

**Viktig påminnelse:** En öppen port är *inte* en sårbarhet. Att logga in med ett testkonto är *inte* att äga hela systemet. Vårt värde ligger i att kunna *förklara vad en observation betyder* och veta när vi ska sluta (scope!).

**Arbeta som ett experiment:** Hypotes före handling. Ha en fråga med dig in ("Kan jag komma åt den här porten?"), skjut inte från höften. Håll isär vad du *vet* och vad du *tror*.

## Active Directory (AD)

**Problemet AD löser:** Ett företag med 500 anställda och massor av servrar/skrivare. Utan katalogtjänst måste IT byta lösenord manuellt på varje server. Med AD finns identiteten *centralt* – byt lösenord en gång, det gäller överallt.

- Kom med **Windows Server 2000** (släpptes februari 2000), ca 26 år sedan. Världens mest använda katalogtjänst i företagsmiljö.
- I molnet: hette Azure AD, heter numera **Entra ID** (Microsoft annonserade namnbytet 11 juli 2023, trädde i kraft 1 oktober 2023).
- Historik: X.500 → NIS → LDAP → Novell NDS → Active Directory.
- Heter egentligen **ADDS** (Active Directory Domain Services).
- Linux kan binda sig till AD och delvis simulera det.
- **Nästan alla ransomware-attacker mot kommuner/företag involverar AD** – det är där identiteterna och vägarna in finns.

**Analogin med brickan:** Din bricka (identitet) släpper in dig i hisshallen och i just det här rummet – men inte överallt. Receptionen (katalogtjänsten) kan centralt ge dig tillgång till fler rum utan att flytta sig.

### Struktur i AD
- **Domän** – t.ex. `firma.karoshi.local`. INTE samma som en internetdomän.
- **Forest** – innehåller flera domäner. Mellan domäner finns **federering** (samarbete så konton i en domän når tjänster i en annan).
- **Domänkontrollant (DC)** – servern som lagrar katalogen, kontrollerar inloggningar, delar ut åtkomst. Man har ofta flera för **redundans** (och en per ort som replikerar). Går alla ner → ingen kan autentisera sig.

### Tre typer av identiteter
1. **Användarkonton** – för människor.
2. **Datorkonton** – varje domänansluten dator har ett eget konto.
3. **Tjänstekonton (service accounts)** – för program/tjänster (databaser, webbappar). Ofta höga rättigheter, byter *sällan* lösenord → attraktiva mål. Ex: `SA` i MS SQL, IIS-kontot.

### Grupper
- Samlar användare med samma behörighetsbehov (ekonomi, HR, utvecklare osv). Ger behörighet till *gruppen*, inte varje person.
- **Nästlade grupper** (grupper i grupper) – ovanligt i andra system, finns i AD. Smidigt administrativt, men **farligt**: svårt att veta en användares *effektiva* rättigheter. En angripare letar efter folk som råkat få behörigheter de inte borde ha.
- Inbyggda kraftfulla grupper: **Domain Admins** (full kontroll över domänen), **Enterprise Admins**. **Administrator** = lokal admin på en enskild dator.

### OU och GPO
- **OU (Organizational Unit)** – "mapp" i katalogen för att organisera objekt. Läses höger-till-vänster som ett domännamn (servrar → ekonomi → Helsingborg).
- **GPO (Group Policy Object)** – tvingar konfiguration på datorer: lösenordsregler, skärmlås, tillåtna program, inloggningsskript. Går att styra på mobiler också.
- **Grupper ger behörighet, OU + GPO ger struktur.**
- Kommer du åt att redigera GPO:er → du styr i princip alla datorer. Obs: lösenord förekommer ibland i inloggningsskript (bekvämt = osäkert).

## Autentisering vs auktorisering (tentafråga!)
- **Autentisering** = *Vem är du?* (lösenord, smartkort, fingeravtryck, hårdvarunyckel).
- **Auktorisering** = *Vad får du göra?* (behörigheterna).
- Att autentisera sig som Jonas gör dig inte automatiskt admin.

## Kerberos
- Utvecklat på **MIT** på 1980-talet (Project Athena). Namnet från den trehövdade vakthunden i grekisk mytologi – tre "ben" som protokollet bygger på.
- Vi bevisar vem vi är **en gång** och får tidsbegränsade **tickets**. Lösenordet skickas *inte* till varje server.
- Grunden för hela behörighetsmodellen i Windows-nätverk. Fungerar även på Linux/macOS.

**Liseberg-analogin:**
- Kommer till entrén = **domänkontrollanten (KDC)** ger dig tillgång eller inte.
- Åkbandet = **TGT (Ticket Granting Ticket)** – en biljett du använder för att *få* biljetter.
- Visar armbandet vid en attraktion → får en **serviceticket** som gäller *bara* den tjänsten.

**Flödet (övergripande – behöver inte gräva i tekniken):**
1. Klienten autentiserar sig och begär TGT.
2. KDC utfärdar TGT.
3. Klienten visar TGT och begär serviceticket.
4. KDC utfärdar serviceticket (om behörighet finns).
5. Klienten visar servicetickett för tjänsten.
6. **Tjänsten** avgör vad kontot får göra.

**Varför intressant för oss:**
- Vem som helst med domänkonto kan begära tickets.
- Auktoriseringen *avgörs* hos **tjänsten**. (Nyans för VG: KDC bäddar in gruppmedlemskapen i ticketen via **PAC:en** – Privilege Attribute Certificate – men själva beslutet fattas hos tjänsten.)
- Del av servicetickett krypteras med **tjänstekontots** lösenord → svagt lösenord kan gissas **offline** = **Kerberoasting**.
- Motsvarande på autentiseringen (konton utan Kerberos-förautentisering) = **AS-REP roasting**.
- Grundproblem: svaga lösenord och felkonfiguration (mänskliga faktorn).

## Portar att kunna (tentan!)

| Port | Tjänst | Not |
|------|--------|-----|
| **53** | DNS | Hittar domänkontrollanter och tjänster |
| **88** | Kerberos | Inloggning / tickets |
| **389** | LDAP | Okrypterat |
| **636** | LDAPS | Krypterat (TLS – jämför HTTP/HTTPS) |
| **445** | SMB | Filresurser + fjärradmin via **RPC över SMB** (namngivna pipes) |
| **3389** | RDP | Windows-skrivbordet |

- **NTLM** – uråldrig autentiseringsmekanism (**NT LAN Manager**), ingen egen port. Tas upp för att den *fortfarande används* ("If it works, don't fix it").
- **Obs om PowerShell mot AD:** själva AD-frågorna (Get-ADUser m.m.) går över **LDAP (389/636)**, inte 445. 445 är för SMB-baserad fjärradmin.
- **WinRM** (Windows Remote Management) är en *separat* teknik för fjärrstyrning och kör på **5985 (HTTP) / 5986 (HTTPS)** – blanda inte ihop med SMB/RPC på 445.
- Ute i verkligheten: äldre switchar/routrar kör fortfarande **Telnet** (okrypterat, lösenord i klartext).

*Verklighetskoll: Ni kommer INTE mötas av topp-notch-miljöer med YubiKeys och irisskanning ute på LIA. Säkerhet kostar pengar och budget kommer ofta först efter att något hänt. Företag släpar efter för att "det funkar".*

## Hashning
- Lösenord skickas genom en hashalgoritm → fast sträng. Samma indata ger *alltid* samma hash.
- Kan *inte* räknas ut baklänges – bara **gissas fram** (testa lösenord tills hashen matchar).
- Används även för filintegritetskontroll.
- Ex: SHA-1 (40 hex-tecken), SHA-256, SHA-512, MD5.

## Lösenordsattacker
- **Brute force** – många lösenord mot *ett* konto (ger många försök per konto → syns lätt).
- **Password spraying** – vanliga lösenord mot *många* konton (få försök per konto → smyger under larm). "Sommar2026!" funkar tyvärr ofta.
- Utropstecknet är det vanligaste specialtecknet folk klistrar på i slutet.
- **OSINT (Open Source Intelligence)** – LinkedIn, Google, GitHub för att hitta admins, namnstandard på konton osv. Sikta gärna på slarviga vanliga användare (Lisa i receptionen) – bättre att vara inne än inte alls.

**Försvar:** förbjud dåliga lösenord i policy, **MFA** (Microsoft: >99,9 % av *automatiserade* attacker blockeras – återstående ~0,1 % är avancerade token-/phishing-attacker), larm på många misslyckade inloggningar.

## System Hacking – stegen (från CEH)
1. **Initial åtkomst** – få tag på ett giltigt domänkonto (behöver *inte* vara admin).
2. **Privilege escalation** – högre rättigheter, t.ex. bli lokal admin.
3. **Lateral movement (förflyttning)** – använda åtkomsten för att ta sig vidare i nätverket.
4. **Persistens** – se till att kunna komma tillbaka (t.ex. bakdörr) även om hålet täpps och lösenord byts.
5. **Åtkomst till information** – vad kan vi läsa/ändra? (ekonomi, e-post, AD).
6. **Spår & detektion** – städa bort spåren. Syns du inte, är du svår att hitta.

*I varje steg: har vi tillstånd att gå hit?*

## Inventering (kommandon)
- `whoami` – vilken domän + kontonamn (finns även i Linux).
- `whoami /groups` – vilka grupper.
- `whoami /priv` – vilka privilegier.
- Guld värt när du väl är inne som t.ex. Jonas – du ser direkt vad du får göra.

**AD-kommandon (PowerShell, kräver AD-modul – finns i THM-maskinerna):**
- `Get-ADDomain` – domännamn + domänkontrollanter.
- `Get-ADUser -Filter *` – alla användare (`*` = wildcard, `|` skickar vidare).
- `Get-ADGroupMember -Identity "Domain Admins"` – vilka som är i gruppen.
- Alla tre är **read-only** – förändrar inget.

*Tips från Jonas: Gör INTE skärmdumpar i rapporter – de är inte sökbara. Kopiera texten. Och ladda inte upp känsliga skärmdumpar till amerikanska AI-tjänster.*

## Angreppskedjor & BloodHound
Exempel: **Anna** → medlem i **Helpdesk** → Helpdesk får byta lösenord på **SVC Backup** → SVC Backup är lokal admin på **File01** → File01 har **ekonomidata**. Ingen *tänkte* att Anna skulle nå ekonomidata – det blev en oavsiktlig väg.

- **BloodHound** kartlägger sådana kedjor automatiskt (länk finns i Omniway).
- En kedja blir inte starkare av dramatiska röda pilar – verifiera *varje steg*.

## Vanliga riskmönster i AD
- Onödigt medlemskap i privilegierade grupper (chefer i alla admin-grupper "för att de är chefer").
- Svaga/återanvända lösenord. Obs: superkomplexa lösenord hamnar på post-it under tangentbordet – komplexitet ≠ säkerhet. Sikta på balans.
- Tjänstekonton med för stora rättigheter + gamla lösenord. **Least privilege**: exakt de rättigheter som behövs, varken mer eller mindre.
- Utdelade mappar med för öppen läs/skriv (fasas ut i takt med Microsoft 365/OneDrive, men lever kvar på många ställen).
- Äldre protokoll: **NTLM**, **LLMNR** (Link-Local Multicast Name Resolution), **LAN Manager** (NetBEUI/NetBIOS, broadcast, WINS). Stäng av där det går.
- Samma konto för vardag *och* admin. Bättre: separat admin-konto (t.ex. `Jonas-Admin`), som kan låsas när det inte används.
- För lite loggning → man *gissar* i stället för att *veta*.
- Delegeringar/rättigheter som ingen längre förstår (någon blev admin en gång och det togs aldrig bort). Löses med **IAM**.

## Detektion – Windows säkerhetslogg
- **4624** lyckad inloggning / **4625** misslyckad inloggning.
- **4768** TGT begärd / **4769** serviceticket.
- **Baseline** = det normala (t.ex. 15–25 misslyckade/timme). Går det plötsligt till 400 på en kvart → något händer. Samma logik som "900 Mbit mot webbservern? Inte normalt."
- Automatiska system gör detta – ingen orkar stirra i loggen 8–17.

## Förebyggande vs detekterande (tentafråga!)
- **Förebyggande** = gör angrepp svårare/omöjligt (stäng av datorn = omöjligt att attackera). Ex: least privilege, separata admin-konton, MFA, långa lösenord + **gMSA** (Group Managed Service Accounts) för tjänstekonton, stäng av NTLM/LLMNR, tier-indelning (admin-konton får inte logga in på arbetsstationer), regelbunden granskning av gruppmedlemskap.
- **Detekterande** = upptäcker efter att det hänt (björnspåren i skogen). Ex: larm på misslyckade inloggningar, larm på ändringar i privilegiegrupper, **honeypots** (lockbeteskonton ingen ska använda), SIEM/logganalys.

## Tänk som en försvarare (gör detta redan i TryHackMe)
För varje sak du lyckas med, ställ fyra frågor:
1. Vilken svaghet gjorde det här möjligt?
2. Vilken åtgärd hade förhindrat det?
3. Vilken logghändelse hade avslöjat det?
4. Hur återtestar vi att åtgärden fungerar?

**Klicka inte bara igenom labbarna** – förstå *varför*. THM använder riktiga maskiner, riktig programvara, riktiga scanningar.

## Rapportskrivning
Viktiga delar när du hittar något:
- **Titel** – konkret, inte sensationellt ("port 22 öppen" räcker, ingen Aftonbladet-dramatik).
- **Berörd resurs** – exakt vilket system/grupp/mapp.
- **Observation** – vad du såg + hur du **reproducerar** det (var det en slump att det funkade?).
- **Konsekvens** – sannolikhet + allvarlighet. **Motivera, motivera, motivera** – det är enda sättet att få ledningen att förstå (peka gärna på GDPR-böter och ransomware i pressen).
- **Åtgärd** – **root cause**, inte "datorn var påslagen". Håll dig borta från **blame game** – kollektivt ansvar, peka inte ut Kalle.
- **Återtest** – verifiera att fixen fungerar.
- **Bevisningens gräns** – ange även vad du *inte* har visat ("visar för bred läsbehörighet, INTE administrativ kontroll").

**Viktig lärdom:** Det du *inte* kan visa är lika viktigt som det du kan. Du behöver inte lyckas ta dig in – "jag vet inte" är bättre än tystnad. Det är ingen tävling.

---

## Att göra
- **TryHackMe:** rummet **EH System Hack** (ligger uppe). Klara de **tre betygsgrundande modulerna** i Omniway **senast fredag kl. 17**.
- **Onsdag kl. 13:** gästföreläsare (Mattias & Jonas) – planera in att stanna kvar efter lunch. Inte obligatoriskt, inte betygsgrundande, men kom.
- **Tentan:** bygger *helt* på presentationerna (PDF:erna är enda underlaget). G-del = flervalsfrågor, VG-del = mer text/egna svar. Kunna portnummer och begreppen ovan.


