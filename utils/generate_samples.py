import os
import fitz  # PyMuPDF

# Define the 10 candidate profiles
CANDIDATES = [
    {
        "name": "Jane Doe",
        "title": "Senior Backend Engineer",
        "email": "jane.doe@email.com",
        "phone": "+1-555-0101",
        "linkedin": "linkedin.com/in/janedoe-backend",
        "text": (
            "JANE DOE\n"
            "Senior Backend Engineer | Python Expert\n"
            "Email: jane.doe@email.com | Phone: +1-555-0101 | LinkedIn: linkedin.com/in/janedoe-backend\n\n"
            "SUMMARY\n"
            "Distinguished Backend Engineer with 8 years of experience building scalable architectures and cloud microservices. "
            "Expert in Python backend design, databases, APIs, and cloud deployments.\n\n"
            "EXPERIENCE\n"
            "Enterprise Solutions - Lead Backend Developer (2021 - Present)\n"
            "- Architected microservices using Python, Django, FastAPI, and PostgreSQL, increasing system throughput by 50%.\n"
            "- Managed AWS cloud infrastructure using Terraform, Docker, and Kubernetes.\n"
            "- Implemented Git CI/CD deployment pipelines using GitHub Actions.\n\n"
            "WebScale Corp - Software Engineer (2017 - 2021)\n"
            "- Built web APIs using Flask and Python, integrated with MySQL and Redis caches.\n"
            "- Optimized slow SQL queries, reducing page load times by 40%.\n\n"
            "EDUCATION\n"
            "Master of Science in Computer Science - University of Washington (2015 - 2017)\n"
            "Bachelor of Science in Software Engineering - Oregon State University (2011 - 2015)\n\n"
            "SKILLS\n"
            "Languages: Python, SQL, JavaScript, HTML, CSS\n"
            "Frameworks: Django, Flask, FastAPI\n"
            "Databases: PostgreSQL, MySQL, Redis\n"
            "Cloud/DevOps: AWS, Docker, Kubernetes, Terraform, Git, CI/CD"
        )
    },
    {
        "name": "Alice Smith",
        "title": "Fullstack Developer",
        "email": "alice.smith@email.com",
        "phone": "+1-555-0102",
        "linkedin": "linkedin.com/in/alicesmith-dev",
        "text": (
            "ALICE SMITH\n"
            "Fullstack Software Developer\n"
            "Email: alice.smith@email.com | Phone: +1-555-0102 | LinkedIn: linkedin.com/in/alicesmith-dev\n\n"
            "SUMMARY\n"
            "Dynamic Fullstack Developer with 4 years of experience building modern user interfaces and backend APIs. "
            "Strong skillset across both frontend components and server setups.\n\n"
            "EXPERIENCE\n"
            "AppStudio Inc - Fullstack Developer (2022 - Present)\n"
            "- Designed responsive user interfaces using React, TypeScript, and CSS Tailwind.\n"
            "- Built server controllers using Node.js and Express, connected to MongoDB databases.\n"
            "- Written unit and integration tests using Jest and Webpack configurations.\n\n"
            "CoreWeb Solutions - Junior Developer (2020 - 2022)\n"
            "- Built layout pages using HTML, Sass CSS, and JavaScript.\n"
            "- Maintained databases using SQLite and MySQL schemas.\n\n"
            "EDUCATION\n"
            "Bachelor of Science in Computer Science - University of California, Irvine (2016 - 2020)\n\n"
            "SKILLS\n"
            "Languages: JavaScript, TypeScript, HTML, CSS, SQL\n"
            "Frameworks: React, Express, Node.js, TailwindCSS, Bootstrap\n"
            "Databases: MongoDB, MySQL, SQLite\n"
            "Tools: Git, Vite, Webpack, Postman"
        )
    },
    {
        "name": "Bob Johnson",
        "title": "DevOps Engineer",
        "email": "bob.johnson@email.com",
        "phone": "+1-555-0103",
        "linkedin": "linkedin.com/in/bobjohnson-devops",
        "text": (
            "BOB JOHNSON\n"
            "Senior DevOps & Infrastructure Engineer\n"
            "Email: bob.johnson@email.com | Phone: +1-555-0103 | LinkedIn: linkedin.com/in/bobjohnson-devops\n\n"
            "SUMMARY\n"
            "Dedicated DevOps Engineer with 6 years of expertise in automation, cloud computing, container orchestration, and continuous integration pipelines. "
            "Strong advocate of Infrastructure as Code (IaC).\n\n"
            "EXPERIENCE\n"
            "CloudOps Labs - Lead DevOps Architect (2022 - Present)\n"
            "- Built cloud architectures in AWS using Terraform, Ansible, and Docker containers.\n"
            "- Maintained production Kubernetes clusters (EKS), optimizing resource allocation.\n"
            "- Built automated pipeline suites using Jenkins, GitLab CI, and GitHub Actions.\n\n"
            "SaaSify - Systems Administrator (2018 - 2022)\n"
            "- Managed Linux server clusters, running Nginx and Apache reverse proxies.\n"
            "- Setup system monitoring dashboards using Prometheus and Grafana dashboards.\n"
            "EDUCATION\n"
            "Bachelor of Science in Computer Engineering - Texas A&M University (2014 - 2018)\n\n"
            "SKILLS\n"
            "Cloud: AWS, Azure, GCP\n"
            "DevOps: Docker, Kubernetes, Terraform, Ansible, Jenkins, CI/CD\n"
            "Servers: Linux, Nginx, Apache, Prometheus, Grafana\n"
            "Languages: Bash, Python, Go"
        )
    },
    {
        "name": "Charlie Brown",
        "title": "Junior Data Scientist",
        "email": "charlie.brown@email.com",
        "phone": "+1-555-0104",
        "linkedin": "linkedin.com/in/charliebrown-ds",
        "text": (
            "CHARLIE BROWN\n"
            "Junior Data Scientist / Analyst\n"
            "Email: charlie.brown@email.com | Phone: +1-555-0104 | LinkedIn: linkedin.com/in/charliebrown-ds\n\n"
            "SUMMARY\n"
            "Enthusiastic Data Scientist with 2 years of experience analyzing complex datasets, training machine learning models, and building analytical report visualizations.\n\n"
            "EXPERIENCE\n"
            "Insight Analytics - Junior Data Analyst (2023 - Present)\n"
            "- Analyzed large user datasets using Python, Pandas, and NumPy modules.\n"
            "- Trained predictive regression and classification models using Scikit-Learn.\n"
            "- Created data visual dashboards using Matplotlib, Seaborn, and Jupyter notebooks.\n\n"
            "Research Labs - Graduate Intern (2022 - 2023)\n"
            "- Conducted text preprocessing and sentiment modeling using NLTK and SpaCy libraries.\n\n"
            "EDUCATION\n"
            "Master of Science in Data Science - Boston University (2021 - 2023)\n"
            "Bachelor of Science in Mathematics - Boston College (2017 - 2021)\n\n"
            "SKILLS\n"
            "Languages: Python, R, SQL\n"
            "Libraries: Pandas, NumPy, Scikit-Learn, NLTK, SpaCy, Matplotlib, Seaborn\n"
            "Tools: Jupyter Notebooks, Git, SQL Server"
        )
    },
    {
        "name": "David Miller",
        "title": "Frontend Engineer",
        "email": "david.miller@email.com",
        "phone": "+1-555-0105",
        "linkedin": "linkedin.com/in/davidmiller-front",
        "text": (
            "DAVID MILLER\n"
            "Frontend Engineer | React Specialist\n"
            "Email: david.miller@email.com | Phone: +1-555-0105 | LinkedIn: linkedin.com/in/davidmiller-front\n\n"
            "SUMMARY\n"
            "UI/UX-focused Frontend Developer with 5 years of experience creating highly responsive web interfaces, optimizing render pipelines, and setting up design systems.\n\n"
            "EXPERIENCE\n"
            "DesignCraft Inc - Frontend Developer (2021 - Present)\n"
            "- Programmed single-page applications (SPAs) using React, Next.js, Webpack, and Sass.\n"
            "- Built custom components libraries using TailwindCSS and styled-components.\n"
            "- Collaborated with UI designers on responsive screen breakpoints.\n\n"
            "PixelPerfect Agency - UI Programmer (2019 - 2021)\n"
            "- Coded frontend websites using Vanilla JS, HTML5, CSS3, and Bootstrap grids.\n"
            "EDUCATION\n"
            "Bachelor of Arts in Interactive Media Design - University of Washington (2015 - 2019)\n\n"
            "SKILLS\n"
            "Languages: HTML5, CSS3, JavaScript, TypeScript\n"
            "Libraries/Frameworks: React, Next.js, Redux, TailwindCSS, Bootstrap, Sass\n"
            "Build Tools: Webpack, Vite, Babel, npm, Git"
        )
    },
    {
        "name": "Eva Green",
        "title": "Technical Product Manager",
        "email": "eva.green@email.com",
        "phone": "+1-555-0106",
        "linkedin": "linkedin.com/in/evagreen-pm",
        "text": (
            "EVA GREEN\n"
            "Technical Product Manager\n"
            "Email: eva.green@email.com | Phone: +1-555-0106 | LinkedIn: linkedin.com/in/evagreen-pm\n\n"
            "SUMMARY\n"
            "Strategic Technical Product Manager with 6 years of experience guiding cross-functional teams, defining product roadmaps, and managing Agile sprints.\n\n"
            "EXPERIENCE\n"
            "FinTech Solutions - Product Owner (2021 - Present)\n"
            "- Gathered specifications, wrote User Stories, and organized backlogs in Jira.\n"
            "- Led daily Scrum standups, planning sprints, and retrospective sessions.\n"
            "- Documented product specifications using Confluence wiki pages.\n\n"
            "DevLabs - Scrum Master (2018 - 2021)\n"
            "- Guided engineering teams through project lifecycles, boosting delivery velocity by 25%.\n"
            "EDUCATION\n"
            "Bachelor of Science in Business Information Systems - Indiana University (2014 - 2018)\n\n"
            "SKILLS\n"
            "Methodologies: Agile, Scrum, Kanban, Project Management\n"
            "Tools: Jira, Confluence, Trello, Figma\n"
            "Soft Skills: Leadership, Communication, Negotiation, Teamwork"
        )
    },
    {
        "name": "Frank Wright",
        "title": "Senior Java Developer",
        "email": "frank.wright@email.com",
        "phone": "+1-555-0107",
        "linkedin": "linkedin.com/in/frankwright-java",
        "text": (
            "FRANK WRIGHT\n"
            "Senior Enterprise Java Developer\n"
            "Email: frank.wright@email.com | Phone: +1-555-0107 | LinkedIn: linkedin.com/in/frankwright-java\n\n"
            "SUMMARY\n"
            "Enterprise Engineer with 9 years of experience designing robust, high-availability software using Java and JVM architectures. Core backend specialist.\n\n"
            "EXPERIENCE\n"
            "LegacyCorp Systems - Lead Java Developer (2020 - Present)\n"
            "- Developed secure SOAP and REST APIs using Spring Boot, Spring Security, and Maven.\n"
            "- Configured relational databases using Oracle and Microsoft SQL Server.\n"
            "- Managed application builds and deployments using Jenkins and GitLab CI pipelines.\n\n"
            "Global Solutions - Java Programmer (2015 - 2020)\n"
            "- Maintained databases using Java Hibernate ORM frameworks and MySQL databases.\n"
            "EDUCATION\n"
            "Bachelor of Science in Computer Science - University of Illinois (2011 - 2015)\n\n"
            "SKILLS\n"
            "Languages: Java, SQL, XML, HTML\n"
            "Frameworks: Spring Boot, Spring MVC, Hibernate\n"
            "Databases: Oracle, Microsoft SQL Server, MySQL, SQLite\n"
            "DevOps: Git, Jenkins, Maven, Docker"
        )
    },
    {
        "name": "Grace Hopper",
        "title": "Cloud Architect",
        "email": "grace.hopper@email.com",
        "phone": "+1-555-0108",
        "linkedin": "linkedin.com/in/gracehopper-cloud",
        "text": (
            "GRACE HOPPER\n"
            "Senior Cloud Architect & Golang Dev\n"
            "Email: grace.hopper@email.com | Phone: +1-555-0108 | LinkedIn: linkedin.com/in/gracehopper-cloud\n\n"
            "SUMMARY\n"
            "AWS Certified Solutions Architect with 7 years of design experience. Highly proficient in Infrastructure as Code (IaC) and building Go backend APIs.\n\n"
            "EXPERIENCE\n"
            "Apex Cloud Services - Cloud Solutions Architect (2021 - Present)\n"
            "- Designed AWS infrastructures using VPC, EC2, ECS, Lambda, IAM, and S3 resources.\n"
            "- Coded high-speed systems using Go (Golang) and gRPC interfaces.\n"
            "- Provisioned modular stacks using Terraform, Kubernetes, and Helm charts.\n\n"
            "NetScale Tech - Cloud Programmer (2017 - 2021)\n"
            "- Built automation tasks using Go, Python, and Serverless frameworks on AWS.\n"
            "EDUCATION\n"
            "Bachelor of Science in Cyber Security - Penn State University (2013 - 2017)\n\n"
            "SKILLS\n"
            "Languages: Go, Golang, Python, Bash, SQL\n"
            "Cloud Providers: AWS, Google Cloud Platform, Azure\n"
            "DevOps Tools: Terraform, Kubernetes, Docker, Helm, Git, GitLab CI"
        )
    },
    {
        "name": "Henry Ford",
        "title": "Systems Administrator",
        "email": "henry.ford@email.com",
        "phone": "+1-555-0109",
        "linkedin": "linkedin.com/in/henryford-sysadmin",
        "text": (
            "HENRY FORD\n"
            "Linux Systems Administrator\n"
            "Email: henry.ford@email.com | Phone: +1-555-0109 | LinkedIn: linkedin.com/in/henryford-sysadmin\n\n"
            "SUMMARY\n"
            "Analytical Systems Administrator with 5 years of experience managing Linux OS kernels, configurations, network routers, and user permissions.\n\n"
            "EXPERIENCE\n"
            "InfraHost Systems - Linux Administrator (2022 - Present)\n"
            "- Maintained server networks, firewalls, routing protocols, and active user directories.\n"
            "- Wrote shell automation scripts using Bash, PowerShell, and basic Python scripts.\n"
            "- Resolved hardware failures, server logs errors, and user login access queries.\n\n"
            "SecureServer Inc - Support Administrator (2019 - 2022)\n"
            "- Installed Linux CentOS distributions, managing system security patch configurations.\n"
            "EDUCATION\n"
            "Associate Degree in Network Engineering - Austin Community College (2017 - 2019)\n\n"
            "SKILLS\n"
            "Operating Systems: Linux (CentOS, RedHat, Ubuntu), Windows Server\n"
            "Languages: Bash, PowerShell, Python\n"
            "Networking: TCP/IP, VPN, DNS, Firewalls, SSH, Active Directory\n"
            "Tools: Git, Vim, Nginx"
        )
    },
    {
        "name": "Ivy Watson",
        "title": "Senior AI Engineer",
        "email": "ivy.watson@email.com",
        "phone": "+1-555-0110",
        "linkedin": "linkedin.com/in/ivywatson-ai",
        "text": (
            "IVY WATSON\n"
            "Senior AI & Machine Learning Engineer\n"
            "Email: ivy.watson@email.com | Phone: +1-555-0110 | LinkedIn: linkedin.com/in/ivywatson-ai\n\n"
            "SUMMARY\n"
            "Innovative AI Specialist with 6 years of expertise building deep learning neural networks, natural language processors, and custom APIs in cloud runtimes.\n\n"
            "EXPERIENCE\n"
            "NeuraTech Labs - Lead AI Engineer (2022 - Present)\n"
            "- Built NLP classifiers and model endpoints using Hugging Face, PyTorch, and Python.\n"
            "- Developed high-performance API structures using FastAPI, Docker, and GCP.\n"
            "- Implemented deep neural models using TensorFlow, Pandas, and NumPy pipelines.\n\n"
            "ML Engine Corp - Backend ML Developer (2018 - 2022)\n"
            "- Cleaned huge vector databases, built training loops, and ran evaluations with Scikit-Learn.\n"
            "EDUCATION\n"
            "Master of Science in Artificial Intelligence - Carnegie Mellon University (2016 - 2018)\n"
            "Bachelor of Science in Computer Science - CMU (2012 - 2016)\n\n"
            "SKILLS\n"
            "Languages: Python, C++, SQL, R\n"
            "AI Libraries: PyTorch, TensorFlow, Hugging Face, Scikit-Learn, NumPy, Pandas\n"
            "Infrastructure: GCP, AWS, Docker, Git, REST API, WebSockets"
        )
    }
]

def generate_pdf_from_text(text: str, output_path: str):
    """
    Creates a text-based PDF file.
    """
    doc = fitz.open()
    page = doc.new_page()
    rect = fitz.Rect(40, 40, 560, 760)
    page.insert_textbox(
        rect, 
        text, 
        fontsize=10, 
        fontname="helv", 
        align=fitz.TEXT_ALIGN_LEFT
    )
    doc.save(output_path)
    doc.close()

def generate_all_samples(target_dir: str = "sample_resumes"):
    """
    Generates all 10 candidate PDFs inside the target directory.
    """
    os.makedirs(target_dir, exist_ok=True)
    print(f"Generating 10 candidate resume PDFs in: {os.path.abspath(target_dir)}...")
    
    for c in CANDIDATES:
        safe_name = c["name"].lower().replace(" ", "_")
        filename = f"{safe_name}_resume.pdf"
        filepath = os.path.join(target_dir, filename)
        generate_pdf_from_text(c["text"], filepath)
        print(f" -> Generated: {filename}")
        
    print("All sample resumes created successfully!\n")

if __name__ == "__main__":
    generate_all_samples()
