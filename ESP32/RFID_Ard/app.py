from flask import Flask, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from dotenv import load_dotenv
import os

app = Flask(__name__)

# ── Config ──────────────
app.config['SECRET_KEY'] = 'mypassword'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost/rfid'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

load_dotenv()

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

MIN_WEEKLY_HOURS = 21 

db      = SQLAlchemy(app)
migrate = Migrate(app, db)
mail    = Mail(app)


# ── Models ───────────

class User(db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(50))
    uid      = db.Column(db.String(30), unique=True, nullable=False)
    email    = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

class ClockEvent(db.Model):
    """Every RFID scan is stored as a clock-in or clock-out."""
    __tablename__ = 'clock_events'
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    direction = db.Column(db.String(3), nullable=False)  # 'in' or 'out'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ── Helpers ──────────────

def get_logged_in_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None


def get_current_direction(user_id):
    """Next scan is 'in' if last was 'out' (or no events yet), else 'out'."""
    last = (ClockEvent.query
            .filter_by(user_id=user_id)
            .order_by(ClockEvent.timestamp.desc())
            .first())
    if last is None or last.direction == 'out':
        return 'in'
    return 'out'


def get_week_start(dt=None):
    """Return the Monday 00:00 of the current week, naive UTC."""
    if dt is None:
        dt = datetime.utcnow()
    return (dt - timedelta(days=dt.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0)


def calc_hours_for_week(user_id, week_start):
    """Total hours worked in the 7-day period starting at week_start."""
    week_end = week_start + timedelta(days=7)
    events = (ClockEvent.query
              .filter_by(user_id=user_id)
              .filter(ClockEvent.timestamp >= week_start,
                      ClockEvent.timestamp <  week_end)
              .order_by(ClockEvent.timestamp)
              .all())
    total, clock_in_time = timedelta(), None
    for e in events:
        # Strip timezone so subtraction always works
        ts = e.timestamp.replace(tzinfo=None)
        if e.direction == 'in':
            clock_in_time = ts
        elif e.direction == 'out' and clock_in_time:
            diff = ts - clock_in_time
            total += diff
            clock_in_time = None
    result = round(total.total_seconds() / 3600, 2)
    print(f"[DEBUG] total hours = {result}")
    return result


DUTCH_DAYS = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']

def build_daily_summary(user_id, week_start):
    """List of (day_label, hours) for each of the 7 days in the week."""
    days = []
    for i in range(7):
        day_start = week_start + timedelta(days=i)
        day_end   = day_start  + timedelta(days=1)
        events = (ClockEvent.query
                  .filter_by(user_id=user_id)
                  .filter(ClockEvent.timestamp >= day_start,
                          ClockEvent.timestamp <  day_end)
                  .order_by(ClockEvent.timestamp)
                  .all())
        total, clock_in_time = timedelta(), None
        for e in events:
            ts = e.timestamp.replace(tzinfo=None)
            if e.direction == 'in':
                clock_in_time = ts
            elif e.direction == 'out' and clock_in_time:
                total += ts - clock_in_time
                clock_in_time = None
        label = f"{DUTCH_DAYS[i]} {day_start.strftime('%d-%m')}"
        days.append((label, round(total.total_seconds() / 3600, 2)))
    return days


# ── Weekly email job ───────────────

def send_weekly_emails():
    """Runs every Friday at 18:00. Emails employees who worked < MIN_WEEKLY_HOURS."""
    with app.app_context():
        week_start = get_week_start()
        employees  = User.query.filter_by(is_admin=False).all()
        for emp in employees:
            hours = calc_hours_for_week(emp.id, week_start)
            if hours < MIN_WEEKLY_HOURS and emp.email:
                daily = build_daily_summary(emp.id, week_start)
                rows  = "\n".join(f"  {day}: {h} uur" for day, h in daily)
                msg = Message(
                    subject="⚠️ Te weinig uren gewerkt deze week",
                    recipients=[emp.email]
                )
                msg.body = (
                    f"Hallo {emp.name or emp.uid},\n\n"
                    f"Je hebt deze week slechts {hours} uur gewerkt. "
                    f"Het minimum is {MIN_WEEKLY_HOURS} uur.\n\n"
                    f"Overzicht per dag:\n{rows}\n\n"
                    f"Neem contact op met je leidinggevende.\n\n"
                    f"Met vriendelijke groet,\nHet systeem"
                )
                mail.send(msg)


scheduler = BackgroundScheduler()
scheduler.add_job(send_weekly_emails, 'cron', day_of_week='fri', hour=18, minute=0)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


# ── RFID scan endpoint (called by Arduino) ──────────────────

@app.get("/scan")
def scan():
    uid  = request.args.get("uid")
    user = User.query.filter_by(uid=uid).first()

    if not user:
        user = User(uid=uid, name=None, is_admin=False)
        db.session.add(user)
        db.session.commit()
        return {"status": "registered_pending", "uid": uid}

    direction = get_current_direction(user.id)
    event = ClockEvent(user_id=user.id, direction=direction)
    db.session.add(event)
    db.session.commit()

    return {
        "status":    "ok",
        "name":      user.name,
        "direction": direction,
        "admin":     user.is_admin
    }


# ── Login / Logout ─────────────────────────

@app.get("/login")
def login_page():
    return render_template("login.html")

@app.post("/login")
def login():
    uid  = request.form.get("uid", "").strip()
    user = User.query.filter_by(uid=uid).first()
    if not user:
        return render_template("login.html", error="UID niet gevonden.")
    session["user_id"] = user.id
    if user.is_admin:
        return redirect(url_for("admin_page"))
    return redirect(url_for("user_page", user_id=user.id))

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ── Admin page ───────────────────────────

@app.get("/admin")
def admin_page():
    current = get_logged_in_user()
    if not current or not current.is_admin:
        return redirect(url_for("login_page"))

    week_start = get_week_start()
    users      = User.query.order_by(User.id).all()

    user_data = []
    for u in users:
        hours      = calc_hours_for_week(u.id, week_start)
        clocked_in = (get_current_direction(u.id) == 'out')
        user_data.append({
            "user":       u,
            "hours":      hours,
            "clocked_in": clocked_in,
            "low_hours":  not u.is_admin and hours < MIN_WEEKLY_HOURS
        })

    return render_template("admin.html",
                           user_data=user_data,
                           week_start=week_start,
                           min_hours=MIN_WEEKLY_HOURS,
                           current=current)

@app.post("/admin/edit/<int:user_id>")
def admin_edit_user(user_id):
    current = get_logged_in_user()
    if not current or not current.is_admin:
        return redirect(url_for("login_page"))
    user          = User.query.get_or_404(user_id)
    user.name     = request.form.get("name", "").strip() or None
    user.email    = request.form.get("email", "").strip() or None
    user.is_admin = "is_admin" in request.form
    db.session.commit()
    return redirect(url_for("admin_page"))

@app.post("/admin/delete/<int:user_id>")
def admin_delete_user(user_id):
    current = get_logged_in_user()
    if not current or not current.is_admin:
        return redirect(url_for("login_page"))
    user = User.query.get_or_404(user_id)
    ClockEvent.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin_page"))


# ── User page ───────────────────────────────

@app.get("/user/<int:user_id>")
def user_page(user_id):
    current = get_logged_in_user()
    if not current:
        return redirect(url_for("login_page"))
    if not current.is_admin and current.id != user_id:
        return redirect(url_for("user_page", user_id=current.id))

    user       = User.query.get_or_404(user_id)
    week_start = get_week_start()
    week_hours = calc_hours_for_week(user.id, week_start)
    daily      = build_daily_summary(user.id, week_start)
    clocked_in = (get_current_direction(user.id) == 'out')

    events = (ClockEvent.query
              .filter_by(user_id=user_id)
              .order_by(ClockEvent.timestamp.desc())
              .limit(20).all())

    return render_template("user.html",
                           user=user,
                           week_hours=week_hours,
                           daily=daily,
                           clocked_in=clocked_in,
                           events=events,
                           min_hours=MIN_WEEKLY_HOURS,
                           current=current)


# ── Root ────────────────────────────

@app.get("/")
def index():
    current = get_logged_in_user()
    if not current:
        return redirect(url_for("login_page"))
    if current.is_admin:
        return redirect(url_for("admin_page"))
    return redirect(url_for("user_page", user_id=current.id))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')