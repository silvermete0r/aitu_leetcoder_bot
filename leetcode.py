import requests
import random

######################
# GraphQL - Settings #
######################

# url = "https://leetcode.com/problems/random-one-question/all"
# all_problems = "https://leetcode.com/api/problems/all"
# graphql = "https://leetcode.com/graphql"

# Getting Daily LeetCode Problem for Daily Notifications
def getDailyLeetCodeProblem():
  try:
    query = '''
        query questionOfToday {
          activeDailyCodingChallengeQuestion {
            date
            userStatus
            link
            question {
              acRate
              difficulty
              freqBar
              frontendQuestionId: questionFrontendId
              isFavor
              isPaidOnly
              status
              title
              titleSlug
              hasVideoSolution
              hasSolution
              topicTags {
                name
                id
                slug
              }
            }
          }
        }
    '''
    res = requests.post('https://leetcode.com/graphql',
                        json={'query': query})
    data = res.json()
    link = 'https://leetcode.com' + data['data'][
      'activeDailyCodingChallengeQuestion']['link']
    data = data['data']['activeDailyCodingChallengeQuestion']['question']
    title = data['title']
    difficulty = data['difficulty']
    successRate = round(data['acRate'], 1)
    topics = data['topicTags']
    tags = topics[0]['name']
    for i in range(1, len(topics)):
      tags += ', ' + topics[i]['name']
    problem_dict = {
      'title': title,
      'difficulty': difficulty,
      'acRate': successRate,
      'topics': tags,
      'link': link
    }
    return problem_dict
  except Exception as e:
    print("Error in getDailyLeetCodeProblem: ", e)
    problem_dict = {
      'title': 'Two Sum',
      'difficulty': 'Easy',
      'acRate': '50.9',
      'topics': 'Array, Hash Table',
      'link': 'https://leetcode.com/problems/two-sum/description/'
    }
    return problem_dict


# Getting Random (Lucky) LeetCode Problem
def getLuckyLeetCodeProblem():
  try:
    query = '''
      query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
          categorySlug: $categorySlug
          limit: $limit
          skip: $skip
          filters: $filters
        ) {
          total: totalNum
          questions: data {
            acRate
            difficulty
            freqBar
            frontendQuestionId: questionFrontendId
            isFavor
            paidOnly: isPaidOnly
            status
            title
            titleSlug
            topicTags {
              name
              id
              slug
            }
          }
        }
      }
    '''
    skip_val = random.randint(0, 3000)
    variables = {"categorySlug": "", "skip": skip_val, "limit": 1, "filters": {}}
    response = requests.post('https://leetcode.com/graphql',
                              json={
                                'query': query,
                                'variables': variables
                              })
    data = response.json()['data']['problemsetQuestionList']['questions'][0]
    title = data['title']
    difficulty = data['difficulty']
    successRate = round(data['acRate'], 1)
    topics = data['topicTags']
    tags = topics[0]['name']
    for i in range(1, len(topics)):
      tags += ', ' + topics[i]['name']
    problem_dict = {
      'title': title,
      'difficulty': difficulty,
      'acRate': successRate,
      'topics': tags,
      'link': 'https://leetcode.com/problems/' + data['titleSlug']
    }
  except Exception as e:
    print("Error in getLuckyLeetCodeProblem: ", e)
    problem_dict = {
      'title': 'Two Sum',
      'difficulty': 'Easy',
      'acRate': '50.9',
      'topics': 'Array, Hash Table',
      'link': 'https://leetcode.com/problems/two-sum/description/'
    }
  finally:
    return problem_dict


# Get LeetCode Problem Details by ID
def get_leetcode_problem_details(problem_id):
  try: 
    query = '''
        query getQuestionDetail($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
            questionFrontendId
            title
            titleSlug
            content
            difficulty
            acRate
            similarQuestions
            sampleTestCase
            metaData
            stats
            hints
            topicTags {
              name
              id
              slug
            }
          }
        }
    '''
    variables = {'titleSlug': problem_id}
    response = requests.post('https://leetcode.com/graphql',
                             json={
                               'query': query,
                               'variables': variables
                             })
    problem_data = response.json()['data']['question']
    title = problem_data['title']
    difficulty = problem_data['difficulty']
    successRate = round(problem_data['acRate'], 1)
    topics = problem_data['topicTags']
    tags = ""
    if len(topics) != 0:
      tags += topics[0]['name']
      for i in range(1, len(topics)):
        tags += ', ' + topics[i]['name']
    else:
      tags = "General"
    problem_url = 'https://leetcode.com/problems/' + problem_id
    problem_dict = {
      'title': title,
      'difficulty': difficulty,
      'acRate': successRate,
      'topics': tags,
      'link': problem_url
    }
  except Exception as e:
    print("Error in get_leetcode_problem_details: ", e)
    problem_dict = {
      'title': 'Two Sum',
      'difficulty': 'Easy',
      'acRate': '50.9',
      'topics': 'Array, Hash Table',
      'link': 'https://leetcode.com/problems/two-sum/description/'
    }
  finally:
    return problem_dict


