# Stile Ibrido: Pixel Art + Sfondi 2D Moderni

Molte avventure grafiche indie contemporanee combinano personaggi/oggetti in pixel art a bassa risoluzione con sfondi disegnati a risoluzione piena, in stile painterly/vettoriale, ricchi di colore e gradienti. Per far convivere i due stili senza stonare:

## 1. Coerenza cromatica

- Estrai o definisci una palette "madre" condivisa (es. 6-10 colori chiave: cielo, ombra dominante, luce dominante, colore terra, colore accento) e usala sia per costruire lo sfondo sia per derivare la palette ridotta dei personaggi pixel art.
- Applica lo stesso color grading complessivo (es. leggera dominante calda al tramonto, o fredda notturna) su entrambi gli strati, così anche se le tecniche di rendering sono diverse il "mood" resta identico.

## 2. Direzione della luce coerente

- Decidi una direzione luce unica per la scena (es. luce da sinistra-alto) e rispettala sia nelle ombre disegnate nello sfondo sia nello shading dei personaggi pixel.

## 3. Scala e proporzioni

- I personaggi pixel art, anche se costruiti su una griglia piccola (es. 32x64), vanno poi scalati (upscaling nearest-neighbor, es. x3/x4) per abbinarsi in proporzione allo sfondo ad alta risoluzione: calcola la scala confrontando l'altezza voluta del personaggio in scena (es. 180px su uno sfondo di 720px di altezza) con l'altezza del suo canvas pixel nativo.
- Evita di scalare i personaggi con fattori non interi (es. x3.5): produce sfocatura o pixel di dimensioni irregolari. Se serve una taglia intermedia, ridisegna il personaggio a una griglia nativa più grande piuttosto che scalare con fattori frazionari.

## 4. Contrasto tra i due strati

- Poiché lo sfondo è "morbido" (gradienti, dithering leggero o nessuno) e il personaggio è "netto" (bordi pixel duri), aggiungi un leggerissimo bordo/ombra di contatto sotto i piedi del personaggio (una macchia d'ombra ellittica sfumata, disegnata come parte dello sfondo o come layer separato) per ancorarlo visivamente alla scena, altrimenti il personaggio "galleggia".

## 5. Texture e rumore

- Se lo sfondo moderno usa texture/rumore/gradient noise per dare profondità (es. carta, tela), puoi applicare un rumore leggerissimo (pochi valori di opacità random) anche sulle zone piatte dei personaggi pixel per non farli sembrare "adesivi" incollati sopra: attenzione a non violare la griglia dei pixel logici, il rumore va applicato per blocco-pixel, non per singolo pixel fisico dell'immagine finale.

## 6. Livelli/parallasse

- Per gli sfondi, è utile generare 2-4 layer separati (es. cielo/lontano, edifici/medio, primo piano) con trasparenza, così l'integrazione in un motore può applicare parallasse in base allo scroll orizzontale. Salva ogni layer come PNG separato con suffisso `_layerN` oltre al composito finale.
