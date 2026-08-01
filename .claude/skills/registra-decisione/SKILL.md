---
name: registra-decisione
description: Registra una decisione di design o architettura di AGGGA nella sezione "Decisioni prese" di CLAUDE.md, includendo sempre le alternative scartate e il motivo della scelta. Usa questa skill ogni volta che viene presa una decisione strutturale sul progetto — scelta di un pattern, di come rappresentare uno stato, di come organizzare scene o sistemi, di una convenzione, di una libreria, di un formato dati — e anche quando una decisione finora aperta viene chiusa. Usala quando l'utente dice "ok facciamo così", "scegliamo questa", "decidiamo per X", "registra la decisione", "aggiorna CLAUDE.md", o quando ti accorgi di aver appena proposto un'alternativa e averla vista accettata.
---

# Registrare una decisione — AGGGA

`CLAUDE.md` stabilisce che ogni decisione di design o architettura rilevante
vada registrata **con le alternative scartate e il perché, non solo il
risultato finale**. Questa skill serve a rispettare quella richiesta nella
sostanza.

## Perché le alternative scartate contano più della scelta

La scelta finale è visibile nel codice: chiunque legga il progetto la
ritrova. Ciò che il codice non dice mai è *cosa è stato considerato e
respinto*.

Senza quella parte, tra sei mesi la decisione è indistinguibile da un caso.
Qualcuno — probabilmente tu — proporrà l'alternativa già scartata, e non
esisterà modo di sapere se fu valutata e respinta per un buon motivo o
semplicemente mai considerata. Il risultato è rifare la stessa analisi, o
peggio, cambiare rotta reintroducendo un problema già risolto.

C'è un secondo effetto, meno ovvio: registrare il *perché* rende la
decisione **revocabile in modo informato**. Se le condizioni cambiano — il
progetto cresce, arriva il supporto mobile, il prototipo smentisce
un'assunzione — sapere su quale premessa poggiava la scelta dice
immediatamente se vale ancora. Una decisione senza motivazione non si può
rivedere: si può solo subire o ribaltare alla cieca.

Questo vale in modo particolare per AGGGA, dove i sistemi si vincolano a
vicenda: la scelta sull'inventario condiziona i dialoghi, che condizionano
lo stato dei personaggi. Una motivazione registrata è ciò che permette di
capire, quando un sistema si muove, quali altri vanno rimessi in
discussione.

## Procedura

1. Apri `CLAUDE.md` e leggi la sezione **"Decisioni prese (e perché)"** per
   allinearti allo stile delle voci esistenti.
2. Aggiungi la nuova voce **in fondo** all'elenco: l'ordine cronologico
   racconta l'evoluzione del progetto meglio di qualsiasi raggruppamento
   tematico.
3. Se la decisione chiude un punto elencato in **"Decisioni ancora aperte"**,
   rimuovilo da lì. Una voce che resta in entrambe le sezioni rende il
   documento inaffidabile, e un documento inaffidabile smette di essere
   consultato.
4. Se la decisione ne apre di nuove — capita spesso, una scelta struttura il
   problema successivo — aggiungile a "Decisioni ancora aperte".

## Formato

Voce semplice:

```markdown
- **<Decisione in poche parole>**: <cosa si è scelto>. <Perché>.
  Alternative scartate: <alternativa> (<motivo>); <alternativa> (<motivo>).
```

Voce articolata, quando le alternative meritano spazio proprio:

```markdown
- **<Decisione in poche parole>**: <cosa si è scelto e perché>.
  - **<Alternativa scartata>**: <perché è stata respinta. Se aveva dei
    pregi reali, dillo: una motivazione che descrive l'alternativa come
    priva di meriti non è credibile e non aiuta a rivalutarla domani.>
  - **<Alternativa scartata>**: <perché>.
  - Nota: <condizione che, se cambiasse, giustificherebbe di rivedere la
    scelta — se ne esiste una identificabile>.
```

## Esempio

Decisione presa: inventario condiviso tra tutti i personaggi.

```markdown
- **Inventario condiviso** tra tutti i personaggi invece che separato per
  ciascuno: semplifica i puzzle cooperativi, che restano leggibili senza
  costringere il giocatore a ricordare chi porta cosa.
  - **Inventario separato per personaggio**: più realistico e apre puzzle
    basati sullo scambio di oggetti — che è esattamente il tipo di enigma
    previsto dal progetto. Scartato perché moltiplica i passaggi necessari
    a ogni soluzione (raggiungi il personaggio giusto, scambia, torna) e
    sposta la difficoltà dalla trovata alla gestione, che non è il genere
    di sfida cercato.
  - **Ibrido** (fondo comune più oggetti personali): rimandato. Recupera i
    pregi di entrambi, ma richiede di comunicare al giocatore la distinzione
    tra i due tipi di oggetto, e non c'è ancora abbastanza materiale di
    gioco per sapere se serve davvero.
  - Nota: da rivalutare se in fase di scrittura emergono puzzle che
    richiedono davvero il possesso esclusivo di un oggetto.
```

Nota cosa fa questo esempio: l'alternativa scartata è descritta nei suoi
**pregi reali** prima del motivo del rifiuto. Una voce che dipinge le
alternative come ovviamente sbagliate non sta documentando una decisione,
sta scrivendo una giustificazione a posteriori — e non aiuterà nessuno a
riconsiderarla quando le condizioni cambiano.

## Cosa registrare e cosa no

Registra quando la decisione **vincola il lavoro futuro**: struttura di
sistemi, rappresentazione dello stato, convenzioni che il codice dovrà
seguire, scelte che sarebbero costose da invertire, e ogni chiusura di un
punto in "Decisioni ancora aperte".

Non registrare le scelte locali e reversibili — il nome di un metodo, l'ordine
di due istruzioni, un valore di tuning. Riempiono il documento e ne
diluiscono la parte utile, che è il segnale che qualcosa è stato ponderato.

Nel dubbio, il criterio è: *se qualcuno tra sei mesi facesse il contrario,
sarebbe un problema?* Se sì, registra.

## Dopo aver scritto

Mostra all'utente la voce aggiunta e conferma quali sezioni hai toccato —
in particolare se hai rimosso un punto da "Decisioni ancora aperte", perché
è una modifica che altera il piano di lavoro e va vista.
