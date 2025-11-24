import os
from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import flash, render_template, request  # Add request if not already
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = '71777'  # Replace with something unique, e.g., a random string like 'supersecret123'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://postgres:aiymka23@localhost/assign3?client_encoding=utf8'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db
db.init_app(app)

# db = SQLAlchemy(app)
from models import UserAccount, Caregiver, Member, Job, Appointment, JobApplication

# ---------------------- HOME ----------------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------------- USER CRUD ----------------------
@app.route('/users')
def list_users():
    users = UserAccount.query.all()
    return render_template('users/list_user.html', users=users)

@app.route('/users/add_user', methods=['GET', 'POST'])
def add_user():
    print("add_user route reached!")
    if request.method == 'POST':
        new_user = UserAccount(
            email=request.form['email'],
            given_name=request.form['given_name'],
            surname=request.form['surname'],
            city=request.form['city'],
            phone_number=request.form['phone_number'],
            profile_description=request.form['profile_description'],
            password=request.form['password']
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('list_users'))
    return render_template('users/add_user.html')

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = UserAccount.query.get_or_404(user_id)
    if request.method == 'POST':
        user.email = request.form['email']
        user.given_name = request.form['given_name']
        user.surname = request.form['surname']
        user.city = request.form['city']
        user.phone_number = request.form['phone_number']
        user.profile_description = request.form['profile_description']
        db.session.commit()
        return redirect(url_for('list_users'))
    return render_template('users/edit_user.html', user=user)


from flask import flash, render_template, request
from sqlalchemy.exc import IntegrityError

