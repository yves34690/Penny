# 🤝 Contribuer à Penny

Merci de votre intérêt pour contribuer au projet Penny !

## 🐛 Signaler un bug

Si vous trouvez un bug :

1. Allez sur [Issues](https://github.com/yves34690/Penny/issues)
2. Cliquez sur **New Issue**
3. Décrivez le problème :
   - Ce que vous avez fait
   - Ce qui s'est passé
   - Ce que vous attendiez
   - Vos logs (si possible)

## 💡 Proposer une amélioration

Si vous avez une idée pour améliorer Penny :

1. Vérifiez que ça n'existe pas déjà dans les [Issues](https://github.com/yves34690/Penny/issues)
2. Créez une **nouvelle Issue** avec le tag \`enhancement\`
3. Expliquez votre idée clairement

## 🔧 Contribuer au code

### Prérequis

- Python 3.12+
- Docker Desktop
- Git

### Étapes pour contribuer

1. **Forkez le projet**
   - Cliquez sur le bouton **Fork** en haut à droite sur GitHub
   - Cela crée une copie du projet dans votre compte

2. **Clonez votre fork**
   \`\`\`bash
   git clone https://github.com/VOTRE_NOM/Penny.git
   cd Penny
   \`\`\`

3. **Créez une branche pour votre modification**
   \`\`\`bash
   git checkout -b feature/ma-super-fonctionnalite
   \`\`\`

4. **Faites vos modifications**
   - Modifiez le code
   - Testez que ça marche : \`python verify_setup.py\`
   - Testez les notebooks : \`python src/notebook_scheduler.py\`

5. **Commitez vos changements**
   \`\`\`bash
   git add .
   git commit -m "feat: Ajout de ma super fonctionnalité"
   \`\`\`

6. **Poussez vers votre fork**
   \`\`\`bash
   git push origin feature/ma-super-fonctionnalite
   \`\`\`

7. **Créez une Pull Request**
   - Allez sur votre fork sur GitHub
   - Cliquez sur **Compare & pull request**
   - Expliquez vos modifications
   - Cliquez sur **Create pull request**

8. **Attendez la review**
   - Je vais regarder votre code
   - Peut-être demander des modifications
   - Si tout est bon : je merge ! 🎉

## 📝 Conventions de code

### Messages de commit

Utilisez le format [Conventional Commits](https://www.conventionalcommits.org/) :

- \`feat:\` Nouvelle fonctionnalité
- \`fix:\` Correction de bug
- \`docs:\` Documentation
- \`refactor:\` Refactoring (sans changer le comportement)
- \`test:\` Ajout de tests
- \`chore:\` Maintenance (dépendances, config)

Exemples :
\`\`\`
feat: Ajout export Excel pour les factures
fix: Correction erreur connexion PostgreSQL
docs: Amélioration guide débutant
\`\`\`

### Style Python

- Suivre [PEP 8](https://pep8.org/)
- Utiliser des noms de variables explicites
- Commenter les parties complexes
- Ajouter des docstrings aux fonctions

### Notebooks Jupyter

- Alterner cellules Markdown (explication) et Code
- Ajouter des \`print()\` pour visualiser chaque étape
- Utiliser des émojis pour rendre ça plus visuel : ✅ ❌ 📊

## 🧪 Tests

Avant de soumettre une Pull Request :

1. Vérifiez que le setup fonctionne :
   \`\`\`bash
   python verify_setup.py
   \`\`\`

2. Testez l'exécution des notebooks :
   \`\`\`bash
   python src/notebook_scheduler.py
   \`\`\`

3. Vérifiez qu'il n'y a pas d'erreur :
   \`\`\`bash
   docker-compose logs scheduler
   \`\`\`

## 📖 Documentation

Si vous ajoutez une fonctionnalité, mettez à jour la documentation :

- \`README.md\` : Ajouter dans la section appropriée
- \`DEMARRAGE_RAPIDE.md\` : Si ça impacte les débutants
- \`GUIDE_AUTOMATION.md\` : Si ça touche à Docker

## ❓ Questions

Si vous avez des questions :

1. Regardez d'abord dans la [documentation](README.md)
2. Cherchez dans les [Issues existantes](https://github.com/yves34690/Penny/issues)
3. Créez une nouvelle Issue avec le tag \`question\`

## 🎉 Merci !

Chaque contribution, petite ou grande, est appréciée ! 🙏

---

**Mainteneur** : Yves Cloarec ([@yves34690](https://github.com/yves34690))
