####################################
# Project: AITU LeetCoder Bot      #
# Author: Arman Zhalgasbayev       #
# © 2023 - All Rights Reserved     #
####################################

# Importing Dependencies
import threading
import telebot
import datetime
import time
import json
from background import keep_alive
from constants import BOT_TOKEN, ADMIN_ID
from telebot import types
from database import *
from leetcode import *
from codeforces import *

create_table()
# sample_data()
print_students()
# update_student_rankings(save_plangs=False)

###########################
# Telegram - Bot Settings #
###########################

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)


# Welcome Message 'Start' command
@bot.message_handler(commands=['start'])
def welcome_message(message):
  bot.send_message(message.chat.id,
                   f'''👋 Привет, <b>{message.chat.first_name}</b>!\n
📢 Если вы студент Astana IT University (AITU) и хотите быть в рейтинге лучших литкодеров нашего университета, отправьте команду: <code>/push username group</code>\n
💬 <i><b>username</b> - ник в литкод, пример: silvermete0r</i>
💬 <i><b>group</b> - группа в AITU, пример: SE-2209</i>\n
📜 Подборка важнейших команд:\n
🔻 /mystats - для просмотра личной статистики (после регистрации);
🔻 <code>/stats username</code> - для того, чтобы просто чекнуть кого-то статистику на LeetCode;
🔻 /notify - для получения ежедневных задач от LeetCode;
🔻 /lucky - для получения счастливой задачи;
🔻 /experts - для получения помощи по задачам от экспертов AITU;
📊 Для просмотра рейтинга AITU: /standings
⚙️ Для вывода инструкции: /help\n
🙌 Поддержка: <code>supwithproject@gmail.com</code>''',
                   parse_mode='html')


# Instructions Message 'Help' command
@bot.message_handler(commands=['help'])
def instructions_message(message):
  bot.send_message(message.chat.id,
                   '''📜 Подборка важнейших команд:\n
🔻 /mystats - для просмотра личной статистики (после регитрации);
🔻 <code>/stats username</code> - для того, чтобы просто чекнуть кого-то статистику на LeetCode;
🔻 /notify - для получения ежедневных задач от LeetCode;
🔻 /lucky - для получения счастливой задачи;
🔻 /experts - для получения помощи по задачам от экспертов AITU;\n
📊 Для просмотра рейтинга AITU: /standings
⚙️ Для вывода инструкции: /help\n
🙌 Поддержка: <code>supwithproject@gmail.com</code>''',
                   parse_mode='html')


# Experts Connection 'Experts' command
@bot.message_handler(commands=['experts'])
def experts_message(message):
  bot.send_message(message.chat.id,
                   '''👨‍💻 Experts: <code>Kazakhstan LeetCode Community</code>\n
💬 LeetCode KZ Discussion: https://t.me/leetcodekz
💬 AITU LeetCode Chat: https://t.me/aitu_gdsc_leetcode_events
💬 AITU StackOverflow: https://t.me/+talhV-yKO1lkMjhi
🤖 ChatGPT: https://chat.openai.com\n
🙌 Поддержка: supwithproject@gmail.com''',
                   parse_mode='html',
                   disable_web_page_preview=True)


# About Message 'About' command
@bot.message_handler(commands=['about'])
def about_message(message):
  bot.send_message(message.chat.id,
                   '''👨‍💻 Author: <code>Arman Zhalgasbayev</code>\n
🕸 Telegram/Instagram: @silvermete0r
🕸 Github: https://github.com/silvermete0r
🕸 Linkedin: https://www.linkedin.com/in/arman-zhalgasbayev\n
🙌 Поддержка: supwithproject@gmail.com''',
                   parse_mode='html',
                   disable_web_page_preview=True)


# Special Feature: Admin Access 'Delete User' command
@bot.message_handler(commands=['delete_user'])
def delete_user(message):
  if str(message.from_user.id) == ADMIN_ID:
    data = message.text.split()
    if len(data) != 2:
      ans = "Something went Wrong! Please Try Again! [Length != 2]"
    else:
      if delete_student_by_leetcode(data[1]) == 'SUCCESS':
        ans = f"User <code>{data[1]}</code> has been Successfully Deleted!"
      else:
        ans = f"Something went wrong in the process of deleting user <code>{data[1]}</code>"

  bot.send_message(message.chat.id, ans, parse_mode='html')


