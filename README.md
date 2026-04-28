# MariaDB DataViewer

Visualizzatore interattivo per database MariaDB/MySQL basato su terminale.

## Requisiti

- Python 3.8+
- Server MariaDB/MySQL in esecuzione
- Credenziali di accesso al database

## Installazione

```bash
pip install -r requirements.txt
```

## Utilizzo

```bash
python mariadb_viewer.py
```

Al primo avvio ti verranno richiesti:
- Host (default: localhost)
- Porta (default: 3306)
- Username
- Password
- Database (opzionale)

## Funzionalità

### Menu principale

1. **Esegui query SQL** - Editor SQL interattivo per query manuali
2. **Query builder (con filtri)** - Costruttore guidato con JOIN, filtri, ordinamento
3. **Lista tabelle** - Mostra tutte le tabelle del database corrente
4. **Struttura tabella** - Visualizza schema di una tabella
5. **Cambia database** - Passa a un altro database
6. **Lista database** - Mostra tutti i database disponibili
7. **Esci** - Chiude la connessione

### Editor query (opzione 1)

- Scrivi query SQL multiriga
- Termina con `;` e premi invio
- Oppure premi invio su riga vuota dopo aver scritto la query
- Syntax highlighting automatico
- Visualizzazione risultati in tabelle formattate
- Export risultati in CSV
- Scrivi `exit` per tornare al menu

### Query Builder (opzione 2)

Costruttore guidato per creare query senza scrivere SQL:

**Selezione tabelle:**
- Tabella principale
- JOIN multipli (INNER, LEFT, RIGHT)
- Specifica colonne di join per ogni relazione

**Selezione colonne:**
- Scegli colonne da ogni tabella
- Formato automatico `tabella.colonna`

**Filtri WHERE:**
- Aggiungi multipli filtri
- Operatori: `=`, `!=`, `>`, `<`, `>=`, `<=`, `LIKE`, `IN`, `IS NULL`, `IS NOT NULL`
- Supporto wildcard `%` con LIKE
- Riconoscimento automatico tipo dato (numerico vs stringa)

**Ordinamento:**
- ORDER BY su qualsiasi colonna
- ASC o DESC

**Limite risultati:**
- LIMIT per controllare numero righe

**Esempio flusso JOIN:**
```
1. Tabella principale: dipendenti
2. Aggiungere un JOIN? y
3. Tabella da unire: reparti
4. Tipo JOIN: INNER
5. Colonna di dipendenti: reparto_id
6. Colonna di reparti: id
7. Aggiungere un JOIN? y
8. Tabella da unire: progetti
9. ...
10. Colonne da dipendenti: 1,2,3 (nome, cognome, email)
11. Colonne da reparti: 1 (nome)
12. Filtro: reparti.sede = 'Milano'
```

Genera automaticamente:
```sql
SELECT dipendenti.nome, dipendenti.cognome, dipendenti.email, reparti.nome
FROM dipendenti
INNER JOIN reparti ON dipendenti.reparto_id = reparti.id
WHERE reparti.sede = 'Milano'
LIMIT 100;
```

### Esempi query manuali

```sql
-- Selezione base
SELECT * FROM users LIMIT 10;

-- Con filtro
SELECT name, email FROM users WHERE age > 30;

-- Aggregazione
SELECT city, COUNT(*) as count 
FROM users 
GROUP BY city 
ORDER BY count DESC;

-- JOIN manuale
SELECT d.nome, d.cognome, r.nome AS reparto
FROM dipendenti d
INNER JOIN reparti r ON d.reparto_id = r.id
WHERE r.sede = 'Milano';

-- JOIN multipli
SELECT 
    d.nome AS dipendente,
    p.nome AS progetto,
    t.ore_lavorate
FROM timesheet t
INNER JOIN dipendenti d ON t.dipendente_id = d.id
INNER JOIN progetti p ON t.progetto_id = p.id
WHERE t.data_lavoro > '2024-01-01'
ORDER BY t.ore_lavorate DESC;

-- Operazioni DML
INSERT INTO users (name, email) VALUES ('Mario', 'mario@example.com');
UPDATE users SET age = 30 WHERE id = 1;
DELETE FROM users WHERE id = 5;
```

### Wildcard con LIKE

La wildcard `%` cerca pattern nei testi:

```sql
-- Inizia con "Mar"
WHERE nome LIKE 'Mar%'
-- Trova: Mario, Marco, Martina

-- Finisce con "a"
WHERE nome LIKE '%a'
-- Trova: Laura, Anna, Sofia

-- Contiene "ro"
WHERE nome LIKE '%ro%'
-- Trova: Mario, Roberto, Mauro

-- Email con dominio
WHERE email LIKE '%@gmail.com'
```

Underscore `_` per un singolo carattere:
```sql
WHERE nome LIKE 'M_rio'
-- Trova: Mario, Morio (solo 5 caratteri)
```

## Note tecniche

- Usa `mysql-connector-python` per la connessione
- Interfaccia terminale con `rich` per formattazione
- Supporta query SELECT e DML (INSERT, UPDATE, DELETE)
- Auto-commit per modifiche
- Gestione errori SQL con messaggi dettagliati
- Export risultati in formato CSV

## Struttura

```
mariadb_viewer.py          # Applicazione principale
requirements_mariadb.txt   # Dipendenze
README_mariadb.md         # Documentazione
```

La classe `MariaDBViewer` gestisce:
- Connessione al server
- Esecuzione query
- Recupero metadati (database, tabelle, strutture)
- Switch tra database
