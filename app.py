from datetime import timedelta, datetime
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import config
import relay

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = timedelta(minutes=config.SESSION_TIMEOUT_MINUTES)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

relay.setup_pin(config.GPIO_RELAY_PIN)

last_trigger_time = None


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


@app.route("/")
@login_required
def index():
    return render_template("index.html", last_trigger=last_trigger_time)


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    error = None
    if request.method == "POST":
        pin = request.form.get("pin", "")
        if pin == config.PIN_CODE:
            session.permanent = True
            session["authenticated"] = True
            return redirect(url_for("index"))
        else:
            error = "Felaktig PIN-kod"
    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/trigger", methods=["POST"])
@login_required
def trigger():
    global last_trigger_time
    try:
        relay.pulse_relay(config.GPIO_RELAY_PIN, config.RELAY_PULSE_MS)
        last_trigger_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({"success": True, "message": "Porten utlöst", "time": last_trigger_time})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
