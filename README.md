# diff.blog

diff.blog is an aggregator of developer blogs.

Our mission is to bring visibility to great self hosted developer blogs and fight against centralized blogging platforms like Medium.

Read more at https://diff.blog/FAQ

---

## Dev Environment Setup

### 1. **Install Docker-Compose**

Get docker-compose [here](https://docs.docker.com/compose/install/).

### 2. **Clone the Repository**

```bash
git clone https://github.com/diffblog/diff.blog
```

### 3. **Run the Setup Script**

```bash
cd diff.blog
docker-compose run web ./scripts/setup_docker_dev_env
```

### 4. **Start the Development Server**

```bash
docker-compose up
```

Visit [http://localhost:8000/](http://localhost:8000/) to access the local server.
