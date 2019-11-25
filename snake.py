from upemtk import *
from time import sleep
from random import randint

# dimensions du jeu
TAILLE_CASE = 15
LARGEUR_PLATEAU = 40  # en nombre de cases
HAUTEUR_PLATEAU = 30  # en nombre de cases
DELAI_POMMES = 4     # délai entre l'apparition des pommes, en secondes (pour un framerate de 10/s)
MAX_POMMES = 3        # nombre maximum de pomme présentes à l'écran en même temps

CYCLE_COULEUR = ['green', 'darkgreen', 'lightgreen', 'blue', 'cyan',
                 'lightblue', 'red', 'pink', 'yellow', 'orange',
                 'magenta', 'purple', 'black', 'white']
RAINBOW_COULEUR = ['red', 'orange', 'yellow', 'green', 'cyan',
                   'blue', 'purple']

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

def affiche_pommes(pommes, pommes_special, rainbow):
    for pomme in pommes:
        x, y = case_vers_pixel(pomme)
        couleur = 'red'
        if pomme in pommes_special:
            if pommes_special[pomme] == 'super':
                couleur = rainbow
            elif pommes_special[pomme] == 'bleu':
                couleur = 'blue'
            elif pommes_special[pomme] == 'or':
                couleur = 'yellow'
        cercle(x, y, TAILLE_CASE/2,
               couleur='darkred', remplissage=couleur)
        rectangle(x-2, y-TAILLE_CASE*.4, x+2, y-TAILLE_CASE*.7,
                  couleur='darkgreen', remplissage='darkgreen')

def affiche_murs(murs):
    for mur in murs:
        x, y = case_vers_pixel(mur)
        rectangle(x-TAILLE_CASE/2, y-TAILLE_CASE/2, x+TAILLE_CASE/2,
                  y+TAILLE_CASE/2, couleur='black', remplissage='grey')

def affiche_serpent(serpent, couleur, rainbow):
    for i in range(len(serpent)):
        x, y = case_vers_pixel(serpent[i])

        if not rainbow:
            cercle(x, y, TAILLE_CASE/2 + 1,
                   couleur='black', remplissage=couleur)
        else:
            j = RAINBOW_COULEUR.index(couleur)
            if (j+i)%len(RAINBOW_COULEUR) == len(RAINBOW_COULEUR):
                c = 0
            else:
                c = (j+i)%len(RAINBOW_COULEUR)
            cercle(x, y, TAILLE_CASE/2 + 1,
                   couleur='black', remplissage=RAINBOW_COULEUR[c])

def couleur_serpent(couleur_serp, couleur_rainbow, rainbow):
    if not rainbow:
        return couleur_serp
    else:
        return couleur_rainbow

def cycle_rainbow(couleur):
    i = RAINBOW_COULEUR.index(couleur)
    if i == len(RAINBOW_COULEUR)-1:
        return RAINBOW_COULEUR[0]
    else:
        return RAINBOW_COULEUR[i+1]
    
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
    new_x = x + u
    new_y = y + v

    if pomme_mangee:
        serpent.insert(0, (new_x, new_y))
    else:
        for i in range(len(serpent)-1):
            serpent[len(serpent)-i-1] = serpent[len(serpent)-i-2]

        if new_x < 0:
            new_x = LARGEUR_PLATEAU - 1
        elif new_x >= LARGEUR_PLATEAU:
            new_x = 0

        if new_y < 0:
            new_y = HAUTEUR_PLATEAU - 1
        elif new_y >= HAUTEUR_PLATEAU:
            new_y = 0

        serpent[0] = (new_x, new_y)

    return serpent

def detection(serpent, murs, direction, invincible):
    if invincible:
        return False
    x, y = serpent[0]
    u, v = direction
    if (x + u < 0 or x + u >= LARGEUR_PLATEAU or y + v < 0 or y + v >= HAUTEUR_PLATEAU) and not torus:
        return True
    if (x + u, y + v) in serpent and direction != (0, 0):
        return True
    if (x + u, y + v) in murs:
        return True
    return False

