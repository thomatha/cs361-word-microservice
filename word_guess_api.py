""" Word Guessing Microservice API
using HTTP GET url & parameter: url/?guess=GUESSWORD
Picks a new word each day.
Compare guess word to hidden daily word. 
Check if guess word is in the list.
For each letter give hints: 
(1) grey = not in word at all
(2) gold = in wrong spot
(3) green = in right spot
"""


import random
from datetime import date
from flask import Flask, jsonify, request
from words import get_words_list
from github import Github
import os

app = Flask(__name__)


def get_word():
    """ returns the randomly selected daily word """

    words = get_words_list()
    size = len(words)
    number = random.randint(0, 10000)
    today = str(date.today())

    # convert random number that is > size of words list
    if number > size:
        number = number % size

    # daily word stored in github repo
    github_api = Github(os.getenv('WORD_TOKEN'))
    repository = github_api.get_user().get_repo('cs361-word-microservice')

    # read file for daily word
    file = repository.get_contents('daily_word.txt')
    content = file.decoded_content.decode()

    # convert string to list
    content = content.split('\n')
    daily_word = content[0].strip()
    day = content[1]

    # if new day, write new word and date to file
    if day != today:
        daily_word = words[number]
        repository.update_file('daily_word.txt', 'update word', daily_word + '\n' + today, file.sha)
    
    return daily_word


def word_in_list(guess_word):
    """ returns True if guess word is in the list, else False """

    words_list = get_words_list()
    if guess_word in words_list:
        return True
    else:
        return False


def get_hints(guess_word, daily_word):
    """ compares guess word to daily word
    for each letter returns hint: not-in, not-in-position, in-position """

    secret_letters = list(daily_word)
    guess_letters = list(guess_word)

    hints = dict(word=guess_word, letters=[
                                dict(letter=guess_letters[0], hint=''), 
                                dict(letter=guess_letters[1], hint=''), 
                                dict(letter=guess_letters[2], hint=''), 
                                dict(letter=guess_letters[3], hint=''), 
                                dict(letter=guess_letters[4], hint='')])

    for index, letter in enumerate(guess_letters):
        if letter not in secret_letters:
            hints['letters'][index]['hint'] = 'not-in'
        else:
            if letter == secret_letters[index]:
                hints['letters'][index]['hint'] = 'in-position'
            else:
                hints['letters'][index]['hint'] = 'not-in-position'

    return jsonify(hints)


# allows web app to make cross origin requests
@app.after_request
def cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# root route
@app.route('/')
def get():
    """ HTTP GET API endpoint & parameter: url/?guess=GUESSWORD 
    returns error or hints """

    guess_word = request.args.get('guess').upper()

    if not word_in_list(guess_word):
        error = dict(error='Word not in list.')
        return jsonify(error)
    
    return get_hints(guess_word, get_word())




if __name__ == '__main__':
    app.run(debug=False)