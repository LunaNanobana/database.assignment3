# # python pfrom app import db
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()


# class UserAccount(db.Model):
#     __tablename__ = "user_account"
#     user_id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     given_name = db.Column(db.String(100), nullable=False)
#     surname = db.Column(db.String(100), nullable=False)
#     city = db.Column(db.String(100))
#     phone_number = db.Column(db.String(50))
#     profile_description = db.Column(db.Text)
#     password = db.Column(db.String(255), nullable=False)


#     caregiver = db.relationship('Caregiver', backref='user', uselist=False)
#     member = db.relationship('Member', backref='user', uselist=False)
#     jobs = db.relationship('Job', backref='member', lazy=True)
#     appointments = db.relationship('Appointment', backref='user', lazy=True)


# class Caregiver(db.Model):
#     __tablename__ = "caregiver"
#     caregiver_user_id = db.Column(db.Integer, db.ForeignKey('user_account.user_id'), primary_key=True)
#     photo = db.Column(db.Text)
#     gender = db.Column(db.String(10))
#     caregiving_type = db.Column(db.String(50))
#     hourly_rate = db.Column(db.Numeric(6,2))
#     appointments = db.relationship('Appointment', backref='caregiver', lazy=True)


# class Member(db.Model):
#     __tablename__ = "member"
#     member_user_id = db.Column(db.Integer, db.ForeignKey('user_account.user_id'), primary_key=True)
#     house_rules = db.Column(db.Text)
#     dependent_description = db.Column(db.Text)
#     jobs = db.relationship('Job', backref='member_detail', lazy=True)


# class Job(db.Model):
#     __tablename__ = "job"
#     job_id = db.Column(db.Integer, primary_key=True)
#     member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id'), nullable=False)
#     required_caregiving_type = db.Column(db.String(50))
#     other_requirements = db.Column(db.Text)
#     date_posted = db.Column(db.Date)


# class Appointment(db.Model):
#     __tablename__ = "appointment"
#     appointment_id = db.Column(db.Integer, primary_key=True)
#     caregiver_user_id = db.Column(db.Integer, db.ForeignKey('caregiver.caregiver_user_id'), nullable=False)
#     member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id'), nullable=False)
#     appointment_date = db.Column(db.Date)
#     appointment_time = db.Column(db.Time)
#     work_hours = db.Column(db.Integer)
#     status = db.Column(db.String(50))
# class JobApplication(db.Model):
#     __tablename__ = "job_application"
#     application_id = db.Column(db.Integer, primary_key=True)
#     caregiver_user_id = db.Column(db.Integer, db.ForeignKey('caregiver.caregiver_user_id'), nullable=False)
#     job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'), nullable=False)
#     date_applied = db.Column(db.Date, nullable=False)

#     caregiver = db.relationship('Caregiver', backref='applications')
#     job = db.relationship('Job', backref='applications')
from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

# ------------------------
# UserAccount
# ------------------------
class UserAccount(db.Model):
    __tablename__ = 'user_account'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    given_name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    phone_number = db.Column(db.String(50))
    profile_description = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=False)

    # One-to-one relationships
    member = db.relationship('Member', back_populates='user', uselist=False)
    caregiver = db.relationship('Caregiver', back_populates='user', uselist=False)


# ------------------------
# Caregiver
# ------------------------
class Caregiver(db.Model):
    __tablename__ = 'caregiver'

    caregiver_user_id = db.Column(db.Integer, db.ForeignKey('user_account.user_id'), primary_key=True)
    photo = db.Column(db.Text)
    gender = db.Column(db.String(10))
    caregiving_type = db.Column(db.String(50))
    hourly_rate = db.Column(db.Numeric(6,2))

    user = db.relationship('UserAccount', back_populates='caregiver')
    appointments = db.relationship('Appointment', back_populates='caregiver')
    job_applications = db.relationship('JobApplication', back_populates='caregiver')


# ------------------------
# Member
# ------------------------
class Member(db.Model):
    __tablename__ = 'member'

    member_user_id = db.Column(db.Integer, db.ForeignKey('user_account.user_id'), primary_key=True)
    house_rules = db.Column(db.Text)
    dependent_description = db.Column(db.Text)

    user = db.relationship('UserAccount', back_populates='member')
    jobs = db.relationship('Job', back_populates='member')
    appointments = db.relationship('Appointment', back_populates='member')
    addresses = db.relationship('Address', back_populates='member')


# ------------------------
# Address
# ------------------------
class Address(db.Model):
    __tablename__ = 'address'

    address_id = db.Column(db.Integer, primary_key=True)
    member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id'))
    house_number = db.Column(db.String(20))
    street = db.Column(db.String(200))
    town = db.Column(db.String(100))

    member = db.relationship('Member', back_populates='addresses')


# ------------------------
# Job
# ------------------------
class Job(db.Model):
    __tablename__ = 'job'

    job_id = db.Column(db.Integer, primary_key=True)
    member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id'))
    required_caregiving_type = db.Column(db.String(50))
    other_requirements = db.Column(db.Text)
    date_posted = db.Column(db.Date, default=date.today)

    member = db.relationship('Member', back_populates='jobs')
    applications = db.relationship('JobApplication', back_populates='job')


# ------------------------
# JobApplication
# ------------------------
class JobApplication(db.Model):
    __tablename__ = 'job_application'

    application_id = db.Column(db.Integer, primary_key=True)
    caregiver_user_id = db.Column(db.Integer, db.ForeignKey('caregiver.caregiver_user_id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'))
    date_applied = db.Column(db.Date, default=date.today)

    caregiver = db.relationship('Caregiver', back_populates='job_applications')
    job = db.relationship('Job', back_populates='applications')


# ------------------------
# Appointment
# ------------------------
class Appointment(db.Model):
    __tablename__ = 'appointment'

    appointment_id = db.Column(db.Integer, primary_key=True)
    caregiver_user_id = db.Column(db.Integer, db.ForeignKey('caregiver.caregiver_user_id'))
    member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id'))
    appointment_date = db.Column(db.Date)
    appointment_time = db.Column(db.Time)
    work_hours = db.Column(db.Integer)
    status = db.Column(db.String(20))

    caregiver = db.relationship('Caregiver', back_populates='appointments')
    member = db.relationship('Member', back_populates='appointments')