# Get Students LeetCode General Statistics
def get_leetcode_user_stats(username):
  data = {"status": "error"}
  try:
    url = 'https://leetcode.com/graphql'
    query = """
        query getUserStats($username: String!) {
          allQuestionsCount {
            difficulty
            count
          }
          matchedUser(username: $username) {
            username
            profile {
              reputation
              ranking
            }
            contributions {
              points
            }
            submitStatsGlobal {
              acSubmissionNum {
                difficulty
                count
              }
            }
          }
        }
      """
    variables = {"username": username}
    response = requests.post(url,
                             json={
                               "query": query,
                               "variables": variables
                             })
    if response.json().get(
        "errors") is not None or response.status_code != 200:
      return {"status": "error"}
    data = response.json()["data"]
    total_solved = data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"][
      0]["count"]
    total_questions = data["allQuestionsCount"][0]["count"]
    easy_solved = data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"][
      1]["count"]
    total_easy = data["allQuestionsCount"][1]["count"]
    medium_solved = data["matchedUser"]["submitStatsGlobal"][
      "acSubmissionNum"][2]["count"]
    total_medium = data["allQuestionsCount"][2]["count"]
    hard_solved = data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"][
      3]["count"]
    total_hard = data["allQuestionsCount"][3]["count"]
    ranking = data["matchedUser"]["profile"]["ranking"]
    contribution_points = data["matchedUser"]["contributions"]["points"]
    reputation = data["matchedUser"]["profile"]["reputation"]
    data = {
      "status": "success",
      "totalSolved": total_solved,
      "totalQuestions": total_questions,
      "easySolved": easy_solved,
      "totalEasy": total_easy,
      "mediumSolved": medium_solved,
      "totalMedium": total_medium,
      "hardSolved": hard_solved,
      "totalHard": total_hard,
      "ranking": ranking,
      "contributionPoints": contribution_points,
      "reputation": reputation
    }
  except Exception as e:
    print("Error in get_leetcode_user_stats: ", e)
  finally:
    return data


# Get Students Contest Statistics
def get_contest_stats(username):
  try:
    url = 'https://leetcode.com/graphql'
    headers = {'Content-Type': 'application/json'}
    query = '''
    query GetUserContestRanking($username: String!) {
      userContestRanking(username: $username) {
        attendedContestsCount
        rating
        globalRanking
        totalParticipants
        topPercentage    
      }
    }
    '''
    variables = {'username': username}
    response = requests.post(url,
                             json={
                               'query': query,
                               'variables': variables
                             },
                             headers=headers)
    if response.json().get(
        "errors") is not None or response.status_code != 200:
      return {"status": "error"}
    data = response.json()
    contest_stats = data['data']['userContestRanking']
    if contest_stats is None:
      return_data = {'status': 'error', 'global_ranking': 300000}
    else:
      return_data = {
        'status': 'success',
        'attended_contests_count': contest_stats['attendedContestsCount'],
        'rating': contest_stats['rating'],
        'global_ranking': contest_stats['globalRanking'],
        'total_participants': contest_stats['totalParticipants'],
        'top_percentage': contest_stats['topPercentage']
      }
  except Exception as e:
    print("Error in get_contest_stats: ", e)
    return_data = {'status': 'error'}
  finally:
    return return_data
  
# Get Programming Languages Stats by LeetCode username
def get_leetcode_user_planguages(username):
  url = 'https://leetcode.com/graphql'
  query = """
      query languageStats($username: String!) {
      matchedUser(username: $username) {
          languageProblemCount {
          languageName
          problemsSolved
          }
      }
      }
      """
  variables = {"username": username}
  response = requests.post(url, json={"query": query, "variables": variables})
  try:
    if response.json().get(
        "errors") is not None or response.status_code != 200:
      return 'Not Found'
    data = response.json()["data"]["matchedUser"]["languageProblemCount"]
    return max(data, key=lambda x: x['problemsSolved'])['languageName'].strip()
  except Exception as e:
    print(f'Error in get_leetcode_user_planguages: {str(e)}')
    return 'Not Found'
  
if __name__ == "__main__":
  # print(get_contest_stats('silvermete0r'))
  # print(getDailyLeetCodeProblem())
  print(getLuckyLeetCodeProblem())
    