def generation_pomme(pommes, pommes_special, serpent, murs, timer, powerups):
    if len(pommes) < MAX_POMMES:
        if timer >= DELAI_POMMES:
            while True:
                pomme = (randint(0, LARGEUR_PLATEAU-1), randint(0, HAUTEUR_PLATEAU-1))
                if (pomme not in pommes) and (pomme not in serpent) and (pomme not in murs):
                    pommes.append(pomme)
                    if powerups:
                        tirage = randint(1, 100)
                        if tirage <= 5:
                            pommes_special[pomme] = 'super'
                        elif tirage <= 10:
                            pommes_special[pomme] = 'bleu'
                        elif tirage <= 17:
                            pommes_special[pomme] = 'or'
                    return pommes, pommes_special, 0
    return pommes, pommes_special, timer

def generation_mur(murs, nb_murs):
    for i in range(nb_murs):
        mur = (randint(0, LARGEUR_PLATEAU-1), randint(0, HAUTEUR_PLATEAU-1))
        while mur in murs or mur == (LARGEUR_PLATEAU//2, HAUTEUR_PLATEAU//2):
            mur = (randint(0, LARGEUR_PLATEAU-1), randint(0, HAUTEUR_PLATEAU-1))
        murs.append(mur)
    return murs

def mange_pomme(serpent, pommes, pommes_special, score, ralenti, invincible):
    if serpent[0] in pommes:
        if serpent[0] in pommes_special:
            if pommes_special[serpent[0]] == 'or':
                pommes.remove(serpent[0])
                pommes_special.pop(serpent[0])
                return True, pommes, pommes_special, score+10, ralenti, invincible
            elif pommes_special[serpent[0]] == 'bleu':
                pommes.remove(serpent[0])
                pommes_special.pop(serpent[0])
                return True, pommes, pommes_special, score+1, 5, invincible
            elif pommes_special[serpent[0]] == 'super':
                pommes.remove(serpent[0])
                pommes_special.pop(serpent[0])
                return True, pommes, pommes_special, score+1, ralenti, 10
        else:
            pommes.remove(serpent[0])
            return True, pommes, pommes_special, score+1, ralenti, invincible
    else:
        return False, pommes, pommes_special, score, ralenti, invincible

def ecran_titre(torus, accel, nb_murs, couleur_serp, powerups):
    while True:
        efface_tout()
        texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/8,
              "Bienvenue à", ancrage='center')
        texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/4,
              "Snake", ancrage='center', taille=48, couleur='green')
        texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/2,
              "Faites un clic gauche pour commencer", taille=14, ancrage='center')

        affiche_bouton(300, 346, 180, 60, 'Options', rempl='grey')
        
        while True:
                ev= attend_ev()
                ty = type_ev(ev)
                if ty == 'Quitte':
                    ferme_fenetre()
                elif ty == 'ClicGauche':
                    if clique_bouton(300, 346, 180, 60, ev):
                        torus, accel, nb_murs, couleur_serp, powerups = options(torus, accel, nb_murs, couleur_serp, powerups)
                        break
                    else:
                        return torus, accel, nb_murs, couleur_serp, powerups

def affiche_boutons_options(torus, accel, nb_murs, couleur_serp, powerups):
    if torus:
        affiche_bouton(300, 200, 180, 60, 'Torus', rempl='green')
    else:
        affiche_bouton(300, 200, 180, 60, 'Torus', rempl='red')
    
    if accel:
        affiche_bouton(300, 280, 260, 60, 'Accélération', rempl='green')
    else:
        affiche_bouton(300, 280, 260, 60, 'Accélération', rempl='red')
    
    if nb_murs == 0:
        affiche_bouton(300, 360, 300, 60, 'Murs', rempl='red')
    elif nb_murs == 20:
        affiche_bouton(300, 360, 300, 60, 'Murs : peu', rempl='green')
    elif nb_murs == 50:
        affiche_bouton(300, 360, 300, 60, 'Murs : moyen', rempl='green')
    else:
        affiche_bouton(300, 360, 300, 60, 'Murs : beaucoup', rempl='green')
    
    if powerups:
        affiche_bouton(300, 440, 260, 60, 'Bonus', rempl='green')
    else:
        affiche_bouton(300, 440, 260, 60, 'Bonus', rempl='red')
    
    texte(300, 80, 'Couleur du serpent', ancrage='center', taille = 14)
    affiche_bouton(300, 120, 180, 60, '', rempl=couleur_serp)

