from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chiave_segreta_wikitech'  # Necessaria per i messaggi flash

# Crea la cartella database se non esiste
if not os.path.exists('database'):
    os.makedirs('database')

# Crea il database e la tabella per gli iscritti
def init_db():
    conn = sqlite3.connect('database/subscribers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            date_subscribed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabella per i contenuti della newsletter
    c.execute('''
        CREATE TABLE IF NOT EXISTS newsletter_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Inizializza il database
init_db()

# Route per la homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route per approfondimenti
@app.route('/approfondimenti')
def approfondimenti():
    return render_template('approfondimenti.html')

# Route per programmazione
@app.route('/programmazione')
def programmazione():
    return render_template('programmazione.html')

# Route per altro
@app.route('/altro')
def altro():
    return render_template('altro.html')

# Route per newsletter
@app.route('/newsletter')
def newsletter():
    return render_template('newsletter.html')

# Route per iscrizione alla newsletter
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    
    if not email:
        flash('Email richiesta!', 'error')
        return redirect(url_for('newsletter'))
    
    try:
        conn = sqlite3.connect('database/subscribers.db')
        c = conn.cursor()
        c.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        conn.close()
        flash('Iscrizione completata con successo!', 'success')
    except sqlite3.IntegrityError:
        flash('Questa email è già iscritta!', 'warning')
    except Exception as e:
        flash(f'Si è verificato un errore: {str(e)}', 'error')
    
    return redirect(url_for('newsletter'))

# Pannello admin (semplificato)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if title and content:
            conn = sqlite3.connect('database/subscribers.db')
            c = conn.cursor()
            c.execute('INSERT INTO newsletter_content (title, content) VALUES (?, ?)', 
                     (title, content))
            conn.commit()
            
            # Recupera tutte le email
            c.execute('SELECT email FROM subscribers')
            subscribers = c.fetchall()
            
            # Qui in un caso reale invieresti le email
            # Per ora solo simuliamo
            subscriber_count = len(subscribers)
            conn.close()
            
            flash(f'Newsletter inviata a {subscriber_count} iscritti!', 'success')
        else:
            flash('Titolo e contenuto sono richiesti!', 'error')
    
    # Recupera i dati per visualizzarli
    conn = sqlite3.connect('database/subscribers.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM subscribers')
    subscriber_count = c.fetchone()[0]
    
    c.execute('SELECT id, title, date_created FROM newsletter_content ORDER BY date_created DESC')
    newsletters = c.fetchall()
    
    # Ottieni le ultime 10 iscrizioni
    c.execute('SELECT email, date_subscribed FROM subscribers ORDER BY date_subscribed DESC LIMIT 10')
    recent_subscribers = c.fetchall()
    
    conn.close()
    
    return render_template('admin.html', 
                          subscriber_count=subscriber_count,
                          newsletters=newsletters,
                          recent_subscribers=recent_subscribers)

if __name__ == '__main__':
    app.run(debug=True)