import random


def rate_die_zahl():
    geheime_zahl = random.randint(1, 100)
    versuche = 7

    print("Ich habe mir eine Zahl zwischen 1 und 100 überlegt.")
    print(f"Du hast {versuche} Versuche, um sie zu erraten!\n")

    while versuche > 0:
        tipp = input(f"Versuch ({versuche} übrig) - Dein Tipp: ")

        # Prüfen, ob die Eingabe eine gültige ganze Zahl ist
        if not tipp.isdigit():
            print("Bitte gib eine gültige Zahl ein.\n")
            continue

        tipp = int(tipp)

        if tipp == geheime_zahl:
            print(f"Glückwunsch! Du hast die Zahl {geheime_zahl} erraten!")
            return
        elif tipp < geheime_zahl:
            print("Zu niedrig!")
        else:
            print("Zu hoch!")

        versuche -= 1
        print()

    print(
        f"Schade, keine Versuche mehr! Die gesuchte Zahl war: {geheime_zahl}"
    )


if __name__ == "__main__":
    rate_die_zahl()
