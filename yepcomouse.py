import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import threading
import time
import random
import math
import argparse  # Pour gérer les arguments de la ligne de commande

# Variables de physique pour Yepco
gravity = 0.5  # Force gravitationnelle constante
yepco_velocity_x = 3
yepco_velocity_y = 0  # La vitesse verticale démarre à zéro
bounce_factor = -0.7  # Facteur de rebond (perte d'énergie à chaque rebond)
friction = 0.99  # Réduction de la vitesse horizontale à chaque itération
repulsion_force = 50  # Force de repoussement en cas de collision avec la souris
dragging = False  # État pour savoir si on est en train de déplacer Yepco
dragging_basket = False  # État pour savoir si on est en train de déplacer le panier
max_velocity = 50  # Limite de vitesse maximale
score = 0  # Score initial
yepco_size = 150  # Taille initiale de Yepco

# Coordonnées du panier
basket_x = 0
basket_y = 0
score_label = None  # Initialiser la variable score_label à None


# Fonction pour limiter la vitesse à une valeur maximale
def limit_velocity(velocity, max_value):
    if velocity > max_value:
        return max_value
    elif velocity < -max_value:
        return -max_value
    return velocity

# Fonction pour mettre à jour la position de l'image en fonction de la position du curseur
def follow_cursor():
    offset_x = 20  # Décalage horizontal
    offset_y = 20  # Décalage vertical

    while True:
        # Obtenir la position actuelle du curseur
        cursor_x, cursor_y = pyautogui.position()

        # Décaler la position de l'image par rapport au curseur
        cursor_x += offset_x
        cursor_y += offset_y

        # Mettre à jour la position de la fenêtre à l'emplacement du curseur décalé
        cursor_window.geometry(f"+{cursor_x}+{cursor_y}")

        # Vérifier la collision avec Yepco
        check_collision_with_yepco(cursor_x, cursor_y)

        # Attendre un court instant avant de mettre à jour à nouveau
        time.sleep(0.01)

# Fonction pour vérifier la collision entre la souris et Yepco
def check_collision_with_yepco(cursor_x, cursor_y):
    global yepco_velocity_x, yepco_velocity_y

    # Obtenir les coordonnées actuelles de Yepco
    yepco_x = yepco.winfo_x()
    yepco_y = yepco.winfo_y()

    # Taille de Yepco
    yepco_width = yepco_size
    yepco_height = yepco_size

    # Vérifier si la souris est à l'intérieur des limites de Yepco
    if yepco_x < cursor_x < yepco_x + yepco_width and yepco_y < cursor_y < yepco_y + yepco_height:
        # Calculer le vecteur de repoussement en fonction de la position relative de la souris
        dx = cursor_x - (yepco_x + yepco_width / 2)
        dy = cursor_y - (yepco_y + yepco_height / 2)
        distance = math.sqrt(dx**2 + dy**2)

        # Normaliser le vecteur de direction
        if distance != 0:
            dx /= distance
            dy /= distance

        # Appliquer une force de repoussement plus forte en fonction de la distance
        yepco_velocity_x -= dx * repulsion_force  # Repousser dans la direction opposée
        yepco_velocity_y -= dy * repulsion_force

        # Limiter la vitesse maximale
        yepco_velocity_x = limit_velocity(yepco_velocity_x, max_velocity)
        yepco_velocity_y = limit_velocity(yepco_velocity_y, max_velocity)

