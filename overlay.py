import threading
import time
import tkinter as tk
import signal

import pyautogui

class Overlay:

    baseCellSize = 50
    cellSize = baseCellSize
    
    def __init__(self, x, y, width, height):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Supprime la barre de titre
        self.root.attributes("-topmost", True)  # Toujours au premier plan
        self.root.geometry(f"{width}x{height}+{x}+{y}")  # Position et taille identiques au jeu
        self.root.wm_attributes("-transparent", "white")  # Rendre blanc transparent

        self.x = x
        self.y = y
        self.setupSignalHandler() 

        # Création du Canvas pour dessiner
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def close(self, *args):
        print("Fermeture de l'overlay...")
        self.root.quit()
        self.root.destroy()
    
    def signalListener(self):
        """Thread qui surveille SIGINT (CTRL+C) et force la fermeture"""
        while True:
            time.sleep(0.1)  # Vérifie toutes les 100ms
            if not self.root.winfo_exists():  # Si la fenêtre est déjà fermée, on arrête
                break

    def setupSignalHandler(self):
        """Démarre un thread pour écouter CTRL+C sur Windows"""
        signal.signal(signal.SIGINT, lambda sig, frame: self.root.after(0, self.close))
        
        # Lancer un thread séparé pour surveiller l'état de l'application
        signalThread = threading.Thread(target=self.signalListener, daemon=True)
        signalThread.start()

    def drawGrid(self, draw=False):
        baseHeight=1080
        """Dessine une grille adaptée à la résolution actuelle en conservant un ratio 16:9."""
        
        self.root.update_idletasks()  # Mise à jour forcée pour récupérer les dimensions
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Calcul de l'échelle basée sur la hauteur réelle
        scaleFactor = height / baseHeight
        cellSize = int(self.baseCellSize * scaleFactor)
        self.cellSize = cellSize

        if draw :
            print(f"Dessin de la grille : {width}x{height} avec cellSize={cellSize}")  # Debug

            # Dessin des lignes verticales
            for i in range(0, width, cellSize):
                self.canvas.create_line(i, 0, i, height, fill="red", width=2)

            # Dessin des lignes horizontales
            for j in range(0, height, cellSize):
                self.canvas.create_line(0, j, width, j, fill="red", width=2)

    def clickOnCell(self, col, row, offsetX=0, offsetY=0):
        """Simule un clic au centre de la case (row, col) et affiche un cercle temporaire."""
        x, y = self.getPixelPosition(col, row, offsetX, offsetY)

        pyautogui.click(x, y)

    def getPixelPosition(self, col, row, offsetX=0, offsetY=0, local=False):
        """Retourne les coordonnées du centre de la case (row, col)."""
       
        x = (col * self.cellSize) + (self.cellSize // 2) + offsetX
        y = (row * self.cellSize) + (self.cellSize // 2) + offsetY
        
        if not local:
            x += self.x
            y += self.y
        
        return x, y
    
    def getGlobalPosition(self, relX, relY):
        globalX = relX + self.x
        globalY = relY + self.y
        pyautogui.moveTo(globalX, globalY)


    def run(self):
        self.root.mainloop()
