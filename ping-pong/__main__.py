# IMPORTS

import io
import os
import random
import string
import time

from pyfiglet import Figlet

from .defaults import *
from .player import Player
from .rule import Rule
from .score import Score


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
        print("Press a key to continue...")
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


# ROZGRYWKA

def solo_game():
    global rules
    life_count = set_life_count(difficulty)
    score = 0
    number_counter = 1

    while True:
        wrong_input = False
        correct_answer = check_number(number_counter, rules)
        draw_logo()

        start_time = time.time()
        player_input = input("Enter the expression: ")
        end_time = time.time()

        time.sleep(tour_interval)

        if player_input != correct_answer or end_time - start_time > tour_time:
            wrong_input = True
            life_count -= 1
        else:
            score += 1

        if life_count == 0:
            break

        if wrong_input:
            draw_logo()
            if end_time - start_time > tour_time:
                print(f"Time out! Remaining lives: {life_count}. The correct answer was {correct_answer}")
            else:
                print(f"Wrong! Remaining lives: {life_count}. The correct answer was {correct_answer}")

            print("\nPress any key to continue...")
            input()

        number_counter += 1

    draw_logo()
    while True:
        player_name = input("Enter your name: ")

        if " " in player_name or player_name == "":
            draw_logo()
            print("Player name cannot contain spaces or be empty!")
        else:
            check_rankings([difficulty])
            ranking = fetch_ranking(difficulty)
            ranking.append(Score(score, player_name))
            save_ranking(ranking, difficulty)
            print("Your score has been saved in the ranking!\n")
            time.sleep(1)
            break

    print("GAME OVER")
    print(f"You have scored {score} points!")
    print("\nPress any key to add a replacement rule...")
    print("B - Return to the game menu")

    wybor = input().lower()

    if wybor == "b":
        game_menu()
    else:
        draw_logo()
        while True:
            while True:
                try:
                    number = int(input("Enter a number to replace: "))
                    if number < 1:
                        raise ValueError
                    break
                except ValueError:
                    draw_logo()
                    print("Wrong choice - try again.")
            number = str(number)
            replacement = input("Enter the number's replacement: ")

            if check_repetitions(Rule(number, replacement, "REPLACEMENT"), rules):
                draw_logo()
                print("You can't add two replacements for one number.")
            else:
                break
        rules.append(Rule(number, replacement, "REPLACEMENT"))

        print("\nPress any key to return to the game menu...")
        input()
        game_menu()


def pvp_game():
    global rules
    goal = round_count // 2 + 1
    Player1 = Player("", 0)
    Player2 = Player("", 0)
    round_number = 1

    draw_logo()
    while True:
        Player1.name = input("Enter first player's name: ")

        if Player1.name == "":
            draw_logo()
            print("Player's name cannot be empty!")
        else:
            break

    while True:
        Player2.name = input("Enter second player's name: ")

        if Player2.name == "":
            draw_logo()
            print("Player's name cannot be empty!")
        elif Player1.name == Player2.name:
            draw_logo()
            print("Players' names cannot be equal!")
        else:
            break

    while True:
        draw_logo()
        print(f"Press any key to start round {round_number}...")
        input()
        turn = 1
        number_counter = 1

        while True:
            turn = (turn + 1) % 2
            correct_answer = check_number(number_counter, rules)
            wrong_input = False
            current_player = Player1 if turn == 0 else Player2
            opponent = Player2 if turn == 0 else Player1
            draw_logo()

            start_time = time.time()
            player_input = input(f"{current_player.name}: ")
            end_time = time.time()

            time.sleep(tour_interval)

            if player_input != correct_answer or end_time - start_time > tour_time:
                wrong_input = True
                opponent.score += 1

            if wrong_input:
                draw_logo()
                print(f"ROUND {round_number} FINISHED")
                if end_time - start_time > tour_time:
                    print(f"Time out! The correct answer was {correct_answer}.")
                else:
                    print(f"Wrong! The correct answer was {correct_answer}.")

                print(f"{opponent.name} wins this round! The current score is {Player1.score}-{Player2.score}")
                break

            number_counter += 1

        if Player1.score == goal or Player2.score == goal:
            time.sleep(3)
            break

        round_number += 1

        print("\nPress any key to add a replacement rule...")
        input()

        draw_logo()
        while True:
            while True:
                try:
                    number = int(input("Enter a number to replace: "))
                    if number < 1:
                        raise ValueError
                    break
                except ValueError:
                    draw_logo()
                    print("Wrong choice - try again.")
            number = str(number)
            replacement = input("Enter the number's replacement: ")

            if check_repetitions(Rule(number, replacement, "REPLACEMENT"), rules):
                draw_logo()
                print("You can't add two replacements for one number.")
            else:
                break

        rules.append(Rule(number, replacement, "REPLACEMENT"))

        print(f"A new rule has been added ({number} is replaced with {replacement})!")
        input()

    winner = Player1 if Player1.score == goal else Player2
    loser = Player1 if winner == Player2 else Player2

    draw_logo()
    print(f"{winner.name} WON THE GAME!")
    print(f"{winner.name} wins the game against {loser.name}! Uzyskany wynik to {Player1.score}-{Player2.score}")

    print("\nPress any key to return to the game menu...")
    input()
    game_menu()