@app.route('/users/delete/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    user = UserAccount.query.get_or_404(user_id)

    if request.method == 'POST':
        try:
            # Delete one-to-one dependents first (avoids the AssertionError)
            caregiver = Caregiver.query.filter_by(caregiver_user_id=user_id).first()
            if caregiver:
                db.session.delete(caregiver)
            
            member = Member.query.filter_by(member_user_id=user_id).first()
            if member:
                db.session.delete(member)
            
            # Delete one-to-many dependents (prevents IntegrityError from FKs)
            JobApplication.query.filter_by(caregiver_user_id=user_id).delete()
            Appointment.query.filter_by(caregiver_user_id=user_id).delete()
            Appointment.query.filter_by(member_user_id=user_id).delete()
            Job.query.filter_by(member_user_id=user_id).delete()
            
            # Now delete the user safely
            db.session.delete(user)
            db.session.commit()
            
            flash('User and all dependencies deleted successfully!', 'success')
            return redirect(url_for('list_users'))
        
        except AssertionError as e:
            db.session.rollback()
            flash(f'AssertionError: {str(e)}. Try deleting dependents manually first.', 'danger')
            return redirect(url_for('list_users'))
        
        except IntegrityError:
            db.session.rollback()
            flash('IntegrityError: Cannot delete due to remaining dependencies (e.g., active appointments or jobs).', 'danger')
            return redirect(url_for('list_users'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Unexpected error: {str(e)}', 'danger')
            return redirect(url_for('list_users'))

    # GET: Show confirmation page
    return render_template('users/delete_user.html', user=user)

# ---------------------- CAREGIVER (READ-ONLY) ----------------------
# Caregiver routes
@app.route('/caregivers')
def list_caregiver():
    caregivers = Caregiver.query.all()
    return render_template('caregiver/list_caregiver.html', caregivers=caregivers)


@app.route('/caregivers/add', methods=['GET', 'POST'])
def add_caregiver():
    if request.method == 'POST':
        new_caregiver = Caregiver(
            email=request.form['email'],
            given_name=request.form['given_name'],
            surname=request.form['surname'],
            phone_number=request.form['phone_number'],
            specialty=request.form.get('specialty')
        )
        db.session.add(new_caregiver)
        db.session.commit()
        return redirect(url_for('list_caregiver'))
    return render_template('caregiver/add_caregiver.html')


@app.route('/caregivers/edit/<int:caregiver_user_id>', methods=['GET', 'POST'])
def edit_caregiver(caregiver_user_id):
    caregiver = Caregiver.query.get_or_404(caregiver_user_id)
    if request.method == 'POST':
        caregiver.email = request.form['email']
        caregiver.given_name = request.form['given_name']
        caregiver.surname = request.form['surname']
        caregiver.phone_number = request.form['phone_number']
        caregiver.specialty = request.form.get('specialty')
        db.session.commit()
        return redirect(url_for('list_caregiver'))
    return render_template('caregiver/edit_caregiver.html', caregiver=caregiver)


@app.route('/caregivers/delete/<int:caregiver_user_id>', methods=['GET', 'POST'])
def delete_caregiver(caregiver_user_id):
    caregiver = Caregiver.query.get_or_404(caregiver_user_id)
    if request.method == 'POST':
        db.session.delete(caregiver)
        db.session.commit()
        return redirect(url_for('list_caregiver'))
    return render_template('caregiver/delete_caregiver.html', caregiver=caregiver)


# ---------------------- MEMBER (READ-ONLY) ----------------------
@app.route('/members')
def list_members():
    members = Member.query.all()
    return render_template('members/list_members.html', members=members)

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        try:
            new_member = Member(
                member_user_id=request.form['member_user_id'],   # FK to user_account.user_id
                dependent_description=request.form.get('dependent_description'),
                house_rules=request.form.get('house_rules')
            )

            db.session.add(new_member)
            db.session.commit()

            flash("Member added successfully!", "success")
            return redirect(url_for('list_members'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding member: {e}", "error")

    return render_template('members/add_members.html')

@app.route('/members/edit/<int:member_user_id>', methods=['GET', 'POST'])
def edit_member(member_user_id):
    member = Member.query.get_or_404(member_user_id)

    if request.method == 'POST':
        try:
            member.dependent_description = request.form.get('dependent_description')
            member.house_rules = request.form.get('house_rules')

            db.session.commit()
            flash("Member updated!", "success")
            return redirect(url_for('list_members'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating member: {e}", "error")

    return render_template('members/edit_members.html', member=member)

@app.route('/members/delete/<int:member_user_id>', methods=['GET', 'POST'])
def delete_member(member_user_id):
    member = Member.query.get_or_404(member_user_id)

    if request.method == 'POST':
        try:
            db.session.delete(member)
            db.session.commit()
            flash("Member deleted!", "success")
            return redirect(url_for('list_members'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting member: {e}", "error")

    return render_template('members/delete_members.html', member=member)



# ---------------------- JOB CRUD ----------------------
@app.route('/jobs')
def list_jobs():
    jobs = Job.query.all()
    return render_template('jobs/list_job.html', jobs=jobs)

@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    members = Member.query.all()
    if request.method == 'POST':
        new_job = Job(
            member_user_id=request.form['member_user_id'],
            required_caregiving_type=request.form['required_caregiving_type'],
            other_requirements=request.form['other_requirements'],
            date_posted=datetime.strptime(request.form['date_posted'], '%Y-%m-%d').date()
        )
        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for('list_jobs'))
    return render_template('jobs/add_job.html', members=members)

@app.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    members = Member.query.all()
    if request.method == 'POST':
        job.member_user_id = request.form['member_user_id']
        job.required_caregiving_type = request.form['required_caregiving_type']
        job.other_requirements = request.form['other_requirements']
        job.date_posted = datetime.strptime(request.form['date_posted'], '%Y-%m-%d').date()
        db.session.commit()
        return redirect(url_for('list_jobs'))
    return render_template('jobs/edit_job.html', job=job, members=members)

@app.route('/jobs/delete/<int:job_id>')
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('list_jobs'))

# ---------------------- APPOINTMENT CRUD ----------------------
@app.route('/appointments')
def list_appointments():
    appointments = Appointment.query.all()
    return render_template('appointments/list_appoitnments.html', appointments=appointments)

@app.route('/appointments/add', methods=['GET', 'POST'])
def add_appointment():
    caregivers = Caregiver.query.all()
    members = Member.query.all()
    if request.method == 'POST':
        new_appointment = Appointment(
            caregiver_user_id=request.form['caregiver_user_id'],
            member_user_id=request.form['member_user_id'],
            appointment_date=datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(request.form['appointment_time'], '%H:%M').time(),
            work_hours=request.form['work_hours'],
            status=request.form['status']
        )
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('list_appointments'))
    return render_template('appointments/add_appointment.html', caregivers=caregivers, members=members)

@app.route('/appointments/edit/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    caregivers = Caregiver.query.all()
    members = Member.query.all()
    if request.method == 'POST':
        appointment.caregiver_user_id = request.form['caregiver_user_id']
        appointment.member_user_id = request.form['member_user_id']
        appointment.appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()
        appointment.appointment_time = datetime.strptime(request.form['appointment_time'], '%H:%M').time()
        appointment.work_hours = request.form['work_hours']
        appointment.status = request.form['status']
        db.session.commit()
        return redirect(url_for('list_appointments'))
    return render_template('appointments/edit_appointment.html', appointment=appointment, caregivers=caregivers, members=members)

@app.route('/appointments/delete/<int:appointment_id>')
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('list_appointments'))


# ---------------------- JOB APPLICATION CRUD ----------------------
@app.route('/job_applications')
def list_job_applications():
    applications = JobApplication.query.all()
    return render_template('jobapplications/list_job_applications.html', applications=applications)

@app.route('/job_applications/add', methods=['GET', 'POST'])
def add_job_application():
    caregivers = Caregiver.query.all()
    jobs = Job.query.all()
    if request.method == 'POST':
        new_application = JobApplication(
            caregiver_user_id=request.form['caregiver_user_id'],
            job_id=request.form['job_id'],
            date_applied=datetime.strptime(request.form['date_applied'], '%Y-%m-%d').date()
        )
        db.session.add(new_application)
        db.session.commit()
        return redirect(url_for('list_job_applications'))
    return render_template('jobapplications/add_job_application.html', caregivers=caregivers, jobs=jobs)

@app.route('/job_applications/edit/<int:application_id>', methods=['GET', 'POST'])
def edit_job_application(application_id):
    application = JobApplication.query.get_or_404(application_id)
    caregivers = Caregiver.query.all()
    jobs = Job.query.all()
    if request.method == 'POST':
        application.caregiver_user_id = request.form['caregiver_user_id']
        application.job_id = request.form['job_id']
        application.date_applied = datetime.strptime(request.form['date_applied'], '%Y-%m-%d').date()
        db.session.commit()
        return redirect(url_for('list_job_applications'))
    return render_template('jobapplications/edit_job_application.html', application=application, caregivers=caregivers, jobs=jobs)

@app.route('/job_applications/delete/<int:application_id>')
def delete_job_application(application_id):
    application = JobApplication.query.get_or_404(application_id)
    db.session.delete(application)
    db.session.commit()
    return redirect(url_for('list_job_applications'))


from models import db, Address, Member  # make sure Address and Member are imported



# List all addresses
@app.route('/addresses')
def list_addresses():
    addresses = Address.query.all()  # variable name is plural
    return render_template('address/list_address.html', addresses=addresses)

# Add a new address
@app.route('/addresses/add', methods=['GET', 'POST'])
def add_address():
    members = Member.query.all()
    if request.method == 'POST':
        new_addr = Address(
            member_user_id=request.form['member_user_id'],
            house_number=request.form['house_number'],
            street=request.form['street'],
            town=request.form['town']
        )
        db.session.add(new_addr)
        db.session.commit()
        return redirect(url_for('list_addresses'))  # use plural
    return render_template('address/add_address.html', members=members)

# Edit an existing address
@app.route('/addresses/edit/<int:address_id>', methods=['GET', 'POST'])
def edit_address(address_id):
    addr = Address.query.get_or_404(address_id)
    members = Member.query.all()
    if request.method == 'POST':
        addr.member_user_id = request.form['member_user_id']
        addr.house_number = request.form['house_number']
        addr.street = request.form['street']
        addr.town = request.form['town']
        db.session.commit()
        return redirect(url_for('list_addresses'))  # use plural
    return render_template('address/edit_address.html', addr=addr, members=members)

# Delete an address
@app.route('/addresses/delete/<int:address_id>', methods=['GET', 'POST'])
def delete_address(address_id):
    addr = Address.query.get_or_404(address_id)
    if request.method == 'POST':
        db.session.delete(addr)
        db.session.commit()
        return redirect(url_for('list_addresses'))  # use plural
    return render_template('address/delete_address.html', addr=addr)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