# Difficulty Level Smiles
smiles = {'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴'}


# Random Problem 'Lucky' command
@bot.message_handler(commands=['lucky'])
def lucky_problem_message(message):
  msg = bot.send_message(message.chat.id, 'Подбираем вам задачу...')
  msg = msg.message_id
  problem_info = getLuckyLeetCodeProblem()
  reply = f"🍀 <b>{problem_info['title']}</b>\n\n"
  reply += f"{smiles[problem_info['difficulty']]} Difficulty: <b>{problem_info['difficulty']}</b>\n"
  reply += f"🔰 Topics: <b>{problem_info['topics']}</b>\n"
  reply += f"🔰 Acceptance Rate: <b>{problem_info['acRate']}</b>%\n\n"
  reply += problem_info['link']
  bot.reply_to(message, reply, parse_mode='html')
  bot.delete_message(message.chat.id, msg)


# LeetCode Daily Problem Sending Schedule 'Notify' command
@bot.message_handler(commands=['notify'])
def notify_daily_problem_message(message):
  state = ""
  if len(message.text.split()) == 2:
    state = message.text.split()[1]
  if state == "off":
    connection = sqlite3.connect("students")
    cursor = connection.cursor()
    try:
      cursor.execute(
        f"SELECT * FROM students WHERE telegram_id = {message.from_user.id};")
      connection.execute(
        f"UPDATE students SET message_chat_id = 0 WHERE telegram_id = {message.from_user.id};"
      )
    except Exception:
      bot.reply_to(message, "Извините, возникли проблемы с сервером.")
      return
    if cursor.fetchone() is None:
      bot.reply_to(
        message,
        "Извините, вы не зарегистрированы в базе рейтинга студентов AITU.")
      return

    reply = "Вы успешно отписались от ежедневной рассылки задач LeetCode!"
    bot.reply_to(message, reply, parse_mode='html')

    connection.commit()
    connection.close()
  else:
    connection = sqlite3.connect("students")
    cursor = connection.cursor()
    try:
      cursor.execute(
        f"SELECT * FROM students WHERE telegram_id = {message.from_user.id};")
      connection.execute(
        f"UPDATE students SET message_chat_id = {message.chat.id} WHERE telegram_id = {message.from_user.id};"
      )
    except Exception:
      bot.reply_to(message, "Извините, возникли проблемы с сервером.")
      return
    if cursor.fetchone() is None:
      bot.reply_to(
        message,
        "Извините, вы не зарегистрированы в базе рейтинга студентов AITU.")
      return
    reply = f"👏 Так держать {message.chat.first_name}!\n\n"
    reply += "🔰 Вы успешно подключились к ежедневным уведомлениям Daily LeetCode Problems.\n\n"
    reply += "⏰ Каждый день в 8:00 по времени Астаны, вы будете получать ежедневную задачу от LeetCode.\n"
    reply += "🏆 При стрике выполнении задач за 1 месяц вы будете получать официальный бейдж от LeetCode.\n\n"
    reply += "Желаю вам удачи 🍀\n\n"
    reply += "<i>Чтобы отписаться от ежедневных уведомлении отправьте команду:</i> <code>/notify off</code>\n"

    connection.commit()
    connection.close()
    bot.reply_to(message, reply, parse_mode='html')


# Daily Notification Sending
def send_daily_problem_notification():
  problem_info = getDailyLeetCodeProblem()
  daily_problem_info = f"🍀 <b>{problem_info['title']}</b>\n\n"
  daily_problem_info += f"{smiles[problem_info['difficulty']]} Difficulty: <b>{problem_info['difficulty']}</b>\n"
  daily_problem_info += f"🔰 Topics: <b>{problem_info['topics']}</b>\n"
  daily_problem_info += f"🔰 Acceptance Rate: <b>{problem_info['acRate']}</b>%\n\n"
  daily_problem_info += problem_info['link']
  connection = sqlite3.connect("students")
  try:
    result = connection.execute(
      "SELECT message_chat_id AS mcid FROM students WHERE mcid!=0;")
    subscribers = [row[0] for row in result.fetchall()]
  except Exception:
    print("Извините, возникли проблемы с сервером!")
    return
  finally:
    connection.close()
  for subscriber in subscribers:
    try:
      bot.send_message(subscriber, daily_problem_info, parse_mode='html')
    except Exception as e:
      print(f'User {subscriber}! Ошибка при отправке сообщения:', e)


