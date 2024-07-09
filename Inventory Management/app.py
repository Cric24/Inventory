from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def create_connection():
    conn = sqlite3.connect('inventory.db')
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = ""
    inventory = []

    if request.method == 'POST':
        search_query = request.form['search']
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM inventory WHERE item_name LIKE ?", ('%' + search_query + '%',))
        inventory = c.fetchall()
        conn.close()
    else:
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM inventory WHERE quantity > 0")
        inventory = c.fetchall()
        conn.close()
    
    return render_template('index.html', inventory=inventory, search_query=search_query)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM inventory WHERE item_name = ?", (item_name,))
        item = c.fetchone()
        if item:
            new_quantity = item[2] + quantity
            c.execute("UPDATE inventory SET quantity = ? WHERE item_name = ?", (new_quantity, item_name))
        else:
            c.execute("INSERT INTO inventory (item_name, quantity) VALUES (?, ?)", (item_name, quantity))
        conn.commit()
        conn.close()
        flash('Item added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/remove', methods=['GET', 'POST'])
def remove_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM inventory WHERE item_name = ?", (item_name,))
        item = c.fetchone()
        if item:
            if item[2] >= quantity:
                new_quantity = item[2] - quantity
                if new_quantity == 0:
                    c.execute("DELETE FROM inventory WHERE item_name = ?", (item_name,))
                else:
                    c.execute("UPDATE inventory SET quantity = ? WHERE item_name = ?", (new_quantity, item_name))
                conn.commit()
                flash('Item removed successfully!', 'success')
            else:
                flash('Not enough quantity to remove!', 'warning')
        else:
            flash('No such item in inventory!', 'error')
        conn.close()
        return redirect(url_for('index'))
    return render_template('remove_item.html')

if __name__ == '__main__':
    app.run(debug=True)