def pve_game():
    global rules
    goal = round_count // 2 + 1
    Player1 = Player("", 0)
    Computer = Player("Computer", 0)
    round_number = 1

    draw_logo()
    while True:
        Player1.name = input("Enter your name: ")

        if Player1.name == "":
            draw_logo()
            print("Player's name cannot be empty!")
        elif Player1.name == Computer.name:
            draw_logo()
            print("Players' names cannot be equal!")
        else:
            break

    while True:
        draw_logo()
        print(f"Press any key to start round {round_number}...")
        input()
        turn = 1
        number_counter = 1

        while True:
            turn = (turn + 1) % 2
            correct_answer = check_number(number_counter, rules)
            wrong_input = False
            current_player = Player1 if turn == 0 else Computer
            opponent = Computer if turn == 0 else Player1
            draw_logo()

            start_time = time.time()

            if current_player == Player1:
                player_input = input(f"{current_player.name}: ")
            else:
                should_be_correct = check_chance(number_counter)

                print(f"{current_player.name}: ")
                time.sleep(1 if tour_time > 2 else float(tour_time / 2))

                draw_logo()

                if should_be_correct:
                    print(f"{current_player.name}: {correct_answer}")
                    player_input = correct_answer
                else:
                    generated_answer = generate_answer()
                    print(f"{current_player.name}: {generated_answer}")
                    player_input = generated_answer

            end_time = time.time()

            time.sleep(tour_interval)

            if player_input != correct_answer or end_time - start_time > tour_time:
                wrong_input = True
                opponent.score += 1

            if wrong_input:
                draw_logo()
                print(f"ROUND {round_number} FINISHED")
                if end_time - start_time > tour_time:
                    print(f"Time out! The correct answer was {correct_answer}.")
                else:
                    print(f"Wrong! The correct answer was {correct_answer}.")

                print(f"{opponent.name} wins this round! Obecny wynik wynosi {Player1.score}-{Computer.score}")
                break

            number_counter += 1

        if Player1.score == goal or Computer.score == goal:
            time.sleep(3)
            break

        round_number += 1

        if current_player == Computer:
            print("\nPress any key to add a replacement rule...")
            input()

            draw_logo()
            while True:
                while True:
                    try:
                        number = int(input("Enter a number to replace: "))
                        if number < 1:
                            raise ValueError
                        break
                    except ValueError:
                        draw_logo()
                        print("Wrong choice - try again.")
                number = str(number)
                replacement = input("Enter the number's replacement: ")

                if check_repetitions(Rule(number, replacement, "REPLACEMENT"), rules):
                    draw_logo()
                    print("You can't add two replacements for one number.")
                else:
                    break

        else:
            while True:
                number = random.randint(1, 100)
                replacement = random.choice(get_words(difficulty))
                if check_repetitions(Rule(number, replacement, "REPLACEMENT"), rules):
                    pass
                else:
                    break

        rules.append(Rule(number, replacement, "REPLACEMENT"))
        print(f"A new rule has been added ({number} is replaced with {replacement})!")
        input()

    winner = Player1 if Player1.score == goal else Computer
    loser = Player1 if winner == Computer else Computer

    draw_logo()
    print(f"{winner.name} WON THE GAME!")
    print(f"{winner.name} wins the game against {loser.name}! The current score is {Player1.score}-{Computer.score}")

    print("\nPress any key to return to the game menu...")
    input()
    game_menu()


