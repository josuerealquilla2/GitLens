import re
import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

CACHE_TTL       = 600   # 10 min — búsqueda por lenguaje (GitHub API)
CACHE_TTL_SHORT = 180   # 3 min  — búsqueda por texto

# ── Base de datos estática de repos populares ──────────────────────────────────
# No requiere API calls → respuesta instantánea sin rate limits
STATIC_REPOS = [
    {"id": 114695608, "name": "freeCodeCamp", "owner": "freeCodeCamp",
     "owner_avatar": "https://avatars.githubusercontent.com/u/9892522?v=4",
     "description": "freeCodeCamp.org's open-source codebase and curriculum. Learn to code for free.",
     "about": "freeCodeCamp.org's open-source codebase and curriculum. Learn to code for free.",
     "stars": 412000, "language": "TypeScript",
     "url": "https://github.com/freeCodeCamp/freeCodeCamp", "project_images": []},
    {"id": 21737465, "name": "awesome", "owner": "sindresorhus",
     "owner_avatar": "https://avatars.githubusercontent.com/u/170270?v=4",
     "description": " Awesome lists about all kinds of interesting topics",
     "about": " Awesome lists about all kinds of interesting topics",
     "stars": 345000, "language": None,
     "url": "https://github.com/sindresorhus/awesome", "project_images": []},
    {"id": 34526884, "name": "public-apis", "owner": "public-apis",
     "owner_avatar": "https://avatars.githubusercontent.com/u/51121562?v=4",
     "description": "A collective list of free APIs for use in software and web development",
     "about": "A collective list of free APIs for use in software and web development",
     "stars": 325000, "language": "Python",
     "url": "https://github.com/public-apis/public-apis", "project_images": []},
    {"id": 13491895, "name": "free-programming-books", "owner": "EbookFoundation",
     "owner_avatar": "https://avatars.githubusercontent.com/u/14127308?v=4",
     "description": "Freely available programming books",
     "about": "Freely available programming books",
     "stars": 342000, "language": None,
     "url": "https://github.com/EbookFoundation/free-programming-books", "project_images": []},
    {"id": 62197036, "name": "developer-roadmap", "owner": "kamranahmedse",
     "owner_avatar": "https://avatars.githubusercontent.com/u/4921183?v=4",
     "description": "Interactive roadmaps, guides and other educational content to help developers grow in their careers.",
     "about": "Interactive roadmaps, guides and other educational content to help developers grow in their careers.",
     "stars": 310000, "language": "TypeScript",
     "url": "https://github.com/kamranahmedse/developer-roadmap", "project_images": []},
    {"id": 58458382, "name": "coding-interview-university", "owner": "jwasham",
     "owner_avatar": "https://avatars.githubusercontent.com/u/536312?v=4",
     "description": "A complete computer science study plan to become a software engineer.",
     "about": "A complete computer science study plan to become a software engineer.",
     "stars": 310000, "language": None,
     "url": "https://github.com/jwasham/coding-interview-university", "project_images": []},
    {"id": 78816133, "name": "system-design-primer", "owner": "donnemartin",
     "owner_avatar": "https://avatars.githubusercontent.com/u/5458997?v=4",
     "description": "Learn how to design large-scale systems. Prep for the system design interview.",
     "about": "Learn how to design large-scale systems. Prep for the system design interview.",
     "stars": 295000, "language": "Python",
     "url": "https://github.com/donnemartin/system-design-primer", "project_images": []},
    {"id": 10270250, "name": "react", "owner": "facebook",
     "owner_avatar": "https://avatars.githubusercontent.com/u/69631?v=4",
     "description": "The library for web and native user interfaces.",
     "about": "The library for web and native user interfaces.",
     "stars": 232000, "language": "JavaScript",
     "url": "https://github.com/facebook/react", "project_images": []},
    {"id": 11730342, "name": "vue", "owner": "vuejs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/6128107?v=4",
     "description": " Vue.js is a progressive JavaScript framework for building UI on the web.",
     "about": " Vue.js is a progressive JavaScript framework for building UI on the web.",
     "stars": 208000, "language": "TypeScript",
     "url": "https://github.com/vuejs/vue", "project_images": []},
    {"id": 155220641, "name": "transformers", "owner": "huggingface",
     "owner_avatar": "https://avatars.githubusercontent.com/u/25720743?v=4",
     "description": " Transformers: State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX.",
     "about": " Transformers: State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX.",
     "stars": 142000, "language": "Python",
     "url": "https://github.com/huggingface/transformers", "project_images": []},
    {"id": 116656635, "name": "next.js", "owner": "vercel",
     "owner_avatar": "https://avatars.githubusercontent.com/u/14985020?v=4",
     "description": "The React Framework – created and maintained by Vercel.",
     "about": "The React Framework – created and maintained by Vercel.",
     "stars": 131000, "language": "JavaScript",
     "url": "https://github.com/vercel/next.js", "project_images": []},
    {"id": 20929025, "name": "TypeScript", "owner": "microsoft",
     "owner_avatar": "https://avatars.githubusercontent.com/u/6154722?v=4",
     "description": "TypeScript is a superset of JavaScript that compiles to clean JavaScript output.",
     "about": "TypeScript is a superset of JavaScript that compiles to clean JavaScript output.",
     "stars": 103000, "language": "TypeScript",
     "url": "https://github.com/microsoft/TypeScript", "project_images": []},
    {"id": 45717250, "name": "tensorflow", "owner": "tensorflow",
     "owner_avatar": "https://avatars.githubusercontent.com/u/15658638?v=4",
     "description": "An Open Source Machine Learning Framework for Everyone",
     "about": "An Open Source Machine Learning Framework for Everyone",
     "stars": 188000, "language": "Python",
     "url": "https://github.com/tensorflow/tensorflow", "project_images": []},
    {"id": 41881900, "name": "vscode", "owner": "microsoft",
     "owner_avatar": "https://avatars.githubusercontent.com/u/6154722?v=4",
     "description": "Visual Studio Code",
     "about": "Visual Studio Code – lightweight, powerful code editor from Microsoft.",
     "stars": 168000, "language": "TypeScript",
     "url": "https://github.com/microsoft/vscode", "project_images": []},
    {"id": 2126244, "name": "bootstrap", "owner": "twbs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/2918581?v=4",
     "description": "The most popular HTML, CSS, and JavaScript framework for responsive, mobile-first projects.",
     "about": "The most popular HTML, CSS, and JavaScript framework for responsive, mobile-first projects.",
     "stars": 172000, "language": "JavaScript",
     "url": "https://github.com/twbs/bootstrap", "project_images": []},
    {"id": 2325298, "name": "linux", "owner": "torvalds",
     "owner_avatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
     "description": "Linux kernel source tree",
     "about": "Linux kernel source tree – the core of the Linux operating system.",
     "stars": 190000, "language": "C",
     "url": "https://github.com/torvalds/linux", "project_images": []},
    {"id": 31792824, "name": "flutter", "owner": "flutter",
     "owner_avatar": "https://avatars.githubusercontent.com/u/14101776?v=4",
     "description": "Flutter makes it easy and fast to build beautiful apps for mobile and beyond",
     "about": "Flutter makes it easy and fast to build beautiful apps for mobile and beyond",
     "stars": 170000, "language": "Dart",
     "url": "https://github.com/flutter/flutter", "project_images": []},
    {"id": 43722861, "name": "Python", "owner": "TheAlgorithms",
     "owner_avatar": "https://avatars.githubusercontent.com/u/20487725?v=4",
     "description": "All algorithms implemented in Python",
     "about": "All algorithms implemented in Python – community-driven collection of algorithm implementations.",
     "stars": 196000, "language": "Python",
     "url": "https://github.com/TheAlgorithms/Python", "project_images": []},
    {"id": 1261813, "name": "ohmyzsh", "owner": "ohmyzsh",
     "owner_avatar": "https://avatars.githubusercontent.com/u/22552083?v=4",
     "description": " A delightful community-driven framework for managing your zsh configuration.",
     "about": " A delightful community-driven framework for managing your zsh configuration.",
     "stars": 177000, "language": "Shell",
     "url": "https://github.com/ohmyzsh/ohmyzsh", "project_images": []},
    {"id": 20580498, "name": "kubernetes", "owner": "kubernetes",
     "owner_avatar": "https://avatars.githubusercontent.com/u/13629408?v=4",
     "description": "Production-Grade Container Scheduling and Management",
     "about": "Production-Grade Container Scheduling and Management",
     "stars": 113000, "language": "Go",
     "url": "https://github.com/kubernetes/kubernetes", "project_images": []},
    {"id": 74997895, "name": "rust", "owner": "rust-lang",
     "owner_avatar": "https://avatars.githubusercontent.com/u/5430905?v=4",
     "description": "Empowering everyone to build reliable and efficient software.",
     "about": "Empowering everyone to build reliable and efficient software.",
     "stars": 101000, "language": "Rust",
     "url": "https://github.com/rust-lang/rust", "project_images": []},
    {"id": 27193779, "name": "node", "owner": "nodejs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/9950313?v=4",
     "description": "Node.js JavaScript runtime ",
     "about": "Node.js JavaScript runtime ",
     "stars": 110000, "language": "JavaScript",
     "url": "https://github.com/nodejs/node", "project_images": []},
    {"id": 65600975, "name": "pytorch", "owner": "pytorch",
     "owner_avatar": "https://avatars.githubusercontent.com/u/21003710?v=4",
     "description": "Tensors and Dynamic neural networks in Python with strong GPU acceleration",
     "about": "Tensors and Dynamic neural networks in Python with strong GPU acceleration",
     "stars": 89000, "language": "Python",
     "url": "https://github.com/pytorch/pytorch", "project_images": []},
    {"id": 293846753, "name": "tauri", "owner": "tauri-apps",
     "owner_avatar": "https://avatars.githubusercontent.com/u/54536011?v=4",
     "description": "Build smaller, faster, and more secure desktop and mobile applications with a web frontend.",
     "about": "Build smaller, faster, and more secure desktop and mobile applications with a web frontend.",
     "stars": 89000, "language": "Rust",
     "url": "https://github.com/tauri-apps/tauri", "project_images": []},
    {"id": 567760187, "name": "ui", "owner": "shadcn-ui",
     "owner_avatar": "https://avatars.githubusercontent.com/u/139895814?v=4",
     "description": "Beautifully designed components that you can copy and paste into your apps.",
     "about": "Beautifully designed components that you can copy and paste into your apps. Accessible. Customizable. Open Source.",
     "stars": 86000, "language": "TypeScript",
     "url": "https://github.com/shadcn-ui/ui", "project_images": []},
    {"id": 4164482, "name": "django", "owner": "django",
     "owner_avatar": "https://avatars.githubusercontent.com/u/27804?v=4",
     "description": "The Web framework for perfectionists with deadlines.",
     "about": "The Web framework for perfectionists with deadlines.",
     "stars": 83000, "language": "Python",
     "url": "https://github.com/django/django", "project_images": []},
    {"id": 74071631, "name": "svelte", "owner": "sveltejs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/23617963?v=4",
     "description": "web development for the rest of us",
     "about": "Svelte – cybernetically enhanced web apps. No virtual DOM, compiles to vanilla JS.",
     "stars": 81000, "language": "JavaScript",
     "url": "https://github.com/sveltejs/svelte", "project_images": []},
    {"id": 1863329, "name": "laravel", "owner": "laravel",
     "owner_avatar": "https://avatars.githubusercontent.com/u/958072?v=4",
     "description": "Laravel is a web application framework with expressive, elegant syntax.",
     "about": "Laravel is a web application framework with expressive, elegant syntax.",
     "stars": 80000, "language": "PHP",
     "url": "https://github.com/laravel/laravel", "project_images": []},
    {"id": 65030440, "name": "vite", "owner": "vitejs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/65625612?v=4",
     "description": "Next generation frontend tooling. It's fast!",
     "about": "Next generation frontend tooling. It's fast!",
     "stars": 70000, "language": "TypeScript",
     "url": "https://github.com/vitejs/vite", "project_images": []},
    {"id": 98629317, "name": "nest", "owner": "nestjs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/28507035?v=4",
     "description": "A progressive Node.js framework for building efficient, scalable, and enterprise-grade server-side applications.",
     "about": "A progressive Node.js framework for building efficient and scalable server-side applications.",
     "stars": 70000, "language": "TypeScript",
     "url": "https://github.com/nestjs/nest", "project_images": []},
    {"id": 9228334, "name": "d3", "owner": "d3",
     "owner_avatar": "https://avatars.githubusercontent.com/u/1562726?v=4",
     "description": "Bring data to life with SVG, Canvas and HTML.",
     "about": "Bring data to life with SVG, Canvas and HTML.",
     "stars": 109000, "language": "JavaScript",
     "url": "https://github.com/d3/d3", "project_images": []},
    {"id": 135079521, "name": "deno", "owner": "denoland",
     "owner_avatar": "https://avatars.githubusercontent.com/u/42048915?v=4",
     "description": "A modern runtime for JavaScript and TypeScript.",
     "about": "A modern runtime for JavaScript and TypeScript.",
     "stars": 100000, "language": "Rust",
     "url": "https://github.com/denoland/deno", "project_images": []},
    {"id": 305394143, "name": "langchain", "owner": "langchain-ai",
     "owner_avatar": "https://avatars.githubusercontent.com/u/126733545?v=4",
     "description": " Build context-aware reasoning applications",
     "about": " Build context-aware reasoning applications",
     "stars": 100000, "language": "Python",
     "url": "https://github.com/langchain-ai/langchain", "project_images": []},
    {"id": 15452919, "name": "axios", "owner": "axios",
     "owner_avatar": "https://avatars.githubusercontent.com/u/32372333?v=4",
     "description": "Promise based HTTP client for the browser and node.js",
     "about": "Promise based HTTP client for the browser and node.js",
     "stars": 106000, "language": "JavaScript",
     "url": "https://github.com/axios/axios", "project_images": []},
    {"id": 23096959, "name": "go", "owner": "golang",
     "owner_avatar": "https://avatars.githubusercontent.com/u/4314092?v=4",
     "description": "The Go programming language",
     "about": "The Go programming language",
     "stars": 125000, "language": "Go",
     "url": "https://github.com/golang/go", "project_images": []},
    {"id": 24195339, "name": "angular", "owner": "angular",
     "owner_avatar": "https://avatars.githubusercontent.com/u/139426?v=4",
     "description": "Deliver web apps with confidence 🚀",
     "about": "Deliver web apps with confidence 🚀",
     "stars": 96000, "language": "TypeScript",
     "url": "https://github.com/angular/angular", "project_images": []},
    {"id": 103680179, "name": "mermaid", "owner": "mermaid-js",
     "owner_avatar": "https://avatars.githubusercontent.com/u/57169982?v=4",
     "description": "Generation of diagrams like flowcharts or sequence diagrams from text in a similar manner as markdown",
     "about": "Generation of diagrams like flowcharts or sequence diagrams from text in a similar manner as markdown",
     "stars": 74000, "language": "TypeScript",
     "url": "https://github.com/mermaid-js/mermaid", "project_images": []},
    {"id": 15045751, "name": "compose", "owner": "docker",
     "owner_avatar": "https://avatars.githubusercontent.com/u/5429470?v=4",
     "description": "Define and run multi-container applications with Docker",
     "about": "Define and run multi-container applications with Docker",
     "stars": 35000, "language": "Go",
     "url": "https://github.com/docker/compose", "project_images": []},
    {"id": 37170176, "name": "scikit-learn", "owner": "scikit-learn",
     "owner_avatar": "https://avatars.githubusercontent.com/u/365630?v=4",
     "description": "scikit-learn: machine learning in Python",
     "about": "scikit-learn: machine learning in Python",
     "stars": 60000, "language": "Python",
     "url": "https://github.com/scikit-learn/scikit-learn", "project_images": []},
    {"id": 16148196, "name": "express", "owner": "expressjs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/5658226?v=4",
     "description": "Fast, unopinionated, minimalist web framework for node.",
     "about": "Fast, unopinionated, minimalist web framework for node.",
     "stars": 66000, "language": "JavaScript",
     "url": "https://github.com/expressjs/express", "project_images": []},
    {"id": 27556774, "name": "Chart.js", "owner": "chartjs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/10342521?v=4",
     "description": "Simple HTML5 Charts using the canvas tag",
     "about": "Simple HTML5 Charts using the canvas tag",
     "stars": 65000, "language": "JavaScript",
     "url": "https://github.com/chartjs/Chart.js", "project_images": []},
    {"id": 26944967, "name": "redux", "owner": "reduxjs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/13142323?v=4",
     "description": "A JS library for predictable global state management",
     "about": "A JS library for predictable global state management",
     "stars": 61000, "language": "TypeScript",
     "url": "https://github.com/reduxjs/redux", "project_images": []},
    {"id": 5751490, "name": "socket.io", "owner": "socketio",
     "owner_avatar": "https://avatars.githubusercontent.com/u/1163181?v=4",
     "description": "Realtime application framework (Node.JS server)",
     "about": "Realtime application framework (Node.JS server)",
     "stars": 61000, "language": "TypeScript",
     "url": "https://github.com/socketio/socket.io", "project_images": []},
    {"id": 7137200, "name": "lodash", "owner": "lodash",
     "owner_avatar": "https://avatars.githubusercontent.com/u/2565403?v=4",
     "description": "A modern JavaScript utility library delivering modularity, performance, & extras.",
     "about": "A modern JavaScript utility library delivering modularity, performance, & extras.",
     "stars": 60000, "language": "JavaScript",
     "url": "https://github.com/lodash/lodash", "project_images": []},
    {"id": 8514, "name": "rails", "owner": "rails",
     "owner_avatar": "https://avatars.githubusercontent.com/u/4223?v=4",
     "description": "Ruby on Rails",
     "about": "Ruby on Rails – web application framework",
     "stars": 56000, "language": "Ruby",
     "url": "https://github.com/rails/rails", "project_images": []},
    {"id": 26032793, "name": "vuex", "owner": "vuejs",
     "owner_avatar": "https://avatars.githubusercontent.com/u/6128107?v=4",
     "description": "🗃️ Centralized State Management for Vue.js.",
     "about": "🗃️ Centralized State Management for Vue.js.",
     "stars": 28000, "language": "TypeScript",
     "url": "https://github.com/vuejs/vuex", "project_images": []},
    {"id": 10360864, "name": "rxjs", "owner": "ReactiveX",
     "owner_avatar": "https://avatars.githubusercontent.com/u/6407041?v=4",
     "description": "A reactive programming library for JavaScript",
     "about": "A reactive programming library for JavaScript",
     "stars": 31000, "language": "TypeScript",
     "url": "https://github.com/ReactiveX/rxjs", "project_images": []},
    {"id": 273791931, "name": "bevy", "owner": "bevyengine",
     "owner_avatar": "https://avatars.githubusercontent.com/u/55303316?v=4",
     "description": "A refreshingly simple data-driven game engine built in Rust",
     "about": "A refreshingly simple data-driven game engine built in Rust",
     "stars": 37000, "language": "Rust",
     "url": "https://github.com/bevyengine/bevy", "project_images": []},
    {"id": 327738549, "name": "turborepo", "owner": "vercel",
     "owner_avatar": "https://avatars.githubusercontent.com/u/14985020?v=4",
     "description": "Build system optimized for JavaScript and TypeScript, written in Rust",
     "about": "Build system optimized for JavaScript and TypeScript, written in Rust",
     "stars": 27000, "language": "Rust",
     "url": "https://github.com/vercel/turborepo", "project_images": []},
    {"id": 498810529, "name": "openai-python", "owner": "openai",
     "owner_avatar": "https://avatars.githubusercontent.com/u/14957082?v=4",
     "description": "The official Python library for the OpenAI API",
     "about": "The official Python library for the OpenAI API",
     "stars": 25000, "language": "Python",
     "url": "https://github.com/openai/openai-python", "project_images": []},
]

