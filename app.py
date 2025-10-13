from flask import Flask, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import joinedload
from models import db, User, Thought
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yourSuperSecretKey'  # Replace with a secure key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Loads user by ID

# ------------------ Routes ------------------
@app.route('/')
def index():
    return redirect(url_for('home')) 

@app.route('/home')
def home():
    #featured_thoughts = Thought.query.order_by(Thought.timestamp.desc()).limit(3).all()
    return render_template('home.html')  # Pass featured_thoughts if using them

# ---------- Registration ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash("Registration successful! You can now login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {str(e)}")
            flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for('register'))
    
    return render_template('register.html')

# ---------- Login ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('thoughts'))
    
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash("Invalid username or password.", "danger")
            app.logger.info("Failed login attempt for user: %s", username)
            return redirect(url_for('login'))
        
        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for('thoughts'))
    
    return render_template('login.html')

# ---------- Logout ----------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

# ---------- Thoughts Feed ----------
@app.route('/thoughts')
@login_required
def thoughts():
    # Eager-load User (no 'likes' relationship now)
    all_thoughts = Thought.query.options(
        joinedload(Thought.user)
    ).order_by(Thought.timestamp.desc()).all()
    return render_template('thoughts.html', thoughts=all_thoughts)

# ---------- Add New Thought ----------
@app.route('/thoughts/new', methods=['GET', 'POST'])
@login_required
def new_thought():
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        mood = request.form.get('mood', 'thoughtful')  # Get mood from form

        if not content:
            flash("Thought cannot be empty.", "danger")
            return redirect(url_for('new_thought'))
        
        # Create the Thought with mood
        new_thought = Thought(user_id=current_user.id, content=content, mood=mood)
        db.session.add(new_thought)
        try:
            db.session.commit()
            flash("Thought added successfully!", "success")
            return redirect(url_for('thoughts'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"New thought error: {str(e)}")
            flash("Error saving thought. Please try again.", "danger")
            return redirect(url_for('new_thought'))
    
    # GET request renders form
    return render_template('new_thought.html')


# ---------- Delete Thought ----------
@app.route('/thoughts/<int:id>/delete', methods=['POST'])
@login_required
def delete_thought(id):
    thought = Thought.query.get_or_404(id)
    
    if thought.user_id != current_user.id:
        flash("You can only delete your own thoughts.", "danger")
        return redirect(url_for('thoughts'))
    
    db.session.delete(thought)
    try:
        db.session.commit()
        flash("Thought deleted.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Delete thought error (Thought ID: {id}): {str(e)}")
        flash("Error deleting thought. Please try again.", "danger")
    
    return redirect(url_for('thoughts'))

# ---------- Edit Thought ----------
@app.route('/thought/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_thought(id):
    thought = Thought.query.get_or_404(id)

    # Only owner can edit
    if thought.user_id != current_user.id:
        flash("You cannot edit someone else's thought.", "danger")
        return redirect(url_for('thoughts'))

    if request.method == 'POST':
        content = request.form.get('content').strip()
        mood = request.form.get('mood', 'thoughtful')
        if not content:
            flash("Thought cannot be empty.", "danger")
            return redirect(url_for('edit_thought', id=id))

        thought.content = content
        thought.mood = mood
        try:
            db.session.commit()
            flash("Thought updated successfully!", "success")
            return redirect(url_for('thoughts'))
        except Exception as e:
            db.session.rollback()
            flash("Error updating thought. Try again.", "danger")
            return redirect(url_for('edit_thought', id=id))

    # GET request -> render edit form
    return render_template('edit_thought.html', thought=thought)

# ---------- Like Thought ----------
# This logic is fine IF thought.liked_by is a list/InstrumentedList (default/lazy='select')
@app.route('/like/<int:id>', methods=['POST'])
@login_required
def like_thought(id):
    thought = Thought.query.get_or_404(id)

    if current_user in thought.liked_by:  # This check now works against a list
        thought.liked_by.remove(current_user)
        liked = False
    else:
        thought.liked_by.append(current_user)
        liked = True

    db.session.commit()
    return jsonify({
        'liked': liked,
        'likes': thought.like_count()
    })

@app.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    from models import Thought, User  # Ensure models are imported if necessary

    user_to_view = User.query.get_or_404(user_id)
    
    # 🚨 FIX START: Use Python's sorted() function 🚨
    # 1. user_to_view.thoughts is already the list of thoughts.
    user_posts_list = user_to_view.thoughts 

    # 2. Sort the list by the 'timestamp' attribute in descending order.
    user_posts = sorted(
        user_posts_list, 
        key=lambda thought: thought.timestamp, 
        reverse=True  # True for newest posts first (descending)
    )
    # 🚨 FIX END 🚨
    
    # Calculate stats using the methods you previously defined
    total_likes = user_to_view.total_likes_received()
    milestones = user_to_view.get_milestones()
    
    return render_template(
        'profile.html', 
        user=user_to_view, 
        posts=user_posts,  # Pass the sorted list to the template
        total_likes=total_likes, 
        milestones=milestones
    )

@login_manager.unauthorized_handler
def unauthorized():
    flash('Please login to access this page.', 'danger')
    return redirect(url_for('home'))

# ------------------ Database Initialization ------------------
with app.app_context():
    db.create_all()  # Creates tables for User and Thought only

# ------------------ Run the App ------------------
if __name__ == "__main__":
    app.run(debug=True)  # Debug mode for development