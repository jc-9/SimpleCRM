# simple_crm/app.py
from flask import Flask, render_template, g, request, flash, redirect, url_for
from datetime import datetime
from database import init_db, get_db, close_db # Import our database functions
from models import Customer, Event # Import our models
import os # For checking if db file exists

app = Flask(__name__)
app.config.from_object('config') # Load configuration from config.py


# --- Database Initialization (Runs once when the app module is loaded) ---
# This ensures the database directory exists and tables are created/updated
# when the app starts, whether via Gunicorn or direct python app.py.
with app.app_context():
    # Get the database file path from config.py
    db_file_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '') # Extract actual file path

    # Ensure the parent directory for the database file exists
    db_dir = os.path.dirname(db_file_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True) # Create directory if it doesn't exist
        print(f"Created database directory: {db_dir}")
    else:
        print(f"Database directory exists: {db_dir}")

    # Initialize the database (create tables if they don't exist)
    # IMPORTANT: Ensure your init_db() function in database.py
    # ONLY calls db.create_all() and does NOT db.drop_all() if you want data to persist.
    print(f"Initializing database at {db_file_path}...")
    init_db()
    print("Database tables created (if they didn't exist).")


# --- Database Hooks ---
# These functions ensure a database session is available for each request
# and is closed properly after each request.

@app.before_request
def before_request():
    """Opens a database connection before the request."""
    # We store the session on Flask's 'g' object, which is global to the request.
    g.db = get_db()

@app.teardown_request
def teardown_request(exception):
    """Closes the database connection after the request."""
    db = getattr(g, 'db', None)
    if db is not None:
        close_db()

# --- Routes ---
# We define routes here initially. For larger apps, these would be in routes.py
# but for now, keeping them together is fine for simplicity.

@app.route('/')
def index():
    """Home page displaying welcome message and customer list."""
    db_session = g.db # Get the database session
    customers = db_session.query(Customer).all() # Query all customers
    return render_template('index.html', customers=customers, current_year=datetime.utcnow().year)

@app.route('/create_customer', methods=['GET', 'POST'])
def create_customer():
    """Handles creating a new customer record."""
    if request.method == 'POST':
        customer_name = request.form['customer_name'].strip()
        primary_contact_name = request.form['primary_contact_name'].strip()
        primary_contact_email = request.form['primary_contact_email'].strip()

        if not customer_name or not primary_contact_name or not primary_contact_email:
            flash('All fields are required!', 'error')
            return render_template('create_customer.html') # Render form again with error

        db_session = g.db # Get the database session from Flask's g object

        # Check if customer name already exists
        existing_customer = db_session.query(Customer).filter_by(customer_name=customer_name).first()
        if existing_customer:
            flash(f'Customer "{customer_name}" already exists. Please use a different name.', 'error')
            return render_template('create_customer.html')

        try:
            new_customer = Customer(
                customer_name=customer_name,
                primary_contact_name=primary_contact_name,
                primary_contact_email=primary_contact_email
            )
            db_session.add(new_customer)
            db_session.commit() # Commit the new customer to the database
            flash(f'Customer "{customer_name}" created successfully!', 'success')
            return redirect(url_for('index')) # Redirect to home page
        except Exception as e:
            db_session.rollback() # Rollback in case of error
            flash(f'An error occurred while creating customer: {e}', 'error')
            # Optionally, log the full error for debugging
            app.logger.error(f"Error creating customer: {e}", exc_info=True)
            return render_template('create_customer.html') # Render form again with error

    # If it's a GET request, just render the empty form
    return render_template('create_customer.html')

