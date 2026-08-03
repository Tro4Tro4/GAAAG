# Tecniche di Pixel Art

## Palette

- Limita sempre il numero di colori: 8-16 per un personaggio piccolo (16x16/32x32), 16-32 per personaggi/scene più dettagliati, max ~64 per uno sfondo pixel art ricco.
- Costruisci **rampe di colore** (color ramps) per ogni colore base: 3-5 tonalità che vanno da ombra a luce, non semplice scurimento/schiarimento lineare dell'RGB ma spostamento anche di tonalità (hue shifting): le ombre tendono verso il viola/blu, le luci verso il giallo/arancio. Questo dà profondità senza sembrare "spento".
- Evita il nero puro per i contorni/ombre più scure: usa un blu/viola molto scuro, resta più gradevole.

## Outline (contorno)

- **Outline nero pieno**: stile cartoon leggibile, buono per personaggi/oggetti piccoli su sfondi variabili (tipico point-and-click).
- **Selective outlining**: il contorno cambia colore in base alla zona (più scuro della rampa di quella zona, non nero fisso) — più organico, usato in pixel art più "moderna".
- **Nessun contorno**: si affida solo al contrasto tonale tra forma e sfondo; richiede più cura nella palette.

## Shading e dithering

- Shading a bande piatte (flat shading a 2-3 livelli per rampa) è lo stile più leggibile a basse risoluzioni.
- Il **dithering** (pattern alternati di due colori, es. a scacchiera o Bayer/ordered dither) simula una transizione morbida senza aumentare i colori usati; utile su superfici ampie (cieli, muri) per evitare bande piatte monotone. Va usato con parsimonia: troppo dithering rende l'immagine rumorosa.
- Anti-aliasing manuale: solo su curve/diagonali importanti (silhouette del personaggio), aggiungendo 1 pixel di colore intermedio per smussare un gradino netto — mai automatico/di libreria.

## Silhouette e leggibilità

- Un personaggio/oggetto deve essere riconoscibile anche solo dalla sagoma nera piena: se la silhouette non è chiara, la forma va rivista prima di aggiungere dettagli interni.
- Evita dettagli sub-pixel (linee più sottili di un pixel logico): a risoluzioni piccole, ogni pixel conta come tratto del disegno.

## Animazione: principi per i cicli di camminata (walk cycle)

Un walk cycle leggibile per un personaggio 2D richiede tipicamente 6-8 frame, basati su pose chiave:
1. **Contact** (contatto): entrambi i piedi vicini al suolo, uno avanti uno indietro — il corpo è nel punto più basso.
2. **Down/Recoil**: il peso si scarica sulla gamba avanzata, leggero abbassamento del bacino.
3. **Passing position**: la gamba libera passa vicino al corpo, punto più alto del ciclo.
4. **Up/High point**: la gamba libera si estende in avanti, corpo di nuovo alto.
5. Ripeti specchiando i passi 1-3 con le gambe invertite per completare il ciclo.

Per un ciclo semplice "arcade" (4 frame) puoi limitarti a contact-sx, passing, contact-dx, passing, alternando lo sfasamento verticale del corpo (bob up/down) per dare senso di peso.

Per animazioni "idle" (fermo): 2-4 frame con oscillazione minima (respiro, ammiccamento occasionale) bastano per evitare l'effetto statico.

## Composizione sprite sheet

- Righe = animazioni diverse (idle, walk, talk...), colonne = frame della stessa animazione, con dimensione di cella fissa e identica per tutte le celle (anche se il contenuto disegnato non riempie tutta la cella) — è fondamentale per l'importazione in motori di gioco (Godot, Unity, GameMaker).
- Lascia 1-2 px di padding trasparente fra celle se il motore di destinazione non gestisce bene lo "sprite bleeding" nei filtri di rendering.
