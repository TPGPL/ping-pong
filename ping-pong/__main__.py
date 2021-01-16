# IMPORTS

import io
import os
import random
import string

from pyfiglet import Figlet

from defaults import *
from score import Score


# UTILITY FUNCTIONS

def draw_logo():
    logo = Figlet(font="slant")
    os.system("cls" if os.name == "nt" else "clear")
    print(logo.renderText("Ping Pong"))


def check_repetitions(checked_rule, rule_list):
    for rule in rule_list:
        if rule.number == checked_rule.number and rule.kind == checked_rule.kind:
            return True

    return False


def check_number(number, rule_list):
    number_replacement = ""

    for rule in rule_list:
        if (rule.kind == "REPLACEMENT" and int(rule.number) != number) or (rule.kind == "DIVISION" and number % int(rule.number) != 0):
            continue
        else:
            if rule.kind == "REPLACEMENT":
                number_replacement = rule.replacement
                break
            else:
                if number_replacement == "":
                    number_replacement = rule.replacement
                else:
                    number_replacement = number_replacement + " " + rule.replacement

    if number_replacement == "":
        return str(number)
    else:
        return number_replacement


def set_life_count(game_difficulty):
    return default_life_count_easy if game_difficulty == "E" else default_life_count_medium if game_difficulty == "M" else default_life_count_hard


def fetch_ranking(game_difficulty):
    ranking = []

    with io.open(f"assets/ranking-{game_difficulty}.txt", mode="r", encoding="utf-8") as file:
        for line in file.read().splitlines():
            var = line.split()

            ranking.append(Score(int(var[0]), var[1]))

    return ranking


def save_ranking(ranking, game_difficulty):
    ranking.sort(reverse=True, key=lambda x: x.score)

    with io.open(f"assets/ranking-{game_difficulty}.txt", mode="w+", encoding="utf-8") as file:
        for score in ranking:
            file.write(f"{score.score} {score.player_name}\n")


def confirmation():
    draw_logo()
    while True:
        choice = input("Are you sure you want to continue? This action is irreversible. (Y/N)\n").lower()

        if choice == "yes" or choice == "y":
            return True
        elif choice == "no" or choice == "n":
            return False
        else:
            draw_logo()
            print("Wrong choice - try again.")


def check_rankings(difficulties):
    errors_found = False

    for ranking_type in difficulties:
        error_found = False
        file_location = f"assets/ranking-{ranking_type}.txt"
        file_size = os.path.getsize(file_location)

        if file_size == 0:
            continue

        with io.open(file_location, mode="r+", encoding="utf-8") as file:
            file_contents = file.read().splitlines()

            line_array = [line.split() for line in file_contents]

            for score in line_array:
                if len(score) != 2:  # check if there are less or more values in a line than 2
                    error_found = True
                    errors_found = True
                    break
                else:
                    pass

                try:  # check if the score is actually an int and not negative
                    test_score = int(score[0])
                    if test_score < 0:
                        raise ValueError
                except ValueError:
                    error_found = True
                    errors_found = True
                    break

            test_ranking = []

            for line in file_contents:
                if error_found:
                    break

                var = line.split()

                test_ranking.append(Score(int(var[0]), var[1]))

            test_sorted_ranking = test_ranking.copy()
            test_sorted_ranking.sort(reverse=True, key=lambda x: x.score)

            if test_ranking != test_sorted_ranking:
                error_found = True
                errors_found = True

            if error_found:
                print(f"There were errors found in the \"{file_location}\" file. In order to prevent incoming errors in the app, the file will be erased.")
                file.truncate(0)

    if errors_found:
        print("Click any key to continue...")
        input()


def fetch_words(game_difficulty):
    with io.open(f"assets/words-{game_difficulty}.txt", mode="r", encoding="utf-8") as file:
        word_array = [line for line in file.read().splitlines()]

    return word_array


def check_chance(number):
    number_array = [i for i in range(1, 21)]

    random_number = random.randint(1, 20)

    chance_decreaser = 10 if number // 10 > 10 else number // 10  # decrease the chance of a correct answer by 5% per 10 numbers (max -50%)

    for i in range(chance_decreaser):
        number_array.pop(len(number_array) - 1)

    if random_number in number_array:
        return True
    else:
        return False


def generate_answer():
    alphabet = string.ascii_letters
    answer = ""

    for i in range(8):
        answer += random.choice(alphabet)

    return answer


def get_words(game_difficulty):
    return words_E if game_difficulty == "E" else words_M if game_difficulty == "M" else words_H


# MODULE START

round_count = default_round_count
rules = default_rules.copy()
tour_time = default_tour_time
difficulty = default_difficulty
tour_interval = default_tour_interval
show_rules = default_show_rules
words_E = fetch_words("E")
words_M = fetch_words("M")
words_H = fetch_words("H")


def main():
    check_rankings(["E", "M", "H"])
    # main_menu() # TODO


if __name__ == "__main__":
    main()