def options(torus, accel, nb_murs, couleur_serp, powerups):
    while True:
        efface_tout()
        texte(TAILLE_CASE*LARGEUR_PLATEAU/2, 40, "Options", ancrage='center')
        affiche_boutons_options(torus, accel, nb_murs, couleur_serp, powerups)
        affiche_bouton(80, 490, 140, 60, 'Retour', rempl='grey')

        while True:
                ev = attend_ev()
                ty = type_ev(ev)
                if ty == 'Quitte':
                    ferme_fenetre()
                elif ty == 'ClicGauche':
                    if clique_bouton(300, 200, 180, 60, ev):
                        torus = not torus
                        break
                    elif clique_bouton(300, 280, 260, 60, ev):
                        accel = not accel
                        break
                    elif clique_bouton(300, 360, 180, 60, ev):
                        if nb_murs == 0:
                            nb_murs = 20
                        elif nb_murs == 20:
                            nb_murs = 50
                        elif nb_murs == 50:
                            nb_murs = 70
                        else:
                            nb_murs = 0
                        break
                    elif clique_bouton(300, 120, 180, 60, ev):
                        actuel = CYCLE_COULEUR.index(couleur_serp)
                        if actuel == len(CYCLE_COULEUR)-1:
                            couleur_serp = CYCLE_COULEUR[0]
                        else:
                            couleur_serp = CYCLE_COULEUR[actuel+1]
                        break
                    elif clique_bouton(300, 440, 260, 60, ev):
                        powerups = not powerups
                        break
                    elif clique_bouton(80, 490, 140, 60, ev):
                        return torus, accel, nb_murs, couleur_serp, powerups
                elif ty == 'ClicDroit':
                    if clique_bouton(300, 120, 180, 60, ev):
                        actuel = CYCLE_COULEUR.index(couleur_serp)
                        if actuel == 0:
                            couleur_serp = CYCLE_COULEUR[-1]
                        else:
                            couleur_serp = CYCLE_COULEUR[actuel-1]
                        break


def affiche_bouton(x, y, longueur, largeur, text='', coul='black', rempl=''):
    rectangle(x - longueur/2, y - largeur/2, x + longueur/2, y + largeur/2, remplissage=rempl, couleur=coul)
    texte(x, y, text, police='Arial Black', ancrage='center')

def clique_bouton(x, y, longueur, largeur, ev):
    if (x-longueur/2 <= abscisse(ev) <= x+longueur/2) and (y-largeur/2 <= ordonnee(ev) <= y+largeur/2):
        return True
    return False

def game_over(score, timer):
    efface_tout()
    texte(300, 112.5, "Game Over", ancrage='center', taille=48, couleur='red')
    texte(300, 225, "Votre score final est : " + str(score), ancrage='center', taille=14)
    texte(300, 195, "Vous avez tenu : " + chaine_temps(timer), ancrage='center', taille=14)
    
    texte(300, 300, "Voulez-vous rejouer ?", ancrage='center', taille=14)

    affiche_bouton(300, 346, 180, 60, 'Oui', rempl='green')
    affiche_bouton(300, 409, 180, 60, 'Non', rempl='red')
    
    while True:
            ev = attend_ev()
            ty = type_ev(ev)
            if ty == 'Quitte':
                ferme_fenetre()
            elif ty == 'ClicGauche':
                if clique_bouton(300, 346, 180, 60, ev):
                    break
                elif clique_bouton(300, 409, 180, 60, ev):
                    ferme_fenetre()

def pause():
    texte(TAILLE_CASE*LARGEUR_PLATEAU/2, TAILLE_CASE*HAUTEUR_PLATEAU/2,
          "Pause", taille=72, ancrage='center', tag='pause', couleur='blue')
    while True:
        ev= attend_ev()
        ty = type_ev(ev)
        if ty == 'Quitte':
            ferme_fenetre()
        elif ty == 'Touche':
             if touche(ev) == 'p':
                break
    efface('pause')

def chaine_temps(timer):
    secondes, minutes = int(timer)%60, int(timer)//60
    if secondes < 10:
        secondes = '0' + str(secondes)
    else:
        secondes = str(secondes)
    if minutes < 10:
        minutes = '0' + str(minutes)
    else:
        minutes = str(minutes)

    return minutes + ':' + secondes

