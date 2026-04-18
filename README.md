# MariaDB DataViewer

Visualizzatore interattivo per database MariaDB/MySQL basato su terminale.

## Requisiti

- Python 3.8+
- Server MariaDB/MySQL in esecuzione
- Credenziali di accesso al database

## Installazione

```bash
pip install -r requirements_mariadb.txt
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

1. **Esegui query** - Editor SQL interattivo
2. **Lista tabelle** - Mostra tutte le tabelle del database corrente
3. **Struttura tabella** - Visualizza schema di una tabella
4. **Cambia database** - Passa a un altro database
5. **Lista database** - Mostra tutti i database disponibili
6. **Esci** - Chiude la connessione

### Editor query

- Scrivi query SQL multiriga
- Termina con `;` e premi invio su riga vuota
- Syntax highlighting
- Visualizzazione risultati in tabelle formattate
- Export risultati in CSV
- Scrivi `exit` per tornare al menu

### Esempi query

```sql
SELECT * FROM users LIMIT 10;

SELECT name, email FROM users WHERE age > 30;

SELECT city, COUNT(*) as count 
FROM users 
GROUP BY city 
ORDER BY count DESC;

INSERT INTO users (name, email) VALUES ('Mario', 'mario@example.com');

UPDATE users SET age = 30 WHERE id = 1;

DELETE FROM users WHERE id = 5;
```

## Note tecniche

- Usa `mysql-connector-python` per la connessione
- Interfaccia terminale con `rich` per formattazione
- Supporta query SELECT e DML (INSERT, UPDATE, DELETE)
- Auto-commit per modifiche
- Gestione errori SQL con messaggi dettagliati

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
