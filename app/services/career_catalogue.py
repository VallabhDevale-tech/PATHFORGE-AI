"""
PATHFORGE AI - Career Role Catalogue
Predefined, structured, and expandable catalogue of 13 primary career roles
used by Feature 2 (Career Path Recommender), Feature 3 (Skill Gap Analyzer),
Feature 4 (Roadmaps), Feature 5 (Projects), and Feature 6 (Adaptive Learning).
"""

from typing import Dict, List, Any, Optional

PROFICIENCY_LEVELS = {
    1: "Beginner",
    2: "Intermediate",
    3: "Advanced",
    4: "Expert"
}

CAREER_ROLES_CATALOGUE: List[Dict[str, Any]] = [
    {
        "slug": "software-developer",
        "title": "Software Developer",
        "category": "Software Engineering",
        "description": "Designs, writes, tests, and maintains robust computer software and application systems using modern programming languages and architectural patterns.",
        "skill_requirements": [
            {"name": "Python", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Core scripting, automation, backend logic, and algorithmic problem solving."},
            {"name": "Java", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Enterprise backend systems, object-oriented design, and multithreaded services."},
            {"name": "Data Structures & Algorithms", "category": "Core Computer Science", "required_level": 3, "priority": "High", "why_matters": "Critical for time/space computational efficiency and standard engineering interviews."},
            {"name": "Object-Oriented Programming (OOP)", "category": "Core Computer Science", "required_level": 3, "priority": "High", "why_matters": "Ensures modular, reusable, testable, and maintainable software architecture."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 2, "priority": "High", "why_matters": "Essential for collaboration, branching workflows, pull requests, and code versioning."},
            {"name": "SQL", "category": "Databases & Storage", "required_level": 2, "priority": "Medium", "why_matters": "Querying relational databases, structuring transactions, and aggregating business records."},
            {"name": "REST API", "category": "Backend Engineering", "required_level": 2, "priority": "Medium", "why_matters": "Designing and consuming clean web services across microservices and clients."},
            {"name": "Unit Testing", "category": "Quality Assurance", "required_level": 2, "priority": "Medium", "why_matters": "Automating test suites with pytest/JUnit to prevent regressions in production."},
            {"name": "Linux", "category": "Operating Systems", "required_level": 2, "priority": "Low", "why_matters": "Server navigation, bash scripting, file permissions, and process management."},
            {"name": "Docker", "category": "Cloud & DevOps", "required_level": 2, "priority": "Low", "why_matters": "Containerizing applications for consistent deployment across local and cloud environments."}
        ],
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
        "description": "Constructs visually compelling, responsive, and accessible user interfaces for web applications using client-side technologies.",
        "skill_requirements": [
            {"name": "JavaScript", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "The core language of web interactivity, asynchronous event loops, and DOM manipulation."},
            {"name": "TypeScript", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Type safety, robust refactoring, and enterprise frontend scalability."},
            {"name": "HTML & CSS", "category": "Frontend Technologies", "required_level": 3, "priority": "High", "why_matters": "Semantic structure, responsive styling, flexbox/grid layouts, and accessibility standards."},
            {"name": "React", "category": "Frameworks & Libraries", "required_level": 3, "priority": "High", "why_matters": "Industry standard component-based UI development, hooks, and state management."},
            {"name": "Responsive Design", "category": "Frontend Technologies", "required_level": 3, "priority": "High", "why_matters": "Delivering seamless user experiences across mobile, tablet, and desktop viewports."},
            {"name": "Next.js", "category": "Frameworks & Libraries", "required_level": 2, "priority": "Medium", "why_matters": "Server-side rendering (SSR), static site generation (SSG), and modern full-stack routing."},
            {"name": "REST API Integration", "category": "Backend Integration", "required_level": 2, "priority": "Medium", "why_matters": "Connecting frontend client state with backend JSON APIs and handling async states."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 2, "priority": "High", "why_matters": "Version control, branching, and team collaboration on UI codebases."},
            {"name": "Tailwind CSS / Bootstrap", "category": "Frontend Technologies", "required_level": 2, "priority": "Medium", "why_matters": "Rapid prototyping and maintaining consistent UI design systems and utility classes."},
            {"name": "Web Performance & Accessibility", "category": "Quality Assurance", "required_level": 2, "priority": "Low", "why_matters": "Lighthouse audits, core web vitals, and WCAG accessibility compliance."}
        ],
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
        "skill_requirements": [
            {"name": "Python", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Writing clean, performant server logic, async services, and microservices."},
            {"name": "FastAPI", "category": "Frameworks & Libraries", "required_level": 3, "priority": "High", "why_matters": "High-performance async REST APIs, automatic OpenAPI documentation, and Pydantic validation."},
            {"name": "SQL & PostgreSQL", "category": "Databases & Storage", "required_level": 3, "priority": "High", "why_matters": "Relational data modeling, ACID transactions, complex joins, and index optimization."},
            {"name": "REST API Design", "category": "Backend Engineering", "required_level": 3, "priority": "High", "why_matters": "Crafting clean HTTP contracts, status codes, pagination, and error responses."},
            {"name": "Data Modeling", "category": "Databases & Storage", "required_level": 3, "priority": "High", "why_matters": "Schema normalization, entity relationships, migrations, and constraint integrity."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 2, "priority": "High", "why_matters": "Source control and collaborative engineering workflows."},
            {"name": "Docker", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Containerizing backend services for reliable execution across environments."},
            {"name": "Redis & Caching", "category": "Databases & Storage", "required_level": 2, "priority": "Medium", "why_matters": "In-memory caching, session storage, and rate-limiting high-traffic endpoints."},
            {"name": "Authentication & JWT", "category": "Security", "required_level": 2, "priority": "Medium", "why_matters": "Securing endpoints with OAuth2, token verification, and role-based permissions."},
            {"name": "Linux", "category": "Operating Systems", "required_level": 2, "priority": "Low", "why_matters": "Deploying servers, environment variables, systemd services, and log analysis."}
        ],
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
        "skill_requirements": [
            {"name": "JavaScript", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Primary frontend language and full-stack runtime capability."},
            {"name": "TypeScript", "category": "Programming Languages", "required_level": 2, "priority": "High", "why_matters": "Type-safe scalability, interface contracts, and robust codebases."},
            {"name": "Python", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Backend service development, data processing, and scripting."},
            {"name": "React", "category": "Frameworks & Libraries", "required_level": 3, "priority": "High", "why_matters": "Component-based web client architecture and interactive user dashboards."},
            {"name": "FastAPI", "category": "Frameworks & Libraries", "required_level": 3, "priority": "High", "why_matters": "High-throughput async server architecture and API endpoints."},
            {"name": "SQL & Relational Databases", "category": "Databases & Storage", "required_level": 3, "priority": "High", "why_matters": "Designing application schemas, storing business data, and writing performant queries."},
            {"name": "HTML & CSS", "category": "Frontend Technologies", "required_level": 3, "priority": "High", "why_matters": "Core presentation layer, semantic structure, and responsive mobile-first layouts."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 2, "priority": "High", "why_matters": "Tracking changes and shipping production updates reliably."},
            {"name": "REST API Integration", "category": "Backend Engineering", "required_level": 3, "priority": "High", "why_matters": "Connecting client-side states with server endpoints seamlessly."},
            {"name": "Docker", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Packaging multi-container applications (frontend + backend + database)."},
            {"name": "Cloud Deployment", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Deploying apps to cloud hosting providers with automated CI/CD pipelines."}
        ],
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
        "skill_requirements": [
            {"name": "Python", "category": "Programming Languages", "required_level": 4, "priority": "High", "why_matters": "Mastery of Python idioms, data structures, generators, decorators, and memory model."},
            {"name": "OOP in Python", "category": "Core Computer Science", "required_level": 3, "priority": "High", "why_matters": "Writing clean class hierarchies, abstraction layers, and design patterns."},
            {"name": "FastAPI", "category": "Frameworks & Libraries", "required_level": 3, "priority": "High", "why_matters": "Modern async framework of choice for Python web APIs and microservices."},
            {"name": "SQL & PostgreSQL", "category": "Databases & Storage", "required_level": 3, "priority": "High", "why_matters": "Database querying, ORMs (SQLAlchemy), migrations (Alembic), and connections."},
            {"name": "REST API", "category": "Backend Engineering", "required_level": 3, "priority": "High", "why_matters": "Standard architectural contract for microservices and API gateways."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 2, "priority": "High", "why_matters": "Version control, branching, release tags, and team reviews."},
            {"name": "pytest & Unit Testing", "category": "Quality Assurance", "required_level": 2, "priority": "Medium", "why_matters": "Writing comprehensive test suites, mocks, fixtures, and parameterized tests."},
            {"name": "Pandas", "category": "Data & Analytics", "required_level": 2, "priority": "Medium", "why_matters": "Data parsing, tabular manipulation, data cleaning, and export routines."},
            {"name": "Asyncio", "category": "Programming Languages", "required_level": 2, "priority": "Medium", "why_matters": "Non-blocking event loop execution, tasks, and high-concurrency operations."},
            {"name": "Docker", "category": "Cloud & DevOps", "required_level": 2, "priority": "Low", "why_matters": "Containerizing Python runtimes and resolving dependency environments."}
        ],
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
        "skill_requirements": [
            {"name": "SQL", "category": "Databases & Storage", "required_level": 3, "priority": "High", "why_matters": "Advanced queries, aggregations, window functions, CTEs, and cohort analyses."},
            {"name": "Excel & Spreadsheets", "category": "Analytics & Reporting", "required_level": 3, "priority": "High", "why_matters": "Financial modeling, pivot tables, VLOOKUP/XLOOKUP, and rapid metric calculations."},
            {"name": "Python", "category": "Programming Languages", "required_level": 2, "priority": "High", "why_matters": "Scripting data transformation workflows and automating repetitive reporting."},
            {"name": "Pandas", "category": "Data & Analytics", "required_level": 3, "priority": "High", "why_matters": "DataFrame manipulation, handling missing data, grouping, and feature derivation."},
            {"name": "Data Visualization", "category": "Analytics & Reporting", "required_level": 3, "priority": "High", "why_matters": "Communicating insights via Matplotlib, Seaborn, and intuitive business visual charts."},
            {"name": "Tableau / Power BI", "category": "Business Intelligence", "required_level": 2, "priority": "Medium", "why_matters": "Building executive BI dashboards with drill-downs and real-time KPI filters."},
            {"name": "Statistics & Probability", "category": "Core Analytics", "required_level": 2, "priority": "Medium", "why_matters": "Hypothesis testing, A/B testing evaluation, mean/median distributions, and sampling."},
            {"name": "Exploratory Data Analysis (EDA)", "category": "Core Analytics", "required_level": 3, "priority": "High", "why_matters": "Uncovering underlying data patterns, anomalies, correlations, and outliers."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 1, "priority": "Low", "why_matters": "Maintaining reproducible analysis notebooks and SQL query repositories."}
        ],
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
        "skill_requirements": [
            {"name": "Python", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Primary computing language for data science, modeling, and prototyping."},
            {"name": "Statistics & Probability", "category": "Core Analytics", "required_level": 3, "priority": "High", "why_matters": "Rigorous foundation in regression, distributions, significance testing, and Bayes theorem."},
            {"name": "SQL", "category": "Databases & Storage", "required_level": 3, "priority": "High", "why_matters": "Extracting large feature datasets from data warehouses and relational engines."},
            {"name": "Pandas & NumPy", "category": "Data & Analytics", "required_level": 3, "priority": "High", "why_matters": "Vectorized computations, matrix math, and extensive dataset transformations."},
            {"name": "Machine Learning", "category": "Artificial Intelligence", "required_level": 3, "priority": "High", "why_matters": "Supervised and unsupervised algorithms (trees, clustering, SVMs, ensembles)."},
            {"name": "Scikit-Learn", "category": "Frameworks & Libraries", "required_level": 3, "priority": "High", "why_matters": "Constructing end-to-end ML pipelines, cross-validation, and hyperparameter tuning."},
            {"name": "Feature Engineering", "category": "Data & Analytics", "required_level": 2, "priority": "Medium", "why_matters": "Scaling, encoding, dimensionality reduction (PCA), and domain feature construction."},
            {"name": "Data Visualization", "category": "Analytics & Reporting", "required_level": 2, "priority": "Medium", "why_matters": "Translating model interpretations and predictions to business stakeholders."},
            {"name": "Deep Learning Fundamentals", "category": "Artificial Intelligence", "required_level": 2, "priority": "Low", "why_matters": "Neural network basics, activation functions, and backpropagation concepts."}
        ],
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
        "skill_requirements": [
            {"name": "Python", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Production model code, data pipelines, inference services, and tool integration."},
            {"name": "Machine Learning", "category": "Artificial Intelligence", "required_level": 3, "priority": "High", "why_matters": "Theoretical foundations and applied mastery of predictive modeling architectures."},
            {"name": "Scikit-Learn", "category": "Frameworks & Libraries", "required_level": 3, "priority": "High", "why_matters": "Production classification, regression, and preprocessing pipelines."},
            {"name": "Deep Learning", "category": "Artificial Intelligence", "required_level": 2, "priority": "High", "why_matters": "CNNs, RNNs, Transformers, and representation learning architectures."},
            {"name": "TensorFlow or PyTorch", "category": "Frameworks & Libraries", "required_level": 2, "priority": "High", "why_matters": "Building, training, and optimizing computational graph deep learning models."},
            {"name": "NumPy & Pandas", "category": "Data & Analytics", "required_level": 3, "priority": "High", "why_matters": "High-speed array manipulation and feature dataset manipulation."},
            {"name": "SQL", "category": "Databases & Storage", "required_level": 2, "priority": "Medium", "why_matters": "Accessing training datasets and relational feature stores."},
            {"name": "MLOps & Model Serving", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Deploying models to low-latency REST endpoints, monitoring drift, and CI/CD for ML."},
            {"name": "Docker", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Packaging reproducible environments and inference containers."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 2, "priority": "High", "why_matters": "Tracking model experiments, codebases, and configurations."}
        ],
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
        "skill_requirements": [
            {"name": "Python", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Backend engineering and orchestration of AI SDKs, agents, and pipelines."},
            {"name": "AI Integration & LLM APIs", "category": "Artificial Intelligence", "required_level": 3, "priority": "High", "why_matters": "Integrating Claude, OpenAI, and open models using structured tool calling and streaming."},
            {"name": "Prompt Engineering", "category": "Artificial Intelligence", "required_level": 3, "priority": "High", "why_matters": "Few-shot prompting, system prompts, role delimitation, and structured JSON output guarantees."},
            {"name": "FastAPI & REST APIs", "category": "Backend Engineering", "required_level": 3, "priority": "High", "why_matters": "Serving real-time inference, webhook handling, and AI microservices."},
            {"name": "Vector Databases & Embeddings", "category": "Databases & Storage", "required_level": 2, "priority": "High", "why_matters": "Generating embeddings and indexing high-dimensional vectors for semantic similarity."},
            {"name": "RAG Architectures", "category": "Artificial Intelligence", "required_level": 2, "priority": "High", "why_matters": "Retrieval-Augmented Generation to ground LLMs in external proprietary knowledge."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 2, "priority": "High", "why_matters": "Version control and collaborative AI codebase management."},
            {"name": "Docker", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Containerizing AI microservices with model dependencies."},
            {"name": "LangChain / LlamaIndex", "category": "Frameworks & Libraries", "required_level": 2, "priority": "Medium", "why_matters": "Composable agent chains, document loaders, chunkers, and memory components."}
        ],
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
        "skill_requirements": [
            {"name": "AWS / Cloud Computing", "category": "Cloud & DevOps", "required_level": 3, "priority": "High", "why_matters": "Core cloud compute (EC2), serverless (Lambda), storage (S3), and load balancers."},
            {"name": "Linux Systems Administration", "category": "Operating Systems", "required_level": 3, "priority": "High", "why_matters": "Command line administration, security policies, SSH keys, cron jobs, and daemons."},
            {"name": "Cloud Networking & VPCs", "category": "Security & Networking", "required_level": 3, "priority": "High", "why_matters": "Configuring subnets, CIDR blocks, route tables, internet gateways, and DNS (Route 53)."},
            {"name": "Cloud Security & IAM", "category": "Security & Networking", "required_level": 3, "priority": "High", "why_matters": "Least-privilege access, IAM roles, security groups, KMS encryption, and audit logs."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 2, "priority": "High", "why_matters": "Infrastructure code versioning, branch protections, and PR reviews."},
            {"name": "Terraform & IaC", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Infrastructure as Code for provisioning repeatable cloud topologies declaratively."},
            {"name": "Docker & Containers", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Container orchestration fundamentals, image builds, and registry management."},
            {"name": "Python or Bash Scripting", "category": "Programming Languages", "required_level": 2, "priority": "Medium", "why_matters": "Automating cloud operations, backup routines, and resource cleanup scripts."},
            {"name": "Kubernetes", "category": "Cloud & DevOps", "required_level": 2, "priority": "Low", "why_matters": "Managing pod scheduling, ingress controllers, config maps, and deployments."}
        ],
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
        "skill_requirements": [
            {"name": "Linux", "category": "Operating Systems", "required_level": 3, "priority": "High", "why_matters": "Core platform powering production containers and cloud virtual instances."},
            {"name": "CI/CD Pipelines", "category": "Cloud & DevOps", "required_level": 3, "priority": "High", "why_matters": "Building automated testing, building, and deployment workflows (GitHub Actions, GitLab)."},
            {"name": "Docker & Containerization", "category": "Cloud & DevOps", "required_level": 3, "priority": "High", "why_matters": "Multi-stage builds, lightweight images, security scanning, and layer caching."},
            {"name": "Git", "category": "Tools & Version Control", "required_level": 3, "priority": "High", "why_matters": "GitOps delivery paradigms and repository automation."},
            {"name": "Bash & Python Scripting", "category": "Programming Languages", "required_level": 3, "priority": "High", "why_matters": "Writing operational automation, health check scripts, and CI runners."},
            {"name": "Cloud Fundamentals (AWS/Azure)", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Hosting clusters, object stores, DNS, and load balancers on major providers."},
            {"name": "Kubernetes", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Cluster orchestration, service discovery, rolling updates, and autoscaling."},
            {"name": "Terraform", "category": "Cloud & DevOps", "required_level": 2, "priority": "Medium", "why_matters": "Declarative infrastructure management and cloud resource life-cycles."},
            {"name": "Prometheus & Grafana Observability", "category": "Monitoring & Quality", "required_level": 2, "priority": "Medium", "why_matters": "Real-time metrics collection, dashboard alerting, and latency monitoring."}
        ],
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
        "skill_requirements": [
            {"name": "Computer Networking (TCP/IP)", "category": "Security & Networking", "required_level": 3, "priority": "High", "why_matters": "Deep understanding of OSI layers, IP routing, ports, protocols, and packet headers."},
            {"name": "Linux & OS Security", "category": "Operating Systems", "required_level": 3, "priority": "High", "why_matters": "System hardening, user privileges, file audits, and kernel security modules."},
            {"name": "Vulnerability Assessment", "category": "Security & Risk", "required_level": 3, "priority": "High", "why_matters": "Scanning systems for CVEs, assessing CVSS risk scores, and managing patches."},
            {"name": "Security Principles & Threat Modeling", "category": "Security & Risk", "required_level": 3, "priority": "High", "why_matters": "CIA triad, defense-in-depth, zero trust architecture, and threat surfaces."},
            {"name": "Firewalls & Network Defense", "category": "Security & Networking", "required_level": 3, "priority": "High", "why_matters": "Configuring access control lists (ACLs), IDS/IPS rules, and perimeter security."},
            {"name": "SIEM & Log Analysis", "category": "Security & Risk", "required_level": 2, "priority": "Medium", "why_matters": "Aggregating event logs, detecting anomalies, and correlating threat alerts."},
            {"name": "Wireshark & Packet Inspection", "category": "Tools & Version Control", "required_level": 2, "priority": "Medium", "why_matters": "Capturing live traffic and diagnosing malicious payload transmissions."},
            {"name": "Python for Security", "category": "Programming Languages", "required_level": 2, "priority": "Medium", "why_matters": "Writing security audit scripts, log parsers, and automated recon tasks."}
        ],
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
        "skill_requirements": [
            {"name": "UI/UX Design Principles", "category": "Design & Product", "required_level": 3, "priority": "High", "why_matters": "Visual hierarchy, typography scale, whitespace, contrast, and cognitive load management."},
            {"name": "Figma & Prototyping", "category": "Design Tools", "required_level": 3, "priority": "High", "why_matters": "Industry leading vector tool for components, auto-layouts, variants, and interactive prototypes."},
            {"name": "Wireframing & Information Architecture", "category": "Design & Product", "required_level": 3, "priority": "High", "why_matters": "Low-fidelity wireframes, sitemaps, user journey flows, and task navigation."},
            {"name": "User Research & Usability Testing", "category": "User Research", "required_level": 3, "priority": "High", "why_matters": "Qualitative interviews, usability observation sessions, and synthesis into personas."},
            {"name": "Design Systems", "category": "Design & Product", "required_level": 3, "priority": "High", "why_matters": "Building tokens, reusable component libraries, and cross-team design guidelines."},
            {"name": "HTML & CSS Fundamentals", "category": "Frontend Technologies", "required_level": 2, "priority": "Medium", "why_matters": "Understanding browser rendering constraints and effectively communicating with frontend engineers."},
            {"name": "Visual Communication", "category": "Design & Product", "required_level": 3, "priority": "High", "why_matters": "Color theory, iconography, brand consistency, and high-impact visual storytelling."}
        ],
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

# Ensure backward compatibility with Feature 2 (Career Recommender)
for _role in CAREER_ROLES_CATALOGUE:
    if "required_skills" not in _role:
        _role["required_skills"] = [
            s["name"] for s in _role["skill_requirements"] if s["priority"] == "High"
        ]
    if "recommended_skills" not in _role:
        _role["recommended_skills"] = [
            s["name"] for s in _role["skill_requirements"] if s["priority"] != "High"
        ]


def get_catalogue_dict() -> Dict[str, Dict[str, Any]]:
    return {role["slug"]: role for role in CAREER_ROLES_CATALOGUE}


def get_role_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    for role in CAREER_ROLES_CATALOGUE:
        if role["slug"] == slug:
            return role
    return None