# MENU

def main_menu():
    draw_logo()
    print("1. Play")
    print("2. Settings")
    print("3. Credits")
    print("4. Exit")

    choice = input()

    if choice == "1":
        game_menu()
    elif choice == "2":
        settings_menu()
    elif choice == "3":
        credits_menu()
    elif choice == "4":
        draw_logo()
        print("Thanks for playing!")
        time.sleep(2)
        exit()

    else:
        main_menu()


def game_menu():
    draw_logo()
    print("1. Play in Solo mode")
    print("2. Play in PvE mode")
    print("3. Play in PvP mode")
    print("4. Change the difficulty")
    print("5. View rankings for the Solo mode")
    if show_rules:
        print("6. View the rule list")
    print("\nB - Return to the main menu")

    choice = input().lower()

    if choice == "1":
        solo_menu()
    elif choice == "2":
        pve_menu()
    elif choice == "3":
        pvp_menu()
    elif choice == "4":
        difficulty_menu()
    elif choice == "5":
        ranking_list_menu()
    elif choice == "6" and show_rules:
        rule_list_menu()
    elif choice == "b":
        main_menu()
    else:
        game_menu()


def settings_menu():
    draw_logo()
    print("1. Add a new rule")
    print("2. Clear the rule list")
    print("3. Remove a rule")
    print("4. Set the round count")
    print("5. Set a single tour time")
    print("6. Set the tour interval")
    print("7. Toggle rule list display in the game menu")
    print("8. Revert all settings to default")
    print("9. Clear the rankings")
    print("\nB - Return to the main menu")
    print("Note: If you enter a setting by mistake, press B to return to this menu.")

    choice = input().lower()

    if choice == "1":
        add_rule()
    elif choice == "2":
        clear_rules()
    elif choice == "3":
        remove_rule()
    elif choice == "4":
        set_round_count()
    elif choice == "5":
        set_tour_time()
    elif choice == "6":
        set_tour_interval()
    elif choice == "7":
        display_rule_list()
    elif choice == "8":
        revert_to_default()
    elif choice == "9":
        clear_rankings()
    elif choice == "b":
        main_menu()
    else:
        settings_menu()


def credits_menu():
    draw_logo()
    print("Ping Pong v2021.116")
    print("A word-based game made in Python.")
    print("Author: TPGPL")
    print("Ping Pong © 2020-2021")

    print("\nPress any key to return to the main menu...")
    input()
    main_menu()


def difficulty_menu():
    global difficulty
    draw_logo()
    print("Choose your difficulty level:")
    print("1. Easy (5 lives, simple words)")
    print("2. Medium (3 lives, more difficult words)")
    print("3. Hard (1 life, complicated words)")
    print("\nB - Return to the game menu")

    choice = input().lower()

    if choice == "1":
        draw_logo()
        difficulty = "E"
        print("You have chosen the Easy difficulty!")
    elif choice == "2":
        draw_logo()
        difficulty = "M"
        print("You have chosen the Medium difficulty!")
    elif choice == "3":
        draw_logo()
        difficulty = "H"
        print("You have chosen the Hard difficulty!")
    elif choice == "b":
        game_menu()
    else:
        difficulty_menu()

    print("\nPress any key to return to the game menu...")
    input()
    game_menu()


def rule_list_menu():
    game_difficulty = "Easy" if difficulty == "E" else "Medium" if difficulty == "M" else "Hard"
    draw_logo()
    print("Game rules:")
    print(f"- Game difficulty: {game_difficulty}")
    print(f"- Length of a single tour: {tour_time}")
    print(f"- Round count: {round_count}")
    print(f"- Tour interval: {tour_interval}")

    print("---------------------------------------")
    if not rules:
        print("No additional rules.")
    else:
        for rule in rules:
            if rule.kind == "REPLACEMENT":
                print(f"{rule.number} is replaced with {rule.replacement}")
            else:
                print(f"Numbers divisible by {rule.number} are replaced with {rule.replacement}")

    print("\nPress any key to return to the game menu...")
    input()
    game_menu()


def solo_menu():
    draw_logo()
    print("Play in Solo mode to achieve the highest score possible. When you run out of lives, your score will be added to the ranking and you will be able to add a new replacement rule. Difficulty level affects your base life count.")
    print("\nPress any key to start the game...")
    print("\nB - Return to the game menu")

    choice = input().lower()

    if choice == "b":
        game_menu()
    else:
        solo_game()