@app.route('/customer/<int:customer_id>', methods=['GET', 'POST'])
def view_customer(customer_id):
    """
    Displays a single customer's details and handles adding new events.
    """
    db_session = g.db
    customer = db_session.query(Customer).get(customer_id)

    if customer is None:
        flash('Customer not found!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        event_type = request.form['event_type'].strip()
        description = request.form['description'].strip()

        if not event_type or not description:
            flash('Event type and description are required!', 'error')
            # Render the page again, preserving the customer context
            return render_template('view_customer.html', customer=customer)

        try:
            new_event = Event(
                customer_id=customer.id,
                event_type=event_type,
                description=description
            )
            db_session.add(new_event)
            db_session.commit()
            flash('Event added successfully!', 'success')
            # Redirect to the same page to prevent form resubmission on refresh
            return redirect(url_for('view_customer', customer_id=customer.id))
        except Exception as e:
            db_session.rollback()
            flash(f'An error occurred while adding event: {e}', 'error')
            app.logger.error(f"Error adding event for customer {customer.id}: {e}", exc_info=True)
            return render_template('view_customer.html', customer=customer)

    # If it's a GET request, just render the customer details
    return render_template('view_customer.html', customer=customer)

@app.route('/delete_customer/<int:customer_id>', methods=['GET', 'POST'])
def delete_customer(customer_id):
    """
    Handles deleting a customer record (with confirmation).
    """
    db_session = g.db
    customer = db_session.query(Customer).get(customer_id)

    if customer is None:
        flash('Customer not found!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # If it's a POST request, proceed with deletion
        try:
            db_session.delete(customer) # Mark the customer for deletion
            db_session.commit() # Commit the deletion to the database
            flash(f'Customer "{customer.customer_name}" deleted successfully!', 'success')
            return redirect(url_for('index')) # Redirect to the home page
        except Exception as e:
            db_session.rollback()
            flash(f'An error occurred while deleting customer: {e}', 'error')
            app.logger.error(f"Error deleting customer {customer.id}: {e}", exc_info=True)
            return redirect(url_for('index')) # Redirect back to index with error

    # If it's a GET request, show the confirmation page
    return render_template('delete_customer.html', customer=customer)

@app.route('/delete_event/<int:customer_id>/<int:event_id>', methods=['POST'])
def delete_event(customer_id, event_id):
    """
    Deletes a specific event log entry for a customer.
    """
    db_session = g.db
    event = db_session.query(Event).get(event_id)

    if event is None:
        flash('Event not found!', 'error')
        return redirect(url_for('view_customer', customer_id=customer_id))

    # Optional: Basic security check - ensure the event belongs to the customer
    if event.customer_id != customer_id:
        flash('Event does not belong to this customer!', 'error')
        return redirect(url_for('view_customer', customer_id=customer_id))

    try:
        db_session.delete(event) # Mark the event for deletion
        db_session.commit() # Commit the deletion
        flash('Event log entry deleted successfully!', 'success')
    except Exception as e:
        db_session.rollback()
        flash(f'An error occurred while deleting event: {e}', 'error')
        app.logger.error(f"Error deleting event {event_id} for customer {customer_id}: {e}", exc_info=True)

    # Always redirect back to the customer's view page
    return redirect(url_for('view_customer', customer_id=customer_id))



# We will add other routes like /create_customer, /customer/<id>, etc. here later.

# --- Application Startup Logic ---
# def create_app():
#     with app.app_context():
#         # Ensure the directory for the database file exists on the mounted volume
#         db_file_path = app.config['DATABASE']
#         db_dir = os.path.dirname(db_file_path)
#         if not os.path.exists(db_dir):
#             os.makedirs(db_dir, exist_ok=True) # exist_ok=True prevents error if directory already exists

        # Call init_db to create tables if they don't exist.
        # Your `init_db` function (in database.py) should ideally just call db.create_all().
        # If init_db() drops tables, it will wipe data on every app restart.
        # init_db() # This should only create tables if they don't exist.


    
    # """
    # Factory function to create and configure the application.
    # Useful for testing or when using application factories.
    # """
    # # Ensure database is initialized when the app starts
    # with app.app_context():
    #     # Check if the database file exists before initializing
    #     # This prevents re-initializing if it already has data
    #     if not os.path.exists(app.config['DATABASE']):
    #         print("Database file not found. Initializing database...")
    #         init_db()
    #     else:
    #         print("Database file found. Skipping initialization.")
    # return app

if __name__ == '__main__':
    # When running directly, call create_app and then run the Flask app
    # app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001) # debug=True for development, host='0.0.0.0' for Docker