# Register new student to the AITU students rankings 'Register' command
@bot.message_handler(commands=['push'])
def register_aitu_leetcoder(message):
  msg = bot.send_message(message.chat.id, 'Проверяем ваши данные...')
  msg = msg.message_id
  bot.send_chat_action(message.chat.id, 'typing')
  new_user = message.text.split()
  if len(new_user) != 3:
    bot.reply_to(message, "Извините, данные были введены неправильно.")
    bot.delete_message(message.chat.id, msg)
    return
  group = new_user[2].upper()
  group_data = group.split('-')
  if len(group_data) != 2:
    bot.reply_to(message,
                 "Извините, данные о группе были введены неправильно.")
    bot.delete_message(message.chat.id, msg)
    return
  if group_data[0] not in ('SE', 'MT', 'ST', 'CS', 'IT', 'ITM', 'ITE', 'MCS',
                           'BDA', 'DJ'):
    bot.reply_to(message,
                 f"Извините, но группы {group_data[0]} не существует.")
    bot.delete_message(message.chat.id, msg)
    return
  if not group_data[1].isnumeric():
    bot.reply_to(
      message,
      "Извините, но идентификатор группы должен содержать лишь цифры.")
    bot.delete_message(message.chat.id, msg)
    return
  if int(group_data[1][:2]) < 19 or int(
      group_data[1][:2]) > (datetime.date.today().year % 100):
    bot.reply_to(
      message,
      f"Извините, но идентификатора группы {group_data[1]} не существует.")
    bot.delete_message(message.chat.id, msg)
    return
  username = new_user[1]
  data = get_leetcode_user_stats(username)
  if data["status"] == "error":
    bot.reply_to(message, "Извините, этот пользователь не был найден.")
    bot.delete_message(message.chat.id, msg)
    return
  try:
    data['contest_ranking'] = get_contest_stats(username)['global_ranking']
    prog_lang = get_leetcode_user_planguages(username)
    add_student(int(message.from_user.id), group,
                str(datetime.date.today()), username, prog_lang, data['totalSolved'],
                data['easySolved'], data['mediumSolved'], data['hardSolved'],
                data['reputation'], data['contributionPoints'],
                data['ranking'], data['contest_ranking'])

  except AlreadyExistError:
    reply = "Ваши данные Telegram или Leetcode аккаунта уже присутствуют в базе!"

  except DatabaseError:
    reply = "Что-то пошло не так. Проблемы с сервером."

  else:
    reply = "Ваши данные были успешно загружены в общую базу студентов AITU! Чекнуть свою статистику: /mystats"

  bot.reply_to(message, reply, parse_mode='html')
  print(f'''
☑️ New student Successfully added to Database:
- Date: {datetime.date.today()};
- LeetCode: {username}; 
- Telegram: {str(message.from_user.username)};
- Edu Group: {group};
''')
  bot.delete_message(message.chat.id, msg)


# Inline Keyboard Callback Functions
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
  msg = None
  function_status, leetcode_username = call.data.split(" ", 1)
  try:
    if function_status == "get_contest_stats":
      msg = bot.send_message(call.message.chat.id, 'Загружаем данные...')
      msg = msg.message_id
      bot.send_chat_action(call.message.chat.id, 'typing')
      data = get_contest_stats(leetcode_username)

      if data["status"] == "error":
        bot.send_message(
          call.message.chat.id,
          f"У пользователя <b>{leetcode_username}</b> отсутствуют данные по контестам!",
          parse_mode='html')
        bot.delete_message(call.message.chat.id, msg)
        return

      contest_stats = f"🧗‍♂️ Статистика пользователя <b>{leetcode_username}</b>, по контестам в LeetCode!\n\n"
      contest_stats += f"🔰 Всего посещении контестов: <b>{data['attended_contests_count']}</b>\n"
      contest_stats += f"🔰 Пункты Рейтинга: <b>{round(data['rating'], 2)}</b>\n"
      contest_stats += f"🔰 Место в Мировом Рейтинге: <b>{data['global_ranking']}</b>\n"
      contest_stats += f"🔰 Всего участников контестов в мире: <b>{data['total_participants']}</b>\n\n"
      contest_stats += f"⭐ Лучший показатель по контесту: <b>TOP {data['top_percentage']}%</b>\n\n"

      bot.send_message(call.message.chat.id, contest_stats, parse_mode='html')
  except Exception as e:
    print(f'Error: {e}')
  finally:
    if msg:
      bot.delete_message(call.message.chat.id, msg)


