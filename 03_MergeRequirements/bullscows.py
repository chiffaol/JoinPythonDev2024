import random
from urllib.request import urlopen
import argparse
from cowsay import *

def bullscows(guess: str, secret: str) -> (int, int):
    """
    озвращает количество «быков» и «коров» из guess в secret
    """
    bulls = 0
    cows = 0
    for i in range(min(len(guess), len(secret))):
        bulls += guess[i] == secret[i]
    cows = len(set(guess).intersection(set(secret)))
    return bulls, cows

def gameplay(ask: callable, inform: callable, words: list[str]) -> int:
    """
    функция-приложение, обеспечивающая геймплей:
    Задумывает случайное слово из списка слов words: list[str]
    Спрашивает у пользователя слово с помощью функции ask("Введите слово: ", words)
    Выводит пользователю результат с помощью функции inform("Быки: {}, Коровы: {}", b, c)
    Если слово не отгадано, переходит к п.1 
    Если слово отгадано, возвращает количество попыток — вызовов ask()
    """
    ask_cnt = 0
    b = 0
    secret = random.choice(words)
    
    while b != len(secret):
        guess = ask(cowsay("Введите слово:", cow=get_random_cow()), words)
        ask_cnt += 1

        (b, c) = bullscows(guess, secret)
        inform("Быки: {}, Коровы: {}", b, c)
        if b == len(secret):
            print(ask_cnt)
            break
    
    return ask_cnt

def ask(prompt: str, valid: list[str] = None) -> str:
    """
    Если необязательный параметр valid не пуст, 
    допустим только ввод слова из valid, иначе спрашивает повторно
    
    ask("Введите слово: ", words)
    """
    if valid:
        while True:
            tmp = input(prompt + "\n")
            if tmp in valid:
                break
    else:
        tmp = input(prompt + "\n")
    
    return tmp

def inform(format_string: str, bulls: int, cows: int) -> None:
    """
    inform("Быки: {}, Коровы: {}", b, c)
    """
    print(cowsay(format_string.format(bulls, cows), cow=get_random_cow()))

def get_words(url: str) -> list:
    """
    Возвращает список слов со  страницы url
    """
    with urlopen(url) as response:
        words = response.read().decode('utf-8').splitlines()
    return words



def main():
    parser = argparse.ArgumentParser(description='Bulls and Cows game.')
    parser.add_argument('dictionary', help='URL name')
    parser.add_argument('length_w', nargs = '?', type=int, default=5, help='Word length')

    args = parser.parse_args()
    
    if args.dictionary.startswith('http'):
        words = get_words(args.dictionary)
    else:
        with open(args.dictionary, 'r') as file:
            words = file.read().splitlines()

    if not words:
        print('Error: Empty dictionary')
        return
    
    valid_words = [
        word for word in words if len(word) == args.length_w
        ]
    
    gameplay(ask, inform, valid_words)
    
    
if __name__ == '__main__':
    main()