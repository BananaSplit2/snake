from upemtk import *
from time import sleep
from random import randint

# dimensions du jeu
TAILLE_CASE = 15
LARGEUR_PLATEAU = 40  # en nombre de cases
HAUTEUR_PLATEAU = 30  # en nombre de cases
DELAI_POMMES = 4     # délai entre l'apparition des pommes, en secondes (pour un framerate de 10/s)

def case_vers_pixel(case):
    """
    Reçoit les coordonnées d'une case du plateau sous la 
    forme d'un couple d'entiers (ligne, colonne) et renvoie les 
    coordonnées du pixel se trouvant au centre de cette case. Ce calcul 
    prend en compte la taille de chaque case, donnée par la variable 
    globale TAILLE_CASE.
    """
    i, j = case
    return (i + .5) * TAILLE_CASE, (j + .5) * TAILLE_CASE

def affiche_pommes(pommes):
    for pomme in pommes:
        x, y = case_vers_pixel(pomme)
        cercle(x, y, TAILLE_CASE/2,
               couleur='darkred', remplissage='red')
        rectangle(x-2, y-TAILLE_CASE*.4, x+2, y-TAILLE_CASE*.7,
                  couleur='darkgreen', remplissage='darkgreen')

def affiche_serpent(serpent):
    for partie in serpent:
        x, y = case_vers_pixel(partie)

        cercle(x, y, TAILLE_CASE/2 + 1,
               couleur='darkgreen', remplissage='green')

def change_direction(direction, touche):
    if touche == 'Up':
        return (0, -1)
    elif touche == 'Down':
        return (0, 1)
    elif touche == 'Left':
        return (-1, 0)
    elif touche == 'Right':
        return (1, 0)
    else:
        return direction

def avance_serpent(serpent, direction, pomme_mangee):
    x, y = serpent[0]
    u, v = direction

    if pomme_mangee:
        serpent.insert(0, (x + u, y + v))
    else:
        for i in range(len(serpent)-1):
            serpent[len(serpent)-i-1] = serpent[len(serpent)-i-2]
        serpent[0] = (x + u, y + v)

    return serpent

def detection(serpent, direction):
    x, y = serpent[0]
    u, v = direction
    if x + u < 0 or x + u >= LARGEUR_PLATEAU or y + v < 0 or y + v >= HAUTEUR_PLATEAU:
        return True
    if (x + u, y + v) in serpent and direction != (0, 0):
        return True
    return False

def generation_pomme(pommes, serpent, timer):
    if timer >= DELAI_POMMES * 10:
        while True:
            pomme = (randint(0, LARGEUR_PLATEAU-1), randint(0, HAUTEUR_PLATEAU-1))
            if (pomme not in pommes) and (pomme not in serpent):
                pommes.append(pomme)
                return pommes, 0
    else:
        return pommes, timer

def mange_pomme(serpent, pommes, score):
    if serpent[0] in pommes:
        pommes.remove(serpent[0])
        print('Score =', score+1)
        return True, pommes, score+1
    else:
        return False, pommes, score

def ecran_titre():
    texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/8, "Bienvenue à", ancrage='center')
    texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/4, "Snake", ancrage='center', taille=48, couleur='green')
    texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/2, "Faites un clic gauche pour commencer", taille=14, ancrage='center')

def game_over(score):
    texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/4, "Game Over", ancrage='center', taille=48, couleur='red')
    texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/2, "Votre score final est : " + str(score), ancrage='center', taille=14)

def pause():
    texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/2, "Pause", taille=72, ancrage='center', tag='pause', couleur='blue')
    while True:
        ev= attend_ev()
        ty = type_ev(ev)
        if ty == 'Quitte':
            ferme_fenetre()
        elif ty == 'Touche':
             if touche(ev) == 'p':
                break
    efface('pause')

def affiche_temps(timer):
    secondes, minutes = int(timer)%60, int(timer)//60
    if secondes < 10:
        secondes = '0' + str(secondes)
    else:
        secondes = str(secondes)
    if minutes < 10:
        minutes = '0' + str(minutes)
    else:
        minutes = str(minutes)
    
    texte(330, HAUTEUR_PLATEAU*TAILLE_CASE+80/5, "Temps : " + minutes + ':' + secondes, taille=24, police='Arial Black', couleur='white')

def affiche_score(score):
    texte(10, HAUTEUR_PLATEAU*TAILLE_CASE+80/5, 'Score : ' + str(score), taille=24, police='Arial Black', couleur='white')

def affiche_hud(score, timer):
    rectangle(0, HAUTEUR_PLATEAU * TAILLE_CASE, LARGEUR_PLATEAU*TAILLE_CASE, HAUTEUR_PLATEAU * TAILLE_CASE + 80, couleur='', remplissage='black')
    affiche_score(score)
    affiche_temps(timer)

# programme principal
if __name__ == "__main__":

    # initialisation du jeu
    framerate = 10    # taux de rafraîchissement du jeu en images/s
    direction = (0, 0)  # direction initiale du serpent
    pommes = [] # liste des coordonnées des cases contenant des pommes
    serpent = [(LARGEUR_PLATEAU//2, HAUTEUR_PLATEAU//2)] # liste des coordonnées de cases adjacentes décrivant le serpent
    cree_fenetre(TAILLE_CASE * LARGEUR_PLATEAU,
                 TAILLE_CASE * HAUTEUR_PLATEAU + 80)
    timer_pomme = 0
    pomme_mangee = False
    score = 0
    timer = 0

    # écran titre
    ecran_titre()
    while True:
        ev= attend_ev()
        ty = type_ev(ev)
        if ty == 'Quitte':
            ferme_fenetre()
        elif ty == 'ClicGauche':
            break

    # boucle principale
    jouer = True
    while jouer:
        # affichage des objets
        efface_tout()
        affiche_pommes(pommes) 
        affiche_serpent(serpent)
        affiche_hud(score, timer)
        mise_a_jour()
        
        # gestion des événements
        ev = donne_ev()
        ty = type_ev(ev)
        if ty == 'Quitte':
            ferme_fenetre()
        elif ty == 'Touche':
            print(touche(ev))
            direction = change_direction(direction, touche(ev))
            if touche(ev) == 'p':
                pause()

        # mouvement du serpent et détection d'une collision avec le mur ou le serpent lui-même
        if detection(serpent, direction):
            jouer = False
        else:
            serpent = avance_serpent(serpent, direction, pomme_mangee)

        # gestion de la consommation des pommes
        pomme_mangee = False
        pomme_mangee, pommes, score = mange_pomme(serpent, pommes, score)

        # gestion de la génération des pommes
        pommes, timer_pomme = generation_pomme(pommes, serpent, timer_pomme)
        timer_pomme += 1

        # attente avant rafraîchissement
        sleep(1/framerate)
        timer += 1/framerate

    # écran de fin
    efface_tout()
    game_over(score)
    while True:
        ev= attend_ev()
        ty = type_ev(ev)
        if ty == 'Quitte':
            ferme_fenetre()
        elif ty == 'ClicGauche':
            break

    # fermeture et sortie
    ferme_fenetre()
