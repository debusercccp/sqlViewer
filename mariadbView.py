#!/usr/bin/env python3
"""
MariaDB DataViewer - Terminal-based database query tool
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich import box
import sys
from typing import Optional, List, Tuple

console = Console()


class MariaDBViewer:
    """Manages MariaDB connection and query execution"""
    
    def __init__(self):
        self.conn: Optional[mysql.connector.MySQLConnection] = None
        self.cursor = None
        self.current_db: Optional[str] = None
    
    def connect(self, host: str, user: str, password: str, database: str = None, port: int = 3306) -> bool:
        """Connect to MariaDB server"""
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            self.cursor = self.conn.cursor()
            self.current_db = database
            console.print(f"[green]Connesso a {host}:{port}[/green]")
            if database:
                console.print(f"[green]Database: {database}[/green]")
            return True
        except Error as e:
            console.print(f"[red]Errore connessione: {e}[/red]")
            return False
    
    def execute_query(self, query: str) -> Tuple[bool, Optional[pd.DataFrame], str]:
        """Execute SQL query and return results"""
        if not self.conn or not self.cursor:
            return False, None, "Nessuna connessione attiva"
        
        try:
            self.cursor.execute(query)
            
            # Check if query returns results
            if self.cursor.description:
                columns = [desc[0] for desc in self.cursor.description]
                rows = self.cursor.fetchall()
                df = pd.DataFrame(rows, columns=columns)
                return True, df, f"{len(df)} righe"
            else:
                # Query without results (INSERT, UPDATE, DELETE, etc.)
                self.conn.commit()
                return True, None, f"Query eseguita. Righe affette: {self.cursor.rowcount}"
        except Error as e:
            return False, None, f"Errore SQL: {e}"
    
    def get_databases(self) -> List[str]:
        """Get list of databases"""
        if not self.cursor:
            return []
        
        try:
            self.cursor.execute("SHOW DATABASES")
            return [db[0] for db in self.cursor.fetchall()]
        except:
            return []
    
    def get_tables(self) -> List[str]:
        """Get list of tables in current database"""
        if not self.cursor or not self.current_db:
            return []
        
        try:
            self.cursor.execute("SHOW TABLES")
            return [table[0] for table in self.cursor.fetchall()]
        except:
            return []
    
    def get_table_structure(self, table_name: str) -> Optional[pd.DataFrame]:
        """Get table structure"""
        if not self.cursor:
            return None
        
        try:
            self.cursor.execute(f"DESCRIBE {table_name}")
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            return pd.DataFrame(rows, columns=columns)
        except:
            return None
    
    def use_database(self, database: str) -> bool:
        """Switch to different database"""
        if not self.cursor:
            return False
        
        try:
            self.cursor.execute(f"USE {database}")
            self.current_db = database
            console.print(f"[green]Database corrente: {database}[/green]")
            return True
        except Error as e:
            console.print(f"[red]Errore: {e}[/red]")
            return False
    
    def close(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            console.print("[yellow]Connessione chiusa[/yellow]")


def display_dataframe(df: pd.DataFrame, title: str = "Risultati"):
    """Display pandas DataFrame as rich table"""
    table = Table(title=title, box=box.ROUNDED, show_lines=True)
    
    # Add columns
    for col in df.columns:
        table.add_column(str(col), style="cyan", no_wrap=False)
    
    # Add rows
    for _, row in df.iterrows():
        table.add_row(*[str(val) for val in row])
    
    console.print(table)
    console.print(f"\n[dim]Righe: {len(df)} | Colonne: {len(df.columns)}[/dim]")


def show_menu():
    """Display main menu"""
    menu = Panel(
        "[1] Esegui query SQL\n"
        "[2] Query builder (con filtri)\n"
        "[3] Lista tabelle\n"
        "[4] Struttura tabella\n"
        "[5] Cambia database\n"
        "[6] Lista database\n"
        "[7] Esci",
        title="Menu",
        box=box.DOUBLE
    )
    console.print(menu)


def connect_to_db() -> Optional[MariaDBViewer]:
    """Interactive connection setup"""
    console.print(Panel("Connessione MariaDB", style="bold blue"))
    
    host = Prompt.ask("Host", default="localhost")
    port = Prompt.ask("Porta", default="3306")
    user = Prompt.ask("Username", default="root")
    password = Prompt.ask("Password", password=True)
    database = Prompt.ask("Database (opzionale, premi invio per saltare)", default="")
    
    viewer = MariaDBViewer()
    
    if viewer.connect(
        host=host,
        user=user,
        password=password,
        database=database if database else None,
        port=int(port)
    ):
        return viewer
    
    return None


def query_mode(viewer: MariaDBViewer):
    """Interactive query execution"""
    console.print("\n[bold]Editor Query[/bold]")
    console.print("[dim]Scrivi la query SQL (termina con ';' e premi invio su riga vuota)[/dim]")
    console.print("[dim]Oppure scrivi 'exit' per tornare al menu[/dim]\n")
    
    query_lines = []
    
    while True:
        line = input("> ")
        
        if line.strip().lower() == 'exit':
            return
        
        query_lines.append(line)
        
        # Check if query is complete (ends with semicolon)
        if line.strip().endswith(';'):
            query = '\n'.join(query_lines)
            
            # Display query with syntax highlighting
            syntax = Syntax(query, "sql", theme="monokai", line_numbers=False)
            console.print(Panel(syntax, title="Query", border_style="blue"))
            
            # Execute
            success, df, message = viewer.execute_query(query)
            
            if success:
                console.print(f"[green]{message}[/green]")
                if df is not None and not df.empty:
                    display_dataframe(df)
                    
                    # Export option
                    if Confirm.ask("\nEsportare risultati in CSV?", default=False):
                        filename = Prompt.ask("Nome file", default="output.csv")
                        df.to_csv(filename, index=False)
                        console.print(f"[green]Salvato in {filename}[/green]")
            else:
                console.print(f"[red]{message}[/red]")
            
            # Reset
            query_lines = []
            console.print()


def query_builder(viewer: MariaDBViewer):
    """Interactive query builder with filters"""
    if not viewer.current_db:
        console.print("[yellow]Nessun database selezionato[/yellow]")
        return
    
    console.print("\n[bold]Query Builder[/bold]")
    
    # Select table
    tables = viewer.get_tables()
    if not tables:
        console.print("[yellow]Nessuna tabella disponibile[/yellow]")
        return
    
    console.print("\n[bold]Tabelle disponibili:[/bold]")
    for i, t in enumerate(tables, 1):
        console.print(f"  {i}. {t}")
    
    table = Prompt.ask("\nTabella da interrogare")
    if table not in tables:
        console.print("[red]Tabella non trovata[/red]")
        return
    
    # Get table structure
    structure = viewer.get_table_structure(table)
    if structure is None:
        console.print("[red]Errore recupero struttura tabella[/red]")
        return
    
    columns = structure['Field'].tolist()
    
    # Select columns
    console.print("\n[bold]Colonne disponibili:[/bold]")
    for i, col in enumerate(columns, 1):
        col_type = structure[structure['Field'] == col]['Type'].values[0]
        console.print(f"  {i}. {col} ({col_type})")
    
    console.print("\n[dim]Inserisci numeri separati da virgola (es: 1,3,5) o 'all' per tutte[/dim]")
    col_choice = Prompt.ask("Colonne da selezionare", default="all")
    
    if col_choice.lower() == 'all':
        selected_cols = columns
    else:
        try:
            indices = [int(x.strip()) - 1 for x in col_choice.split(',')]
            selected_cols = [columns[i] for i in indices if 0 <= i < len(columns)]
        except:
            console.print("[red]Input non valido[/red]")
            return
    
    if not selected_cols:
        console.print("[red]Nessuna colonna selezionata[/red]")
        return
    
    # Build WHERE clause
    filters = []
    console.print("\n[bold]Filtri (WHERE)[/bold]")
    
    while True:
        if not Confirm.ask("\nAggiungere un filtro?", default=False):
            break
        
        console.print("\n[bold]Colonne per filtro:[/bold]")
        for i, col in enumerate(columns, 1):
            col_type = structure[structure['Field'] == col]['Type'].values[0]
            console.print(f"  {i}. {col} ({col_type})")
        
        filter_col = Prompt.ask("Colonna da filtrare")
        if filter_col not in columns:
            console.print("[red]Colonna non trovata[/red]")
            continue
        
        operator = Prompt.ask(
            "Operatore",
            choices=["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "IS NULL", "IS NOT NULL"],
            default="="
        )
        
        if operator in ["IS NULL", "IS NOT NULL"]:
            filters.append(f"{filter_col} {operator}")
        elif operator == "IN":
            values = Prompt.ask("Valori (separati da virgola)")
            values_list = [f"'{v.strip()}'" for v in values.split(',')]
            filters.append(f"{filter_col} IN ({', '.join(values_list)})")
        elif operator == "LIKE":
            value = Prompt.ask("Valore (usa % per wildcard)")
            filters.append(f"{filter_col} LIKE '{value}'")
        else:
            value = Prompt.ask("Valore")
            col_type = structure[structure['Field'] == filter_col]['Type'].values[0]
            
            # Check if numeric type
            if any(t in col_type.lower() for t in ['int', 'decimal', 'float', 'double']):
                filters.append(f"{filter_col} {operator} {value}")
            else:
                filters.append(f"{filter_col} {operator} '{value}'")
    
    # ORDER BY
    order_col = None
    if Confirm.ask("\nAggiungere ordinamento (ORDER BY)?", default=False):
        console.print("\n[bold]Colonne per ordinamento:[/bold]")
        for i, col in enumerate(selected_cols, 1):
            console.print(f"  {i}. {col}")
        
        order_col = Prompt.ask("Colonna per ordinamento")
        if order_col in selected_cols:
            order_dir = Prompt.ask("Direzione", choices=["ASC", "DESC"], default="ASC")
        else:
            console.print("[yellow]Colonna non valida, ordinamento saltato[/yellow]")
            order_col = None
    
    # LIMIT
    limit = None
    if Confirm.ask("\nLimitare numero risultati (LIMIT)?", default=True):
        limit = Prompt.ask("Numero massimo righe", default="100")
    
    # Build final query
    query = f"SELECT {', '.join(selected_cols)} FROM {table}"
    
    if filters:
        query += f"\nWHERE {' AND '.join(filters)}"
    
    if order_col:
        query += f"\nORDER BY {order_col} {order_dir}"
    
    if limit:
        query += f"\nLIMIT {limit}"
    
    query += ";"
    
    # Display and execute
    syntax = Syntax(query, "sql", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="Query Generata", border_style="blue"))
    
    if not Confirm.ask("\nEseguire questa query?", default=True):
        return
    
    success, df, message = viewer.execute_query(query)
    
    if success:
        console.print(f"[green]{message}[/green]")
        if df is not None and not df.empty:
            display_dataframe(df)
            
            if Confirm.ask("\nEsportare risultati in CSV?", default=False):
                filename = Prompt.ask("Nome file", default="output.csv")
                df.to_csv(filename, index=False)
                console.print(f"[green]Salvato in {filename}[/green]")
    else:
        console.print(f"[red]{message}[/red]")


def list_tables(viewer: MariaDBViewer):
    """Display tables in current database"""
    if not viewer.current_db:
        console.print("[yellow]Nessun database selezionato[/yellow]")
        return
    
    tables = viewer.get_tables()
    
    if not tables:
        console.print("[yellow]Nessuna tabella trovata[/yellow]")
        return
    
    table = Table(title=f"Tabelle in {viewer.current_db}", box=box.ROUNDED)
    table.add_column("Nome Tabella", style="cyan")
    
    for t in tables:
        table.add_row(t)
    
    console.print(table)


def describe_table(viewer: MariaDBViewer):
    """Show table structure"""
    if not viewer.current_db:
        console.print("[yellow]Nessun database selezionato[/yellow]")
        return
    
    tables = viewer.get_tables()
    if not tables:
        console.print("[yellow]Nessuna tabella disponibile[/yellow]")
        return
    
    console.print("\n[bold]Tabelle disponibili:[/bold]")
    for i, t in enumerate(tables, 1):
        console.print(f"  {i}. {t}")
    
    table_name = Prompt.ask("\nNome tabella")
    
    if table_name not in tables:
        console.print("[red]Tabella non trovata[/red]")
        return
    
    structure = viewer.get_table_structure(table_name)
    
    if structure is not None:
        display_dataframe(structure, title=f"Struttura: {table_name}")


def change_database(viewer: MariaDBViewer):
    """Switch to different database"""
    databases = viewer.get_databases()
    
    if not databases:
        console.print("[yellow]Nessun database disponibile[/yellow]")
        return
    
    console.print("\n[bold]Database disponibili:[/bold]")
    for i, db in enumerate(databases, 1):
        console.print(f"  {i}. {db}")
    
    db_name = Prompt.ask("\nNome database")
    viewer.use_database(db_name)


def list_databases(viewer: MariaDBViewer):
    """Display all databases"""
    databases = viewer.get_databases()
    
    if not databases:
        console.print("[yellow]Nessun database disponibile[/yellow]")
        return
    
    table = Table(title="Database", box=box.ROUNDED)
    table.add_column("Nome Database", style="cyan")
    
    for db in databases:
        style = "bold green" if db == viewer.current_db else ""
        table.add_row(db, style=style)
    
    console.print(table)


def main():
    console.print(Panel.fit(
        "[bold blue]MariaDB DataViewer[/bold blue]\n"
        "Visualizzatore interattivo per database MariaDB/MySQL",
        border_style="blue"
    ))
    
    # Connect to database
    viewer = connect_to_db()
    
    if not viewer:
        console.print("[red]Connessione fallita. Uscita.[/red]")
        sys.exit(1)
    
    # Main loop
    try:
        while True:
            console.print()
            show_menu()
            choice = Prompt.ask("Scelta", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "1":
                query_mode(viewer)
            elif choice == "2":
                query_builder(viewer)
            elif choice == "3":
                list_tables(viewer)
            elif choice == "4":
                describe_table(viewer)
            elif choice == "5":
                change_database(viewer)
            elif choice == "6":
                list_databases(viewer)
            elif choice == "7":
                if Confirm.ask("\nSei sicuro di voler uscire?"):
                    break
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrotto dall'utente[/yellow]")
    
    finally:
        viewer.close()


if __name__ == "__main__":
    main()