PAGE_SIZE = 12


def _github_headers():
    h = {"Accept": "application/vnd.github+json", "User-Agent": "OtterHub-App/1.0"}
    token = getattr(settings, 'GITHUB_TOKEN', '')
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _filter_static_by_language(lenguaje: str, page: int, per_page: int):
    """Filtra STATIC_REPOS por lenguaje (case-insensitive) con paginación."""
    lang_lower = lenguaje.lower()
    filtered = [r for r in STATIC_REPOS if (r.get("language") or "").lower() == lang_lower]
    start = (page - 1) * per_page
    return filtered[start:start + per_page], len(filtered)


def _fetch_repos_github(lenguaje, page, per_page):
    """Búsqueda por lenguaje usando Search API con fallback a datos estáticos."""
    url = (
        f"https://api.github.com/search/repositories"
        f"?q=language:{lenguaje}+stars:>1000&sort=stars&order=desc"
        f"&page={page}&per_page={per_page}"
    )
    headers = _github_headers()
    try:
        response = requests.get(url, headers=headers, timeout=6)
    except Exception:
        # Red caída → fallback estático
        repos, total = _filter_static_by_language(lenguaje, page, per_page)
        return {
            "lenguaje": lenguaje, "page": page, "per_page": per_page,
            "total": total, "repos": repos, "source": "local",
        }, None

    if response.status_code != 200:
        # Rate limit u otro error → fallback estático
        repos, total = _filter_static_by_language(lenguaje, page, per_page)
        return {
            "lenguaje": lenguaje, "page": page, "per_page": per_page,
            "total": total, "repos": repos, "source": "local",
        }, None

    data = response.json()
    items = data.get("items", [])

    if not items:
        # GitHub devolvió lista vacía (rate limit secundario) → fallback
        repos, total = _filter_static_by_language(lenguaje, page, per_page)
        return {
            "lenguaje": lenguaje, "page": page, "per_page": per_page,
            "total": total, "repos": repos, "source": "local",
        }, None

    repos = []
    for repo in items:
        repos.append({
            "id":           repo["id"],
            "name":         repo["name"],
            "description":  repo.get("description"),
            "about":        repo.get("description") or "Sin descripción",
            "stars":        repo["stargazers_count"],
            "language":     repo.get("language"),
            "url":          repo["html_url"],
            "owner_avatar": repo["owner"]["avatar_url"],
            "owner":        repo["owner"]["login"],
            "project_images": [],
        })

    return {
        "lenguaje": lenguaje, "page": page, "per_page": per_page,
        "total": data.get("total_count"), "repos": repos, "source": "github",
    }, None


