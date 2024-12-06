#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    # Ajouter le répertoire parent au PYTHONPATH
    project_root = Path(__file__).resolve().parent
    sys.path.append(str(project_root))

    # Définir les paramètres par défaut
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?\n"
            "Did you forget to activate a virtual environment?\n"
            "Error: %s" % exc
        )

    # Gérer les commandes spéciales
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # Configuration spéciale pour les tests
            os.environ.setdefault('DJANGO_CONFIGURATION', 'Test')
        elif sys.argv[1] == 'shell':
            # Configuration pour le shell
            try:
                import IPython
                IPython.start_ipython(argv=[])
                return
            except ImportError:
                pass

    # Exécuter la commande
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
