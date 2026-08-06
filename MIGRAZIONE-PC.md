# Migrazione dell'ambiente di sviluppo su PC

File di servizio: si cancella quando la migrazione è fatta.

Stato al momento in cui è stato scritto: branch e `main` allineati su `aa67157`,
working tree pulito, niente in sospeso. Non c'è lavoro a metà da recuperare.

---

## 1. Cosa fare sul PC

### Godot
Scarica **Godot 4.7, build standard** (*non* la .NET: il progetto è GDScript)
da [godotengine.org/download](https://godotengine.org/download). Non si
installa, è un archivio da estrarre.

Metti l'eseguibile nel PATH con il nome `godot`: serve al punto 4.

### Repository
```
git clone https://github.com/Tro4Tro4/GAAAG.git
cd GAAAG
```
Poi in Godot: *Import* → seleziona `project.godot`. Al primo import genera
`.godot/` e i file `.import`, che sono ignorati da git. **Play (F5) parte da
`scenes/Main.tscn`** — il README dice ancora `TestRoom`, è la prima cosa da
correggere (vedi §4).

Su Windows: `.gitattributes` normalizza tutto a LF, quindi non serve toccare
`core.autocrlf`. Lascialo come lo trovi.

### Claude Code
Installa la CLI sul PC e lancia `claude` **dentro la cartella del repository**:
`CLAUDE.md` e le sette skill in `.claude/skills/` vengono caricate da sole,
senza che tu debba dire niente.

La sessione in sé **non si trasferisce**: quello che si trasferisce è il
contesto, ed è già tutto scritto in `CLAUDE.md`. Il prompt del §5 serve a dire
alla sessione nuova dove si è arrivati e cosa fare per prima cosa.

### Librerie opzionali
```
pip install gdtoolkit          # gdparse, il controllo di sintassi
pip install pillow             # tools/make_*.py, gli asset grafici
pip install numpy scipy        # la skill audio
```

---

## 2. Cosa il PC cambia davvero

**Godot diventa eseguibile da riga di comando.** È il guadagno grosso: finora
la verifica automatica si fermava a `gdparse`, che legge solo la forma di un
`.gd`. Con l'engine installato si può controllare che il progetto importi e
giri:

```
godot --headless --quit                 # importa tutto e riporta gli errori
godot --headless --check-only --script scripts/rooms/room.gd
godot --headless --quit-after 3         # avvia il gioco per tre secondi
```

`gdparse` resta utile come controllo veloce, ma smette di essere l'unico.

**Le trappole del telefono restano scritte ma smettono di applicarsi qui.** La
nota su `/storage/emulated/0`, il livello FUSE e il `git reset --hard` che
spacca il clone vale per l'editor Android. Non va cancellata da `CLAUDE.md`
finché il telefono resta un ambiente di lavoro; va solo saputo che sul PC non
può succedere.

**La verifica sul dispositivo non sparisce.** Il PC non può validare né il
premi-trascina-rilascia della verb-coin, né `emulate_mouse_from_touch`, né la
dimensione reale dei badge (24 unità che a 5× diventano 120 pixel veri).
Tutto quello che in `CLAUDE.md` è marcato *"verificato sul dispositivo"* è
verificato lì e non altrove.

**Il C# non si torna a fare.** La decisione *"Da C# a GDScript"* dice di
rivederla solo se arriva un desktop **e** il progetto è ancora abbastanza
piccolo. La prima condizione si avvera adesso, la seconda no: allora erano due
script e ~110 righe, oggi sono una trentina di file, sette skill e un
prototipo verticale intero. La riconversione costerebbe settimane e non
comprerebbe niente che oggi manchi. Va invece registrato in `CLAUDE.md` che la
premessa è cambiata e che la decisione **resta**, con questo motivo.

---

## 3. Cosa resta aperto (lo stato vero da portarsi dietro)

Sta tutto in `CLAUDE.md` → *"Decisioni ancora aperte"*. Le due che aspettavano
proprio un occhio e non una riga di codice:

- **La scala per profondità contro la pixel art.** L'atrio ha
  `depth_top_scale = 0.85` / `depth_bottom_scale = 1.05` su 60 unità di
  pavimento. La raccomandazione registrata è **metterla a 1 e 1 nell'atrio**,
  da confermare guardando Lino camminare. Il PC la mostra a 3×, il telefono a
  5×: il caso vero è il telefono.
- **Layer di parallasse negli sfondi.** Da decidere **prima** di dipingere il
  corridoio dei tubi, che è largo due schermate ed è il posto dove si
  vedrebbe. Ogni layer è un file in più e non si scompone dopo.

Le altre (terzo riproduttore audio, suono dei passi, voce, slot di
salvataggio, storia completa, nome del progetto) non hanno nessun blocco
legato alla macchina.

---

## 4. Primo giro sul PC, in ordine

1. `godot --headless --quit` e leggi cosa dice: è il primo controllo che
   questo progetto non ha mai potuto fare.
2. Play su `Main.tscn`, cammina, apri la verb-coin, fai l'enigma del prototipo.
3. Correggi il `README.md`, che è rimasto a `TestRoom` e a una descrizione del
   progetto di parecchi mesi fa.
4. Chiudi la decisione sulla scala per profondità dell'atrio.
5. Cancella questo file.

---

## 5. Il prompt per la sessione nuova

Da incollare in `claude` lanciato dentro la cartella del repository.

> Riprendo lo sviluppo di AGGGA su PC: fino a ieri il progetto si sviluppava
> dall'editor Godot per Android, adesso ho una macchina desktop con Godot 4.7
> standard installato e raggiungibile da riga di comando come `godot`.
>
> Leggi `CLAUDE.md` prima di rispondere: è il registro completo delle decisioni
> di design e architettura, e contiene anche le convenzioni con cui devi
> lavorare su questo progetto. Leggi anche `MIGRAZIONE-PC.md`, che è il
> passaggio di consegne dalla sessione precedente e si cancella quando la
> migrazione è chiusa.
>
> Lo stato: working tree pulito, `main` e il branch di lavoro allineati,
> niente lavoro a metà. L'ultima cosa fatta è stata dare a Lino gli sprite
> veri al posto dei poligoni segnaposto, dopo aver dato all'atrio uno sfondo
> dipinto vero.
>
> Cosa cambia adesso che siamo su PC, e che voglio tu tenga presente:
> - Godot si può eseguire, quindi la verifica non si ferma più a `gdparse`.
>   Usa `godot --headless --quit` per far importare il progetto e leggere gli
>   errori, e `--check-only --script` sui singoli file. Fallo prima di
>   committare, al posto del solo controllo di sintassi.
> - Le note su `/storage/emulated/0`, sul livello FUSE e sul `git reset --hard`
>   riguardano l'editor Android e non questa macchina. Non cancellarle da
>   `CLAUDE.md`: il telefono resta un ambiente di prova.
> - **Non** riproporre il ritorno a C#. La decisione registrata dice di
>   rivederla solo se arrivasse un desktop *e* il progetto fosse ancora
>   piccolo: la prima condizione si è avverata, la seconda no.
> - La verifica al tocco resta cosa del telefono: verb-coin, gesto di
>   trascinamento e dimensione reale dei badge non si validano qui.
>
> Il primo lavoro, in quest'ordine:
> 1. Fai importare il progetto con Godot da riga di comando e dimmi cosa
>    riporta — è un controllo che questo progetto non ha mai potuto fare.
> 2. Aggiorna `README.md`: dice ancora che la scena di avvio è `TestRoom`,
>    mentre è `Main.tscn`, e descrive il progetto com'era a inizio sviluppo.
> 3. Registra in `CLAUDE.md` il cambio di ambiente di sviluppo, con la
>    conferma che la scelta di GDScript resta e il motivo per cui resta anche
>    ora che la premessa è caduta. Usa la skill `registra-decisione`.
>
> Dopo quello parliamo della scala per profondità dell'atrio, che è la
> decisione aperta più vicina a chiudersi.
