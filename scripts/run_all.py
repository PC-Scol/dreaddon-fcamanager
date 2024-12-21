import subprocess
import sys

def executer_script(script_name):
    """
    Exécute un script Python en tant que sous-processus et renvoie le statut de réussite.
    """
    try:
        print(f"Exécution de {script_name}...")
        subprocess.run([sys.executable, script_name], check=True)
        print(f"{script_name} s'est terminé avec succès.\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de {script_name} : {e}\n")
        return False

if __name__ == "__main__":
    # Exécuter activite.py
    if executer_script("activite.py"):
        # Si activite.py réussit, exécuter action.py
        if executer_script("action.py"):
            # Si action.py réussit, exécuter zfca_enseignement.py
            executer_script("zfca_enseignement.py")
        else:
            print("Erreur dans action.py. zfca_enseignement.py n'a pas été exécuté.")
    else:
        print("Erreur dans activite.py. action.py et zfca_enseignement.py n'ont pas été exécutés.")
