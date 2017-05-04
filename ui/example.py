import sys

while True:
    string = str(input())
    if string == 'exit':
        break
    else:
        print(string[::-1])