# ── Views ─────────────────────────────────────────────────────────────────────

class ReposPorLenguajeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lenguaje   = request.query_params.get('lenguaje', '').strip()
        query_text = request.query_params.get('q', '').strip()
        page       = max(1, int(request.query_params.get('page', 1)))
        per_page   = min(30, int(request.query_params.get('per_page', 12)))

        # ── Búsqueda por texto ──
        if query_text:
            cache_key = f"search_{query_text}_{page}"
            cached = cache.get(cache_key)
            if cached:
                return Response(cached)

            # Buscar primero en estáticos (instantáneo)
            q_lower = query_text.lower()
            local = [
                r for r in STATIC_REPOS
                if q_lower in r["name"].lower()
                or q_lower in (r.get("description") or "").lower()
                or q_lower in (r.get("language") or "").lower()
            ]

            # Intentar también GitHub API
            headers = _github_headers()
            url = (
                f"https://api.github.com/search/repositories"
                f"?q={requests.utils.quote(query_text)}&sort=stars&order=desc"
                f"&page={page}&per_page={per_page}"
            )
            try:
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    if items:
                        repos = [{
                            "id": r["id"], "name": r["name"],
                            "description": r.get("description"),
                            "about": r.get("description") or "Sin descripción",
                            "stars": r["stargazers_count"], "language": r.get("language"),
                            "url": r["html_url"], "owner_avatar": r["owner"]["avatar_url"],
                            "owner": r["owner"]["login"], "project_images": [],
                        } for r in items]
                        result = {"repos": repos, "page": page,
                                  "total": resp.json().get("total_count"), "source": "github"}
                        cache.set(cache_key, result, CACHE_TTL_SHORT)
                        return Response(result)
            except Exception:
                pass

            # Fallback: resultados locales
            start = (page - 1) * per_page
            paged = local[start:start + per_page]
            result = {"repos": paged, "page": page, "total": len(local), "source": "local"}
            if paged:
                cache.set(cache_key, result, CACHE_TTL_SHORT)
            return Response(result)

        # ── Búsqueda por lenguaje ──
        if not lenguaje:
            return Response({"error": "Envía lenguaje o q"}, status=400)

        cache_key = f"lang_{lenguaje}_{page}_{per_page}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        result, _ = _fetch_repos_github(lenguaje, page, per_page)
        if result.get("repos"):
            cache.set(cache_key, result, CACHE_TTL)
        return Response(result)


