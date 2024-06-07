from flask import Flask, jsonify
from flask import render_template
from threading import Thread
import requests
import sqlite3
import json

########################
# Database -  Settings #
########################

# Get HTML Classes by Programming Language
def get_language_style(langx):
  plang = 'devicon-debian-plain red-color'
  if langx == 'C++':
    plang = 'devicon-cplusplus-plain blue-color'
  elif langx == 'Python3' or langx == 'Python':
    plang = 'devicon-python-plain purple-color'
  elif langx == 'Java':
    plang = 'devicon-java-plain orange-color'
  elif langx == 'C':
    plang = 'devicon-c-plain blue-color'
  elif langx == 'C#':
    plang = 'devicon-csharp-plain green-color'
  elif langx == 'Go':
    plang = 'devicon-go-original-wordmark blue-color'
  elif langx == 'PHP':
    plang = 'devicon-php-plain purple-color'
  elif langx == 'JavaScript':
    plang = 'devicon-javascript-plain orange-color'
  elif langx == 'Kotlin':
    plang = 'devicon-kotlin-plain purple-color'
  elif langx == 'Ruby':
    plang = 'devicon-ruby-plain red-color'
  elif langx == 'Swift':
    plang = 'devicon-swift-plain orange-color'
  elif langx == 'Scala':
    plang = 'devicon-scala-plain red-color'
  elif langx == 'Rust':
    plang = 'devicon-rust-plain red-color'
  elif langx == 'TypeScript':
    plang = 'devicon-typescript-plain blue-color'
  elif langx == 'R':
    plang = 'devicon-r-plain blue-color'
  elif langx == 'Dart':
    plang = 'devicon-dart-plain blue-color'
  return plang


# Getting Students Data
def get_students():
  connection = sqlite3.connect("students")
  try:
    cursor_object = connection.execute(
      "SELECT aitu_rank, aitu_ranking, leetcode_username, edu_group, prog_lang, total_problems, easy_tasks, medium_tasks, hard_tasks, reputation, leetcoins, global_ranking, contest_ranking FROM students"
    )
    rows = cursor_object.fetchall()
    ratings = dict()
    for row in rows:
      student = dict()
      student['aitu_rank'] = row[0]
      student['aitu_ranking'] = row[1]
      student['leetcode_nickname'] = row[2]
      student['educational_group'] = row[3]
      student['plang'] = get_language_style(row[4])
      student['total_solved_problems'] = row[5]
      student['easy_problems'] = row[6]
      student['medium_problems'] = row[7]
      student['hard_problems'] = row[8]
      student['reputation_upvotes'] = row[9]
      student['leetcoins'] = row[10]
      student['global_ranking'] = row[11]
      student['contest_ranking'] = row[12]
      ratings[f'student-{row[0]}'] = student
    connection.commit()
  except Exception as e:
    print("Error", e)
  finally:
    connection.close()
    return ratings


########################
# Flask App - Settings #
########################

app = Flask(__name__)


@app.route('/')
def home():
  return render_template('index.html', ratings=get_students())

@app.route('/users')
def get_table():
  return jsonify(get_students())

@app.route('/user/<id>')
def get_user(id):
  try:
    return jsonify(get_students()[f'student-{id}'])
  except:
    return jsonify({"message": "error-404"})

def run():
  app.run(port=8080, debug=False)


def keep_alive():
  t = Thread(target=run)
  t.start()

if __name__ == "__main__":
  keep_alive()
  print("Server is running...")