def pve_menu():
    draw_logo()
    print("Play against AI in a mode with a limited round count. After each round, the winner will be able to add a new replacement rule. Difficulty affects the complexity of words used by the AI.")
    print("\nPress any key to start the game...")
    print("\nB - Return to the game menu")

    choice = input().lower()

    if choice == "b":
        game_menu()
    else:
        pve_game()


def pvp_menu():
    draw_logo()
    print("Play against another player in a mode with a limited round count. After each round, the winner will be able to add a new replacement rule.")
    print("\nPress any key to start the game...")
    print("\nB - Return to the game menu")

    choice = input().lower()

    if choice == "b":
        game_menu()
    else:
        pvp_game()


def ranking_list_menu():
    draw_logo()
    print("View a ranking for the Solo mode:")
    print("1. Ranking for the Easy difficulty")
    print("2. Ranking for the Medium difficulty")
    print("3. Ranking for the Hard difficulty")
    print("\nB - Return to the game menu")

    choice = input().lower()

    if choice == "1":
        view_ranking("E")
    elif choice == "2":
        view_ranking("M")
    elif choice == "3":
        view_ranking("H")
    elif choice == "b":
        game_menu()
    else:
        ranking_list_menu()


def view_ranking(game_difficulty):
    check_rankings([game_difficulty])
    ranking = fetch_ranking(game_difficulty)
    kind = "Easy" if game_difficulty == "E" else "Medium" if game_difficulty == "M" else "Hard"
    draw_logo()

    if not ranking:
        print("There are no scores available. Maybe it's time to set some?")
    else:
        var = None  # ensures scores with the same points have equal placement in the ranking
        placement = 0

        print(f"Ranking for the {kind} difficulty:")

        for score in ranking:
            if var is None or score.score < var:
                var = score.score
                placement += 1
            print(f"#{placement} {score.score} - {score.player_name}")

    print("\nPress any key to return to the ranking list...")
    input()
    ranking_list_menu()


# SETTINGS

def add_rule():
    global rules
    draw_logo()
    while True:
        kind = input("Choose the type of a new rule (available types: DIVISION, REPLACEMENT): ").lower()

        if kind == "division" or kind == "replacement":
            break
        elif kind == "b":
            settings_menu()
        else:
            draw_logo()
            print("Wrong choice - try again.")

    if kind == "replacement":
        while True:
            while True:
                try:
                    number = int(input("Enter a number to replace: "))
                    if number < 1:
                        raise ValueError
                    break
                except ValueError:
                    draw_logo()
                    print("Wrong choice - try again.")

            number = str(number)

            while True:
                replacement = input("Enter the number's replacement: ")

                if replacement == "":
                    draw_logo()
                    print(f"Enter a number to replace: {number}")
                    print("Number replacement can't be empty.")
                else:
                    break

            if check_repetitions(Rule(number, replacement, "REPLACEMENT"), rules):
                draw_logo()
                print("You can't add two replacements for one number.")
            else:
                break
        rules.append(Rule(number, replacement, "REPLACEMENT"))
    else:
        while True:
            while True:
                try:
                    divisor = int(input("Enter the number divisor: "))
                    if divisor < 1:
                        raise ValueError
                    break
                except ValueError:
                    draw_logo()
                    print("Wrong choice - try again.")

            divisor = str(divisor)

            while True:
                replacement = input("Enter the replacement of divisible numbers: ")

                if replacement == "":
                    draw_logo()
                    print(f"Enter the number divisor: {divisor}")
                    print("Number replacement can't be empty.")
                else:
                    break

            if check_repetitions(Rule(divisor, replacement, "DIVISION"), rules):
                draw_logo()
                print("You can't add two replacements for one divisor.")
            else:
                break
        rules.append(Rule(divisor, replacement, "DIVISION"))

    print("A new rule has been added!")
    print("\nPress any key to return to the settings...")
    input()
    settings_menu()


def clear_rules():
    choice = confirmation()

    if not choice:
        settings_menu()
    else:
        pass

    global rules
    rules.clear()

    draw_logo()
    print("The rule list has been cleared!")
    print("\nPress any key to return to the settings...")
    input()
    settings_menu()


