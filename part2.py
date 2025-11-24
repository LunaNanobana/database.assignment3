# part2.py
# Python 3.8+

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env file if present
print("Script started")

DATABASE_URL = os.getenv("DATABASE_URL")  # e.g. postgresql+psycopg2://user:pass@localhost:5432/care_db
if not DATABASE_URL:
    raise SystemExit("Set DATABASE_URL in .env or environment (postgresql+psycopg2://user:pw@host:port/dbname)")

engine = create_engine(DATABASE_URL, echo=False, future=True)

def run_statement(conn, sql, params=None, fetch=False):
    stmt = text(sql)
    result = conn.execute(stmt, params or {})
    if fetch:
        return result.fetchall()
    return result.rowcount

def print_rows(rows):
    if not rows:
        print("(no rows)")
    else:
        for r in rows:
            print(tuple(r))

def main():
    with engine.begin() as conn:
        try:
            print("Connected to database.\n")
            # ---------------------------
            # Part 2.3 Update SQL Statements
            # 3.1 Update phone number of Arman Armanov
            print("3.1 Updating phone number for Arman Armanov...")
            sql = """
            UPDATE user_account
            SET phone_number = '+77773414141'
            WHERE given_name = 'Arman' AND surname = 'Armanov';
            """
            affected = run_statement(conn, sql)
            print(f"Rows updated: {affected}\n")

            # 3.2 Add commission fee to caregivers hourly_rate: +0.3 if <10, else +10%
            print("3.2 Applying commission to caregiver.hourly_rate...")
            sql = """
            UPDATE caregiver
            SET hourly_rate = CASE
                WHEN hourly_rate < 10 THEN hourly_rate + 0.3
                ELSE ROUND(hourly_rate * 1.10::numeric, 2)
            END;
            """
            affected = run_statement(conn, sql)
            print(f"Rows updated: {affected}\n")

            # ---------------------------
            # Part 2.4 Delete SQL Statements
            # 4.1 Delete the jobs posted by Amina Aminova.
            print("4.1 Deleting jobs posted by Amina Aminova...")
            sql = """
            DELETE FROM job
            USING user_account ua
            WHERE job.member_user_id = ua.user_id
              AND ua.given_name = 'Amina' AND ua.surname = 'Aminova';
            """
            affected = run_statement(conn, sql)
            print(f"Jobs deleted: {affected}\n")

      # 4.2 Delete all members who live on Kabanbay Batyr street.
            print("4.2 Deleting members who live on 'Kabanbay Batyr' street...")
            sql = """
            DELETE FROM member
            WHERE member_user_id IN (
                SELECT member_user_id FROM address WHERE lower(street) = lower('Kabanbay Batyr')
            );
            """
            affected = run_statement(conn, sql)
            print(f"Members deleted: {affected}\n")

            # ---------------------------
            #Part 2.5 Simple Queries
            print("5.1 Select caregiver and member names for the accepted appointments.")
            sql = """
            SELECT ca_u.given_name AS caregiver_given, ca_u.surname AS caregiver_surname,
                   m_u.given_name AS member_given, m_u.surname AS member_surname,
                   a.appointment_date, a.appointment_time
            FROM appointment a
            JOIN caregiver c ON a.caregiver_user_id = c.caregiver_user_id
            JOIN user_account ca_u ON ca_u.user_id = c.caregiver_user_id
            JOIN member m ON a.member_user_id = m.member_user_id
            JOIN user_account m_u ON m_u.user_id = m.member_user_id
            WHERE a.status = 'accepted'
            ORDER BY a.appointment_date;
            """
            rows = run_statement(conn, sql, fetch=True)
            print_rows(rows); print()

            print("5.2 List job ids that contain 'soft-spoken' in other_requirements.")
            sql = "SELECT job_id, other_requirements FROM job WHERE lower(other_requirements) LIKE '%soft-spoken%';"
            rows = run_statement(conn, sql, fetch=True)
            print_rows(rows); print()

            print("5.3 List the work_hours of all babysitter positions (appointments where caregiver is babysitter).")
            sql = """
            SELECT a.appointment_id, a.work_hours, ua.given_name, ua.surname
            FROM appointment a
            JOIN caregiver c ON a.caregiver_user_id = c.caregiver_user_id
            JOIN user_account ua ON ua.user_id = c.caregiver_user_id
            WHERE lower(c.caregiving_type) = 'babysitter';
            """
            rows = run_statement(conn, sql, fetch=True)
            print_rows(rows); print()

            print("5.4 Members who are looking for Elderly Care in Astana and have 'No pets.' rule.")
            sql = """
            SELECT DISTINCT ua.user_id, ua.given_name, ua.surname, ua.city, m.house_rules
            FROM job j
            JOIN member m ON j.member_user_id = m.member_user_id
            JOIN user_account ua ON ua.user_id = m.member_user_id
            WHERE lower(j.required_caregiving_type) = 'elderly'
              AND lower(ua.city) = 'astana'
              AND m.house_rules LIKE '%No pets.%';
            """
            rows = run_statement(conn, sql, fetch=True)
            print_rows(rows); print()

            # ---------------------------
            # Part 2.6 Complex Queries
            print("6.1 Count the number of applicants for each job (job id, poster name, count).")
            sql = """
            SELECT j.job_id, poster.given_name AS poster_given, poster.surname AS poster_surname,
                   COUNT(ja.application_id) AS num_applicants
            FROM job j
            JOIN user_account poster ON poster.user_id = j.member_user_id
            LEFT JOIN job_application ja ON ja.job_id = j.job_id
            GROUP BY j.job_id, poster.given_name, poster.surname
            ORDER BY j.job_id;
            """
            rows = run_statement(conn, sql, fetch=True)
            print_rows(rows); print()

            print("6.2 Total hours spent by care givers for all accepted appointments.")
            sql = """
            SELECT SUM(work_hours) AS total_hours
            FROM appointment
            WHERE status = 'accepted';
            """
            rows = run_statement(conn, sql, fetch=True)
            print_rows(rows); print()

            print("6.3 Average pay of caregivers based on accepted appointments (avg per caregiver).")
            sql = """
            SELECT c.caregiver_user_id, ua.given_name, ua.surname,
                   AVG(c.hourly_rate * a.work_hours) AS avg_pay
            FROM appointment a
            JOIN caregiver c ON c.caregiver_user_id = a.caregiver_user_id
            JOIN user_account ua ON ua.user_id = c.caregiver_user_id
            WHERE a.status = 'accepted'
            GROUP BY c.caregiver_user_id, ua.given_name, ua.surname
            ORDER BY avg_pay DESC;
            """
            rows = run_statement(conn, sql, fetch=True)
            print_rows(rows); print()

            print("6.4 Caregivers who earn above average based on accepted appointments.")
            sql = """
            WITH caregiver_avg AS (
    SELECT c.caregiver_user_id, AVG(c.hourly_rate * a.work_hours) AS avg_pay
    FROM appointment a
    JOIN caregiver c ON c.caregiver_user_id = a.caregiver_user_id
    WHERE a.status = 'accepted'
    GROUP BY c.caregiver_user_id
), overall_avg AS (
    SELECT AVG(avg_pay) AS overall_avg_pay FROM caregiver_avg
)
SELECT ca.caregiver_user_id,
       ua.given_name,
       ua.surname,
       ca.avg_pay
FROM caregiver_avg ca
CROSS JOIN overall_avg oa
JOIN user_account ua ON ua.user_id = ca.caregiver_user_id
WHERE ca.avg_pay > oa.overall_avg_pay
ORDER BY ca.avg_pay DESC;
            """
            rows = run_statement(conn, sql, fetch=True)
            print_rows(rows); print()

            # ---------------------------
            # Part 2.7 Query with a Derived Attribute
            print("7. Total cost to pay for each caregiver for all accepted appointments (derived attribute).")
            sql = """
            SELECT c.caregiver_user_id, ua.given_name, ua.surname,
                   SUM(c.hourly_rate * a.work_hours) AS total_cost
            FROM caregiver c
            JOIN appointment a ON a.caregiver_user_id = c.caregiver_user_id
            JOIN user_account ua ON ua.user_id = c.caregiver_user_id
            WHERE a.status = 'accepted'
            GROUP BY c.caregiver_user_id, ua.given_name, ua.surname
            ORDER BY total_cost DESC;
            """
            rows = run_statement(conn, sql, fetch=True)
            print_rows(rows); print()

            # ---------------------------
            # Part 2.8 View Operation
            print("8. Create view: job_applicants_view (job applications + applicant info).")
            sql_create_view = """
            CREATE OR REPLACE VIEW job_applicants_view AS
            SELECT j.job_id, j.member_user_id AS poster_member_id,
                   poster_ua.given_name AS poster_given, poster_ua.surname AS poster_surname,
                   ja.application_id, ja.caregiver_user_id AS applicant_user_id,
                   app_ua.given_name AS applicant_given, app_ua.surname AS applicant_surname,
                   ja.date_applied
            FROM job j
            LEFT JOIN job_application ja ON ja.job_id = j.job_id
            LEFT JOIN member poster ON poster.member_user_id = j.member_user_id
            LEFT JOIN user_account poster_ua ON poster_ua.user_id = j.member_user_id
            LEFT JOIN caregiver app ON app.caregiver_user_id = ja.caregiver_user_id
            LEFT JOIN user_account app_ua ON app_ua.user_id = ja.caregiver_user_id
            ;
            """
            run_statement(conn, sql_create_view)
            print("View created (job_applicants_view). Now selecting from it:\n")
            rows = run_statement(conn, "SELECT * FROM job_applicants_view ORDER BY job_id, application_id;", fetch=True)
            print_rows(rows); print()

            print("All operations complete.")

        except SQLAlchemyError as e:
            print("Database error:", e)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
print("Script end")
