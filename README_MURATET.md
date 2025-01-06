# Spy Projet ISG, IORDACHE MOVSESSIAN MAICHE

## Systèmes modifiés:
- BlocLimitationManager: Ajout du bloc Fonction
- CurrentActionManager: Gestion d'appel de fonction / Instanciation des fonctions (panel d'execution etc) / Gestion des instructions executées dans les fonctions / Gestion de fin de fonction
- DragDropSystem: Gestion d'input de nom de fonction
- EndGameManager: Ajout d'une fin si le nom de fonction n'est pas valide
- HighLightSystem: Ajout gestion dans le panel de fonction
- EditorLevelDataSystem: Gestion des fonctions dans l'éditeur
- SaveFileSystem: Save des fonctions pré-implémenté
- LevelGenerator: Read les fonctions save pour leur génération
- ScriptGenerator: Transforme une "FunctionToLoad" en GameObject
- StepSystem: Gestion pour l'execution dans une fonction
- UISystem: Créations des containeur pour les fonctions / Nettoyage a la fin d'une execution
- TitleScreenSystem: Fix du path pour la lecture des scenarios locaux **(Oubliez pas les points bonus)**

## Systèmes ajoutés:
- EditableContainerSystemFunction: Copie du Système EditableContainerSystem pour gérer les container de fonctions
- LaunchDashboardScript: Script du lancement du script python qui créer le Dashboard.

## Component Modifiés / Ajoutés
- Function
- AddSpecificContainerFunction 
- FunctionToLoad
- ScriptRef
- NewEnd