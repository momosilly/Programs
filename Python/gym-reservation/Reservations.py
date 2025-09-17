import os
from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates")
def reserve(name, from_time, to_time, sporthall):
    folder = r"C:\Users\dudim\Desktop\Deltion\Programmas\Python\gym-reservation"
    filename = os.path.join(folder, "reservations.txt")
    if not os.path.exists(filename):
        with open(filename, 'a') as f:
            pass
    # Check if from_time or to_time is already reserved
    with open(filename, 'r') as f:
        for reservations in f:
            parts = reservations.strip().split('|')
            reserved_from_time = parts[0].strip()
            reserved_to_time = parts[1].strip() if len(parts) > 1 else ''
            if reserved_from_time == from_time.strip():
                return f"time {from_time} is already reserved"
            elif reserved_to_time == to_time.strip():
                return f"time {to_time} is already reserved"
    # Add new reservation
    with open(filename, 'a') as f:
        f.write(f"{from_time.strip()} | {to_time.strip()} | {name.strip()} | {sporthall.strip()}\n")
        return f"Reservation confirmed for {name} at {from_time} until {to_time} in sport hall {sporthall}"

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    if request.method == 'POST':
        name = request.form.get('name')
        from_time = request.form.get('startTime')
        to_time = request.form.get('endTime')
        sporthall = request.form.get('sportHall')
        message = reserve(name, from_time, to_time, sporthall)
        return render_template('index.html', message=message)
    return render_template('index.html', message=None)

if __name__ == '__main__':
    app.run(debug=True)