# Show stats 'My-Stats' command
@bot.message_handler(commands=['mystats'])
def get_mystats(message):
  msg = bot.send_message(message.chat.id, 'Загружаем ваши данные...')
  msg = msg.message_id
  bot.send_chat_action(message.chat.id, 'typing')
  connection = sqlite3.connect("students")
  try:
    result = connection.execute(
      f"SELECT * FROM students WHERE telegram_id = {message.from_user.id};")
    student_data = result.fetchone()
    if student_data[0] != 1:
      closest_opponent = connection.execute(
        f"SELECT * FROM students WHERE aitu_rank = {student_data[0]} - 1;")
      closest_opponent_data = closest_opponent.fetchone()
  except Exception:
    bot.reply_to(
      message,
      "Извините, вы не зарегистрированы в базе рейтинга студентов AITU.")
    bot.delete_message(message.chat.id, msg)
    return
  connection.commit()
  connection.close()

  aituRating, leetcode_username = student_data[0], student_data[5]
  data = get_leetcode_user_stats(leetcode_username)
  if data["status"] == "error":
    bot.reply_to(message, "Извините, этот пользователь не был найден.")
    bot.delete_message(message.chat.id, msg)
    return
  update_student(leetcode_username)

  keyboard = types.InlineKeyboardMarkup()
  user_contest_stats_button = telebot.types.InlineKeyboardButton(
    text="Contest Stats",
    callback_data="get_contest_stats " + leetcode_username)

  keyboard.add(user_contest_stats_button)

  goal = ((data['totalSolved'] // 100) + 1) * 100
  neededGoal = goal - data['totalSolved']
  reply = f"👨🏻‍💻 Держите, {message.from_user.first_name} -> статистика для пользователя: <b>{leetcode_username}</b>\n\n"
  reply += f"🔰 Предпочитаемый язык программирования: <b>{get_leetcode_user_planguages(leetcode_username)}</b> \n"
  reply += f"🔰 Общее количество решенных задач: <b>{data['totalSolved']}</b> \n"
  reply += f"🔰 Вам осталось решить всего <b>{neededGoal}</b> задач чтобы дойти до <b>{goal}</b> решенных задач и подняться в рейтинге!\n\n"

  reply += f"🟢 Легкие задачи: <b>{data['easySolved']} / {data['totalEasy']} ({round((data['easySolved'] / data['totalEasy'])*100, 2)}%)</b>\n"
  reply += f"🟡 Средние задачи: <b>{data['mediumSolved']} / {data['totalMedium']} ({round((data['mediumSolved'] / data['totalMedium'])*100, 2)}%)</b>\n"
  reply += f"🔴 Сложные задачи: <b>{data['hardSolved']} / {data['totalHard']} ({round((data['hardSolved'] / data['totalHard'])*100, 2)}%)</b>\n\n"
  reply += f"🔰 Репутация в LeetCode, по количеству upvotes: <b>{data['reputation']} ⬆️</b>\n"
  reply += f"🔰 Количество заработанных LeetCoin-ов: <b>{data['contributionPoints']} 💰</b>\n\n"
  reply += f"📈 Место в мировом рейтинге LeetCode: <b>{data['ranking']}</b>\n"
  reply += f"📊 Место в рейтинге студентов AITU: <b>{aituRating}</b>\n\n"
  if aituRating == 1:
    reply += f"🔰 Абсолютная доминация, поздравляем <code>{leetcode_username}</code>, вы король рейтинга студентов AITU 👑\n\n"
  elif aituRating == 2:
    reply += f"🔰 Вы второй сильнейший литкодер AITU, поздравляем <code>{leetcode_username}</code>, чтобы возглавить рейтинг лучших литкодеров вам нужно подняться на <b>{abs(data['ranking'] - closest_opponent_data[12])}</b> пунктов рейтинга!\n"
  elif aituRating == 3:
    reply += f"🔰 Вы третий сильнейший литкодер AITU, чтобы добраться до серебра вам необходимо подняться на <b>{abs(data['ranking'] - closest_opponent_data[12])}</b> пунктов рейтинга!\n"
  else:
    reply += f"🔰 Чтобы обогнать ближайшего участника <code>{closest_opponent_data[5]}</code> в рейтинге AITU, вам нужно подняться всего лишь на <b>{abs(data['ranking'] - closest_opponent_data[12])}</b> пунктов рейтинга!\n"
  reply += "🔰 Топ 3 лучших литкодеров: /top3\n\n"
  bot.reply_to(message, reply, parse_mode='html', reply_markup=keyboard)
  bot.delete_message(message.chat.id, msg)


# Show AITU LeetCode Rankings
@bot.message_handler(commands=['standings'])
def aitu_leetcode_rankings(message):
  keyboard = types.InlineKeyboardMarkup()
  ratings_button = types.InlineKeyboardButton(text="AITU-Ratings",
                                              url="https://b2a.kz/rkO")

  keyboard.add(ratings_button)

  msg = bot.send_message(message.chat.id, 'Загружаем рейтинг студентов...')
  msg = msg.message_id
  bot.send_chat_action(message.chat.id, 'typing')

  bot.send_message(message.chat.id,
                   f'📈 Нажмите, чтобы увидеть live-рейтинг студентов AITU:',
                   reply_markup=keyboard)
  bot.delete_message(message.chat.id, msg)


# Show stats 'Stats' command
@bot.message_handler(commands=['stats'])
def get_stats(message):
  msg = bot.send_message(message.chat.id, 'Загружаем данные пользователя...')
  msg = msg.message_id
  bot.send_chat_action(message.chat.id, 'typing')
  text = message.text.split()
  if len(text) != 2:
    bot.reply_to(message, "Извините, произошла ошибка.")
    bot.delete_message(message.chat.id, msg)
    return
  username = text[1]
  data = get_leetcode_user_stats(username)
  if data["status"] == "error":
    bot.reply_to(message, "Извините, этот пользователь не был найден.")
    bot.delete_message(message.chat.id, msg)
    return

  keyboard = types.InlineKeyboardMarkup()
  user_contest_stats_button = telebot.types.InlineKeyboardButton(
    text="Contest Stats", callback_data="get_contest_stats " + username)

  keyboard.add(user_contest_stats_button)

  reply = f"👨🏻‍💻 Держите, {message.from_user.first_name} -> статистика для пользователя: <b>{username}</b>\n\n"
  reply += f"🔰 Предпочитаемый язык программирования: <b>{get_leetcode_user_planguages(username)}</b> \n"
  reply += f"🔰 Общее количество решенных задач: <b>{data['totalSolved']}</b> \n"
  reply += f"🟢 Легкие задачи: <b>{data['easySolved']} / {data['totalEasy']} ({round((data['easySolved'] / data['totalEasy'])*100, 2)}%)</b>\n"
  reply += f"🟡 Средние задачи: <b>{data['mediumSolved']} / {data['totalMedium']} ({round((data['mediumSolved'] / data['totalMedium'])*100, 2)}%)</b>\n"
  reply += f"🔴 Сложные задачи: <b>{data['hardSolved']} / {data['totalHard']} ({round((data['hardSolved'] / data['totalHard'])*100, 2)}%)</b>\n\n"
  reply += f"🔰 Репутация в LeetCode, по количеству upvotes: <b>{data['reputation']} ⬆️</b>\n"
  reply += f"🔰 Количество заработанных LeetCoin-ов: <b>{data['contributionPoints']} 💰</b>\n\n"
  reply += f"📈 Место в мировом рейтинге LeetCode: <b>{data['ranking']}</b>\n"
  bot.reply_to(message, reply, parse_mode='html', reply_markup=keyboard)
  bot.delete_message(message.chat.id, msg)


# Show stats 'Top-3' command
@bot.message_handler(commands=['top3'])
def get_top3(message):
  connection = sqlite3.connect("students")
  result = connection.execute(
    "SELECT leetcode_username, aitu_ranking FROM students ORDER BY aitu_rank ASC LIMIT 3;"
  )
  top = result.fetchall()
  connection.commit()
  connection.close()
  if len(top) < 3:
    reply = "💬 Извините, количество зарегистрированных пользователей меньше 3 человек, поэтому ТОП-3 еще не составлен."
  else:
    reply = "🔰 ТОП-3 лучших 🔥\n\n"
    reply += f"🥇 <code>{top[0][0]}</code>, AITU Score: <b>{top[0][1]}</b>\n"
    reply += f"🥈 <code>{top[1][0]}</code>, AITU Score: <b>{top[1][1]}</b>\n"
    reply += f"🥉 <code>{top[2][0]}</code>, AITU Score: <b>{top[2][1]}</b>\n\n"
  bot.reply_to(message, reply, parse_mode='html')


# Feature: Checking Codeforces user info
@bot.message_handler(commands=['codeforces'])
def get_codeforces_user_info(message):
  msg = bot.send_message(message.chat.id, 'Загружаем данные пользователя...')
  msg = msg.message_id
  bot.send_chat_action(message.chat.id, 'typing')
  lst = message.text.split()
  if len(lst) != 2:
    bot.reply_to(message, "Извините, данные были введены неправильно.")
    bot.delete_message(message.chat.id, msg)
    return
  codeforces_handle = lst[1]
  user_info = get_codeforces_user(codeforces_handle)
  if user_info["status"] == "OK":
    user_info = user_info['result'][0]
    days_in_codeforces = convert_seconds_to_days(
      int(user_info['registrationTimeSeconds']))
    fullname = user_info['firstName'] + " " + user_info[
      'lastName'] if 'firstName' in user_info and 'lastName' in user_info else 'Не указано'
    rank_info = f"{user_info['rank']} (max: {user_info['maxRank']})" if 'rank' in user_info and 'maxRank' in user_info else 'Не в рейтинге'
    rating_info = f"{user_info['rating']} (max: {user_info['maxRating']})" if 'rating' in user_info and 'maxRating' in user_info else 'Не в рейтинге'
    if 'organization' in user_info and user_info['organization'] != '':
      organization_info = user_info['organization']
    else:
      organization_info = 'Не состоит'
    reply = f"👨🏻‍💻 Держите, {message.from_user.first_name} -> статистика для пользователя: <b>{codeforces_handle}</b>\n\n"
    reply += f"🔰 ФИО: <b>{fullname}</b>\n"
    reply += f"🔰 Ранг: <b>{rank_info}</b>\n"
    reply += f"🔰 Организация: <b>{organization_info}</b>\n\n"
    reply += f"⭐️ Рейтинг: <b>{rating_info}</b>\n"
    reply += f"🏔️ Вклад: <b>{user_info['contribution']}</b>\n"
    reply += f"👐 Количество друзей: <b>{user_info['friendOfCount']}</b>\n"
    reply += f"👽 В Codeforces уже <b>{days_in_codeforces}</b> дней.\n\n"
    reply += f"🔗 Ссылка на профиль: <code><a href='https://codeforces.com/profile/{codeforces_handle}'>{codeforces_handle}</a></code>"
    bot.delete_message(message.chat.id, msg)
    bot.reply_to(message, reply, parse_mode='html')
    return
  else:
    bot.reply_to(
      message,
      f"Извините, пользователя под ником {codeforces_handle} не существует!")
    bot.delete_message(message.chat.id, msg)
    return


# Secret Command: 'myNewLeetcode' for changing leetcode username
@bot.message_handler(commands=['myNewLeetcode'])
def get_my_new_leetcode_username(message):
  msg = bot.send_message(message.chat.id, 'Проверяем ваши данные...')
  msg = msg.message_id
  bot.send_chat_action(message.chat.id, 'typing')
  text = message.text.split()
  if len(text) != 2:
    bot.reply_to(message, "Извините, данные были введены неравильно.")
    bot.delete_message(message.chat.id, msg)
    return
  username = text[1]
  data = get_leetcode_user_stats(username)
  if data["status"] == "error":
    bot.reply_to(message, "Извините, этот пользователь не был найден.")
    bot.delete_message(message.chat.id, msg)
    return
  status = update_student_leetcode_username_by_telegram_id(
    message.from_user.id, username)
  if status == 'ERROR':
    bot.reply_to(message, "Извините, что-то пошло не так.")
    bot.delete_message(message.chat.id, msg)
    return
  bot.reply_to(
    message,
    f"Ваше имя пользователя в LeetCode был успешно обновлен на <code>{username}</code>.",
    parse_mode='html')
  bot.delete_message(message.chat.id, msg)


# Secret Command: 'myGroup' for changing information about edu group
@bot.message_handler(commands=['myGroup'])
def get_myGroup(message):
  msg = bot.send_message(message.chat.id, 'Проверяем ваши данные...')
  msg = msg.message_id
  bot.send_chat_action(message.chat.id, 'typing')
  group = message.text.split()
  if len(group) != 2:
    bot.reply_to(message, "Извините, данные были введены неправильно.")
    bot.delete_message(message.chat.id, msg)
    return
  edu_group = group[1].upper()
  group_data = edu_group.split('-')
  if len(group_data) != 2:
    bot.reply_to(message,
                 "Извините, данные о группе были введены неправильно.")
    bot.delete_message(message.chat.id, msg)
    return
  if group_data[0] not in ('SE', 'MT', 'ST', 'CS', 'IT', 'ITM', 'ITE', 'MCS',
                           'BDA', 'DJ'):
    bot.reply_to(message,
                 f"Извините, но группы {group_data[0]} не существует.")
    bot.delete_message(message.chat.id, msg)
    return
  if not group_data[1].isnumeric():
    bot.reply_to(
      message,
      "Извините, но идентификатор группы должен содержать лишь цифры.")
    bot.delete_message(message.chat.id, msg)
    return
  if int(group_data[1][:2]) < 19 or int(
      group_data[1][:2]) > (datetime.date.today().year % 100):
    bot.reply_to(
      message,
      f"Извините, но идентификатора группы {group_data[1]} не существует.")
    bot.delete_message(message.chat.id, msg)
    return

  connection = sqlite3.connect("students")
  try:
    result = connection.execute(
      f"SELECT * FROM students WHERE telegram_id = {message.from_user.id};")
    fetched_data = result.fetchone()
  except Exception:
    bot.reply_to(
      message,
      "Извините, вы не зарегистрированы в базе рейтинга студентов AITU.")
    bot.delete_message(message.chat.id, msg)
    return
  connection.commit()
  connection.close()

  old_edu_group = fetched_data[3]
  if old_edu_group == edu_group:
    bot.reply_to(
      message,
      f"Извините, но ваша образовательная группа в системе и есть: <code>{edu_group}</code>.",
      parse_mode='html')
    bot.delete_message(message.chat.id, msg)
    return
  update_student_edu_group_by_telegramID(message.from_user.id, edu_group)
  bot.reply_to(
    message,
    f"Ваша образовательная группа была успешно обновлена с <code>{old_edu_group}</code> на <code>{edu_group}</code>.",
    parse_mode='html')
  bot.delete_message(message.chat.id, msg)


# Unknown Messages Handling '???' command
@bot.message_handler(func=lambda message: True)
def handle_unknown_message(message):
  msg = f'💬 Извините, <b>{message.chat.first_name}</b>. Я вас не понимаю.\n\n'
  msg += '💁 Помощь: /help'
  bot.send_message(message.chat.id, msg, parse_mode='html')


# Set the time for the daily notification (in 24-hour format)
notification_time = "02:00"

# Remove Webhook & Keeping Bot Alive on the Server
bot.remove_webhook()
keep_alive()

# Define the function that starts the bot polling in a separate thread
def start_polling():
  bot.polling()

# Start the bot polling in a separate thread
polling_thread = threading.Thread(target=start_polling)
polling_thread.start()

# Send Daily Notification
while True:
  now = datetime.datetime.now().time().strftime('%H:%M')
  if now == notification_time:
    update_student_rankings(save_plangs=False)
    send_daily_problem_notification()
    time.sleep(86400)
  else:
    time.sleep(1)