def affiche_temps(timer):
    texte(400, 473, "Temps : " + chaine_temps(timer), taille=18,
          police='Arial Black', couleur='white')

def affiche_score(score):
    texte(10, 473, 'Score : ' + str(score), taille=18,
          police='Arial Black', couleur='white')

def affiche_vitesse(framerate):
    texte(170, 473, 'Vitesse : %d' % (framerate*10) + '%', taille=18,
          police='Arial Black', couleur='white')

def affiche_hud(score, timer, framerate, ralenti):
    rectangle(0, HAUTEUR_PLATEAU * TAILLE_CASE, LARGEUR_PLATEAU*TAILLE_CASE,
              HAUTEUR_PLATEAU * TAILLE_CASE + 80, couleur='', remplissage='black')
    affiche_score(score)
    affiche_temps(timer)
    if ralenti:
        affiche_vitesse(framerate/1.5)
    else:
        affiche_vitesse(framerate)

# programme principal
if __name__ == "__main__":

    # initialisation du jeu
    cree_fenetre(TAILLE_CASE * LARGEUR_PLATEAU,
                 TAILLE_CASE * HAUTEUR_PLATEAU + 80)

    # état par défaut des options
    torus = False
    accel = False
    powerups = False
    nb_murs = 0
    couleur_serp = 'green'


    # boucle permettant de recommencer une nouvelle partie
    while True:
        # écran titre
        torus, accel, nb_murs, couleur_serp, powerups = ecran_titre(torus, accel, nb_murs, couleur_serp, powerups)

        # initialisation de la partie
        framerate = 10    # taux de rafraîchissement du jeu en images/s
        direction = (0, 0)  # direction initiale du serpent
        pommes = [] # liste des coordonnées des cases contenant des pommes
        pommes_special = {} # dictionnaire permettant de retenir quelles pommes sont spéciales
        serpent = [(LARGEUR_PLATEAU//2, HAUTEUR_PLATEAU//2)] # liste des coordonnées de cases adjacentes décrivant le serpent
        murs = []
        timer_pomme = 0
        pomme_mangee = False
        score = 0
        timer = 0
        ralenti = 0
        invincible = 0
        rainbow = 'red'
        frein_debut = True
        murs = generation_mur(murs, nb_murs)
        couleur = couleur_serp
        
        # boucle principale
        jouer = True
        while jouer:
            # affichage des objets
            efface_tout()
            affiche_pommes(pommes, pommes_special, rainbow) 
            affiche_serpent(serpent, couleur, invincible > 0)
            affiche_hud(score, timer, framerate, ralenti > 0)
            affiche_murs(murs)
            mise_a_jour()
            if frein_debut:
                frein_debut = direction == (0, 0)
            
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
            if detection(serpent, murs, direction, invincible > 0):
                jouer = False
            else:
                serpent = avance_serpent(serpent, direction, pomme_mangee)

            # gestion des couleurs
            rainbow = cycle_rainbow(rainbow)
            couleur = couleur_serpent(couleur_serp, rainbow, invincible > 0)

            # gestion de la consommation des pommes
            pomme_mangee = False
            pomme_mangee, pommes, pommes_special, score, ralenti, invincible = mange_pomme(serpent, pommes, pommes_special, score, ralenti, invincible)

            # gestion de la génération des pommes
            if not frein_debut:
                pommes, pommes_special, timer_pomme = generation_pomme(pommes, pommes_special, serpent, murs, timer_pomme, powerups)
                timer_pomme += 1/framerate
                timer += 1/framerate

            if invincible > 0:
                invincible -= 1/framerate
            else:
                invincible = 0

            if ralenti > 0:
                ralenti -= 1/framerate
            else:
                ralenti = 0

            if accel and framerate < 70 and pomme_mangee:
                framerate += 0.25
                print(framerate)

            # attente avant rafraîchissement
            if ralenti > 0:
                sleep(1.5/(framerate))
            else:
                sleep(1/framerate)
            

        # écran de fin
        game_over(score, timer)
        

    # fermeture et sortie
    ferme_fenetre()
