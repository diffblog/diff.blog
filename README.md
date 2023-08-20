# diff.blog

In a world increasingly dominated by centralized platforms, diff.blog takes a stand for the independent voices of the internet. Our mission is clear and vital: *Revive and amplify the power of self-hosted blogs.*

**Our Goals:**

1. **Champion the Underdogs**: We spotlight posts from self-hosted blogs, ensuring they don't get overshadowed by big platforms.
2. **Build Better Tools**: We're crafting tools to make self-hosting not just feasible, but desirable.

---

## Join the Revolution

This repository powers [diff.blog](https://diff.blog). If you believe in a decentralized web and the power of individual voices, we want you on board.
"`
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
