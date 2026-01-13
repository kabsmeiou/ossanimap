# ossanimap

ossanimap is an osu! beatmapset packager that aggregates ranked/loved osu! beatmaps into downloadable packages grouped by the anime name.

### Why create ossanimap?

ossanimap is created to simplify the process of searching and downloading the songs from the anime series you love! It fetches all the ranked maps associated with the anime name and bundles them into a downloadable artifact. 

### Who is ossanimap for?

ossanimap is for those who want to save time downloading all the songs from an anime series, especially long running ones with lots of OSTs. It is mainly for me!

have fun!

## Setup

Running ossanimap locally is very simple! Just follow the steps below and you'll have it on your localhost:


### Environment Variables
Before running the application, you need to set up some environment variables for the backend. Create a `.env` file in the `backend` directory with the following content:

#### backend/.env
```
DATABASE_URL=sqlite+aiosqlite:///./ossanimap.db
OSU_CLIENT_ID=your_osu_client_id
OSU_CLIENT_SECRET=your_osu_client_secret
```

### Step 1: Cloning the repository

```bash
git clone https://github.com/kabsmeiou/ossanimap.git
cd ossanimap
```

Once cloned, you must open another terminal window. This is important to run both the backend and the frontend servers.

### Step 2A: Setting up the backend

There are two ways to set up the backend: using **uv** or using **pip**.

```
Note: always create a virtual environment before installing dependencies!
```

#### Option 1: Using uv (assuming you have uv installed if not, visit https://docs.astral.sh/uv/getting-started/installation/)
```bash
cd backend
uv sync
```

#### Option 2: Using pip
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Step 2B: Running the backend server

The backend uses uvicorn so you can run it using the command below:
```bash
uv run app.main:app --reload
```

### Step 3A: Setting up the frontend

On another terminal window, navigate to the `frontend` directory and install the dependencies.

Requirements (recommended): Node v20.19.5

```bash
cd ../frontend
npm install
```

### Step 3B: Running the frontend server

```bash
npm run dev
```

That is all! You can now access the ossanimap web app at `http://localhost:5173` (or the port shown in your terminal).


## Usage

Using ossanimap is very simple! Just enter the name of the anime you want to download the beatmapset pack for in the search bar and click on the suggestion that appears. The backend will process your request and generate a downloadable package for you.

