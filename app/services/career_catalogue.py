"""
PATHFORGE AI - Career Role Catalogue
Predefined, structured, and expandable catalogue of 13 primary career roles
used by Feature 2 (Career Path Recommender) and Feature 3 (Skill Gap Analyzer).
"""

from typing import Dict, List, Any, Optional

CAREER_ROLES_CATALOGUE: List[Dict[str, Any]] = [
    {
        "slug": "software-developer",
        "title": "Software Developer",
        "category": "Software Engineering",
        "description": "Designs, writes, tests, and maintains robust computer software and application systems using modern programming languages and architectural patterns.",
        "required_skills": ["Python", "Java", "C++", "Data Structures", "Algorithms", "Git", "Object-Oriented Programming (OOP)"],
        "recommended_skills": ["SQL", "Linux", "CI/CD", "Unit Testing", "REST API", "Docker"],
        "soft_skills": ["Problem-solving", "Teamwork", "Adaptability", "Attention to Detail"],
        "market_demand": "Very High",
        "typical_roles": ["Junior Software Developer", "Software Engineer", "Senior Software Developer"],
        "suggested_next_steps": [
            "Strengthen algorithms and data structures proficiency through daily coding problems.",
            "Build a modular open-source project demonstrating OOP principles and unit testing.",
            "Contribute to a team repository using Git feature branches and pull requests."
        ]
    },
    {
        "slug": "frontend-developer",
        "title": "Frontend Developer",
        "category": "Software Engineering",
        "description": "Constructs visually compelling, responsive, and accessible user interfaces for web and mobile web applications using client-side technologies.",
        "required_skills": ["JavaScript", "HTML", "CSS", "React", "TypeScript", "Responsive Design"],
        "recommended_skills": ["Next.js", "Tailwind CSS", "Bootstrap", "REST API", "Git", "Webpack/Vite"],
        "soft_skills": ["Attention to Detail", "Communication", "Collaboration", "Creative Thinking"],
        "market_demand": "High",
        "typical_roles": ["Frontend Engineer", "UI Developer", "Lead Web App Developer"],
        "suggested_next_steps": [
            "Build responsive, modern web applications incorporating React state management.",
            "Master TypeScript for type-safe user interface development.",
            "Learn accessibility (a11y) standards and performance optimization techniques."
        ]
    },
    {
        "slug": "backend-developer",
        "title": "Backend Developer",
        "category": "Software Engineering",
        "description": "Architects server-side logic, microservices, databases, and secure APIs powering web platforms and enterprise integrations.",
        "required_skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "REST API", "Git", "Data Modeling"],
        "recommended_skills": ["Docker", "Redis", "Kafka", "Django", "Node.js", "Linux", "Microservices"],
        "soft_skills": ["Analytical Thinking", "Problem-solving", "Systematic Debugging"],
        "market_demand": "Very High",
        "typical_roles": ["Backend Engineer", "API Specialist", "Server Systems Architect"],
        "suggested_next_steps": [
            "Design and deploy production-grade REST APIs using FastAPI or Django with JWT auth.",
            "Implement relational data models with PostgreSQL, indexing, and migration workflows.",
            "Containerize backend services with Docker and set up automated health checks."
        ]
    },
    {
        "slug": "full-stack-developer",
        "title": "Full Stack Developer",
        "category": "Software Engineering",
        "description": "Builds end-to-end web applications covering user interfaces, database persistence, server architectures, and third-party integrations.",
        "required_skills": ["JavaScript", "Python", "React", "FastAPI", "SQL", "HTML", "CSS", "Git"],
        "recommended_skills": ["TypeScript", "Docker", "PostgreSQL", "Node.js", "AWS", "CI/CD"],
        "soft_skills": ["Adaptability", "Multi-tasking", "Communication", "Collaboration"],
        "market_demand": "Very High",
        "typical_roles": ["Full Stack Engineer", "Web Applications Developer", "Technical Co-founder"],
        "suggested_next_steps": [
            "Ship a full-stack SaaS product integrating React frontend, FastAPI backend, and PostgreSQL.",
            "Deploy the end-to-end project on modern cloud hosting with automated CI/CD pipelines.",
            "Implement user authentication, session security, and state synchronization."
        ]
    },
    {
        "slug": "python-developer",
        "title": "Python Developer",
        "category": "Software Engineering",
        "description": "Specializes in building backend services, data pipelines, automation tools, and web microservices leveraging the Python ecosystem.",
        "required_skills": ["Python", "FastAPI", "Django", "SQL", "Git", "REST API", "OOP in Python"],
        "recommended_skills": ["Pandas", "PyMuPDF", "Docker", "PostgreSQL", "pytest", "Asyncio"],
        "soft_skills": ["Problem-solving", "Clean Code Practices", "Continuous Learning"],
        "market_demand": "High",
        "typical_roles": ["Python Engineer", "Backend Python Specialist", "Automation Engineer"],
        "suggested_next_steps": [
            "Deepen knowledge of asynchronous Python (asyncio) and concurrent backend architectures.",
            "Write comprehensive test suites using pytest and maintain high test coverage.",
            "Package and publish reusable Python modules or CLI utilities."
        ]
    },
    {
        "slug": "data-analyst",
        "title": "Data Analyst",
        "category": "Data & Analytics",
        "description": "Transforms raw business and application data into actionable insights, dashboards, statistical summaries, and strategic reports.",
        "required_skills": ["SQL", "Excel", "Python", "Data Analysis", "Data Visualization", "Pandas"],
        "recommended_skills": ["Tableau", "Power BI", "Statistics", "NumPy", "Jupyter", "ETL"],
        "soft_skills": ["Communication", "Critical Thinking", "Business Acumen", "Storytelling"],
        "market_demand": "High",
        "typical_roles": ["Junior Data Analyst", "Business Intelligence Analyst", "Analytics Consultant"],
        "suggested_next_steps": [
            "Master complex SQL queries, window functions, aggregations, and data joins.",
            "Perform exploratory data analysis (EDA) using Python (Pandas, Matplotlib, Seaborn).",
            "Build an interactive dashboard tracking key business KPIs and actionable conclusions."
        ]
    },
    {
        "slug": "data-scientist",
        "title": "Data Scientist",
        "category": "Data & Analytics",
        "description": "Leverages statistical modeling, machine learning, and advanced analytics to uncover predictive patterns and solve complex data problems.",
        "required_skills": ["Python", "SQL", "Pandas", "NumPy", "Statistics", "Machine Learning", "Scikit-Learn"],
        "recommended_skills": ["Data Visualization", "Jupyter", "TensorFlow", "Deep Learning", "Feature Engineering"],
        "soft_skills": ["Critical Thinking", "Research Mindset", "Communication", "Problem Formulation"],
        "market_demand": "Very High",
        "typical_roles": ["Data Scientist", "Applied Scientist", "Quantitative Research Analyst"],
        "suggested_next_steps": [
            "Implement predictive regression and classification pipelines on realistic datasets.",
            "Develop strong mathematical foundations in probability, linear algebra, and hypothesis testing.",
            "Document experimental methodologies and model performance metrics rigorously."
        ]
    },
    {
        "slug": "machine-learning-engineer",
        "title": "Machine Learning Engineer",
        "category": "Artificial Intelligence",
        "description": "Designs, trains, optimizes, and productionizes machine learning models into reliable, high-throughput software pipelines.",
        "required_skills": ["Python", "Machine Learning", "Scikit-Learn", "NumPy", "Pandas", "Git", "Data Pipelines"],
        "recommended_skills": ["TensorFlow", "PyTorch", "Docker", "MLOps", "FastAPI", "Model Serving"],
        "soft_skills": ["Analytical Thinking", "Experimentation", "Cross-functional Collaboration"],
        "market_demand": "Very High",
        "typical_roles": ["ML Engineer", "MLOps Engineer", "Applied AI Practitioner"],
        "suggested_next_steps": [
            "Train and fine-tune models with Scikit-Learn or PyTorch, addressing bias and overfitting.",
            "Build low-latency inference REST APIs deploying trained models via FastAPI.",
            "Learn MLOps practices for model versioning, drift monitoring, and automated retraining."
        ]
    },
    {
        "slug": "ai-engineer",
        "title": "AI Engineer",
        "category": "Artificial Intelligence",
        "description": "Integrates Large Language Models (LLMs), multi-agent systems, semantic search, and generative AI into scalable software products.",
        "required_skills": ["Python", "AI Integration", "Prompt Engineering", "FastAPI", "REST API", "Git"],
        "recommended_skills": ["LangChain", "Vector Databases", "Embeddings", "RAG", "Docker", "Claude API", "OpenAI API"],
        "soft_skills": ["Continuous Learning", "Systems Thinking", "Ethical AI Awareness"],
        "market_demand": "Very High",
        "typical_roles": ["AI Solutions Engineer", "Generative AI Specialist", "Agentic Systems Architect"],
        "suggested_next_steps": [
            "Develop Retrieval-Augmented Generation (RAG) applications using embeddings and vector search.",
            "Build autonomous agent workflows with structured tool-calling and memory architectures.",
            "Evaluate model performance against structured JSON schemas with automated validation."
        ]
    },
    {
        "slug": "cloud-engineer",
        "title": "Cloud Engineer",
        "category": "Cloud & Infrastructure",
        "description": "Architects, deploys, and maintains resilient cloud environments, serverless components, and virtualized enterprise infrastructure.",
        "required_skills": ["AWS", "Linux", "Cloud Computing", "Networking", "Security", "Git"],
        "recommended_skills": ["Azure", "GCP", "Terraform", "Docker", "Kubernetes", "Python", "Bash"],
        "soft_skills": ["Reliability Focus", "Problem-solving", "Team Communication"],
        "market_demand": "High",
        "typical_roles": ["Cloud Systems Engineer", "Cloud Infrastructure Architect", "Site Reliability Engineer"],
        "suggested_next_steps": [
            "Achieve an industry cloud certification (e.g., AWS Solutions Architect or Azure Administrator).",
            "Learn Infrastructure as Code (IaC) with Terraform to provision reproducible cloud resources.",
            "Configure VPC networking, subnets, IAM role policies, and automated backups."
        ]
    },
    {
        "slug": "devops-engineer",
        "title": "DevOps Engineer",
        "category": "Cloud & Infrastructure",
        "description": "Automates release pipelines, manages containerized services, establishes observability, and bridges development and operations.",
        "required_skills": ["Linux", "Git", "CI/CD", "Docker", "Bash Scripting", "Cloud Fundamentals"],
        "recommended_skills": ["Kubernetes", "Terraform", "Prometheus", "Grafana", "Python", "AWS"],
        "soft_skills": ["Collaboration", "Incident Management", "Continuous Improvement"],
        "market_demand": "Very High",
        "typical_roles": ["DevOps Specialist", "Platform Engineer", "SRE"],
        "suggested_next_steps": [
            "Build multi-stage CI/CD pipelines with GitHub Actions or GitLab CI including automated tests.",
            "Deploy containerized microservices to Kubernetes clusters with helm charts.",
            "Implement centralized logging, metric alerting, and uptime monitoring."
        ]
    },
    {
        "slug": "cybersecurity-analyst",
        "title": "Cybersecurity Analyst",
        "category": "Security & Risk",
        "description": "Protects organizational computer systems, networks, and data assets against unauthorized access, vulnerabilities, and cyber threats.",
        "required_skills": ["Networking", "Linux", "Security Principles", "Vulnerability Assessment", "Firewalls"],
        "recommended_skills": ["Python", "SIEM", "Wireshark", "Identity & Access Management (IAM)", "Incident Response"],
        "soft_skills": ["Vigilance", "Ethical Integrity", "Crisis Management", "Communication"],
        "market_demand": "Very High",
        "typical_roles": ["Information Security Analyst", "SOC Analyst", "Security Consultant"],
        "suggested_next_steps": [
            "Master TCP/IP networking, packet analysis with Wireshark, and subnet routing fundamentals.",
            "Practice vulnerability scanning and safe ethical penetration testing labs (e.g. TryHackMe).",
            "Study key security frameworks (NIST, ISO 27001) and security auditing protocols."
        ]
    },
    {
        "slug": "ui-ux-designer",
        "title": "UI/UX Designer",
        "category": "Design & Product",
        "description": "Researches user behaviors, crafts wireframes, designs intuitive design systems, and creates polished interfaces for digital products.",
        "required_skills": ["UI/UX Design", "Wireframing", "Prototyping", "User Research", "Visual Design"],
        "recommended_skills": ["Figma", "Design Systems", "HTML", "CSS", "Usability Testing", "Information Architecture"],
        "soft_skills": ["Empathy", "Visual Communication", "Active Listening", "Feedback Receptiveness"],
        "market_demand": "High",
        "typical_roles": ["Product Designer", "User Experience Researcher", "Interface Specialist"],
        "suggested_next_steps": [
            "Build a design portfolio in Figma featuring end-to-end case studies and interactive prototypes.",
            "Conduct structured usability tests with representative users to validate design decisions.",
            "Collaborate closely with frontend engineers on design system tokens and component specs."
        ]
    }
]


def get_catalogue_dict() -> Dict[str, Dict[str, Any]]:
    return {role["slug"]: role for role in CAREER_ROLES_CATALOGUE}


def get_role_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    for role in CAREER_ROLES_CATALOGUE:
        if role["slug"] == slug:
            return role
    return None
