import sqlite3
import json
from prettytable import PrettyTable
from exceptions import AlreadyExistError, DatabaseError
from leetcode import get_leetcode_user_stats, get_contest_stats

########################
# Database -  Settings #
########################

# Create a table for storing data
def create_table():
  connection = sqlite3.connect("students")
  try:
    connection.execute(
      "CREATE TABLE IF NOT EXISTS students ( aitu_rank INTEGER NULL, aitu_ranking REAL NULL, telegram_id INTEGER PRIMARY KEY, edu_group TEXT NOT NULL, registration_date TEXT NOT NULL, leetcode_username TEXT NOT NULL UNIQUE, prog_lang TEXT DEFAULT 0, total_problems INTEGER NOT NULL, easy_tasks INTEGER NOT NULL, medium_tasks INTEGER NOT NULL, hard_tasks INTEGER NOT NULL, reputation INTEGER NOT NULL, leetcoins INTEGER NOT NULL, global_ranking INTEGER NOT NULL, contest_ranking INTEGER NOT NULL, message_chat_id INTEGER DEFAULT 0);"
    )
    connection.commit()
  except Exception as e:
    print("Error in create_table: ", e)
  finally:
    connection.close()

# Perform CRUD operations
# Add new Student
def add_student(telegram_id, edu_group, registration_date,
                leetcode_username, prog_lang, total_problems, easy_tasks, medium_tasks, hard_tasks, reputation, leetcoins, global_ranking, contest_ranking):
  aitu_ranking = get_aitu_ranking(global_ranking, contest_ranking, reputation)
  params = (aitu_ranking, telegram_id, edu_group, registration_date,
                leetcode_username, prog_lang, total_problems, easy_tasks, medium_tasks,
                hard_tasks, reputation, leetcoins, global_ranking, contest_ranking)
  connection = sqlite3.connect("students")
  try:
    connection.execute(
      "INSERT INTO students(aitu_rank, aitu_ranking, telegram_id, edu_group, registration_date, \
                leetcode_username, prog_lang, total_problems, easy_tasks, medium_tasks, \
                hard_tasks, reputation, leetcoins, global_ranking, contest_ranking) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", params)
    update_aitu_top_rankings(connection)
    connection.commit()
  except sqlite3.IntegrityError:
    raise AlreadyExistError()
  except Exception:
    raise DatabaseError()
  finally:
    connection.close()

# Get AITU Ranking
def get_aitu_ranking(global_ranking, contest_ranking, reputation):
  global_ranking = min(1000000, global_ranking)
  contest_ranking = min(300000, contest_ranking)
  reputation = min(3000, reputation)
  aitu_ranking = 500 * (1000000 - global_ranking) / 1000000 + 450 * (300000 - contest_ranking) / 300000 + 50 * (3000 - reputation) / 3000
  return round(aitu_ranking, 3)

# AITU Students Top Rankings Update
def update_aitu_top_rankings(connection):
  connection.execute("""
    WITH st1 AS (
      SELECT *,
             ROW_NUMBER() OVER (ORDER BY aitu_ranking DESC) AS row_num
      FROM students
    )
    UPDATE students
    SET aitu_rank = (SELECT row_num FROM st1 WHERE st1.leetcode_username = students.leetcode_username);
    """)


# Getting Students Data
def print_students():
  connection = sqlite3.connect("students")
  try:
    update_aitu_top_rankings(connection)
    cursor_object = connection.execute(
      "SELECT * FROM students ORDER BY aitu_rank;")
    rows = cursor_object.fetchall()
    table = PrettyTable()
    table.field_names = [i[0] for i in cursor_object.description]
    for row in rows:
      table.add_row(row)
    print(table)
    connection.commit()
  except Exception as e:
    print("Error in print_students: ", e)
  finally:
    connection.close()


