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
0. Installer git et clone le package
```bash
sudo apt install git
git clone https://github.com/thanh-xuan-vu/thermo_connecte.git
```
1. Installer pip3 
```bash
sudo apt install pip3
pip3 list
```
2. Installer Python3 et les bibliothèques dans requirements.txt
```bash
pip3 install -r requirements:txt
```
## Lancer le code 
Se positionner dans le répertoire thermo_connecte qu'on vient d'installer.
```bash
cd thermo_connecte
python3 -m src.send_email
```