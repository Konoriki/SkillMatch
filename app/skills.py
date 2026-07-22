"""Liste des compétences qu'on sait reconnaître dans un CV.

On utilise un dictionnaire de mots-clés plutôt qu'un modèle de NLP :
c'est plus simple à comprendre et à expliquer, et ça suffit largement
pour ce projet.
"""

SKILLS_DICTIONARY: dict[str, list[str]] = {
    "Langages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "PHP",
        "Go", "Rust", "Kotlin", "Swift", "Ruby", "SQL",
    ],
    "Frameworks & bibliothèques": [
        "FastAPI", "Django", "Flask", "React", "Angular", "Vue.js",
        "Node.js", "Spring", ".NET", "Symfony", "Laravel",
    ],
    "Bases de données": [
        "SQLite", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Oracle",
        "SQL Server",
    ],
    "DevOps & Cloud": [
        "Docker", "Kubernetes", "Git", "GitHub Actions", "GitLab CI",
        "Jenkins", "AWS", "Azure", "GCP", "Terraform", "Linux",
    ],
    "Data & IA": [
        "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch",
        "Power BI", "Excel",
    ],
}
