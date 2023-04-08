# Projet S8
## Authors
CHAPRON Lucas - chapron.e2105151@etud.univ-ubs.fr  
COUTAND Bastien - coutand.e2100676@etud.univ-ubs.fr  
MARCHAND Robin - marchand.e2101234@etud.univ-ubs.fr  

## Réalisation
WEB - CHAPRON Lucas / COUTAND Bastien  
Programme Obfuscation/Désobfuscation - COUTAND Bastien / MARCHAND Robin

## Description du projet
Ce projet vient du problème que tout le monde peut voir un pdf ou une image en entier une fois mis en ligne et qu'il n'y a plus de contrôle d'accès. Nous avons rendu possible l'accès de certaines informations selon les rôles afin que seul un groupe de personnes ait accès à l'information. Pour mettre cela en place, nous avons dû utiliser nos compétences en stéganographie et web. Pour utiliser cet outil nous avons mis en place une interface web mais l'outil est tout à fait utilisable en ligne de commande même si ceci est très peu intuitif et il vous faut récupérer les coordonnées des mots que vous voudriez cacher.

## Contenu du dossier
### docker-compose.yml
Fichier de configuration de docker-compose

### app-container
Contient les fichiers nécessaires au fonctionnement de l'application : application web et programme pour cacher/récupérer les données de fichier png, jpg, jpeg et pdf.

# Getting started
L'utilisation du site web peut se faire de deux manières différentes :
- En local
- Via docker

## Installation
### En local
#### Prérequis
- Python 3.* (Testé avec la version 3.11)

#### Installation
- Cloner le projet
- Installer les dépendances python en se mettant dans le dossier /app-container et en exécutant la commande suivante : `pip install -r requirements.txt`
- Exécuter la commande ``uvicorn api.app:app --reload --port 8000``
- Se rendre à l'adresse ``http://localhost:8000``

### Via docker:
Pour lancer le site web, il faut installer docker et docker-compose.  
Pour installer docker, suivez les instructions sur le site officiel : https://docs.docker.com/engine/install/  
Pour installer docker-compose, suivez les instructions sur le site officiel : https://docs.docker.com/compose/install/  

#### Installation:
- Cloner le projet
- Allez dans le dossier racine du projet
- Lancez la commande ``docker-compose up``
- Aller sur un navigateur à l'adresse ``http://localhost:8000``

## Utilisation
### Page désobfuscation
Cette page permet de désobfusquer un fichier png qui a été préalablement obfusquer avec notre outil. Il vous suffit d'importer le fichier via le bouton "Choisir un fichier" et de cliquer sur le bouton "Importer". Le fichier est envoyé au serveur. Rentrez votre passphrase (mot de passe) et cliquez sur le bouton "Créer le document". Vous verrez ensuite apparaître le fichier désobfusquer en bas de la page. Si vous désirez le télécharger, cliquez sur le bouton "Télécharger".

### Page obfuscation
Cette page permet d'obfusquer une image ou un pdf(marche mieux avec un pdf pour le moment). Il faut que vous importiez le fichier via le bouton "Choisir un fichier" et de cliquer sur le bouton "Importer". Vous verrez ensuite apparaître le fichier en bas de la page. Rentrez les rôles pour qui le fichier sera visible (donc cacher pour les autres). Une fois que vous avez rentré tous les rôles. Maintenez votre clique gauche enfoncé et "encadrer" le mot que vous voulez cacher, une pop up apparaitra où vous devez rentrer le mot à cacher, vous devez ensuite choisir les rôles pour lequel ce mot sera visible (à l'aide du menu déroulant, plusieurs sont séléctionnable). Une fois que vous avez rentré tous les mots, cliquez sur le bouton "Télécharger" et vous aurez un fichier png obfusquer. Vous aurez ensuite accès aux différents mots de passe pour les rôles que vous avez rentré. Notez les biens car vous ne pourrez plus les récupérer par la suite.

# Amélioration
- Rendre le site plus joli
- Check la taille des fichiers en back
- Implémenter les sessions pour que plusieurs personnes puissent utiliser l'outil en même temps
- Améliorer la restriction des extensions de fichier -> regarder les headers du fichier
- Faire de l'OCR pour que l'utilisateur n'ai pas à rentrer les mots à cacher -> problème coordonnées du mot
- Améliorer la sécurisation WEB -> ex : CSRF surtout sécuriser l'échange de data entre le front et le back