def set_round_count():
    global round_count
    draw_logo()
    while True:
        try:
            choice = input("Enter an odd round count: ")

            if choice.lower() == "b":
                settings_menu()

            choice = int(choice)

            if choice % 2 == 0 or choice < 1:
                raise ValueError
            break
        except ValueError:
            draw_logo()
            print("Wrong choice - try again.")

    round_count = choice
    print(f"The round count has been changed to {round_count}!")
    print("\nPress any key to return to the settings...")
    input()
    settings_menu()


def set_tour_time():
    global tour_time
    draw_logo()
    while True:
        try:
            choice = input("Enter the length of a single tour: ")

            if choice.lower() == "b":
                settings_menu()

            choice = float(choice)

            if choice <= 0:
                raise ValueError
            break
        except ValueError:
            draw_logo()
            print("Wrong choice - try again.")

    tour_time = choice
    print(f"The length of a single tour has been changed to {tour_time}s!")
    print("\nPress any key to return to the settings...")
    input()
    settings_menu()


def set_tour_interval():
    global tour_interval
    draw_logo()
    while True:
        try:
            choice = input("Enter the length of the interval between tours: ")

            if choice.lower() == "b":
                settings_menu()

            choice = float(choice)

            if choice < 0:
                raise ValueError
            break
        except ValueError:
            draw_logo()
            print("Wrong choice - try again.")

    tour_interval = choice
    print(f"The length of the interval between tours has been changed to {tour_interval}s!")
    print("\nPress any key to return to the settings...")
    input()
    settings_menu()


def revert_to_default():
    choice = confirmation()

    if not choice:
        settings_menu()
    else:
        pass

    global round_count
    global rules
    global tour_time
    global difficulty
    global tour_interval
    global show_rules

    round_count = default_round_count
    rules = default_rules.copy()
    tour_time = default_tour_time
    difficulty = default_difficulty
    tour_interval = default_tour_interval
    show_rules = default_show_rules

    draw_logo()
    print("All settings have been reverted to default!")
    print("\nPress any key to return to the settings...")
    input()
    settings_menu()


def display_rule_list():
    global show_rules
    draw_logo()

    while True:
        choice = input("Do you want the rule list to be displayed in the game menu? (Y/N)\n").lower()

        if choice == "y" or choice == "yes":
            show_rules = True
            break
        elif choice == "n" or choice == "no":
            show_rules = False
            break
        elif choice == "b":
            settings_menu()
        else:
            draw_logo()
            print("Wrong choice - try again.")

    if show_rules:
        print("The rule list will be displayed in the game menu!")
    else:
        print("The rule list won't be displayed in the game menu!")

    print("\nPress any key to return to the settings...")
    input()
    settings_menu()


def clear_rankings():
    choice = confirmation()

    if not choice:
        settings_menu()
    else:
        pass

    for kind in ["E", "M", "H"]:
        with io.open(f"assets/ranking-{kind}.txt", mode="r+", encoding="utf-8") as file:
            file.truncate(0)

    print("All rankings have been cleared!")
    print("\nPress any key to return to the settings...")
    input()
    settings_menu()


def remove_rule():
    global rules
    draw_logo()

    if not rules:
        print("The rule list is empty.")
        print("\nPress any key to return to the settings...")
        input()
        settings_menu()

    while True:
        counter = 0
        print("Rules:")

        for rule in rules:
            counter += 1

            if rule.kind == "REPLACEMENT":
                print(f"{counter}. {rule.number} is replaced with {rule.replacement}")
            elif rule.kind == "DIVISION":
                print(f"{counter}. Numbers divisible by {rule.number} are replaced with {rule.replacement}")

        try:
            rule_number = input("\nEnter the number of a rule to remove: ")
            if rule_number.lower() == "b":
                settings_menu()

            rule_number = int(rule_number)
            if rule_number < 1 or rule_number > counter:
                raise ValueError
            else:
                choice = confirmation()

                if not choice:
                    remove_rule()
                else:
                    break
        except ValueError:
            draw_logo()
            print("Wrong choice - try again.")

    rules.pop(rule_number - 1)

    print(f"The rule with number {rule_number} has been removed!")
    print("\nPress any key to return to the settings...")
    input()
    settings_menu()


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
    main_menu()


if __name__ == "__main__":
    main()
