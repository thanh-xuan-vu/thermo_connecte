# Thermomètre connecté
## Introduction
L'objective du projet : 
- Prendre de la température des frigos automatiquement à l'aide des Raspberry Pi
- Signaler si la température dépasse un seuil prédéfini (par mél, ou message)
- Créer une interface web pour monitor et surveiller l'emsemble des thermomètres.
- Signaler tout arrêt de fonctionement 

## Equipement
Pour réaliser ce projet, on va utiliser 
- Un Rapsberry Pi zero 
- Un capteur de température et d'humidité BME280
- Un cable plat pour connecter les deux 
- Des boitiers pour le Raspberry Pi et le capteur

## Installation
1. Installer pip3 et [virtualenv](https://raspberrypi-aa.github.io/session4/venv.html)
```bash
sudo apt install pip3
sudo apt install python3-virtualenv
```
Créer un environement virtuel pour lancer le code et l'activer. 
```bash
virtualenv env
source env/bin/activate
pip list
```
2. Installer Python3 et les bibliothèques dans requirements.txt
```bash
pip install -r requirements:txt
```

## Lancer le code 
1. Activer l'environement 
```bash
source env/bin/activate
```
2. Lancer le code 