# Fonction pour déplacer Yepco avec physique et gravité
def smooth_move_with_gravity_yepco():
    global yepco_velocity_x, yepco_velocity_y, dragging, score, yepco_size

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Position initiale de Yepco
    current_x = random.randint(0, screen_width - yepco_size)
    current_y = random.randint(0, screen_height - yepco_size)

    while True:
        if not dragging:  # Ne pas appliquer la gravité si on est en train de déplacer Yepco manuellement
            # Appliquer la gravité à la vélocité verticale
            yepco_velocity_y += gravity

            # Appliquer la vélocité pour mettre à jour la position de Yepco
            current_x += yepco_velocity_x
            current_y += yepco_velocity_y

            # Gérer les collisions avec les bords de l'écran
            if current_x < 0:
                current_x = 0
                yepco_velocity_x *= bounce_factor  # Inverser la direction horizontale lors du contact avec les bords
            elif current_x + yepco_size > screen_width:
                current_x = screen_width - yepco_size
                yepco_velocity_x *= bounce_factor

            if current_y + yepco_size > screen_height:  # Collision avec le sol
                current_y = screen_height - yepco_size  # Repositionner au sol
                yepco_velocity_y *= bounce_factor  # Inverser la direction verticale pour rebondir
                yepco_velocity_x *= friction  # Appliquer la friction pour ralentir horizontalement

                # Si la vitesse est très faible, l'arrêter
                if abs(yepco_velocity_y) < 1:
                    yepco_velocity_y = 0
                if abs(yepco_velocity_x) < 0.1:
                    yepco_velocity_x = 0

            # Si Yepco touche le plafond
            if current_y < 0:
                current_y = 0
                yepco_velocity_y *= bounce_factor  # Inverser la direction verticale

            # Vérifier si Yepco passe dans la zone du panier en utilisant son centre
            if check_scoring_zone(current_x + yepco_size // 2, current_y + yepco_size // 2):
                score += 1
                yepco_size += 10  # Augmenter la taille de Yepco à chaque point
                update_yepco_size()
                update_score_display()

            # Mettre à jour la position de Yepco
            yepco.geometry(f"+{int(current_x)}+{int(current_y)}")

        # Pause pour ralentir le mouvement et le rendre fluide
        time.sleep(0.01)

# Fonction pour redimensionner Yepco lorsque le score augmente
def update_yepco_size():
    global photo, image, yepco_size
    if score_label:
        image = Image.open("yepco.png")
        image = image.resize((yepco_size, yepco_size))  # Redimensionner l'image en fonction de la nouvelle taille
        photo = ImageTk.PhotoImage(image)

        # Mettre à jour l'image de Yepco sur le canvas
        canvas_copy.config(width=yepco_size, height=yepco_size)
        canvas_copy.create_image(0, 0, anchor=tk.NW, image=photo)

# Fonction pour vérifier si le centre de Yepco est dans la zone de score
def check_scoring_zone(yepco_center_x, yepco_center_y):
    global basket_x, basket_y
    # Coordonnées et dimensions de la zone de score
    basket_width = 150
    basket_height = 200

    if (basket_x < yepco_center_x < basket_x + basket_width and
        basket_y < yepco_center_y < basket_y + basket_height):
        return True
    return False

# Fonction pour mettre à jour l'affichage du score
def update_score_display():
    if score_label:
        score_label.config(text=f"Score: {score}")

# Fonction pour gérer le clic sur Yepco
def on_yepco_click(event):
    global dragging
    dragging = True

# Fonction pour déplacer Yepco lors du glisser-déposer
def on_yepco_drag(event):
    if dragging:
        # Mettre à jour la position de Yepco en suivant la souris
        yepco.geometry(f"+{event.x_root}+{event.y_root}")

# Fonction pour gérer le relâchement du clic
def on_yepco_release(event):
    global dragging
    dragging = False

# Fonction pour gérer le clic sur le panier
def on_basket_click(event):
    global dragging_basket
    dragging_basket = True

# Fonction pour déplacer le panier lors du glisser-déposer
def on_basket_drag(event):
    global basket_x, basket_y
    if dragging_basket:
        # Mettre à jour la position du panier en suivant la souris
        basket_x = event.x_root
        basket_y = event.y_root
        basket_window.geometry(f"+{basket_x}+{basket_y}")

# Fonction pour gérer le relâchement du clic sur le panier
def on_basket_release(event):
    global dragging_basket
    dragging_basket = False

# Main logic
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", action="store_true", help="Activer le jeu du panier")
    args = parser.parse_args()

    # Créer la fenêtre principale tkinter pour le curseur
    root = tk.Tk()
    root.withdraw()  # Masquer la fenêtre principale pour qu'elle ne s'affiche pas

    # Obtenir les dimensions de l'écran
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Créer une fenêtre secondaire pour le curseur
    cursor_window = tk.Toplevel(root)
    cursor_window.overrideredirect(True)  # Supprimer les bordures de la fenêtre
    cursor_window.attributes("-topmost", True)  # Toujours au-dessus des autres fenêtres
    cursor_window.attributes("-transparentcolor", 'white')  # Rendre une couleur transparente

    # Charger et configurer l'image pour le curseur Yepco
    cursor_image = Image.open("yepcocurseur.png")
    cursor_image = cursor_image.resize((150, 150))  # Redimensionner l'image si nécessaire
    cursor_photo = ImageTk.PhotoImage(cursor_image)

    # Créer un canvas pour afficher l'image du curseur Yepco
    cursor_canvas = tk.Canvas(cursor_window, width=150, height=150, bg='white', highlightthickness=0)
    cursor_canvas.pack()

    # Ajouter l'image au canvas
    cursor_canvas.create_image(0, 0, anchor=tk.NW, image=cursor_photo)

    # Créer une deuxième fenêtre tkinter pour la copie de Yepco qui se balade
    yepco = tk.Toplevel(root)
    yepco.overrideredirect(True)
    yepco.attributes("-topmost", True)
    yepco.attributes("-transparentcolor", 'white')

    # Créer un canvas pour afficher l'image dans la copie de Yepco
    canvas_copy = tk.Canvas(yepco, width=yepco_size, height=yepco_size, bg='white', highlightthickness=0)
    canvas_copy.pack()

    # Charger et configurer l'image Yepco
    image = Image.open("yepco.png")
    image = image.resize((yepco_size, yepco_size))  # Redimensionner l'image si nécessaire
    photo = ImageTk.PhotoImage(image)

    # Ajouter l'image au canvas avec une référence pour la mise à jour future
    image_id = canvas_copy.create_image(0, 0, anchor=tk.NW, image=photo)

    # Associer les événements de clic et de glisser-déposer à Yepco
    canvas_copy.bind("<Button-1>", on_yepco_click)  # Détecter le clic sur Yepco
    canvas_copy.bind("<B1-Motion>", on_yepco_drag)  # Détecter le glisser de Yepco
    canvas_copy.bind("<ButtonRelease-1>", on_yepco_release)  # Détecter le relâchement du clic

    # Lancer le suivi du curseur dans un thread séparé pour ne pas bloquer l'interface
    cursor_thread = threading.Thread(target=follow_cursor, daemon=True)
    cursor_thread.start()

    # Lancer le déplacement fluide avec gravité de Yepco dans un thread séparé
    yepco_thread = threading.Thread(target=smooth_move_with_gravity_yepco, daemon=True)
    yepco_thread.start()

    if args.game:
        # Créer une fenêtre transparente et toujours au-dessus pour le score
        score_window = tk.Toplevel(root)
        score_window.overrideredirect(True)
        score_window.attributes("-topmost", True)
        score_window.attributes("-transparentcolor", 'white')
        score_label = tk.Label(score_window, text=f"Score: {score}", font=("Arial", 20), bg='white')
        score_label.pack()
        score_window.geometry(f"+10+10")  # Placer le score en haut à gauche de l'écran

        # Créer une fenêtre transparente et toujours au-dessus pour le panier de basket
        basket_window = tk.Toplevel(root)
        basket_window.overrideredirect(True)
        basket_window.attributes("-topmost", True)
        basket_window.attributes("-transparentcolor", 'white')
        basket_canvas = tk.Canvas(basket_window, width=150, height=200, bg='white', highlightthickness=0)  # Taille augmentée
        basket_canvas.pack()
        basket_image = Image.open("basket.png")
        basket_image = basket_image.resize((150, 200))  # Augmenter la taille de l'image du panier
        basket_photo = ImageTk.PhotoImage(basket_image)
        basket_canvas.create_image(0, 0, anchor=tk.NW, image=basket_photo)
        basket_x = screen_width - 250
        basket_y = screen_height // 2 - 100
        basket_window.geometry(f"+{basket_x}+{basket_y}")  # Positionner à droite

        # Associer les événements de clic et de glisser-déposer au panier
        basket_canvas.bind("<Button-1>", on_basket_click)  # Détecter le clic sur le panier
        basket_canvas.bind("<B1-Motion>", on_basket_drag)  # Détecter le glisser du panier
        basket_canvas.bind("<ButtonRelease-1>", on_basket_release)  # Détecter le relâchement du clic

    # Démarrer la boucle principale tkinter
    root.mainloop()