class ReposPopularesPublicosView(APIView):
    """Repos populares desde datos estáticos — respuesta instantánea."""
    permission_classes = [AllowAny]

    def get(self, request):
        page  = max(1, int(request.query_params.get('page', 1)))
        start = (page - 1) * PAGE_SIZE
        end   = start + PAGE_SIZE
        repos = STATIC_REPOS[start:end]
        return Response({
            "repos": repos,
            "page": page,
            "total": len(STATIC_REPOS),
            "source": "local",
        })


class ReposTendenciasView(APIView):
    """Repos trending del último mes con fallback a estáticos."""
    permission_classes = [AllowAny]

    def get(self, request):
        lenguaje = request.query_params.get('lenguaje', '').strip()
        page     = max(1, int(request.query_params.get('page', 1)))

        cache_key = f"tendencias_v3_{lenguaje}_{page}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        from datetime import datetime, timedelta
        hace_30 = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
        q = f"created:>{hace_30} stars:>50"
        if lenguaje:
            q += f" language:{lenguaje}"

        headers = _github_headers()
        url = (
            f"https://api.github.com/search/repositories"
            f"?q={requests.utils.quote(q)}&sort=stars&order=desc"
            f"&page={page}&per_page=12"
        )
        try:
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if items:
                    repos = [{
                        "id": r["id"], "name": r["name"],
                        "description": r.get("description"),
                        "about": r.get("description") or "Sin descripción",
                        "stars": r.get("stargazers_count", 0), "language": r.get("language"),
                        "url": r["html_url"], "owner_avatar": r["owner"]["avatar_url"],
                        "owner": r["owner"]["login"], "project_images": [],
                    } for r in items]
                    result = {"repos": repos, "page": page, "source": "github"}
                    cache.set(cache_key, result, CACHE_TTL_SHORT)
                    return Response(result)
        except Exception:
            pass

        # Fallback: mostrar populares filtrados como "tendencias"
        if lenguaje:
            repos, _ = _filter_static_by_language(lenguaje, page, 12)
        else:
            start = (page - 1) * 12
            repos = STATIC_REPOS[start:start + 12]

        result = {"repos": repos, "page": page, "source": "local",
                  "msg": "Mostrando repos populares. Añade GITHUB_TOKEN al servidor para ver tendencias reales."}
        return Response(result)
