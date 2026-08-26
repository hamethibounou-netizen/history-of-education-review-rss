# History of Education Review RSS

Petit flux RSS personnel destiné à Zotero.

Le script `generate_feed.py` récupère les 50 publications les plus récentes de
**History of Education Review** via Crossref (eISSN `2054-5649`) et réécrit
`feed.xml`.

Le workflow GitHub Actions `.github/workflows/update-feed.yml` s'exécute
automatiquement une fois par jour et peut aussi être lancé manuellement.

## Mise en ligne avec GitHub Pages

1. Créer un dépôt GitHub public nommé `history-of-education-review-rss`.
2. Déposer tous les fichiers de ce dossier en respectant l'arborescence.
3. Ouvrir **Actions** puis lancer manuellement **Update RSS feed** une première fois.
4. Dans **Settings > Pages** :
   - Source : **Deploy from a branch**
   - Branch : **main**
   - Folder : **/(root)**
5. L'URL du flux sera normalement :

   `https://VOTRE-NOM-GITHUB.github.io/history-of-education-review-rss/feed.xml`

Dans Zotero :
**Fichier > Nouvelle bibliothèque > Nouveau flux > À partir d'une URL**,
puis coller cette adresse.