# Automatic Update of Live Statistics -> LeetCode Actions
def update_student_rankings():
  connection = sqlite3.connect("students")
  try:
    cursor_object = connection.execute(
      "SELECT leetcode_username FROM students ORDER BY aitu_rank;")
    rows = cursor_object.fetchall()
    for leetcode_user in rows:
      update_student(leetcode_user[0])
    update_aitu_top_rankings(connection)
    connection.commit()
  except Exception as e:
    print("Error in update_student_rankings:", e)
  finally:
    connection.close()


def update_student(leetcode_username):
  connection = sqlite3.connect("students")
  try:
    data = get_leetcode_user_stats(leetcode_username)
    data['contest_ranking'] = get_contest_stats(leetcode_username)['global_ranking']
    if data["status"] == "error":
      # delete_student_by_leetcode(leetcode_username)
      return
    connection.execute(
      f"UPDATE students SET total_problems = {data['totalSolved']}, easy_tasks = {data['easySolved']}, medium_tasks = {data['mediumSolved']}, hard_tasks = {data['hardSolved']}, reputation = {data['reputation']}, leetcoins = {data['contributionPoints']}, global_ranking = {data['ranking']}, contest_ranking = {data['contest_ranking']} WHERE leetcode_username = '{leetcode_username}';"
    )
    connection.commit()
  except Exception as e:
    print("Error in update_student: ", e)
  finally:
    connection.close()


# Update student leetcode username by telegram Id
def update_student_leetcode_username_by_telegram_id(telegram_id, new_username):
  connection = sqlite3.connect("students")
  try:
    connection.execute(
      f"UPDATE students SET leetcode_username = '{new_username}' WHERE telegram_id = '{telegram_id}'"
    )
    connection.commit()
    status = 'OK'
  except Exception as e:
    print(f'Error in update_student_leetcode_username_by_telegram_id: {e}')
    status = 'ERROR'
  finally:
    connection.close()
    return status


# Update Student Data by telegram_id
def update_student_edu_group_by_telegramID(telegram_id, edu_group):
  connection = sqlite3.connect("students")
  try:
    connection.execute(
      f"UPDATE students SET edu_group = '{edu_group}' WHERE telegram_id = '{telegram_id}'"
    )
    connection.commit()
  except Exception as e:
    print("Error in update_student_edu_group_by_telegramID: ", e)
  finally:
    connection.close()


# Delete Student By telegram_id
def delete_student_by_telegramID(telegram_id):
  connection = sqlite3.connect("students")
  try:
    connection.execute(
      f"DELETE FROM students WHERE telegram_id = '{telegram_id}'")
    connection.commit()
  except Exception as e:
    print("Error in delete_student_by_telegramID: ", e)
  finally:
    connection.close()


# Delete Student By LeetCode Username
def delete_student_by_leetcode(username):
  status = 'ERROR'
  connection = sqlite3.connect("students")
  try:
    cursor = connection.cursor()
    cursor.execute(
      f"DELETE FROM students WHERE leetcode_username = '{username}'")
    connection.commit()
    status = 'SUCCESS'
  except Exception as e:
    print("Error in delete_student_by_leetcode: ", e)
  finally:
    connection.close()
    return status


# Sample Data for Testing
def sample_data():
  try:
    add_student(702008615, 'SE-2209', '2021-09-01', 'steve_jobs', 'Python', 2334, 50, 30, 20, 20, 100, 232592, 2345)
    add_student(702008616, 'SE-2209', '2021-09-01', 'elon_musk', 'C++', 2355, 50, 30, 20, 694, 100, 123409, 1800)
    add_student(702008617, 'SE-2209', '2021-09-01', 'bill_gates', 'C#', 1456, 50, 30, 20, 302, 100, 503324, 1645)
    add_student(702008618, 'SE-2209', '2021-09-01', 'mark_zuckerberg', 'Go', 2334, 50, 30, 212, 1000, 100, 2325922, 1700)
    add_student(702008619, 'SE-2209', '2021-09-01', 'jeff_bezos', 'Dart', 1234, 50, 30, 20, 140, 100, 232523, 1815)    
  except AlreadyExistError:
    print("Student data already exists in the database!")
  except DatabaseError:
    print("Something went wrong!")