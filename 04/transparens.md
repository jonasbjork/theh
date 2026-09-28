# Transparensrapport

>[!NOTE]
> Jag bad AI faktagranska föreläsningen. Här är resultatet.

Jag har faktagranskat innehållet. Sammanfattande omdöme: lektionen är tekniskt mycket solid. Det mesta stämmer, och flera av de små felen flaggade du själv som osäkra under föreläsningen ("Windows RM", "Winsock"). Här är genomgången.

## Bekräftat korrekt

Portarna (DNS 53, LDAP 389, LDAPS 636, SMB 445, RDP 3389, Kerberos 88), event-ID:na (4624 lyckad / 4625 misslyckad inloggning, 4768 TGT, 4769 serviceticket), hashalgoritmerna (MD5, SHA-1/256/512 – och att SHA-1 ger 40 hex-tecken), Kerberoasting/AS-REP roasting, password spraying vs brute force, BloodHound, least privilege, tier-modellen, LLMNR/NetBIOS/NetBEUI-historiken, samt DN-läsordningen (DC i AD, O/OU i LDAP) – allt detta stämmer.

Även tidsuppgifterna: Windows Server 2000 släpptes i februari 2000, så "ca 25–26 år sedan" är rätt (26 år från 2026). Kerberos utvecklades på MIT på 1980-talet (Project Athena), namnet från den trehövdade Kerberos/Cerberus – korrekt.

## Små felsägningar / oprecisa namn

- NIS = "Network Information System" → officiellt Network Information Service (Suns katalogtjänst, ursprungligen kallad "Yellow Pages"). Båda formerna används i talspråk, men "Service" är det korrekta.
- WINS = "Windows name server" → Windows Internet Name Service. Rätt funktion beskriven (NetBIOS-namnuppslag), bara namnet något fel.
- gMSA – "Group management service" → Group Managed Service Accounts. Konceptet rätt beskrivet.
- Azure AD → EntraID: korrekt att det numera heter Microsoft Entra ID. För tidslinjen om någon frågar: Microsoft annonserade namnbytet den 11 juli 2023, och bytet trädde i kraft 1 oktober 2023. 

## Värt att nyansera i undervisningen

- MFA "tar bort över 90 %": Microsofts faktiska siffra är 99,9 % – "ditt konto är mer än 99,9 % mindre sannolikt att kompromitteras om du använder MFA", enligt Alex Weinert på Microsoft. Ditt ">90 %" är alltså inte fel, bara försiktigt. Notera dock att siffran gäller automatiserade attacker; MFA-phishing/token-stöld är just det som utgör den återstående ~0,1 %. 
slaw

- "Auktoriseringen sker hos tjänsten, inte hos KDC": Bra pedagogisk poäng, men en liten nyans värd att ha koll på om en VG-student frågar: KDC:n bäddar in gruppmedlemskapen i ticketen (i den s.k. PAC:en, Privilege Attribute Certificate). Så auktoriseringsdatan kommer från KDC, men beslutet/enforcement sker hos tjänsten. Din formulering håller på den här nivån.

- SMB 445 / RPC / "Windows RM": Här blandas två saker ihop. Fjärradministration via 445 sker med RPC över SMB (namngivna pipes) – det stämmer. Men WinRM (Windows Remote Management) är en separat teknik som kör på 5985/5986, inte 445. Dessutom: PowerShell mot AD (Get-ADUser m.m.) går primärt över LDAP (389/636), inte 445. 445 är rätt för SMB-baserad admin, men inte för själva AD-frågorna.

- Winsock 1993–1994: Winsock 1.1-specifikationen kom januari 1993, så tidsangivelsen är rimlig.

Inget av detta ändrar helheten – kärnbudskapen och alla tentarelevanta fakta (portar, event-ID, begreppspar, attacksteg) stämmer.

~ Granskad av Claude AI Opus 5.5 den 28 september 2026

